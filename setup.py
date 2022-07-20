try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='ACSE9',
      use_scm_version=True,
      setup_requires=['setuptools_scm'],
      description="Package import for pytest",
      long_descritpion="""n/a""",
      url='https://github.com/acse-2020/acse2020-acse9-finalreport-acse-tc20.git',
      author="Imperial College London",
      author_email='tc20@ic.ac.uk',
      packages=['ACSE9'])