from django.core.management.base import BaseCommand

from pip.util import get_installed_distributions
import os
import subprocess
from optparse import make_option


class Command(BaseCommand):
    help = (
        'Usage: ci "My commit message"\n'
        'Commit all changes made in all editable packages'
    )

    option_list = BaseCommand.option_list + (
        make_option(
            '--st',
            action='store_true',
            dest='status',
            default=False,
            help='Just show the status without actual commiting'
        ),
    )

    def confirm(self, prompt=None, resp=False):
        if prompt is None:
            prompt = 'Confirm'

        if resp:
            prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
        else:
            prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')

        while True:
            ans = raw_input(prompt)
            if not ans:
                return resp
            if ans not in ['y', 'Y', 'n', 'N']:
                print 'please enter y or n.'
                continue
            if ans == 'y' or ans == 'Y':
                return True
            if ans == 'n' or ans == 'N':
                return False

    def confirm_for(self, files):
        return self.confirm(
            prompt = (
                '\nCommit changes to:\n%s\n\n' %
                ('\n'.join(files))),
            resp = True
        )

    def info(self, project_name, message):
        self.stdout.write(
            '=== %s\n' % project_name)
        if message:
            self.stdout.write(
                'Using commit message:\n\n')
            self.stdout.write(message)

    def handle(self, *args, **kwargs):

        status_only = kwargs['status']

        if not status_only and len(args) != 1:
            self.stderr.write(
                'Single commit message argument required')
            self.stderr.write(self.help)
            return

        message = len(args) > 0 and args[0] or ''

        packages = get_installed_distributions(
            local_only=True, editables_only=True)

        packages = sorted(
            packages, key=lambda dist: dist.project_name.lower())

        for dist in packages:
            project_name, version, location = (
                dist.project_name, dist.version, dist.location)

            # test for mercurial
            if os.path.exists(os.path.join(location, '.hg')):
                proc = subprocess.Popen(
                    ['hg','status', '-m'],
                    stdout=subprocess.PIPE, cwd=location)
                files = [
                    l for l in
                    proc.communicate()[0].split('\n')
                    if l
                ]
                if len(files) > 0:

                    self.info(project_name, message)

                    if status_only is True:
                        self.stdout.write(
                            '\nCommit changes to:\n%s\n\n' %
                            ('\n'.join(files)))

                    elif self.confirm_for(files):
                        subprocess.call(
                            ['hg','commit', '-m', message],
                            stdout=self.stdout, cwd=location
                        )
                        subprocess.call(
                            ['hg','push'],
                            stdout=self.stdout, cwd=location
                        )
                    self.stdout.write('\n\n\n')

            # test for git
            if os.path.exists(os.path.join(location, '.git')):
                proc = subprocess.Popen(
                    ['git','ls-files', '-m'],
                    stdout=subprocess.PIPE, cwd=location)
                files = [
                    l for l in
                    proc.communicate()[0].split('\n')
                    if l
                ]
                if len(files) > 0:

                    self.info(project_name, message)

                    if status_only is True:
                        self.stdout.write(
                            '\nCommit changes to:\n%s\n\n' %
                            ('\n'.join(files)))

                    elif self.confirm_for(files):
                        subprocess.call(
                            ['git','commit', '-a', '-m', message],
                            stdout=self.stdout, cwd=location
                        )
                        subprocess.call(
                            ['git','push'],
                            stdout=self.stdout, cwd=location
                        )
                    self.stdout.write('\n\n\n')
