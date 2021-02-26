

# Need to read the single-source-of-truth version file as text
# Importing version_file here can open the door to a cyclic dependency
def get_version(a_path):
    with open(a_path, 'r') as version_file:
        for a_line in version_file:
            if '__version__' in a_line:
                # Cleaning up all spaces and quotes around a string of the form __version__ = "x.y.z"
                return a_line.split("=")[1].split()[0].replace('"', '').replace("'","")
    raise RuntimeError("Unable to find version string.")
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
setup(
  name = 'browserstack-local',
  packages = ['browserstack'],
  version = get_version("browserstack/version.py"),
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

