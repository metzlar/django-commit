from django.core.management.base import BaseCommand

from pip.util import get_installed_distributions
import os
import subprocess
from StringIO import StringIO


def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True

    """
    
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


class Command(BaseCommand):
    help = (
        'Usage: ci "My message"\n'
        'Commit all changes made in all editable packages '
    )

    def handle(self, *args, **kwargs):

        message = args[0]
        
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
                proc = subprocess.Popen(
                    ['git','ls-files', '-m'],
                    stdout=subprocess.PIPE, cwd=location)
                lines_val = proc.communicate()[0].split('\n')
                if len(lines_val) > 0:
                    if confirm(
                        prompt = (
                            'About to commit changes to:\n%s' %
                            ('\n'.join(lines_val))),
                        resp = True
                    ):
                        subprocess.call(
                            ['git','commit', '-a', '-m', message],
                            stdout=self.stdout, cwd=location
                        )
                        subprocess.call(
                            ['git','push'],
                            stdout=self.stdout, cwd=location
                        )