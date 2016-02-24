import unittest, time, os, subprocess, urllib2
from browserstack.local import Local, BrowserStackLocalError

class TestLocal(unittest.TestCase):
  def setUp(self):
    self.local = Local(os.environ['BROWSERSTACK_ACCESS_KEY'])

  def tearDown(self):
    self.local.stop()

  def test_start_local(self):
    self.local.start()
    self.assertNotEqual(self.local.proc.pid, 0)

  def test_verbose(self):
    self.local.start(verbose=True, onlyCommand=True)
    self.assertIn('-v', self.local._generate_cmd())

  def test_local_folder(self):
    self.local.start(f='hello', onlyCommand=True)
    self.assertIn('-f', self.local._generate_cmd())
    self.assertIn('hello', self.local._generate_cmd())

  def test_force_kill(self):
    self.local.start(force=True, onlyCommand=True)
    self.assertIn('-force', self.local._generate_cmd())

  def test_only_automate(self):
    self.local.start(onlyAutomate=True, onlyCommand=True)
    self.assertIn('-onlyAutomate', self.local._generate_cmd())

  def test_force_local(self):
    self.local.start(forcelocal=True, onlyCommand=True)
    self.assertIn('-forcelocal', self.local._generate_cmd())

  def test_proxy(self):
    self.local.start(proxyHost='localhost', proxyPort=2000, proxyUser='hello', proxyPass='test123', onlyCommand=True)
    self.assertIn('-proxyHost localhost', self.local._generate_cmd())
    self.assertIn('-proxyPort 2000', self.local._generate_cmd())
    self.assertIn('-proxyUser hello', self.local._generate_cmd())
    self.assertIn('-proxyPass test123', self.local._generate_cmd())

  def test_local_identifier(self):
    self.local.start(localIdentifier='mytunnel', onlyCommand=True)
    self.assertIn('-localIdentifier mytunnel', self.local._generate_cmd())

  def test_invalid_option(self):
    self.assertRaises(BrowserStackLocalError, lambda: self.local.start(random=True))

  def test_running(self):
    self.assertFalse(self.local.isRunning())
    self.local.start()
    self.assertTrue(self.local.isRunning())
