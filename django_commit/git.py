from vcs import VCS as Base

import subprocess
import StringIO


class _GITVCS(Base):
    ignore_file = '.gitignore'

    def status(self):
        proc = subprocess.Popen(
            #['git','ls-files', '-m'],
            ['git', 'diff', '--name-status'],
            stdout=subprocess.PIPE,
            cwd=self.path
        )

        return [
            l.replace('\t', ' ') for l in
            proc.communicate()[0].split('\n')
            if l
        ]

    def revert(self, file):
        subprocess.call(
            ['git', 'checkout', '--', file],
            stdout=self.stdout,
            cwd=self.path,
        )

    def write_diff(self):
        subprocess.call(
            ['git','diff'],
            stdout=self.stdout,
            cwd=self.path,
        )

    def commit_changes(self, message):
        subprocess.call(
            ['git','commit', '-a', '-m', message],
            stdout=self.stdout,
            cwd=self.path,
        )

    def ignore(self, pattern, add, ignore_file=None):
        return super(_GITVCS, self).ignore(pattern, add, self.ignore_file)

    def pull_n_update(self):
        subprocess.call(
            ['git','pull', 'origin', 'master'],
            stdout=self.stdout,
            cwd=self.path,
        )

    def push_to_origin(self):
        subprocess.call(
            ['git','push'],
            stdout=self.stdout,
            cwd=self.path
        )

VCS = _GITVCS