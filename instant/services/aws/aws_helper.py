import boto3
import os
import subprocess
from instant.utils.constants import DEFAULT_REGIONS
from aws.models.models import Ec2InstanceResponse, RdsInstanceResponse
from instant.utils.general_helper import GeneralHelper


class AwsHelper:
    def __init__(self, aws_profile: None, aws_region: None):
        self.aws_profile = os.getenv("AWS_PROFILE") if aws_profile is None else aws_profile 
        self.aws_region = os.getenv("AWS_REGION") if aws_region is None else aws_region
        # Prompt for AWS region if not provided
        if self.aws_region is None:
            self.aws_region = self._prompt_for_region()

        self.session = boto3.Session(profile_name=self.aws_profile, region_name=self.aws_region)
        self.ec2 = self.session.resource("ec2")

        try:
            self.session.client("sts").get_caller_identity()
        except Exception:
            print("Error: Token has expired. Attempting to log in to AWS SSO...")
            subprocess.run(["aws", "sso", "login", "--profile", self.aws_profile])
            self.session = boto3.Session(profile_name=self.aws_profile, region_name=self.aws_region)

    def _prompt_for_region(self) -> str:
        """Prompt the user to select an AWS region from predefined options."""
        for index, region in enumerate(DEFAULT_REGIONS, start=1):
            print(f"{index}. {region}")
        choice = input("Enter the number of your choice: ")
        return DEFAULT_REGIONS[int(choice) - 1]  # Return the selected region
    
    def get_running_instances(self, prefix: str) -> list[Ec2InstanceResponse]:
        """Retrieve a list of running EC2 instances filtered by the given prefix."""
        filters = [
            {"Name": "instance-state-name", "Values": ["running"]},
            {"Name": "tag:Name", "Values": [f"*{prefix}*"]},
        ]

        instances = self.ec2.instances.filter(Filters=filters)
        return [
            Ec2InstanceResponse(
                instance_id=instance.id,
                name=self._get_instance_name(instance),
                public_ip=instance.public_ip_address
            )
            for instance in instances
        ]

    def select_instance(self, prefix: str) -> Ec2InstanceResponse:
        instances = self.get_running_instances(prefix)

        if not instances:
            print("No running instances found with the given prefix.")
            exit(1)

        options = [instance.name for instance in instances]
        selected = GeneralHelper.select_option(options)
        return next(instance for instance in instances if instance.name == selected)

    @staticmethod
    def _get_instance_name(instance) -> str:
        for tag in instance.tags:
            if tag["Key"] == "Name":
                return tag["Value"]
        return ""

    def list_available_rds(self) -> list[RdsInstanceResponse]:
        """List all available RDS instances in the selected region, including their host endpoints."""
        rds_client = self.session.client("rds")
        response = rds_client.describe_db_instances()
        return [
            RdsInstanceResponse(
                db_instance_identifier=db["DBInstanceIdentifier"],
                db_instance_status=db["DBInstanceStatus"],
                endpoint=db["Endpoint"]["Address"] if "Endpoint" in db else None,  # Get the host endpoint
            )
            for db in response["DBInstances"]
        ]