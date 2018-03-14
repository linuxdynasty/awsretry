========================================
AWSRetry - Boto3 Retry/Backoff Decorator
========================================

AWSRetry is a Python Decorator that can be used to wrap boto3 function calls.
This function was built out of the need to get around a couple of common issues
when working with AWS API's.

* Query API Request Rate
* Eventual Consistency Model.


Exceptions that will get retried when encountered
-------------------------------------------------
* RequestLimitExceeded
* Unavailable
* ServiceUnavailable
* InternalFailure
* InternalError
* ^\w+.NotFound

This list can be extended. (http://docs.aws.amazon.com/AWSEC2/latest/APIReference/errors-overview.html)

Quick Start
-----------
Install awsretry.

.. code-block:: sh

  $ pip install awsretry

I will assume you know about setting up Boto3 Credentials, if not you can read
the instructions here http://boto3.readthedocs.io/en/latest/guide/configuration.html


Keyword Arguments that AWSRetry.backoff accepts
-----------------------------------------------

* tries = The number of times to try before giving up. Default = 10
* delay = The initial delay between retries in seconds. Default = 3
* backoff = backoff multiplier e.g. value of 2 will double the delay each retry. Default = 1.1
* added_exceptions = Other exceptions to retry on, beyond the defaults. Default = list()

Examples
--------
Write a quick function that implements AWSRetry.backoff()

.. code-block:: python

    #!/usr/bin/env python

    import botocore
    import boto3
    from awsretry import AWSRetry


    @AWSRetry.backoff()
    def get_instances():
        client = boto3.client('ec2')
        try:
            instances = client.describe_instances()
            return instances
        except botocore.exceptions.ClientError as e:
            raise e

    instances = get_instances()

Write a quick function that will overwrite the default arguments.

.. code-block:: python

  #!/usr/bin/env python

  import botocore
  import boto3
  from awsretry import AWSRetry


  @AWSRetry.backoff(tries=20, delay=2, backoff=1.5, added_exceptions=['ConcurrentTagAccess'])
  def create_tags():
      client = boto3.client('ec2')
      try:
          resources = ['1-12345678891234']
          tags = [{'Key': 'service', 'Value': 'web-app'}]
          instances = client.create_tags(Resources=resources, Tags=tags)
      except botocore.exceptions.ClientError as e:
          raise e

  create_tags()

Development
-----------
Assuming that you have Python and ``virtualenv`` installed, set up your
environment and install the required dependencies like this instead of
the ``pip install awsretry`` defined above:

.. code-block:: sh

    $ git clone https://github.com/linuxdynasty/awsretry.git
    $ cd awsretry
    $ virtualenv venv
    ...
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    $ pip install -e .

Running Tests
-------------

You can run the tests by using tox which implements nosetest or run them
directly using nosetest.

.. code-block:: sh

    $ tox
    $ tox tests/test_awsretry.py
    $ tox -e py27,py36 tests/
    $ nosetest
