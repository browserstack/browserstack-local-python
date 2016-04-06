import subprocess, os, time
from browserstack.local_binary import LocalBinary
from browserstack.bserrors import BrowserStackLocalError

class Local:
  def __init__(self, key=None, binary_path=None):
    self.options = {
      'key': key,
      'logfile_flag': '-logFile',
      'logfile_path': os.path.join(os.getcwd(), 'local.log')
    }
    self.local_folder_path = None
    self.local_logfile_path = self.options['logfile_path']

  def __xstr(self, obj):
    if obj is None:
      return ''
    return str(obj)

  def _generate_cmd(self):
    options_order = ['logfile_flag', 'logfile_path', 'folder_flag', 'key', 'folder_path', 'forcelocal', 'local_identifier', 'only', 'only_automate', 'proxy_host', 'proxy_port', 'proxy_user', 'proxy_pass', 'forceproxy' 'force', 'verbose', 'hosts']
    cmd = [self.__xstr(self.options.get(o)) for o in options_order if self.options.get(o) is not None]
    return [self.binary_path] + cmd

  def start(self, **kwargs):
    for key, value in kwargs.items():
      self.__add_arg(key, value)
    
    if 'binarypath' in self.options:
      self.binary_path = binary_path
    else:
      self.binary_path = LocalBinary().get_binary()

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

  def __add_arg(self, key, value):
    if key == 'verbose' and value:
      self.options['verbose'] = '-v'
    elif key == 'force' and value:
      self.options['force'] = '-force'
    elif key == 'only' and value:
      self.options['only'] = '-only'
    elif key == 'onlyAutomate' and value:
      self.options['only_automate'] = '-onlyAutomate'
    elif key == 'forcelocal' and value:
      self.options['forcelocal'] = '-forcelocal'
    elif key == 'localIdentifier':
      self.options['local_identifier'] = '-localIdentifier ' + str(value)
    elif key == 'f':
      self.options['folder_flag'] = '-f'
      self.options['folder_path'] = str(value)
    elif key == 'proxyHost':
      self.options['proxy_host'] = '-proxyHost ' + str(value)
    elif key == 'proxyPort':
      self.options['proxy_port'] = '-proxyPort ' + str(value)
    elif key == 'proxyUser':
      self.options['proxy_user'] = '-proxyUser ' + str(value)
    elif key == 'proxyPass':
      self.options['proxy_pass'] = '-proxyPass ' + str(value)
    elif key == 'hosts':
      self.options['hosts'] = str(value)
    elif key == 'forceproxy' and value:
      self.options['forceproxy'] = '-forceproxy'
    elif key == 'logfile':
      self.options['logfile_flag'] = '-logFile'
      self.options['logfile'] = str(value)
      self.local_logfile_path = str(value)
    elif key == 'binarypath':
      self.options['binarypath'] = str(value)
    elif key != 'onlyCommand':
      raise BrowserStackLocalError('Attempted to pass invalid option to binary')

  def stop(self):
    try:
      self.proc.terminate()
      while True:
        if not self.isRunning():
          break
        time.sleep(1)
    except Exception as e:
      return