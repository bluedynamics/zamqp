from setuptools import setup, find_packages
import sys, os

version = '1.0'
shortdesc = 'AMQP hook for zope events.'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='zamqp',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Operating System :: OS Independent',
          'Programming Language :: Python', 
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',        
      ],
      keywords='',
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
          'zope.component',
          'amqplib',
      ],
      extras_require = dict(
          test=[
            'interlude',
          ]
      ),
)