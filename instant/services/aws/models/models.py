class Ec2InstanceResponse:
    """Model representing an EC2 instance."""
    def __init__(self, instance_id: str, name: str, public_ip: str):
        self.id = instance_id
        self.name = name
        self.public_ip = public_ip

    def __repr__(self):
        return f"Instance(ID={self.id}, Name={self.name}, PublicIpAddress={self.public_ip})"

class RdsInstanceResponse:
    """Model representing an RDS instance."""
    def __init__(self, db_instance_identifier: str, db_instance_status: str, endpoint: str):
        self.db_instance_identifier = db_instance_identifier
        self.db_instance_status = db_instance_status
        self.endpoint = endpoint

    def __repr__(self):
        return f"RDSInstance(ID={self.db_instance_identifier}, Status={self.db_instance_status}, Endpoint={self.endpoint})"