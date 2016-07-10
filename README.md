# email-to-slack

##What does it do?

In a nut shell, this is a simple Python script that spawns an SMTP server, accepting emails from any sender. Whenever an email is received, the contents are scanned and the first attached email is then uploaded to the slack channel of your choosing.

##Usage
1. Install dependencies (logbook, slacker, argparse):
```Bash
pip install argparse
pip install logbook
pip install slacker
```
2. Create a Slack bot, and grab the API key suppied [here](https://api.slack.com/bot-users)
3. Run emailServer.py
```Bash
python emailServer.py -c <Your slack channel> -p <SMTP port to listen on - defaults to 2500> -s <Your Bot's Slack API key>
```
Example: 
```Bash
python emailServer.py -p 2800 -s erlkter-ert534e-dfg-234f -c mychannel
```