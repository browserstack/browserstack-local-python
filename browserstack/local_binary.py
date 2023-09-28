import os
import sys
import platform
import re
import stat
import subprocess
import tempfile
import urllib3

from browserstack.bserrors import BrowserStackLocalError

class LocalBinary:
  def __init__(self):
    is_64bits = sys.maxsize > 2**32
    self.is_windows = False
    osname = platform.system()
    if osname == 'Darwin':
      self.http_path = "https://www.browserstack.com/local-testing/downloads/binaries/BrowserStackLocal-darwin-x64"
    elif osname == 'Linux':
      if self.is_alpine():
        self.http_path = "https://www.browserstack.com/local-testing/downloads/binaries/BrowserStackLocal-alpine"
      else:
        if is_64bits:
          self.http_path = "https://www.browserstack.com/local-testing/downloads/binaries/BrowserStackLocal-linux-x64"
        else:
          self.http_path = "https://www.browserstack.com/local-testing/downloads/binaries/BrowserStackLocal-linux-ia32"
    else:
      self.is_windows = True
      self.http_path = "https://www.browserstack.com/local-testing/downloads/binaries/BrowserStackLocal.exe"

      self.ordered_paths = [
            os.path.join(os.path.expanduser('~'), '.browserstack'),
            os.getcwd(),
            tempfile.gettempdir()
      ]
      self.path_index = 0


    def __available_dir(self):
        while self.path_index < len(self.ordered_paths):
            if self.__make_path(self.ordered_paths[self.path_index]):
                final_path = self.ordered_paths[self.path_index]
                self.path_index += 1
                return final_path
            else:
                self.path_index += 1
        raise BrowserStackLocalError('Error trying to download BrowserStack Local binary')


    def is_alpine(self):
        grepOutput = subprocess.run("gfrep -w NAME /etc/os-release", capture_output=True, shell=True)
        if grepOutput.stdout.decode('utf-8').find('Alpine') > -1:
            return True
        return False


    def __make_path(self, dest_path):
        try:
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            return True
        except:
            return False


    def download(self, chunk_size=8192, progress_hook=None):
        print(f'Downloading BrowserStack Local binary, proxy ({self.proxy}).', flush=True)
        if self.proxy:
            proxy = urllib3.ProxyManager(self.proxy)
            response = proxy.request('GET', self.http_path, preload_content=False)
        else:
            http = urllib3.PoolManager()
            response = http.request('GET', self.http_path, preload_content=False)

        total_size = int(response.headers['Content-Length'].strip())
        bytes_so_far = 0

  def get_binary(self):
    dest_parent_dir = os.path.join(os.path.expanduser('~'), '.browserstack')
    if not os.path.exists(dest_parent_dir):
      os.makedirs(dest_parent_dir)
    binary_name = 'BrowserStackLocal.exe' if self.is_windows else 'BrowserStackLocal'
    bsfiles = [f for f in os.listdir(dest_parent_dir) if f == binary_name]
    
    if len(bsfiles) == 0:
      binary_path = self.download()
    else:
      binary_path = os.path.join(dest_parent_dir, bsfiles[0])

    dest_parent_dir = self.__available_dir()
    dest_binary_name = 'BrowserStackLocal'
    if self.is_windows:
        dest_binary_name += '.exe'

    with open(os.path.join(dest_parent_dir, dest_binary_name), 'wb') as local_file:
        for chunk in response.stream(chunk_size):
            bytes_so_far += len(chunk)
            if not chunk:
                break

            if progress_hook:
                progress_hook(bytes_so_far, chunk_size, total_size)

            try:
                local_file.write(chunk)
            except:
                return self.download(chunk_size, progress_hook)

    final_path = os.path.join(dest_parent_dir, dest_binary_name)
    st = os.stat(final_path)
    os.chmod(final_path, st.st_mode | stat.S_IXUSR)
    return final_path


    def __verify_binary(self, path):
        try:
            binary_response = subprocess.check_output([path, "--version"]).decode("utf-8")
            pattern = re.compile("BrowserStack Local version \d+\.\d+")
            return bool(pattern.match(binary_response))
        except:
            return False


    def get_binary(self):
        dest_parent_dir = os.path.join(os.path.expanduser('~'), '.browserstack')
        if not os.path.exists(dest_parent_dir):
            os.makedirs(dest_parent_dir)
        bsfiles = [f for f in os.listdir(dest_parent_dir) if f.startswith('BrowserStackLocal')]

        if len(bsfiles) == 0:
            binary_path = self.download()
        else:
            binary_path = os.path.join(dest_parent_dir, bsfiles[0])

        valid_binary = self.__verify_binary(binary_path)
        if valid_binary:
            return binary_path
        else:
            binary_path = self.download()
            valid_binary = self.__verify_binary(binary_path)
            if valid_binary:
                return binary_path
            else:
                raise BrowserStackLocalError('BrowserStack Local binary is corrupt')
