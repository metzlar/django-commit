from __future__ import absolute_import


from django.core.management.base import BaseCommand

from pip.util import get_installed_distributions
from optparse import make_option

from ...vcs import VCS
from .ci import Command


class Command(Command):
    help = (
        'Usage: ./manage.py pup [--yes] [app_name]'
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

        app_name = len(args) > 0 and args[0] or ''

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
                prompt = 'Pull and update changes for: %s ?\n' % project_name,
                resp = True
            ):
                vcs.pull_n_update()
                self.stdout.write('\n')