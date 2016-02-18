import unittest, time, os, subprocess
from mock import Mock, MagicMock
from browserstack.local import Local, BrowserStackLocalError

class TestLocal(unittest.TestCase):
    def setUp(self):
        mock_readline = MagicMock(return_value='Press Ctrl-C to exit')
        mock_stdout = Mock(readline=mock_readline)
        subprocess.Popen =  MagicMock(return_value=Mock(stdout=mock_stdout))
        self.local = Local(os.environ['BROWSERSTACK_KEY'])

    def tearDown(self):
        self.local.stop()

    def test_start_local(self):
        self.local.start()
        self.assertNotEqual(self.local.proc.pid, 0)

    def test_verbose(self):
        self.local.start(verbose=True)
        self.assertIn('-v', self.local._generate_cmd())

    def test_local_folder(self):
        self.local.start(f='hello')
        self.assertIn('-f', self.local._generate_cmd())
        self.assertIn('hello', self.local._generate_cmd())

    def test_force_kill(self):
        self.local.start(force=True)
        self.assertIn('-force', self.local._generate_cmd())

    def test_only_automate(self):
        self.local.start(only_automate=True)
        self.assertIn('-onlyAutomate', self.local._generate_cmd())

    def test_force_local(self):
        self.local.start(forcelocal=True)
        self.assertIn('-forcelocal', self.local._generate_cmd())

    def test_proxy(self):
        self.local.start(proxy_host='localhost', proxy_port=2000, proxy_user='hello', proxy_pass='test123')
        self.assertIn('-proxyHost localhost', self.local._generate_cmd())
        self.assertIn('-proxyPort 2000', self.local._generate_cmd())
        self.assertIn('-proxyUser hello', self.local._generate_cmd())
        self.assertIn('-proxyPass test123', self.local._generate_cmd())

    def test_local_identifier(self):
        self.local.start(local_identifier='mytunnel')
        self.assertIn('-localIdentifier mytunnel', self.local._generate_cmd())

    def test_invalid_option(self):
        self.assertRaises(BrowserStackLocalError, lambda: self.local.start(random=True))
