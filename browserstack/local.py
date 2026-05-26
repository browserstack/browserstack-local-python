import subprocess, os, time, json, logging, re
import psutil

from browserstack.local_binary import LocalBinary
from browserstack.bserrors import BrowserStackLocalError

logger = logging.getLogger(__name__)
try:
    from importlib.metadata import version as package_version, PackageNotFoundError
except:
    import pkg_resources

# LOC-6719 / INJ-002 (CWE-88): kwargs are forwarded to the BrowserStackLocal
# binary as flags. Without this allowlist an attacker-influenced kwarg can
# inject arbitrary flags — notably proxyHost / proxyPort / forceproxy to
# redirect tunnel traffic through an attacker-controlled proxy.
#
# Cross-referenced against the binary's COMMAND_CONFIGURATION table
# (browserStackTunnel/extensions/node/config/constants.js) and the public docs
# at https://www.browserstack.com/docs/local-testing/binary-params. Both the
# camelCase form ('name') and the kebab-case form ('alias') are accepted
# because user code passes both shapes. Internal-only flags (visible:false:
# region, bsHost, customRepeater, enterprise, public-interface-services,
# identifier, trusted-hosts), help/version flags, and undocumented internal
# flags (-r, -skipCheck, -daemonInstance, -tunnelIdentifier, -uniqueIdentifier)
# are intentionally excluded.
#
# Wrapper-managed keys (key, binarypath, logfile, source) are stripped from
# self.options in start() before this check runs and are not listed here.
# 'daemon' / 'logFile' are also omitted because they are emitted unconditionally
# by _generate_cmd and a user-supplied duplicate would conflict.
ALLOWED_OPTIONS = frozenset({
    # Verbose / logging
    'v', 'vv', 'vvv', 'verbose',
    'enableLoggingForAPI', 'enable-logging-for-api',
    'enableUTCLogging', 'enable-utc-logging',
    # Folder testing
    'f', 'folder',
    # Force / start behaviour
    'force', 'F',
    'forcelocal', 'force-local', 'forceLocal',
    'forceproxy', 'force-proxy', 'forceProxy',
    'onlyAutomate', 'only-automate',
    # Host targeting / restriction
    'only',
    'include-hosts', 'exclude-hosts',
    'localIdentifier', 'local-identifier',
    'parallelRuns', 'parallel-runs',
    # Corporate proxy
    'proxyHost', 'proxy-host',
    'proxyPort', 'proxy-port',
    'proxyUser', 'proxy-user',
    'proxyPass', 'proxy-pass',
    'disableProxyDiscovery', 'disable-proxy-discovery',
    # Local proxy
    'localProxyHost', 'local-proxy-host',
    'localProxyPort', 'local-proxy-port',
    'localProxyUser', 'local-proxy-user',
    'localProxyPass', 'local-proxy-pass',
    # PAC / HTTPS / protocol
    'pacFile', 'pac-file',
    'https-ports',
    'client-protocol',
    # CA certificates
    'useCaCertificate', 'use-ca-certificate',
    'useSystemInstalledCa', 'use-system-installed-ca',
    # NTLM proxy
    'ntlm-username', 'ntlm-password', 'ntlm-domain', 'ntlm-workstation',
    # Dashboard / misc
    'disableDashboard', 'disable-dashboard',
    'config-file',
    'no-container',
    'connect-timeout',
    'timeout',
    'debug-utility', 'debug-url',
})

class Local:
  def __init__(self, key=None, binary_path=None, **kwargs):
    self.key = os.environ['BROWSERSTACK_ACCESS_KEY'] if 'BROWSERSTACK_ACCESS_KEY' in os.environ else key
    self.options = kwargs
    self.local_logfile_path = os.path.join(os.getcwd(), 'local.log')
    LocalBinary.set_version(self.get_package_version())

  def __xstr(self, key, value):
    if key is None:
      return ['']
    if str(value).lower() == "true":
      return ['-' + key]
    elif str(value).lower() == "false":
      return ['']
    else:
      return ['-' + key, str(value)]

  def get_package_version(self):
    name = "browserstack-local"
    version = 'None'
    use_fallback = False
    try:
        temp = package_version
    except NameError: # Only catch if package_version is not defined(and not other errors)
        use_fallback = True

    if use_fallback:
        try:
            version = pkg_resources.get_distribution(name).version
        except pkg_resources.DistributionNotFound:
            version = 'None'
    else:
        try:
            version = package_version(name)
        except PackageNotFoundError:
            version = 'None'

    return version

  def _generate_cmd(self):
    cmd = [self.binary_path, '-d', 'start', '-logFile', self.local_logfile_path, "-k", self.key, '--source', 'python:' + self.get_package_version()]
    for o in self.options.keys():
      if o not in ALLOWED_OPTIONS:
        raise BrowserStackLocalError('Unknown option: {}'.format(o))
      if self.options.get(o) is not None:
        cmd = cmd + self.__xstr(o, self.options.get(o))
    return cmd

  def _generate_stop_cmd(self):
    cmd = self._generate_cmd()
    cmd[2] = 'stop'
    return cmd

  def start(self, **kwargs):
    for k, v in kwargs.items():
        self.options[k] = v

    if 'key' in self.options:
      self.key = self.options['key']
      del self.options['key']

    if 'binarypath' in self.options:
      candidate = os.path.realpath(self.options['binarypath'])
      if not os.path.isfile(candidate):
        raise BrowserStackLocalError('binarypath does not point to a file')
      try:
        version_output = subprocess.check_output([candidate, '--version'], timeout=10).decode('utf-8')
      except (subprocess.SubprocessError, OSError) as e:
        raise BrowserStackLocalError('binarypath failed verification: {}'.format(e))
      if not re.match(LocalBinary.VERSION_REGEX, version_output):
        raise BrowserStackLocalError('binarypath failed verification')
      self.binary_path = candidate
      del self.options['binarypath']
    else:
      l = LocalBinary(self.key)
      try:
        self.binary_path = l.get_binary()
      except Exception as e:
        l = LocalBinary(self.key, e)
        self.binary_path = l.get_binary()

    if 'logfile' in self.options:
      self.local_logfile_path = self.options['logfile']
      del self.options['logfile']

    if "onlyCommand" in kwargs and kwargs["onlyCommand"]:
      return

    if 'source' in self.options:
      del self.options['source']

    logfile_dir = os.path.dirname(self.local_logfile_path)
    if logfile_dir:
        os.makedirs(logfile_dir, exist_ok=True)
    try:
        with open(self.local_logfile_path, 'w') as f:
            f.write('')
    except OSError as e:
        raise BrowserStackLocalError('Unable to open logfile: {}'.format(e))

    self.proc = subprocess.Popen(self._generate_cmd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = self.proc.communicate()

    try:
      if out:
        output_string = out.decode()
      else:
        output_string = err.decode()

      data = json.loads(output_string)

      if data['state'] != "connected":
        raise BrowserStackLocalError(data["message"]["message"])
      else:
        self.pid = data['pid']
    except ValueError:
      logger.error("BinaryOutputParseError: Raw String = '{}'".format(output_string) )
      raise BrowserStackLocalError('Error parsing JSON output from daemon. Raw String = "{}"'.format(output_string))

  def isRunning(self):
    return hasattr(self, 'pid') and psutil.pid_exists(self.pid)

  def stop(self):
    try:
      proc = subprocess.Popen(self._generate_stop_cmd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      (out, err) = proc.communicate()
    except Exception as e:
      return

  def __enter__(self):
    self.start(**self.options)
    return self

  def __exit__(self, *args):
    self.stop()
