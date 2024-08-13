import click
import os
from datetime import datetime, timedelta
from jira.jira_helper import JiraHelper
from instant.utils.cookies_decrypt import ChromeCookiesDecrypt

@click.group()
def cli():
    """JIRA CLI commands."""
    pass

@cli.command()
@click.option('--email', default=lambda: os.getenv('JIRA_EMAIL'), help='The email of the user.')
@click.option('--token', default=lambda: os.getenv('JIRA_PAT'), help='The authorization token.')
@click.option('--use-cookie', is_flag=True, default=False, help='Use cookies for authentication.')
@click.option('--start-timestamp', default=None, type=int, help='Start of the time range (Unix timestamp).')
@click.option('--end-timestamp', default=None, type=int, help='End of the time range (Unix timestamp).')
def get_activity(email, token, use_cookie, start_timestamp, end_timestamp):
    """Fetch and extract today's activities from JIRA."""
    cookies = ChromeCookiesDecrypt().get_cookie_str() if use_cookie else None
    jira_helper = JiraHelper(cookies)

    if not start_timestamp or not end_timestamp:
        today = datetime.utcnow().date()
        start_timestamp = int(datetime(today.year, today.month, today.day).timestamp()) * 1000
        end_timestamp = int((datetime(today.year, today.month, today.day) + timedelta(days=1)).timestamp()) * 1000

    activity_stream = jira_helper.get_activity_stream(email, start_timestamp, end_timestamp, token)
    activities = jira_helper.extract_today_activities(activity_stream)

    for activity in activities.values():
        click.echo(f'{activity.issue_title}')
        click.echo(f'{activity.issue_link}')


@cli.command()
@click.option('--use-cookie', is_flag=True, default=False, help='Use cookies for authentication.')
@click.argument('jira_tickets', required=False)
def get_ticket_md(use_cookie, jira_tickets):
    """
    Fetch and extract JIRA tickets and convert them to markdown.
    
    JIRA_TICKETS_STRING: A string of JIRA ticket keys separated by '%20'.
    """
    cookies = ChromeCookiesDecrypt().get_cookie_str() if use_cookie else None
    jira_helper = JiraHelper(cookies)

    if not jira_tickets:
        jira_tickets_string = click.prompt("Please paste JIRA ticket keys (separated by '%20')")

    jira_tickets = jira_tickets_string.strip().split('%20')

    result = jira_helper.get_jira_ticket_md(jira_tickets)
    click.echo(result)


if __name__ == '__main__':
    cli()