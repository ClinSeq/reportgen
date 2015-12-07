from setuptools import setup

setup(name='reportgen',
      version='0.1.0',
      packages=['reportgen'],
      entry_points={
          'console_scripts': [
              'reportgen = reportgen.__main__:main'
          ]
      },
      )