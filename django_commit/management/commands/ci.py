from django.core.management.base import BaseCommand

from pip.util import get_installed_distributions
import os
from subprocess import call

class Command(BaseCommand):
    help = (
        'Usage: ci "My message"\n'
        'Commit all changes made in all editable packages '
    )

    def handle(self, *args, **kwargs):

        packages = get_installed_distributions(
            local_only=True, editables_only=True)

        packages = sorted(
            packages, key=lambda dist: dist.project_name.lower())

        for dist in packages:
            project_name, version, location = (
                dist.project_name, dist.version, dist.location)

            self.stdout.write(
                'CI: %s (%s)' % (
                    project_name,
                    location
                ))

            # test for git
            if os.path.exists(os.path.join(location, '.git')):
                call(
                    ['git','ls-files', '-m'],
                    stdout=self.stdout, cwd=location)
            