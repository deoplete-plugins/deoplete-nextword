# ============================================================================
# FILE: nextword.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# ============================================================================

from deoplete.base.source import Base

import subprocess


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'nextword'
        self.mark = '[nextword]'
        self.vars = {
            'args': ['-n', '100', '-g'],
        }
        self.is_volatile = True
        self.sorters = []

        self._executable_nextword = self.vim.call('executable', 'nextword')
        self._proc = None

    def on_init(self, context):
        if not self._executable_nextword:
            return
        self._restart()

    def gather_candidates(self, context):
        if not self._proc:
            return []

        try:
            self._proc.stdin.write(context['input'] + '\n')
            self._proc.stdin.flush()
        except BrokenPipeError:
            self._restart()
            return []

        out = self._proc.stdout.readline()
        return [{'word': x} for x in out.split()]

    def _restart(self):
        if self._proc is not None:
            self._proc.terminate()
            self._proc = None

        self._proc = subprocess.Popen(['nextword'] + self.get_var('args'),
                                      encoding='utf-8',
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL)
