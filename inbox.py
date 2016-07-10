'''
Copyright (c) 2012, Kenneth Reitz
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
# -*- coding: utf-8 -*-

import smtpd
import asyncore
import argparse
from email.parser import Parser

from logbook import Logger


log = Logger(__name__)


class InboxServer(smtpd.SMTPServer, object):
    """Logging-enabled SMTPServer instance with handler support."""

    def __init__(self, handler, *args, **kwargs):
        super(InboxServer, self).__init__(*args, **kwargs)
        self._handler = handler

    def process_message(self, peer, mailfrom, rcpttos, data):
        log.info('Collating message from {0}'.format(mailfrom))
        subject = Parser().parsestr(data)['subject']
        log.debug(dict(to=rcpttos, sender=mailfrom, subject=subject, body=data))
        return self._handler(to=rcpttos, sender=mailfrom, subject=subject, body=data)


class Inbox(object):
    """A simple SMTP Inbox."""

    def __init__(self, port=None, address=None):
        self.port = port
        self.address = address
        self.collator = None

    def collate(self, collator):
        """Function decorator. Used to specify inbox handler."""
        self.collator = collator
        return collator

    def serve(self, port=None, address=None):
        """Serves the SMTP server on the given port and address."""
        port = port or self.port
        address = address or self.address

        log.info('Starting SMTP server at {0}:{1}'.format(address, port))

        server = InboxServer(self.collator, (address, port), None)

        try:
            asyncore.loop()
        except KeyboardInterrupt:
            log.info('Cleaning up')

    def dispatch(self):
        """Command-line dispatch."""
        parser = argparse.ArgumentParser(description='Run an Inbox server.')

        parser.add_argument('addr', metavar='addr', type=str, help='addr to bind to')
        parser.add_argument('port', metavar='port', type=int, help='port to bind to')

        args = parser.parse_args()

        self.serve(port=args.port, address=args.addr)