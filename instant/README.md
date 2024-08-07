# BUDDIES CLI

## Description
Contains all mini scripts that help boost productiviy when working with WWE project.

## Installation
 - Configure the .env file with the following variables:

    **COOKIE_FILE_PATH**=`'~/Library/Application Support/Arc/User Data/Profile 1/Cookies'`

    Path to the cookie file for the browser you use
    
    **BROWSER_STORAGE**=`'Arc Safe Storage'`
    
    Name of the browser storage for the browser you use
    
    **BROWSER_NAME**=`'Arc'` 
    
    Name of the browser you use
    
    **JIRA_URL**=`'https://'`

    Replace the values with the appropriate paths and URLs for your system.

- [Configure the AWS profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)

    Configure sso for the first time:

    `aws sso login --profile <aws_profile>`

- Instal `mysql-client` and `mysqldump`

    `brew install mysqlclient`

    **Optional**(Create symlink)

    `ln /opt/homebrew/opt/mysql-client/bin/mysqldump /usr/local/bin/mysqldump`

    `ln /opt/homebrew/opt/mysql-client/bin/mysql /usr/local/bin/mysql`

## Folder structure

```
services/
├── aws/
│ ├── aws_cli.py
│ └── aws_helper.py
├── jira/
│ └── jira_helper.py
├── sql/
│ ├── sql_cli.py
│ └── sql_helper.py
├── ssh/
│ └── ssh_helper.py
└── utils/
├── constants.py
├── cookies_decrypt.py
└── general_helper.py
```
    
New service module can lived in service, this tool use [click]() to create mini CLIs and can be trigger with like:

`python cli.py <service_module> <service_method> --additional_prefix`

