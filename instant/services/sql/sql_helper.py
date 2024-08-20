import os
from sshtunnel import SSHTunnelForwarder
from datetime import datetime
import random
import subprocess
from multiprocessing import Manager, Pool
import pymysql
import time

def run_dump(
    chunk,
    process_num,
    ssh_host,
    ssh_port,
    ssh_user,
    ssh_pkey,
    rds_host,
    rds_port,
    rds_db,
    timestamp_folder,
):
    dump_file = os.path.join("exported_sqls", timestamp_folder, f"{timestamp_folder}_{process_num}.sql")
    # Set up the SSH tunnel
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_pkey=ssh_pkey,
        remote_bind_address=(rds_host, rds_port),
        local_bind_address=("127.0.0.1", random.randint(57000, 57999)),  # Local port for the tunnel
    ) as tunnel:
        print(f"Tunnel established on port {tunnel.local_bind_port}")

        # Define the mysqldump command
        mysqldump_command = [
            "/usr/local/bin/mysqldump",
            "--defaults-file=" + os.path.join(os.path.dirname(__file__), '.db.cnf'),  # Update path here
            "--set-gtid-purged=OFF",  # Disable GTID purging
            "--single-transaction",  # Ensure a consistent dump
            rds_db,
            *chunk,  # Unpack the chunk list directly into the command
            f"--result-file={dump_file}",  # Use the correct path for the result file
            "--no-tablespaces",
            "--add-drop-trigger",
            "--host=127.0.0.1",
            f"--port={tunnel.local_bind_port}",
        ]

        # Run the mysqldump command
        try:
            subprocess.run(mysqldump_command, check=True, capture_output=True, text=True)
            print(f"Dump completed successfully for process {process_num}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred in process {process_num}: {e.stderr}")


def import_single_file(
    sql_file, ssh_host, ssh_port, ssh_user, ssh_pkey, rds_host, rds_port, rds_db, sql_folder
):
    dump_file_path = os.path.join(sql_folder, sql_file)
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_pkey=ssh_pkey,
        remote_bind_address=(rds_host, rds_port),
    ) as tunnel:
        # Define the mysql command for importing
        mysql_command = [
            "/usr/local/bin/mysql",
            "--defaults-file=" + os.path.join(os.path.dirname(__file__), '.db.cnf'),  # Update path here
            f"--database={rds_db}",
            "--host=127.0.0.1",
            f"--port={tunnel.local_bind_port}",
        ]

        # Run the mysql command
        print(f"Importing data from {sql_file}...")
        with open(dump_file_path, "r") as f:
            subprocess.run(
                mysql_command, stdin=f, check=True, capture_output=True, text=True
            )

        print(f"Data import completed for {sql_file}")


class SqlHelper:
    def __init__(self, ssh_host, ssh_port, ssh_user, ssh_pkey, rds_host, rds_port, rds_user, rds_password, rds_db):
        os.makedirs("exported_sqls", exist_ok=True)  # Create exported_sqls directory if it does not exist
        self.timestamp_folder = datetime.now().strftime("%Y%m%d")
        self.dump_file_base = f"./exported_sqls/{self.timestamp_folder}/"
        os.makedirs(self.dump_file_base, exist_ok=True)  # Create timestamped folder if it does not exist

        # Store parameters
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_user = ssh_user
        self.ssh_pkey = ssh_pkey
        self.rds_host = rds_host
        self.rds_port = rds_port
        self.rds_user = rds_user
        self.rds_password = rds_password
        self.rds_db = rds_db

    def dump_data(self, tables_to_dump):
        start_time = time.time()  # Start the timer

        # Split tables into chunks of 20
        chunk_size = 20
        if len(tables_to_dump) < chunk_size:
            chunks = [tables_to_dump]  # Use the entire list as a single chunk
        else:
            chunks = [
                tables_to_dump[i : i + chunk_size] for i in range(0, len(tables_to_dump), chunk_size)
            ]

        # Create a manager to handle shared state
        with Manager() as manager:
            manager.list()  # To track completed processes

            # Create a pool with the appropriate number of processes
            num_processes = min(5, len(chunks))  # Limit to 5 or the number of chunks
            with Pool(processes=num_processes) as pool:
                pool.starmap(
                    run_dump,
                    [
                        (
                            chunk,
                            i,
                            self.ssh_host,
                            self.ssh_port,
                            self.ssh_user,
                            self.ssh_pkey,
                            self.rds_host,
                            self.rds_port,
                            self.rds_db,
                            self.timestamp_folder,
                        )
                        for i, chunk in enumerate(chunks, start=1)
                    ],
                )

        end_time = time.time()  # End the timer
        processing_time = end_time - start_time  # Calculate the processing time
        print(f"All dump processes completed in {processing_time:.2f} seconds.")

    def import_data(
        self, sql_folder
    ):
        """Import SQL files from a specified folder into the database using mysqldump."""
        # Get all SQL files from the specified folder
        sql_files = [f for f in os.listdir(sql_folder) if f.endswith(".sql")]

        # Create a pool of 5 processes
        with Pool(processes=5) as pool:
            # Use pool to import all SQL files
            pool.starmap(
                import_single_file,
                [
                    (
                        sql_file,
                        self.ssh_host,
                        self.ssh_port,
                        self.ssh_user,
                        self.ssh_pkey,
                        self.rds_host,
                        self.rds_port,
                        self.rds_db,
                        sql_folder,
                    )
                    for sql_file in sql_files
                ],
            )

    def get_filtered_table_names(self, ignore_tables_prefix):
        """
        Retrieve table names from the database, filtering out those that start with the specified prefix.

        Args:
            ignore_tables_prefix (str): The prefix of table names to ignore.

        Returns:
            list: A list of table names that do not start with the specified prefix.
        """
        # Assuming you have a method to get all table names from the database
        all_tables = self.get_all_table_names()  # This method should be implemented to fetch all table names
        filtered_tables = [table for table in all_tables if not any(table.startswith(prefix) for prefix in ignore_tables_prefix)]
        return filtered_tables

    def get_all_table_names(self):
        """
        Retrieve all table names from the RDS database using an SSH tunnel.

        Returns:
            list: A list of all table names in the database.
        """
        with SSHTunnelForwarder(
            (self.ssh_host, self.ssh_port),
            ssh_username=self.ssh_user,
            ssh_pkey=self.ssh_pkey,
            remote_bind_address=(self.rds_host, self.rds_port),
        ) as tunnel:
            # Connect to the database through the tunnel
            connection = self.create_db_connection(tunnel.local_bind_port)
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES;")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            connection.close()
        return tables

    def create_db_connection(self, local_port):
        """
        Create a database connection to the RDS instance.

        Args:
            local_port (int): The local port to connect through the SSH tunnel.

        Returns:
            connection: A connection object to the RDS database.
        """
        connection = pymysql.connect(
            host='127.0.0.1',  # Connect to the local port
            port=local_port,
            user=self.rds_user,
            password=self.rds_password,
            database=self.rds_db
        )
        return connection