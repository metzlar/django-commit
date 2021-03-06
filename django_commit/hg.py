from vcs import VCS as Base

import subprocess


class _HGVCS(Base):
    ignore_file = '.hgignore'

    # todo: use Mercurial python libraries instead of subprocess

    def status(self):
        proc = subprocess.Popen(
            ['hg','status', '-m'],
            stdout=subprocess.PIPE,
            cwd=self.path
        )

        return [
            l for l in
            proc.communicate()[0].split('\n')
            if l
        ]

    def revert(self, file):
        subprocess.call(
            ['hg', 'revert', file],
            stdout=self.stdout,
            cwd=self.path,
        )

    def write_diff(self):
        subprocess.call(
            ['hg', 'diff'],
            stdout=self.stdout,
            cwd=self.path,
        )

    def pull_n_update(self):
        subprocess.call(
            ['hg', 'pull', '-u'],
            stdout=self.stdout,
            cwd=self.path,
        )

    def ignore(self, pattern, add, ignore_file=None):
        return super(_HGVCS, self).ignore(pattern, add, self.ignore_file)

    def commit_changes(self, message):
        subprocess.call(
            ['hg', 'commit', '-m', message],
            stdout=self.stdout,
            cwd=self.path,
        )

    def push_to_origin(self):
        subprocess.call(
            ['hg','push'],
            stdout=self.stdout,
            cwd=self.path
        )

VCS = _HGVCS