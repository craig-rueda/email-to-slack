#!/usr/bin/python

import email
from inbox import Inbox
from slacker import Slacker
import tempfile
import base64
import argparse

parser = argparse.ArgumentParser(description='Posts first image attachment of emails to a slack channel')

parser.add_argument('-c', metavar='<channel name>', dest='channel', help='The channel to post messages to',
                    required=True)
parser.add_argument('-p', metavar='<smtp port>', dest='port',
                    help='The port that the SMTP server should listen on (defaults to 2500)',
                    type=int, default=2500, required=False)
parser.add_argument('-s', metavar='<slack api key>', dest='slack_key', help='Your Slack bot''s API key',
                    required=True)

args = parser.parse_args()

slack = Slacker(args.slack_key)
inbox = Inbox()

@inbox.collate
def handle(to, sender, subject, body):
    msg = email.message_from_string(body)
    msg_parts = collect_sub_messages(msg, [])
    image_contents = ""
    msg_txt = ""

    for part in msg_parts:
        partType = part.get_content_type()
        if partType == "text/plain":
            encoding = part.get_all("content-transfer-encoding")
            if encoding is not None and 'base64' in encoding:
                msg_txt = base64.b64decode(part.get_payload())
            else:
                msg_txt = part.get_payload()
        elif "image" in partType:
            image_contents = part.get_payload().replace("\n", "")

    if len(image_contents) == 0:
        slack.chat.post_message(args.channel, subject)
    else:
        temp = tempfile.NamedTemporaryFile(delete=False)
        try:
            temp.write(base64.b64decode(image_contents))
            temp.flush()
            slack.files.upload(temp.name, title=subject, channels=args.channel,
                               filename='img.jpg', initial_comment=msg_txt)
        finally:
            temp.close()


def collect_sub_messages(msg, msgs):
    payload = msg.get_payload()
    if isinstance(payload, list):
        for sub_payload in payload:
            collect_sub_messages(sub_payload, msgs)
    else:
        msgs.append(msg)

    return msgs

print """
#
#   Binding SMTP to Slack Relay on port """ + str(args.port) + """
#   Posting to slack channel '""" + str(args.channel) + """'
#
"""

# Bind directly.
inbox.serve(address='0.0.0.0', port=args.port)
