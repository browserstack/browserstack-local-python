import platform, urllib2, os, sys, zipfile, stat, tempfile
from browserstack.bserrors import BrowserStackLocalError

class LocalBinary:
    def __init__(self):
        is_64bits = sys.maxsize > 2**32
        osname = platform.system()
        if osname == 'Darwin':
            self.http_path = "https://www.browserstack.com/browserstack-local/BrowserStackLocal-darwin-x64.zip"
        elif osname == 'Linux':
            if is_64bits:
                self.http_path = "https://www.browserstack.com/browserstack-local/BrowserStackLocal-linux-x64.zip"
            else:
                self.http_path = "https://www.browserstack.com/browserstack-local/BrowserStackLocal-linux-ia32.zip"
        else:
            self.http_path = "https://www.browserstack.com/browserstack-local/BrowserStackLocal-win32.zip"

        self.ordered_paths = [
            os.path.join(os.path.expanduser('~'), '.browserstack'),
            os.getcwd(),
            tempfile.gettempdir()
        ]
        self.path_index = 0

    def __make_path(self, dest_path):
        try:
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            return True
        except:
            return False

    def __available_dir(self):
        while self.path_index < len(self.ordered_paths):
            if self.__make_path(self.ordered_paths[self.path_index]):
                final_path = self.ordered_paths[self.path_index]
                self.path_index += 1
                return final_path
            else:
                self.path_index += 1
        raise BrowserStackLocalError('Error trying to download BrowserStack Local binary')

    def download(self, chunk_size=8192, progress_hook=None):
        response = urllib2.urlopen(self.http_path)
        total_size = int(response.info().getheader('Content-Length').strip())
        bytes_so_far = 0

        dest_parent_dir = self.__available_dir()

        with open(os.path.join(dest_parent_dir, 'download.zip'), 'wb') as local_file:
            while True:
                chunk = response.read(chunk_size)
                bytes_so_far += len(chunk)

                if not chunk:
                    break

                if progress_hook:
                    progress_hook(bytes_so_far, chunk_size, total_size)

                try:
                    local_file.write(chunk)
                except:
                    return self.download(chunk_size, progress_hook)

        with zipfile.ZipFile(open(os.path.join(dest_parent_dir, 'download.zip'), 'r')) as z:
            for name in z.namelist():
                try:
                    z.extract(name, dest_parent_dir)
                except:
                    return self.download(chunk_size, progress_hook)
                # There is only one file
                final_path = os.path.join(dest_parent_dir, name)
                st = os.stat(final_path)
                os.chmod(final_path, st.st_mode | stat.S_IXUSR)
                return final_path

    def get_binary(self):
        dest_parent_dir = os.path.join(os.path.expanduser('~'), '.browserstack')
        if not os.path.exists(dest_parent_dir):
            os.makedirs(dest_parent_dir)
        bsfiles = [f for f in os.listdir(dest_parent_dir) if f.startswith('BrowserStackLocal')]
        if len(bsfiles) == 0:
            return self.download()
        else:
            return os.path.join(dest_parent_dir, bsfiles[0])
