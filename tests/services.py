import os
import shutil
import signal
import subprocess
import sys

import pytest

from pathlib import Path


DEFAULT_STATE_DIR = '_caterva2'
TEST_STATE_DIR = DEFAULT_STATE_DIR + '_tests'


class Services:
    def __init__(self, state_dir, reuse_state=True):
        self.state_dir = Path(state_dir).resolve()
        self.source_dir = Path(__file__).parent.parent
        self.reuse_state = reuse_state

        self._procs = {}

    def start_all(self):
        if not self.reuse_state and self.state_dir.is_dir():
            shutil.rmtree(self.state_dir)
        self.state_dir.mkdir(exist_ok=True)

        data_dir = self.state_dir / 'data'
        if not data_dir.exists():
            examples_dir = self.source_dir / 'root-example'
            shutil.copytree(examples_dir, data_dir, symlinks=True)
        data_dir.mkdir(exist_ok=True)

        src_dir = self.source_dir / 'src'
        os.environ['CATERVA2_SOURCE'] = str(self.source_dir)

        procs = self._procs
        procs['bro'] = subprocess.Popen([sys.executable,
                                         src_dir / 'bro.py',
                                         '--statedir=%s' % (self.state_dir / 'bro')])
        procs['pub'] = subprocess.Popen([sys.executable,
                                         src_dir / 'pub.py',
                                         '--statedir=%s' % (self.state_dir / 'pub'),
                                         'foo', data_dir])
        procs['sub'] = subprocess.Popen([sys.executable,
                                         src_dir / 'sub.py',
                                         '--statedir=%s' % (self.state_dir / 'sub')])

    def stop_all(self):
        for proc in self._procs.values():
            os.kill(proc.pid, signal.SIGTERM)

    def wait_for_all(self):
        for proc in self._procs.values():
            proc.wait()


@pytest.fixture(scope='session')
def services():
    srvs = Services(TEST_STATE_DIR, reuse_state=False)
    srvs.start_all()
    yield srvs
    srvs.stop_all()
    srvs.wait_for_all()


def main(argv, env):
    state_dir = argv[1] if len(argv) >= 2 else DEFAULT_STATE_DIR
    srvs = Services(state_dir, reuse_state=True)
    srvs.start_all()
    srvs.wait_for_all()


if __name__ == '__main__':
    main(sys.argv, os.environ)
