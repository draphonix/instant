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

@cli.command()
@click.option('--prefix', default='brick', prompt='Give me the instance prefix',
              help='This helps filter the instances result.')
@click.option('--aws-profile', default=os.getenv("AWS_PROFILE"), 
              help='AWS profile to use (optional).')
@click.option('--aws-region', default=os.getenv("AWS_REGION"), 
              help='AWS region to use (optional).')
def update_ssh_profile(prefix, aws_profile, aws_region):
    """
    Update or create a new SSH profile in ~/.ssh/config for the selected EC2 instance.

    Parameters:
    - prefix: str - The prefix to filter instances.
    - aws_profile: str - The AWS profile to use.
    - aws_region: str - The AWS region to use.
    """
    aws_helper = AwsHelper(aws_profile, aws_region)
    result = aws_helper.select_instance(prefix)
    
    if not result:
        click.echo(f"No running instances found with prefix {prefix}")
        return
    
    instance_name = result.name
    instance_ip = result.public_ip
    ssh_user = os.getenv('SSH_USER')
    key_path = os.getenv('KEY_PATH')
    
    ssh_config_path = os.path.expanduser('~/.ssh/config')
    new_config = f"""
Host {instance_name}
    HostName {instance_ip}
    User {ssh_user}
    IdentityFile {key_path}
    RemoteCommand sudo -i
"""
    # Read existing config
    if os.path.exists(ssh_config_path):
        with open(ssh_config_path, 'r') as ssh_config_file:
            existing_config = ssh_config_file.read()
    else:
        existing_config = ""

    # Remove existing config for the instance if it exists
    if f"Host {instance_name}" in existing_config:
        existing_config = existing_config.split(f"Host {instance_name}")[0]

    # Append new config
    with open(ssh_config_path, 'w') as ssh_config_file:
        ssh_config_file.write(existing_config + new_config)
    
    click.echo(f"SSH profile for {instance_name} updated/created in {ssh_config_path}")

if __name__ == '__main__':
    cli()