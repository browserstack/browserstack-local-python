try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
setup(
  name = 'browserstack-local',
  packages = ['browserstack'],
  version = '1.2.4',
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

