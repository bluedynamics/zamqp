from setuptools import setup, find_packages
import sys, os

version = '1.0b1'
shortdesc = 'AMQP broadcasting for python and zope.'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
tests_require = ['interlude']
setup(name='zamqp',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
      ],
      keywords='amqp events zope',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'https://svn.binarybox.net/svn/ztk/zamqp',
      license='GNU General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'amqplib',
          'zope.event',
      ],
      test_suite="zamqp.tests.test_suite",
      tests_require=tests_require,
      extras_require = dict(
          test=tests_require
      ),
)