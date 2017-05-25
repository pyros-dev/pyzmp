from __future__ import absolute_import, division, print_function

import os
import sys
import io

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

import psutil

import pexpect.popen_spawn
from pyzmp.process_observer import ProcessObserver

# Here we test basic process observer behavior, with a bunch of different ways to start and control a process





class TestSubprocessObserver(object):
    __test__ = True

    def setup_method(self, method):
        """Emergency cleanup if something happened and the process from a previous test is still there"""
        if hasattr(self, 'testproc'):
            if self.testproc.poll():
                self.testproc.terminate()
            # if it s still alive, just terminate it.
            if self.testproc.poll():
                self.testproc.kill()
        if hasattr(self, 'testobserver'):
            self.testobserver = None

    def test_start_once(self):
        # start the process
        self.testproc = subprocess.Popen(["/bin/echo", "test_string"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        self.testobserver = ProcessObserver(self.testproc.pid)

        # basic checks
        assert self.testobserver.ppid() == os.getpid()

        # check that we get some output
        try:
            out, err = self.testproc.communicate(timeout=5)
        except psutil.TimeoutExpired:
            self.testproc.terminate()
            out, err = self.testproc.communicate()

        assert out == "test_string\n"
        assert err == ""

    def test_start_once_crash(self):
        # start the process
        self.testproc = subprocess.Popen(["/bin/cat", "no_filename_like_this"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        self.testobserver = ProcessObserver(self.testproc.pid)

        # basic checks
        assert self.testobserver.ppid() == os.getpid()

        # check that we get some error
        try:
            out, err = self.testproc.communicate(timeout=5)
        except psutil.TimeoutExpired:
            self.testproc.terminate()
            out, err = self.testproc.communicate()

        assert out == ""
        assert err == "/bin/cat: no_filename_like_this: No such file or directory\n"

    def test_start_forever_shutdown(self):
        # We are using ed as a long running process to interact with

        self.testproc = pexpect.spawn("/bin/ed -p\*")  # we need to use pexpect to manage interactive programs via a terminal
        #self.testproc = pexpect.popen_spawn.PopenSpawn(["ed", "-p\*"])
        #self.testproc = subprocess.Popen(["ed", "-p\*"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)

        # we can branch the observer onto stdout and stderr.
        self.testobserver = ProcessObserver.from_pexpect(self.testproc)

        # basic checks
        assert self.testobserver.ppid() == os.getpid()

        assert self.testobserver.is_running()

        try:
            self.testobserver.expect("\\*", timeout=5)

            self.testproc.write('H\n')
            self.testobserver.expect("\\*", timeout=5)

            self.testproc.write('a\n')
            self.testobserver.expect("\\*", timeout=5)

            self.testproc.write("some test string\n")
            self.testproc.write(".\n")
            self.testobserver.expect("\\*", timeout=5)

            self.testproc.write("p\n")
            self.testobserver.expect("\\some test string\n", timeout=5)

            self.testproc.write("Q\n")
            self.testobserver.expect("", timeout=5)

        except:  # something went wrong
            print("Exception was thrown")
            print("debug information:")
            print(str(self.testproc))
            # print("stdout:")
            # while not self.testobserver._expect_out.eof():
            #     print(self.testobserver._expect_out.readline())
            # print("stderr:")
            # while not self.testobserver.expecterr.eof():
            #     print(self.testobserver.expecterr.readline())
            raise

        self.testobserver.expect("")
        self.testobserver.expect("")

        # pipes are working well, time to shutdown
        pass


    def test_start_forever_terminate(self):
        self.testproc = psutil.Popen(["ed"],)
        self.testobserver = ProcessObserver(self.testproc.pid)

        while self.testobserver.is_running():
            self.testobserver.monitor()



class TestPsutilObserver(object):
    __test__ = True

    def setup_method(self, method):
        """Emergency cleanup if something happened and the process from a previous test is still there"""
        if hasattr(self, 'testproc'):
            if self.testproc.poll():
                self.testproc.terminate()
            # if it s still alive, just terminate it.
            if self.testproc.poll():
                self.testproc.kill()



class TestPexpectObserver(object):
    __test__ = True

    def setup_method(self, method):
        """Emergency cleanup if something happened and the process from a previous test is still there"""
        if hasattr(self, 'testproc'):
            if self.testproc.poll():
                self.testproc.terminate()
            # if it s still alive, just terminate it.
            if self.testproc.poll():
                self.testproc.kill()





if __name__ == '__main__':
    import pytest
    pytest.main(['-s', '-x', __file__])
