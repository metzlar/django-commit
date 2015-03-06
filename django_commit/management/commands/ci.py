from django.core.management.base import BaseCommand

from pip.util import get_installed_distributions
import os
import subprocess
from optparse import make_option


class Command(BaseCommand):
    help = (
        'Usage: ./manage.py ci [--no-push] "My commit message" [app_name]\n'
        '       Commit all changes made in [app_name] or all editable packages\n'
        '       if [app_name] is not set and push (unless --no-push is specified).'
        '       \n'
        '       ./manage.py ci --st [app_name]\n'
        '       Do not commit but show a list of status messages.'
    )

    option_list = BaseCommand.option_list + (
        make_option(
            '--st',
            action='store_true',
            dest='status',
            default=False,
            help='Just show the status without actual committing'
        ),
        make_option(
            '--no-push',
            action='store_true',
            dest='no_push',
            default=False,
            help='Commit, but do not push.'
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

        status_only = kwargs.get('status')
        no_push = kwargs.get('no_push')

        if not status_only and len(args) == 0:
            self.stderr.write(
                'Single commit message argument required')
            self.stderr.write(self.help)
            return

        message = len(args) > 0 and args[0] or ''
        app_name = len(args) > 1 and args[1] or ''

        if status_only is True:
            if message and (not app_name):
                app_name = message
                message = 'NO commit is performed.'

        if app_name:
            try:
                app_module = __import__(app_name)
                app_name = app_module.__file__
            except ImportError:
                app_name = ''

        packages = get_installed_distributions(
            local_only=True, editables_only=True)

        packages = sorted(
            packages, key=lambda dist: dist.project_name.lower())

        for dist in packages:

            if app_name and (not app_name.startswith(dist.location)):
                continue

            project_name, version, location = (
                dist.project_name, dist.version, dist.location)

            # todo: refactor to support version control backends

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
                        if not no_push:
                            subprocess.call(
                                ['hg','push'],
                                stdout=self.stdout, cwd=location
                            )
                        else:
                            self.stdout.write(
                                'Did NOT push.'
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
                        if not no_push:
                            subprocess.call(
                                ['git','push'],
                                stdout=self.stdout, cwd=location
                            )
                        else:
                            self.stdout.write(
                                'Did NOT push.'
                            )
                    self.stdout.write('\n\n\n')
