import unittest

import botocore

from awsretry import AWSRetry


class RetryTestCase(unittest.TestCase):

    def test_no_failures(self):
        self.counter = 0

        @AWSRetry.backoff(tries=2, delay=0.1)
        def no_failures():
            self.counter += 1

        no_failures()
        self.assertEqual(self.counter, 1)

    def test_retry_once(self):
        self.counter = 0
        err_msg = {'Error': {'Code': 'InstanceId.NotFound'}}

        @AWSRetry.backoff(tries=2, delay=0.1)
        def retry_once():
            self.counter += 1
            if self.counter < 2:
                raise botocore.exceptions.ClientError(
                    err_msg, 'Could not find you'
                )
            else:
                return 'success'

        r = retry_once()
        self.assertEqual(r, 'success')
        self.assertEqual(self.counter, 2)

    def test_reached_limit(self):
        self.counter = 0
        err_msg = {'Error': {'Code': 'RequestLimitExceeded'}}

        @AWSRetry.backoff(tries=4, delay=0.1)
        def fail():
            self.counter += 1
            raise botocore.exceptions.ClientError(err_msg, 'toooo fast!!')

        with self.assertRaises(botocore.exceptions.ClientError):
            fail()
        self.assertEqual(self.counter, 4)

    def test_unexpected_exception_does_not_retry(self):
        self.counter = 0
        err_msg = {'Error': {'Code': 'AuthFailure'}}

        @AWSRetry.backoff(tries=4, delay=0.1)
        def raise_unexpected_error():
            self.counter += 1
            raise botocore.exceptions.ClientError(err_msg, 'unexpected error')

        with self.assertRaises(botocore.exceptions.ClientError):
            raise_unexpected_error()

        self.assertEqual(self.counter, 1)


if __name__ == '__main__':
    unittest.main()
