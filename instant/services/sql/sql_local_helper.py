import os
import subprocess
from multiprocessing import Pool

def import_single_file_local(sql_file, sql_folder, rds_host, rds_port, rds_user, rds_password, rds_db):
        """
        Import a single SQL file into the local database.

        Args:
            sql_file (str): The name of the SQL file to import.
            sql_folder (str): The folder containing the SQL files.
        """
        dump_file_path = os.path.join(sql_folder, sql_file)
        mysql_command = [
            "/usr/local/bin/mysql",
            "--defaults-file=" + os.path.join(os.path.dirname(__file__), '.db.cnf'),  # Update path here
            f"--database={ rds_db}",
            f"--host={rds_host}",
            f"--port={rds_port}",
            f"--user={rds_user}",
            f"--password={rds_password}",
        ]

        # Run the mysql command
        print(f"Importing data from {sql_file}...")
        with open(dump_file_path, "r") as f:
            subprocess.run(
                mysql_command, stdin=f, check=True, capture_output=True, text=True
            )

        print(f"Data import completed for {sql_file}")

class SqlLocalHelper:
    def __init__(self, rds_host, rds_port, rds_user, rds_password, rds_db):
        """
        Initialize the SqlLocalHelper with the necessary database connection details.

        Args:
            rds_host (str): The RDS host.
            rds_port (int): The RDS port.
            rds_db (str): The RDS database name.
        """
        self.rds_host = rds_host
        self.rds_port = rds_port
        self.rds_user = rds_user
        self.rds_password = rds_password
        self.rds_db = rds_db


    def import_data_local(self, sql_folder):
        """
        Import SQL files from a specified folder into the local database.

        Args:
            sql_folder (str): The folder containing the SQL files.
        """
        # Get all SQL files from the specified folder
        sql_files = [f for f in os.listdir(sql_folder) if f.endswith(".sql")]

        # Create a pool of 5 processes
        with Pool(processes=5) as pool:
            # Use pool to import all SQL files
            pool.starmap(
                import_single_file_local,
                [
                    (sql_file, sql_folder, self.rds_host, self.rds_port, self.rds_user, self.rds_password, self.rds_db)
                    for sql_file in sql_files
                ],
            )