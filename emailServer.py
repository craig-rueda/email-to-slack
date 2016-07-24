#!/usr/bin/python

import email
from inbox import Inbox
from slacker import Slacker
import tempfile
import base64
import argparse
import boto
from boto.s3.key import Key
import uuid
import PIL
from PIL import Image
from cStringIO import StringIO

# Init json parsing...
import json

parser = argparse.ArgumentParser(description='Posts first image attachment of emails to a slack channel')

parser.add_argument('-c', metavar='<config file path>', dest='config', help='The location of your config file',
                    required=True)

args = parser.parse_args()

# Load up the config from our JSON file...
config = {}
with open(args.config, 'r') as f:
    config = json.load(f)

slack = Slacker(config['slack_key'])
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
        slack.chat.post_message(config['channel'], subject)
    else:
        resize_and_upload(image_contents, subject, msg_txt)


def resize_and_upload(base_64_contents, subject, msg):
    temp = None
    image_contents = base64.b64decode(base_64_contents)
    key = uuid.uuid4().hex
    full_url = None
    thumb_url = None

    try:
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(image_contents)
        temp.flush()
        full_url = upload_to_s3(temp, 'full', key)

        # slack.files.upload(temp.name, title=subject, channels=config['channel'],
        #                   filename='img.jpg', initial_comment=msg_txt)
    finally:
        temp.close()

    try:
        temp = tempfile.NamedTemporaryFile(delete=False)

        file_imgdata = StringIO(image_contents)
        image = Image.open(file_imgdata)
        image.thumbnail((300, 300), PIL.Image.ANTIALIAS)
        image.save(temp.name, 'PNG')

        thumb_url = upload_to_s3(temp, 'thumb', key)

        # slack.files.upload(temp.name, title=subject, channels=config['channel'],
        #                   filename='img.jpg', initial_comment=msg_txt)
    finally:
        temp.close()

    slack.chat.post_message(config['channel'], msg.strip(), as_user='Camera Bot', username='camerabot',
                            attachments=[{
                                'title': subject.strip(),
                                'title_link': full_url,
                                'image_url': thumb_url
                            }]
                            )


def upload_to_s3(file, folder, key):
    conn = boto.connect_s3(config['aws_access_key'], config['aws_secret_key'])
    bucket = conn.get_bucket(config['s3_bucket'])
    k = Key(bucket)
    k.storage_class = 'STANDARD_IA'
    k.key = folder + '/' + key
    k.set_contents_from_filename(file.name, headers={'Content-Type': 'image/jpeg'})
    return 'https://s3.amazonaws.com/' + config['s3_bucket'] + '/' + k.name


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
#   Binding SMTP to Slack Relay on port """ + str(config['port']) + """
#   Posting to slack channel '""" + str(config['channel']) + """'
#
"""

# Bind directly.
inbox.serve(address='0.0.0.0', port=config['port'])
