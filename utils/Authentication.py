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
# Authentication.py
#

# Import Python system libraries
import sys

#  Import local Python libraries
from utils.Logger import Logger

logger = Logger()

#  Qumulo Python libraries
try:
    import qumulo
    from qumulo.rest_client import RestClient
    from qumulo.lib.auth import Credentials
except ImportError as error:
    logger.error(
        "Unable to import the required Qumulo api bindings. Please run the following command: pip3 install qumulo_api"
    )
    sys.exit()




def login_with_args(args):
    #  Qumulo cluster login
    if args.cluster:
        if args.cluster.access_token:
            try: 
                rc = RestClient(
                    args.cluster.address, cluster.port, Credentials(args.cluster.access_token)
                )
                logger.info(f"Connection established with {args.cluster.address}")
            except:
                logger.error(f'Login error')
                sys.exit(1)
        elif args.cluster.username and args.cluster.password:
            try:
                rc = RestClient(args.cluster.address, cluster.port)
                rc.login(args.cluster.username, args.cluster.password)
                logger.info(f"Connection established with {args.cluster.address}")
            except qumulo.lib.request.RequestError as err:
                logger.error(f'{err}')
                sys.exit(1)
            except:
                logger.error(f'Connection issue with{args.cluster.address}')
                sys.exit(1)
        else:
            logger.error(f"Connection issue with {configs['cluster']['address']}")
            sys.exit(1)
    return rc


def login_with_configs(configs):
    # Qumulo cluster login
    if configs['cluster']['address']:
        if configs['cluster']['access_token']:
            try: 
                rc = RestClient(
                    configs['cluster']['address'], configs['cluster']['port'], Credentials(configs['cluster']['access_token'])
                )
                logger.info(f"Connection established with {configs['cluster']['address']}")
            except:
                logger.error(f'Login error')
                sys.exit(1)
        elif configs['cluster']['username'] and configs['cluster']['password']:
            try:
                rc = RestClient(configs['cluster']['address'], configs['cluster']['port'])
                rc.login(configs['cluster']['username'], configs['cluster']['password'])
                logger.info(f"Connection established with {configs['cluster']['address']}")
            except qumulo.lib.request.RequestError as err:
                logger.error(f'{err}')
                sys.exit(1)
            except:
                logger.error(f"Connection issue with {configs['cluster']['address']}")
                sys.exit(1)
        else:
            logger.error(f"Connection issue with {configs['cluster']['address']}")
            sys.exit(1)
    return rc
