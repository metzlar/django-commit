from vcs import VCS as Base

import subprocess
import StringIO


class _GITVCS(Base):
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

    def push_to_origin(self):
        subprocess.call(
            ['git','push'],
            stdout=self.stdout,
            cwd=self.path
        )

VCS = _GITVCS