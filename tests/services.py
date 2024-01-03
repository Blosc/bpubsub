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

        self.data_dir = self.state_dir / 'data'

        self._procs = {}
        self._setup_done = False

    def _start_proc(self, name, *args):
        self._procs[name] = subprocess.Popen(
            [sys.executable,
             self.source_dir / 'src' / f'{name}.py',
             '--statedir=%s' % (self.state_dir / name),
             *args])

    def _setup(self):
        if self._setup_done:
            return

        if not self.reuse_state and self.state_dir.is_dir():
            shutil.rmtree(self.state_dir)
        self.state_dir.mkdir(exist_ok=True)

        if not self.data_dir.exists():
            examples_dir = self.source_dir / 'root-example'
            shutil.copytree(examples_dir, self.data_dir, symlinks=True)
        self.data_dir.mkdir(exist_ok=True)

        os.environ['CATERVA2_SOURCE'] = str(self.source_dir)

        self._setup_done = True

    def start_all(self):
        self._setup()

        self._start_proc('bro')
        self._start_proc('pub', 'foo', self.data_dir)
        self._start_proc('sub')

    def stop_all(self):
        for proc in self._procs.values():
            os.kill(proc.pid, signal.SIGTERM)

    def wait_for_all(self):
        for proc in self._procs.values():
            proc.wait()


@pytest.fixture(scope='session')
def services():
    srvs = Services(TEST_STATE_DIR, reuse_state=False)
    try:
        srvs.start_all()
        yield srvs
    finally:
        srvs.stop_all()
    srvs.wait_for_all()


def main(argv, env):
    state_dir = argv[1] if len(argv) >= 2 else DEFAULT_STATE_DIR
    srvs = Services(state_dir, reuse_state=True)
    try:
        srvs.start_all()
        srvs.wait_for_all()
    finally:
        srvs.stop_all()


if __name__ == '__main__':
    main(sys.argv, os.environ)