from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='awsretry',

    version='1.0.0',

    description='Decorate your AWS Boto3 Calls with AWSRetry.backoff(). This will allows your calls to get around the AWS Eventual Consistency Errors.',
    long_description=open('README.rst').read(),

    url='https://github.com/linuxdynasty/awsretry',
    packages=find_packages(exclude=['tests*']),

    author='Allen Sanabria',
    author_email='asanabria@linuxdynasty.org',

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='boto3 aws retry awsretry backoff',

    install_requires=['boto', 'boto3', 'botocore'],

    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage', 'nose'],
    },
)
