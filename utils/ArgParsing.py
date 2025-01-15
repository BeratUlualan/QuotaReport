#!/usr/bin/env python3

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
# ArgParsing.py
#

# Import Python system libraries
import sys
import argparse

from utils.Logger import Logger

# Define the name of the Program, Description, and Version.
progname = "Quota Reporting"
progdesc = "Qumulo Directory Quota Reporting"
progvers = "7.3.0"

# Start by getting any command line arguments
def parse_args(parser, commands):
    # Divide argv by commands
    split_argv = [[]]
    for c in sys.argv[1:]:
        if c in commands.choices:
            split_argv.append([c])
        else:
            split_argv[-1].append(c)
    # Initialize namespace
    args = argparse.Namespace()
    for c in commands.choices:
        setattr(args, c, None)
    # Parse each command
    parser.parse_args(split_argv[0], namespace=args)  # Without command
    for argv in split_argv[1:]:  # Commands
        n = argparse.Namespace()
        setattr(args, argv[0], n)
        parser.parse_args(argv, namespace=n)
    return args


def main():
    try:
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"{progname} - Version {progvers}",
        )
        parser.add_argument(
            "-l",
            "--log",
            default="INFO",
            required=False,
            dest="loglevel",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            help="Set the logging level."
        )
        parser.add_argument(
            "-c",
            "--config-file",
            dest="config_file",
            default = "",
            help="The configuration file which has the definitions of how to run this script"
        )



        commands = parser.add_subparsers(title="sub-commands")

        
        # Create a subcommand parser for the "cluster" subcommand
        cluster_parser = commands.add_parser("cluster", help="Qumulo cluster details")
        cluster_parser.add_argument(
            "--address",
            dest="address",
            default="",
            help="Qumulo cluster IP address or hostname",
        )
        cluster_parser.add_argument(
            "--port",
            dest="cluster_port",
            default=8000,
            help="Qumulo cluster port number",
        )
        cluster_parser.add_argument(
            "--username",
            dest="username",
            default="",
            help="Source Qumulo cluster username",
        )
        cluster_parser.add_argument(
            "--password",
            dest="password",
            default="",
            help="Source Qumulo cluster password",
        )
        cluster_parser.add_argument(
            "--access-token",
            dest="access_token",
            default="",
            help="Source Qumulo cluster access token",
        )

        # Create a subcommand parser for the "email" subcommand
        email_parser = commands.add_parser(
            "email", help="Email details"
        )
        email_parser.add_argument(
            "--from",
            dest="email_from",
            default="",
            help="From address for email",
        )
        email_parser.add_argument(
            "--to",
            dest="email_to",
            default="",
            help="To address for email",
        )
        email_parser.add_argument(
            "--login",
            dest="login",
            default="",
            help="SMTP server login user",
        )
        email_parser.add_argument(
            "--password",
            dest="password",
            default="",
            help="SMTP server password",
        )
        email_parser.add_argument(
            "--server",
            dest="server",
            default="",
            help="SMTP server IP address or hostname",
        )
        email_parser.add_argument(
            "--port",
            dest="port",
            default=25,
            help="SMTP server port number",
        )
        email_parser.add_argument(
            "--use",
            dest="use",
            default="none",
            help="SMTP server TLS, SSL, none",
        )


        args = parse_args(parser, commands)
        
        return args

    except argparse.ArgumentTypeError:
        # Log an error
        sys.exit(1)

    # Build a logger to handle logging events.
    logger = Logger(name=progname, version=progvers, level=args.loglevel, log_path=None)


if __name__ == "__main__":
    main()
