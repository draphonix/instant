import paramiko

class SshHelper:
    def __init__(self, hostname: str, username: str, key_path: str):
        self.hostname = hostname
        self.username = username
        self.key_path = key_path
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        private_key = paramiko.RSAKey(filename=self.key_path)
        self.ssh_client.connect(hostname=self.hostname, username=self.username, pkey=private_key)

    def execute_command(self, command: str) -> str:
        stdout= self.ssh_client.exec_command(command)
        return stdout.read().decode()

    def close_connection(self):
        self.ssh_client.close()

