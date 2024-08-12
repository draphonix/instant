import requests
import os
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from bs4 import BeautifulSoup
from jira.models.models import Activity
from typing import Dict 

class JiraHelper:
    def __init__(self, cookies: str = None):
        self.url = os.getenv('JIRA_URL')
        self.cookies = self.parse_cookies(cookies) if cookies is not None else None
        
    # Given a list of Jira URL, return the Jira ticket Name and url in the following MD format:
    # - [TICKET_NAME](TICKET_URL)
    def get_jira_ticket_md(self, jira_urls: list[str]) -> str:
        md = ''
        for url in jira_urls:
            ticket_name = self.get_jira_ticket_name(url)
            md += f'- [{ticket_name}]({url})\n'
        return md
            
    def get_jira_ticket_name(self, url: str) -> str:
        response = requests.get(url, cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'html.parser')
        ticket_name = soup.find('h1', {'id': 'summary-val'}).text.strip()
        return ticket_name
    
    def parse_cookies(self, cookies: str) -> dict:
        cookie_dict = {}
        for cookie in cookies.split(';'):
            name, value = cookie.strip().split('=', 1)
            cookie_dict[name] = value
        return cookie_dict
    

    def extract_today_activities(self, feed_content: str) -> Dict[str, Activity]:
        """
        Extracts activities for today from the provided feed content.

        Args:
            feed_content (str): The XML content of the feed.

        Returns:
            Dict[str, Activity]: A dictionary of activities for today with issue links as keys and Activity objects as values.
        """
        activities = {}
        root = ET.fromstring(feed_content)
        today = datetime.utcnow().date()
        project_key = os.getenv('JIRA_PROJECT')
        jira_base_url = re.escape(self.url)  # Escape the URL for regex pattern

        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            updated = entry.find('{http://www.w3.org/2005/Atom}updated').text
            entry_date = datetime.fromisoformat(updated[:-1]).date()
            
            if entry_date == today:
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                patterns = [
                    rf'href="({jira_base_url}browse/{project_key}-\d+)">\s*({project_key}-\d+.+?)(?=</a>)',
                    rf'href="({jira_base_url}browse/{project_key}-\d+)"><span class=\'resolved-link\'>{project_key}-\d+</span>\s*-\s*(.+?)(?=</a>)'
                ]
                
                match = None
                for pattern in patterns:
                    match = re.search(pattern, title, re.DOTALL)
                    if match:
                        break
                
                if match:
                    issue_link = match.group(1)
                    issue_title = re.sub(r'\s+', ' ', match.group(2)).strip()
                    activity = Activity(issue_link, issue_title)
                    if issue_link not in activities:
                        activities[issue_link] = activity
                    else:
                        print(f"Duplicate issue link found: {issue_link}")
                else:
                    print("No match found!!")
                    print(f'patterns: {patterns}')
                    print(f'title: {title}')
        return activities

    def get_activity_stream(self, email: str, start_timestamp: int, end_timestamp: int, token: str) -> dict:
        """
        Fetches the activity stream for a user within a specified time range.

        Args:
            email (str): The email of the user.
            start_timestamp (int): The start of the time range (Unix timestamp).
            end_timestamp (int): The end of the time range (Unix timestamp).
            token (str): The authorization token.

        Returns:
            dict: The JSON response from the JIRA activity stream API.
        """
        url = f'{self.url}/activity?streams=user+IS+{email}&streams=update-date+BETWEEN+{start_timestamp}+{end_timestamp}'
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.content
    