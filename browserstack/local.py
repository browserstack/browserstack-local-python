import subprocess, os, time, json, psutil
import browserstack.version
from browserstack.local_binary import LocalBinary
from browserstack.bserrors import BrowserStackLocalError


# Python modules report to module_name.__version__ with their version
# Ref: https://www.python.org/dev/peps/pep-0008/#module-level-dunder-names
# With this, browserstack.local.__version__ will respond with <version>
__version__ = browserstack.version.__version__

class Local:
  def __init__(self, key=None, binary_path=None, **kwargs):
    self.key = os.environ['BROWSERSTACK_ACCESS_KEY'] if 'BROWSERSTACK_ACCESS_KEY' in os.environ else key
    self.options = kwargs
    self.local_logfile_path = os.path.join(os.getcwd(), 'local.log')

  def __xstr(self, key, value):
    if key is None:
      return ['']
    if str(value).lower() == "true":
      return ['-' + key]
    else:
      return ['-' + key, value]

  def _get_version(self):
      return __version__

  def _generate_cmd(self):
    cmd = [self.binary_path, '-d', 'start','--source', 'python-' + self._get_version() , '-logFile', self.local_logfile_path, self.key]
    for o in self.options.keys():
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
      self.binary_path = self.options['binarypath']
      del self.options['binarypath']
    else:
      self.binary_path = LocalBinary().get_binary()

    if 'logfile' in self.options:
      self.local_logfile_path = self.options['logfile']
      del self.options['logfile']

    if "onlyCommand" in kwargs and kwargs["onlyCommand"]:
      return

    self.proc = subprocess.Popen(self._generate_cmd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = self.proc.communicate()

    os.system('echo "" > "'+ self.local_logfile_path +'"')
    try:
      if out:
        data = json.loads(out.decode())
      else:
        data = json.loads(err.decode())

      if data['state'] != "connected":
        raise BrowserStackLocalError(data["message"]["message"])
      else:
        self.pid = data['pid']
    except ValueError:
      raise BrowserStackLocalError('Error parsing JSON output from daemon')

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
