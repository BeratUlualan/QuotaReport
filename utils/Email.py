#!/usr/bin/env python

# MIT License
#
# Copyright (c) 2022 Qumulo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------
# Email.py
#
# Generic Class to send the report to an email upon completion

# Import python libraries

import argparse
import os
import smtplib
import sys
import base64
import hmac
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email.base64mime import body_encode as encode_base64
from smtplib import SMTPAuthenticationError as SMTPAuthenticationError

from utils.ConfigFileParser import ConfigFileParser
from utils.Logger import Logger

#
# Override the smtplib.SMTP_SSL routine because of a bug in encoding the login password
#


class Kade_SSL(smtplib.SMTP_SSL):
    def auth(self, mechanism, authobject, *, initial_response_ok=True):
        """Authentication command - requires response processing.
        'mechanism' specifies which authentication mechanism is to
        be used - the valid values are those listed in the 'auth'
        element of 'esmtp_features'.
        'authobject' must be a callable object taking a single argument:
                data = authobject(challenge)
        It will be called to process the server's challenge response; the
        challenge argument it is passed will be a bytes.  It should return
        bytes data that will be base64 encoded and sent to the server.
        Keyword arguments:
            - initial_response_ok: Allow sending the RFC 4954 initial-response
              to the AUTH command, if the authentication methods supports it.
        """
        # RFC 4954 allows auth methods to provide an initial response.  Not all
        # methods support it.  By definition, if they return something other
        # than None when challenge is None, then they do.  See issue #15014.
        mechanism = mechanism.upper()
        initial_response = (authobject() if initial_response_ok else None)
        if initial_response is not None:
            response = encode_base64(initial_response.encode('utf-8'), eol='')
            (code, resp) = self.docmd("AUTH", mechanism + " " + response)
        else:
            (code, resp) = self.docmd("AUTH", mechanism)
        # If server responds with a challenge, send the response.
        if code == 334:
            challenge = base64.decodebytes(resp)
            response = encode_base64(
                authobject(challenge).encode('utf-8'), eol='')
            (code, resp) = self.docmd(response)
        if code in (235, 503):
            return (code, resp)
        raise SMTPAuthenticationError(code, resp)

    def auth_cram_md5(self, challenge=None):
        """ Authobject to use with CRAM-MD5 authentication. Requires self.user
        and self.password to be set."""
        # CRAM-MD5 does not support initial-response.
        if challenge is None:
            return None
        return self.user + " " + hmac.HMAC(
            self.password.encode('utf-8'), challenge, 'md5').hexdigest()


#
# EmailReport Class
#
# This class will send a completed report to some address via SMTP

class Email(object):
    def __init__(self, logger=None):

        # Store the logger... We might use it later.

        self.logger = logger

    # send_mail - Routine to send email report as an attachment to a given user

    def send_mail(self, send_from, send_to, subject, message, server="localhost",
                  port=25, login=None, password=None, use_what=None):

        # Compose and send email with provided info and attachments
        #
        # Args:
        #
        # send_from - email from name
        # send_to - email to name
        # subject - String with a subject line
        # message - String with a message body
        # attachment - path to a file to attach to the email
        # server - mail server host name
        # port - port number
        # username - username to login to SMTP server (if required)
        # password - password to login to SMTP server (if required)
        # use_what - Must be either `tls` or `ssl`

        if self.logger is not None:
            self.logger.debug("Encoding From, To, Date, and Subject for email")

        msg = MIMEMultipart()
        msg["From"] = send_from
        msg["To"] = send_to
        msg["Date"] = formatdate(localtime=True)
        msg["Subject"] = subject

        # Attach the message body to the email

        msg.attach(MIMEText(f'{message}', "html"))

        # Send the email

        if self.logger is not None:
            self.logger.debug("Initializing SMTP server")

        # Either use TLS or SSL

        if use_what == "ssl":
            try:
                smtp = Kade_SSL(server, port, timeout=30)
            except (Exception,) as excpt:
                self.logger.error(f"Could not connect to email server, error was {excpt}")
                raise
        else:
            try:
                smtp = smtplib.SMTP(server, port, timeout=30)
            except (Exception,) as excpt:
                self.logger.error(f"Could not connect to email server, error was {excpt}")
                raise

            if use_what == "tls":
                smtp.starttls()

        # It is possible that we are talking to an email relay. In some cases, those
        # are owned by organizations that only allow email from within the organization.
        # In that case, they may not require a login/password combination
        self.logger.info(f"SMTP connection is established with {login}")
        if login != "":
            if self.logger is not None:
                self.logger.debug("Logging into SMTP server")

            try:
                smtp.login(login, password)
            except Exception as excpt:
                self.logger.error(f"Error while logging into email. Error: {excpt}")
                raise

        if self.logger is not None:
            self.logger.debug("Sending email")

        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.quit()


# Test Main Routine - This is not normally used as this class is usually imported


def main():
    # Define the name of the Program, Description, and Version.

    progname = "Test-Email"
    progdesc = "Testing Email System."
    progvers = "1.0"

    logger = Logger("Test-Email")

    # Get command line arguments

    testargs = commandargs(progname, progvers, progdesc)

    # Verify that the config file is perfectly formed and valid

    config = ConfigFileParser(testargs.config, logger)

    # Validate the config

    try:
        config.validate()
    except Exception as err:
        logger.error(f'Configuration would not validate, error is {err}')
        sys.exit(1)

    # Get the configuration info from the config file

    (email_from,
     email_to,
     login,
     password,
     server,
     port,
     use_what) = email_info(config, logger=logger)

    # Create the default Email class

    email = EmailReport(logger=logger)

    # Build a subject and message line

    subject = "This is a test subject line to verify the Email Server"
    msg_body = "This is a test message body to verify the Email Server."

    if testargs.attachment is not None:
        message = f'{msg_body} There should be a MIME attachment.'
    else:
        message = f'{msg_body}'

    email.send_mail(email_from, email_to, subject, message, server, port, login, password,
                    testargs.attachment, use_what)


# Routine to get the email data from the config file

def email_info(config, logger=None):
    # Get the email information

    email_data = None
    email_enable = True

    try:
        email_data = config.get("email")
    except (Exception,):
        email_enable = False

    # Get the "from" from the email info

    if email_enable:
        try:
            email_from = email_data["from"]
        except (Exception,):
            logger.error('Email "from"" is missing from config file')
            sys.exit(1)

        # Get the "to" from the email info

        try:
            email_to = email_data["to"]
        except (Exception,):
            logger.error('Email "to" is missing from config file')
            sys.exit(1)

        # Get the "login" from the email info

        try:
            email_login = email_data["login"]
        except (Exception,):
            email_login = None

        # Get the "password" from the email info

        try:
            email_password = email_data["password"]
        except (Exception,):
            email_password = None

        # Get the "server" from the email info

        try:
            email_server = email_data["server"]
        except (Exception,):
            logger.error('Email "server"" is missing from config file')
            sys.exit(1)

        # Get the "port" from the email info

        try:
            email_port = email_data["port"]
        except (Exception,):
            logger.error('Email "port"" is missing from config file')
            sys.exit(1)

        # Get the "use" from the email info

        try:
            use_what = email_data["use"]
        except (Exception,):
            use_what = None

        return (email_from, email_to, email_login, email_password, email_server,
                email_port, use_what)

    else:
        logger.debug("Email is not enabled in the config file. We are done!")
        sys.exit(1)


# Get command line arguments - primarily used for cluster info for testing

def commandargs(progname, progvers, desc):
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "--version", action="version", version=f"{progname} - Version {progvers}"
    )
    parser.add_argument(
        "--log",
        default="DEBUG",
        dest="loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "DEBUG"],
        help="Set the logging level.",
    )
    parser.add_argument(
        "--config",
        default="./config/config.json",
        required=True,
        dest="config",
        help="Configuration file pathname.",
    )
    parser.add_argument(
        "--attachment", required=False, dest="attachment", help="Attachment pathname"
    )

    try:
        return parser.parse_args()
    except argparse.ArgumentTypeError:
        # Log an error
        sys.exit(1)


# Main Routine

if __name__ == "__main__":
    main()
