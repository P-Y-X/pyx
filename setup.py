from setuptools import setup, find_packages


def parse_requirements(filename):
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


reqs = parse_requirements('requirements.txt')

setup(name='pyx-cli',
      version='0.0.1',
      description='PYX CLI / framework',
      author='PYX.ai',
      author_email='support@pyx.ai',
      packages=find_packages(),
      install_requires=reqs,
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'pyx = pyx_cli.cli:main',
          ],
      },
      )
