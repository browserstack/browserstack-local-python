try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def get_version(a_path):
    with open(a_path, 'r') as version_file:
        version = "".join(version_file.readlines())
        version = version.split("=")[1].split()[0].replace('"','').replace("'","")
        return version
    raise RuntimeError("Version file not found!")

setup(
  name = 'browserstack-local',
  packages = ['browserstack'],
  version = get_version("version.py"),
  description = 'Python bindings for Browserstack Local',
  author = 'BrowserStack',
  author_email = 'support@browserstack.com',
  url = 'https://github.com/browserstack/browserstack-local-python',
  download_url = 'https://github.com/browserstack/browserstack-local-python/archive/master.zip',
  keywords = ['BrowserStack', 'Local', 'selenium', 'testing'],
  classifiers = [],
  install_requires=[
        'psutil',
  ],
)

