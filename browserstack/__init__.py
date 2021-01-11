import browserstack.version

# Python modules report to module_name.__version__ with their version
# Ref: https://www.python.org/dev/peps/pep-0008/#module-level-dunder-names
# With this, browserstack.__version__ will respond with <version>

__version__ = version.__version__
