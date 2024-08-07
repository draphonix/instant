from typing import Dict

class Activity:
    def __init__(self, issue_link: str, issue_title: str):
        self.issue_link = issue_link
        self.issue_title = issue_title

    def __repr__(self):
        return f'({self.issue_title})[{self.issue_link}]'

    def to_dict(self) -> Dict[str, str]:
        return {self.issue_link: str(self)}
