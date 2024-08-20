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

def get_ssh_targets():
    """
    Retrieve the list of HostNames from the SSH config file.

    Returns:
    - List of HostNames.
    """
    ssh_config_path = os.path.expanduser('~/.ssh/config')
    if not os.path.exists(ssh_config_path):
        return []

    with open(ssh_config_path, 'r') as ssh_config_file:
        lines = ssh_config_file.readlines()

    hostnames = [line.split()[1] for line in lines if line.startswith('Host ')]
    return hostnames

@cli.command()
@click.option(
    '--ssh-target', 
    type=click.Choice(get_ssh_targets()), 
    prompt='SSH target (e.g., user@host)', 
    help='The SSH target to connect to.',
    default=lambda: 'wwe-brick' if get_ssh_targets() else None
)
def deploy_and_restart(ssh_target):
    """
    Deploy the current branch to the remote instance and restart the project.

    Parameters:
    - ssh_target: str - The SSH target to connect to.
    """
    # Get the current branch of the project
    project_path = os.getenv('PROJECT_LOCAL_PATH')
    current_branch = subprocess.check_output(
        ['git', '-C', project_path, 'rev-parse', '--abbrev-ref', 'HEAD']
    ).strip().decode('utf-8')
    
    click.echo(f"Current branch: {current_branch}")
    
    # Get the list of changed files
    changed_files = subprocess.check_output(
        ['git', '-C', project_path, 'diff', '--name-only', 'HEAD']
    ).strip().decode('utf-8').split('\n')
    
    click.echo(f"Changed files: {changed_files}")
    
    # SSH and perform operations
    project_remote_path = os.getenv('PROJECT_REMOTE_PATH')
    temp_remote_path = "/tmp/deploy_temp"
    ssh_commands = f"""
ssh -T {ssh_target} << 'EOF'
cd {project_remote_path}
sudo git stash
sudo git checkout {current_branch}
sudo git pull
mkdir -p {temp_remote_path}
EOF
    """
    click.echo(ssh_commands)
    subprocess.run(ssh_commands, shell=True)
    
#     # Copy changed files to a temporary directory on the remote instance
    for file in changed_files:
        local_file_path = os.path.join(project_path, file)
        remote_temp_file_path = os.path.join(temp_remote_path, file)
        remote_temp_dir = os.path.dirname(remote_temp_file_path)
        click.echo(f'remote temp dir: {remote_temp_dir}')
        # Create the necessary directories on the remote server
        ssh_mkdir_command = f"ssh -T {ssh_target} 'mkdir -p {remote_temp_dir}'"
        subprocess.run(ssh_mkdir_command, shell=True)
        
        # Copy the file to the remote server
        scp_command = f"scp {local_file_path} {ssh_target}:{remote_temp_file_path}"
        subprocess.run(scp_command, shell=True)
    
    # SSH and move files to the desired location with sudo, then restart
    ssh_commands = f"""
ssh -T {ssh_target} << 'EOF'
cd {project_remote_path}
sudo cp -r {temp_remote_path}/* {project_remote_path}/
sudo rm -rf {temp_remote_path}
sudo {os.getenv('PROJECT_RESTART_COMMAND')}
EOF
    """
    subprocess.run(ssh_commands, shell=True)
    click.echo(f"Project on branch {current_branch} deployed and restarted on {ssh_target}")

if __name__ == '__main__':
    cli()