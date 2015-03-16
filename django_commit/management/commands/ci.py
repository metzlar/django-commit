from __future__ import absolute_import

from django.core.management.base import BaseCommand

try:
    from pip.util import get_installed_distributions
except ImportError:
    # newer versions of pip
    from pip import get_installed_distributions

from optparse import make_option

from std2.ducktyping import DuckDict

from ...vcs import VCS


class Command(BaseCommand):

    colors = DuckDict(
        HEADER = '\033[95m',
        OKBLUE = '\033[94m',
        OKGREEN = '\033[92m',
        WARNING = '\033[93m',
        FAIL = '\033[91m',
        ENDC = '\033[0m',
        BOLD = '\033[1m',
        UNDERLINE = '\033[4m',
    )

    help = (
        'Usage: ./manage.py ci [--no-push] "My commit message" [app_name]\n'
        '       Commit all changes made in [app_name] or all editable packages\n'
        '       if [app_name] is not set and push (unless --no-push is specified).'
        '       \n'
        '       ./manage.py ci --st [app_name]\n'
        '       Do not commit but show a list of status messages.'
        '       \n'
        '       ./manage.py ci --diff [app_name]\n'
        '       Do not commit but show a diff instead.'
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
            '--diff',
            action='store_true',
            dest='diff',
            default=False,
            help='Just show the diff without actual committing'
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
            prompt = ('%s '+ self.colors.BOLD +'[%s]|%s: ') % (prompt, 'y', 'n')
        else:
            prompt = ('%s '+ self.colors.BOLD +'[%s]|%s: ') % (prompt, 'n', 'y')

        prompt += self.colors.ENDC

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

    def info(self, project_name, message, vcs):
        self.stdout.write(
            self.colors.OKGREEN +
            '=== %s %s\n' % (project_name, vcs) +
            self.colors.ENDC
        )
        if message:
            self.stdout.write(
                'Using commit message:\n\n')
            self.stdout.write(message)

    @staticmethod
    def get_dists():
        packages = get_installed_distributions(
            local_only=True, editables_only=True)

        packages = sorted(
            packages, key=lambda dist: dist.project_name.lower())

        return packages

    def handle(self, *args, **kwargs):

        status_only = kwargs.get('status')
        no_push = kwargs.get('no_push')
        diff_only = kwargs.get('diff')

        if not diff_only and not status_only and len(args) == 0:
            self.stderr.write(
                'Single commit message argument required')
            self.stderr.write(self.help)
            return

        message = len(args) > 0 and args[0] or ''
        app_name = len(args) > 1 and args[1] or ''

        if status_only is True or diff_only is True:
            if message and (not app_name):
                app_name = message
                message = 'NO commit is performed.'

        if app_name:
            try:
                app_module = __import__(app_name)
                app_name = app_module.__file__
            except ImportError:
                app_name = ''
                # all apps in this case app_name is the message
                # self.stderr.write('App not found %s' % app_name)
                # return

        for dist in Command.get_dists():

            if app_name and (not app_name.startswith(dist.location)):
                continue

            project_name, version, location = (
                dist.project_name, dist.version, dist.location)

            vcs = VCS.create(location, stdout=self.stdout)

            if vcs is None:
                continue

            files = vcs.status()

            if len(files) > 0:
                self.info(project_name, message, vcs)

                if diff_only:
                    vcs.write_diff()
                elif status_only is True:
                    self.stdout.write(
                        '\nCommit changes to:\n%s' %
                        ('\n'.join(files)))
                elif self.confirm_for(files):
                    vcs.commit_changes(message)

                    if not no_push:
                        vcs.push_to_origin()
                    else:
                        self.stdout.write(
                            'Did NOT push.'
                        )
                self.stdout.write('\n\n')
