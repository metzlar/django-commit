import os
import sys


class VCS(object):
    '''
    Represents a VCS. An instance is a (local) repository.
    Instance methods are actions on the (local) repository.
    Class methods are actions in general.
    '''
    def __init__(self, path, stdout = None, stderr = None):
        self.path = path
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    def write_diff(self):
        '''
        Write the contents of the patch to self.stdout.
        '''
        raise NotImplemented('Must implement `get_diff()`')

    def status(self):
        '''
        A list of files and their status. If this list is empty
        no changes exist.
        '''
        raise NotImplemented('Must implement `status()`')

    def commit_changes(self, message):
        '''
        Commits all local changes.
        '''
        raise NotImplemented('Must implement `commit_changes()`')

    def push_to_origin(self):
        '''
        Push this repo to its origin
        '''
        raise NotImplemented('Must implement `push_to_origin()`')

    def __repr__(self):
        return self.__class__.__name__

    @classmethod
    def create(cls, path, **kwargs):
        '''
        Factory method will attempt to create the correct base class
        based on `path`
        '''

        for t in ['hg', 'git']:
            if os.path.exists(os.path.join(path, '.%s' % t)):
                mod = __import__('django_commit.%s' % t, fromlist=['django_commit'])
                return mod.VCS(path, **kwargs)