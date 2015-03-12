from __future__ import absolute_import


from django.core.management.base import BaseCommand

from pip.util import get_installed_distributions
from optparse import make_option

from ...vcs import VCS
from .ci import Command


class Command(Command):
    help = (
        'Usage: ./manage.py ignore [--yes] [add|remove] pattern [app_name]'
    )

    option_list = BaseCommand.option_list + (
        make_option(
            '--yes',
            action='store_true',
            dest='always_yes',
            default=False,
            help='Answer Yes to any questions.'
        ),
    )

    def handle(self, *args, **kwargs):

        always_yes = kwargs.get('always_yes')

        operation = len(args) > 0 and args[0] or ''
        pattern = len(args) > 1 and args[1] or ''
        app_name = len(args) > 2 and args[2] or ''

        last_ignore_file = ''

        if app_name:
            try:
                app_module = __import__(app_name)
                app_name = app_module.__file__
            except ImportError:
                self.stderr.write('App not found %s' % app_name)
                return

        for dist in Command.get_dists():

            if app_name and (not app_name.startswith(dist.location)):
                continue

            project_name, version, location = (
                dist.project_name, dist.version, dist.location)

            vcs = VCS.create(location, stdout=self.stdout)

            if vcs is None:
                continue

            self.info(project_name, None, vcs)

            if always_yes or self.confirm(
                prompt = '%s %s from ignore file for %s ?\n' % (
                    operation,
                    pattern,
                    project_name,
                ),
                resp = True
            ):
                last_ignore_file = '\n'.join(vcs.ignore(pattern, (operation=='add')))
                self.stdout.write('\n')

        self.stdout.write('Last ignore file contents:\n%s' % last_ignore_file)