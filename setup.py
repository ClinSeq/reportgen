from setuptools import setup

setup(name='reportgen',
      version='0.1.0',
      packages=['reportgen'],
      package_data={'': ['assets/ALASCCA_logo.png', 'assets/ki-logo_cmyk_5.png',
                         'assets/rsz_checked_checkbox.png', 'assets/rsz_unchecked_checkbox.png']},
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'writeAlasccaReport = reportgen.__main__:writeAlasccaReport',
              'compileAlasccaGenomicReport = reportgen.__main__:compileAlasccaGenomicReport',
              'compileMetadata = reportgen.__main__:compileMetadata'
          ]
      },
      )
