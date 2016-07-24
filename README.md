# email-to-slack

##What does it do?

In a nut shell, this is a simple Python script that spawns an SMTP server, 
accepting emails from any sender. Whenever an email is received, the contents 
are scanned and the first attached email is then uploaded to S3,
which is then posted to the slack channel of your choosing.

##Usage
1. Install dependencies (logbook, slacker, argparse, boto, pillow):
```Bash
pip install argparse
pip install logbook
pip install slacker
pip install boto
pip install pillow
```
2. Create a Slack bot, and grab the API key suppied [here](https://api.slack.com/bot-users)
3. Run emailServer.py
```Bash
python emailServer.py -c <Your config file>
```
Example: 
```Bash
python emailServer.py -c my_config.json
```

##Configuration
Configuration is done through a JSON config file whose location is passed on the cmd line.
Below is a description of its overall structure:
```json
{
  "aws_access_key": "<IAM user's key>",
  "aws_secret_key": "<IAM user's secret key>",
  "s3_bucket": "<Your S3 bucket to store images>",
  "slack_key": "<Your bot's slack API key>",
  "channel": "<The slack channel to post messages to>",
  "port": <The TCP port number that the SMTP server will listen on>
}
```