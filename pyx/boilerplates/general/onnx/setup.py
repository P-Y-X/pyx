from setuptools import setup, find_packages


def parse_requirements(filename):
    """
    load requirements from a pip requirements file
    """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

reqs = parse_requirements('requirements.txt')

setup(name='pyx_%name%_onnx',
      version='0.0.1',
      description='PYX module',
      url='',
      author='PYX Team',
      author_email='support@pyx.ai',
      packages=find_packages(),
      install_requires=reqs,
      zip_safe=False)
