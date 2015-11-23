from setuptools import setup, find_packages

setup(name='burgerpy',
      version='1.0',
      description='burger irc bot',
      install_requires=[
          'simplejson',
          'twisted',
          'pika',
          'gitpython',
          'lxml',
          'requests>=2.6.1,<2.7',
          'pymongo'],
      packages=find_packages(exclude=['tests']))
