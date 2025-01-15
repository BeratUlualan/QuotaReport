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
# QumuloFileParser.py
#

# Import Python system libraries
import json
import argparse
import json
import os
import sys

import jsonschema
from jsonschema import validate


from utils.Logger import Logger


#
# ConfigFileParser Class
#
# This class deals with loading both a configuration and schema file and then
# validating that the configuration file matches the schema. Once done, the configuration
# file contents can be used by a calling program.


class ConfigFileParser(object):
    def __init__(self, config_path, logger=None):

        # Store the config file
        self.config_path = config_path

        # Store the logger..
        self.logger = logger

        # Create other variables that we will use in this code
        self.schema = None
        self.config = None

    # validate - Take the schema and validate that it matches the config file
    def validate(self):

        # Get the schema file... It must always be in the same directory as the config
        # file and end in .schema (versus .json for the config file)

        config_base = os.path.splitext(self.config_path)[0]

        try:
            with open(f'{config_base}.schema.json', "r") as schemaFile:
                self.schema = json.load(schemaFile)
        except (Exception,) as err:
            if self.logger is not None:
                self.logger.error(f'{config_base}.schema reported error of: {err}')
                raise Exception(err)

        # Get the configuration file...

        try:
            with open(self.config_path, "r") as configFile:
                self.config = json.load(configFile)
        except Exception as err:
            if self.logger is not None:
                self.logger.error(f'{self.config_path} reported error of {err}')
                raise Exception(err)

        # Now, validate the config file against the schema

        is_valid, msg = self.__validate_json(configdata=self.config,
                                             schemadata=self.schema)

        # If the configuration is not valid, print out the error message and exit

        if is_valid is not True:
            if self.logger is not None:
                self.logger.error(f'{self.config_path} did not validate!')
                self.logger.error(f'Error was: {msg}')
                raise jsonschema.exceptions.ValidationError(msg)
    
    @staticmethod
    def __validate_json(configdata, schemadata):

        try:
            validate(instance=configdata, schema=schemadata)
        except jsonschema.exceptions.ValidationError as err:
            return False, err

        message = "Given JSON data is valid"
        return True, message
    
    def get(self, key):
        # Get some configuration value based upon a python Dict key
        try:
            return self.config[key]
        except Exception:
            self.logger.debug(f'Error on getting dictionary item, key was "{key}"')
            raise
    
    def get_configs(self):
        try:
            return self.config
        except Exception:
            self.logger.debug(f'Error on getting configurations.')
            raise

# Test Main Routine - This is not normally used as this class is usually imported
def main():

    # Define the name of the Program, Description, and Version.
    progname = "Test-ConfigFile"
    progdesc = "Testing ConfigFile routine."
    progvers = "1.0"

    logger = Logger("Test-ConfigFile")

    # Get command line arguments
    testargs = commandargs(progname, progvers, progdesc)


    # Create the default Report
    config = ConfigFileParser(testargs.config_file, logger)

    # Validate the config file against the schema
    try:
        config.validate()
    except (Exception,):
        sys.exit(1)

    logger.debug('Configuration file validated properly')

    # Test getting some configuration data
    try:
        config.get('cluster')
    except (Exception,):
        logger.debug('Failed! Could not get the cluster details')
        sys.exit(1)

    try:
        config.get('directories')
    except (Exception,):
        logger.debug('Failed! Could not get the details of the directories')
        sys.exit(1)

    try:
        config.get('email')
    except (Exception,):
        logger.debug('Failed! Could not get email details')
        sys.exit(1)

    # Getting some configuration data
    try:
        configs = config.get_configs()
        return configs
    except (Exception,):
        logger.debug('Failed! Could not get quotas')
        sys.exit(1)

# Get command line arguments - primarily used for cluster info for testing
def commandargs(progname, progvers, desc):
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "--version", action="version", version=f"{progname} - Version {progvers}"
    )
    parser.add_argument(
        "-c"
        "--config-file",
        default="./config/config.json",
        required=True,
        dest="config_file",
        help="Configuration file pathname.",
    )
    parser.add_argument(
        "--log",
        default="DEBUG",
        dest="loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "DEBUG"],
        help="Set the logging level.",
    )

    try:
        return parser.parse_args()
    except argparse.ArgumentTypeError:
        # Log an error
        sys.exit(1)


# Main Routine
if __name__ == "__main__":
    main()