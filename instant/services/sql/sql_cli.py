import click
import os
from instant.utils.constants import DEFAULT_REGIONS, IGNORED_TABLES
from sql_helper import SqlHelper
from aws.aws_helper import AwsHelper
from instant.utils.general_helper import GeneralHelper

@click.group()
def cli():
    """SQL CLI commands."""
    pass

@cli.command()
@click.option('--prefix', default='brick', prompt='Give me the instance prefix',
              help='This helps filter the instances result.')
def dump_data(prefix):
    """Dump RDS data to local."""
    click.echo("Select the AWS region:")
    for index, region in enumerate(DEFAULT_REGIONS, start=1):
        click.echo(f"{index}. {region}")
    
    choice = click.prompt("Enter the number of your choice", type=int)
    region = DEFAULT_REGIONS[choice - 1]
    click.echo(f"Selected region: {region}, prefix {prefix}")

    
    # Lets find the instance with prefix in the selected region
    aws_helper = AwsHelper(aws_profile= os.getenv("AWS_PROFILE"), aws_region=region)
    instances = aws_helper.get_running_instances(prefix)
    
    if not instances:
        click.echo("No running instances found with the given prefix.")
        return

    instance_names = [instance.name for instance in instances]
    selected_instance_name = GeneralHelper.select_option(instance_names)
    selected_instance = next(instance for instance in instances if instance.name == selected_instance_name)

    # List available RDS instances in the selected region
    list_rds = aws_helper.list_available_rds()
    rds_endpoints = [rds.endpoint for rds in list_rds]
    selected_rds_endpoint = GeneralHelper.select_option(rds_endpoints)

    # First init the SqlHelper
    sql_helper = SqlHelper(
        ssh_host=selected_instance.public_ip,  # Assuming the instance has a public IP
        ssh_port=22,  # Default SSH port
        ssh_user=os.getenv('SSH_USER'),  # Adjust as necessary
        ssh_pkey=os.getenv('KEY_PATH'),  # Adjust the path to your SSH key
        rds_host=selected_rds_endpoint,
        rds_port=int(os.getenv('RDS_PORT')),  # Default RDS port
        rds_user=os.getenv('RDS_USER'),  # Adjust as necessary
        rds_password=os.getenv('RDS_PASSWORD'),  # Replace with actual password
        rds_db=os.getenv('RDS_DB'),  # Adjust as necessary
    )

    filtered_tables = sql_helper.get_filtered_table_names(IGNORED_TABLES)
    click.echo(f"filtered_tables {filtered_tables}")
    # Perform the dump_data process
    sql_helper.dump_data(
        tables_to_dump=filtered_tables,  # Replace with your table names
    )

@cli.command()
@click.option('--prefix', default='brick', prompt='Give me the instance prefix',
              help='This helps filter the instances result.')
@click.option('--aws-profile', default=os.getenv("AWS_PROFILE"), 
              help='AWS profile to use (optional).')
@click.option('--source-folder', prompt='Please provide the source data folder', help='Exported data folder' )
def import_data(prefix, aws_profile, source_folder):
    """Import SQL files from a specified folder into the database."""
    click.echo("Select the AWS region:")
    for index, region in enumerate(DEFAULT_REGIONS, start=1):
        click.echo(f"{index}. {region}")
    
    choice = click.prompt("Enter the number of your choice", type=int)
    region = DEFAULT_REGIONS[choice - 1]
    click.echo(f"Selected region: {region}, prefix {prefix}")

    # Initialize the AWS helper
    aws_helper = AwsHelper(aws_profile=aws_profile, aws_region=region)
    instances = aws_helper.get_running_instances(prefix)
    
    if not instances:
        click.echo("No running instances found with the given prefix.")
        return

    instance_names = [instance.name for instance in instances]
    selected_instance_name = GeneralHelper.select_option(instance_names)
    selected_instance = next(instance for instance in instances if instance.name == selected_instance_name)

    # List available RDS instances in the selected region
    list_rds = aws_helper.list_available_rds()
    rds_endpoints = [rds.endpoint for rds in list_rds]
    selected_rds_endpoint = GeneralHelper.select_option(rds_endpoints)

    # Initialize the SqlHelper
    sql_helper = SqlHelper(
        ssh_host=selected_instance.public_ip,
        ssh_port=22,
        ssh_user=os.getenv('SSH_USER'),
        ssh_pkey=os.getenv('KEY_PATH'),
        rds_host=selected_rds_endpoint,
        rds_port=int(os.getenv('RDS_PORT')),
        rds_user=os.getenv('RDS_USER'),
        rds_password=os.getenv('RDS_PASSWORD'),
        rds_db=os.getenv('RDS_DB'),
    )

    # Call the import_data method
    sql_helper.import_data(sql_folder=source_folder)