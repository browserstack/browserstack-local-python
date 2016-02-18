import subprocess
from browserstack.local_binary import LocalBinary

class BrowserStackLocalError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)

class Local:
    def __init__(self, key, binary_path=None):
        if binary_path is None:
            self.binary_path = LocalBinary().get_binary()
        else:
            self.binary_path = binary_path
        self.options = {
            'key': key
        }
        self.local_folder_path = None

    def __xstr(self, obj):
        if obj is None:
            return ''
        return str(obj)

    def _generate_cmd(self):
        options_order = ['folder_flag', 'key', 'folder_path', 'forcelocal', 'local_identifier', 'only', 'only_automate', 'proxy_host', 'proxy_port', 'proxy_user', 'proxy_pass', 'force', 'verbose', 'hosts']
        cmd = [self.__xstr(self.options.get(o)) for o in options_order if self.options.get(o) is not None]
        return [self.binary_path] + cmd

    def start(self, **kwargs):
        for key, value in kwargs.iteritems():
            self.__add_arg(key, value)
        self.proc = subprocess.Popen(self._generate_cmd(), stdout=subprocess.PIPE)
        self.stdout = self.proc.stdout
        self.stderr = self.proc.stderr
        while True:
            line = self.proc.stdout.readline()
            if 'Error:' in line.strip():
                raise BrowserStackLocalError(line)
            elif line.strip() == 'Press Ctrl-C to exit':
                break

    def is_running(self):
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
        elif key == 'only_automate' and value:
            self.options['only_automate'] = '-onlyAutomate'
        elif key == 'forcelocal' and value:
            self.options['forcelocal'] = '-forcelocal'
        elif key == 'local_identifier':
            self.options['local_identifier'] = '-localIdentifier ' + str(value)
        elif key == 'f':
            self.options['folder_flag'] = '-f'
            self.options['folder_path'] = str(value)
        elif key == 'proxy_host':
            self.options['proxy_host'] = '-proxyHost ' + str(value)
        elif key == 'proxy_port':
            self.options['proxy_port'] = '-proxyPort ' + str(value)
        elif key == 'proxy_user':
            self.options['proxy_user'] = '-proxyUser ' + str(value)
        elif key == 'proxy_pass':
            self.options['proxy_pass'] = '-proxyPass ' + str(value)
        elif key == 'hosts':
            self.options['hosts'] = str(value)
        else:
            raise BrowserStackLocalError('Attempted to pass invalid option to binary')

    def stop(self):
        if self.is_running():
            self.proc.terminate()
