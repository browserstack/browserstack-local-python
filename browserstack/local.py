import subprocess, os, time
from browserstack.local_binary import LocalBinary
from browserstack.bserrors import BrowserStackLocalError

class Local:
  def __init__(self, key=os.environ['BROWSERSTACK_ACCESS_KEY'], binary_path=None):
    self.key = key
    self.options = None
    self.local_logfile_path = os.path.join(os.getcwd(), 'local.log')

  def __xstr(self, key, value):
    if key is None:
      return ['']
    if str(value).lower() == "true":
      return ['-' + key]
    else:
      return ['-' + key, value]

  def _generate_cmd(self):
    cmd = [self.binary_path, '-logFile', self.local_logfile_path, self.key]
    for o in self.options.keys():
      if self.options.get(o) is not None:
        cmd = cmd + self.__xstr(o, self.options.get(o))
    return cmd

  def start(self, **kwargs):
    self.options = kwargs

    if 'key' in self.options:
      self.key = self.options['key']
      del self.options['key']

    if 'binarypath' in self.options:
      self.binary_path = binary_path
      del self.options['binarypath']
    else:
      self.binary_path = LocalBinary().get_binary()

    if 'logfile' in self.options:
      self.local_logfile_path = self.options['logfile']
      del self.options['logfile']

    if "onlyCommand" in kwargs and kwargs["onlyCommand"]:
      return

    self.proc = subprocess.Popen(self._generate_cmd(), stdout=subprocess.PIPE)
    self.stderr = self.proc.stderr

    os.system('echo "" > "'+ self.local_logfile_path +'"')
    with open(self.local_logfile_path, 'r') as local_logfile:
      while True:
        line = local_logfile.readline()
        if 'Error:' in line.strip():
          raise BrowserStackLocalError(line)
        elif line.strip() == 'Press Ctrl-C to exit':
          break

    while True:
      if self.isRunning():
        break
      time.sleep(1)

  def isRunning(self):
    if (hasattr(self, 'proc')):
      return True if self.proc.poll() is None else False
    return False

  def stop(self):
    try:
      self.proc.terminate()
      while True:
        if not self.isRunning():
          break
        time.sleep(1)
    except Exception as e:
      return