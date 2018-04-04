from setuptools import setup
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt", session=False)

# reqs is a list of requirement
reqs = [str(ir.req) for ir in install_reqs if ir.req is not None]

setup(name='reportgen',
      version='0.1.1',
      packages=['reportgen', 'reportgen.reporting', 'reportgen.rules'],
      install_requires=reqs,
      package_data={'': ['assets/ALASCCA_MUTATION_TABLE_SPECIFIC.xlsx', 'assets/COLORECTAL_MUTATION_TABLE.xlsx',
                         'assets/ALASCCA_logo.png', 'assets/ki-logo_cmyk_5.png',
                         'assets/rsz_checked_checkbox.png', 'assets/rsz_unchecked_checkbox.png',
                         'assets/templates/alascca.tex', 'assets/templates/alasccaOnly.tex']},
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'writeAlasccaReport = reportgen.__main__:writeAlasccaReport',
              'compileAlasccaGenomicReport = reportgen.__main__:compileAlasccaGenomicReport',
              'compileMetadata = reportgen.__main__:compileMetadata'
          ]
      }
      )
