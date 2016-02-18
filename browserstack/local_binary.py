import platform, urllib2, os, sys, zipfile, stat

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

    def download(self, chunk_size=8192, progress_hook=None):
        response = urllib2.urlopen(self.http_path)
        total_size = int(response.info().getheader('Content-Length').strip())
        bytes_so_far = 0

        dest_parent_dir = os.path.join(os.path.expanduser('~'), '.browserstack')
        if not os.path.exists(dest_parent_dir):
            os.makedirs(dest_parent_dir)

        with open(os.path.join(dest_parent_dir, 'download.zip'), 'wb') as local_file:
            while True:
                chunk = response.read(chunk_size)
                bytes_so_far += len(chunk)

                if not chunk:
                    break

                if progress_hook:
                    progress_hook(bytes_so_far, chunk_size, total_size)

                local_file.write(chunk)

        with zipfile.ZipFile(open(os.path.join(dest_parent_dir, 'download.zip'), 'r')) as z:
            for name in z.namelist():
                z.extract(name, dest_parent_dir)
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
