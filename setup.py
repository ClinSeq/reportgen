from setuptools import setup

setup(name='reportgen',
      version='0.1.0',
      packages=['reportgen'],
      package_data={'': ['ALASCCA_logo.png', 'ki-logo_cmyk_5.png', 'rsz_checked_checkbox.png', 'rsz_unchecked_checkbox.png']},
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'writeReport = reportgen.__main__:main',
              'compileGenomicReport = reportgen.__main__:compileGenomicReport'
          ]
      },
      )