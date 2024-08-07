import click
from aws_helper import AwsHelper
import os

@click.group()
def cli():
    """AWS CLI commands."""
    pass

@cli.command()
@click.option('--prefix', default='brick', prompt='Give me the instance prefix',
              help='This helps filter the instances result.')
@click.option('--aws-profile', default=os.getenv("AWS_PROFILE"), 
              help='AWS profile to use (optional).')
@click.option('--aws-region', default=os.getenv("AWS_REGION"), 
              help='AWS region to use (optional).')
def get_ip(prefix, aws_profile, aws_region):
    """Say hello from AWS CLI."""
    click.echo(f'Hello from AWS CLI! {prefix}')
    aws_helper = AwsHelper(aws_profile, aws_region)  # Pass the required arguments
    result = aws_helper.get_running_instances(prefix)
    click.echo(f"Results {result}")