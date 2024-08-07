import click
from aws.aws_helper import AwsHelper
import os
import subprocess

@click.group()
def cli():
    """SSH CLI commands."""
    pass

@cli.command()
@click.option('--prefix', default='brick', prompt='Give me the instance prefix',
              help='This helps filter the instances result.')
@click.option('--aws-profile', default=os.getenv("AWS_PROFILE"), 
              help='AWS profile to use (optional).')
@click.option('--aws-region', default=os.getenv("AWS_REGION"), 
              help='AWS region to use (optional).')
def ssh_to_instance(prefix, aws_profile, aws_region):
    """
    Fetch the instance based on prefix and perform SSH to that instance.
    """
    aws_helper = AwsHelper(aws_profile, aws_region)  # Pass the required arguments
    result = aws_helper.select_instance(prefix)
    
    if not result:
        click.echo(f"No running instances found with prefix {prefix}")
        return
    
    instance_ip = result.public_ip
    click.echo(f"Connecting to instance with IP: {instance_ip}")
    
    # Perform SSH
    ssh_command = f"ssh -i {os.getenv('KEY_PATH')} {os.getenv('SSH_USER')}@{instance_ip}"
    subprocess.run(ssh_command, shell=True)

if __name__ == '__main__':
    cli()