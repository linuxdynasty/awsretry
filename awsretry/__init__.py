#!/usr/bin/env python

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals
from functools import wraps
import re
import logging
import time

import botocore
import boto
import boto3

__author__ = 'Allen Sanabria'
__version__ = '1.0.2'


class CloudRetry(object):
    """ CloudRetry can be used by any cloud provider, in order to implement a
        backoff algorithm/retry effect based on Status Code from Exceptions.
    """
    # This is the base class of the exception.
    # AWS Example botocore.exceptions.ClientError
    @staticmethod
    def base_class(error):
        """ Return the base class of the error you are matching against.
        Args:
            error (object): The exception itself.
        """
        pass

    @staticmethod
    def status_code_from_exception(error):
        """ Return the status code from the exception object.
        Args:
            error (object): The exception itself.
        """
        pass

    @staticmethod
    def found(response_code):
        """ Return True if the Response Code to retry on was found.
        Args:
            response_code (str): This is the Response Code that is being
                matched against.
        """
        pass

    @classmethod
    def backoff(cls, tries=10, delay=3, backoff=1.1, added_exceptions=list()):
        """ Retry calling the Cloud decorated function using an exponential
            backoff.
        Kwargs:
            tries (int): Number of times to try (not retry) before giving up.
                default=10
            delay (int): Initial delay between retries in seconds.
                default=3
            backoff (int): backoff multiplier e.g. value of 2 will double the
                delay each retry.
                default=2
            added_exceptions (list): Other exceptions to retry on.
                default=[]

        """
        def deco(f):
            @wraps(f)
            def retry_func(*args, **kwargs):
                max_tries, max_delay = tries, delay
                while max_tries > 1:
                    try:
                        return f(*args, **kwargs)
                    except Exception as e:
                        base_exception_class = cls.base_class(e)
                        if isinstance(e, base_exception_class):
                            response_code = cls.status_code_from_exception(e)
                            if cls.found(response_code, added_exceptions):
                                logging.info("{0}: Retrying in {1} seconds...".format(str(e), max_delay))
                                time.sleep(max_delay)
                                max_tries -= 1
                                max_delay *= backoff
                            else:
                                # Return original exception if exception is not
                                # a ClientError.
                                raise e
                        else:
                            # Return original exception if exception is not a
                            # ClientError
                            raise e
                return f(*args, **kwargs)

            return retry_func  # true decorator

        return deco


class AWSRetry(CloudRetry):
    @staticmethod
    def base_class(error):
        if isinstance(error, botocore.exceptions.ClientError):
            return botocore.exceptions.ClientError

        elif isinstance(error, boto.compat.StandardError):
            return boto.compat.StandardError

        elif isinstance(error, botocore.exceptions.WaiterError):
            return botocore.exceptions.WaiterError

        else:
            return type(None)

    @staticmethod
    def status_code_from_exception(error):
        if isinstance(error, botocore.exceptions.ClientError):
            return error.response['Error']['Code']
        if isinstance(error, botocore.exceptions.WaiterError):
            return error.last_response['Error']['Code']
        else:
            return error.error_code

    @staticmethod
    def found(response_code, added_exceptions):
        # This list of failures is based on this API Reference
        # http://docs.aws.amazon.com/AWSEC2/latest/APIReference/errors-overview.html
        retry_on = [
            'RequestLimitExceeded', 'Unavailable', 'ServiceUnavailable',
            'InternalFailure', 'InternalError'
        ]
        retry_on.extend(added_exceptions)

        not_found = re.compile(r'^\w+.NotFound')
        if response_code in retry_on or not_found.search(response_code):
            return True
        else:
            return False
