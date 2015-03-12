import os
import sys
import warnings


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

    def pull_n_update(self):
        '''
        Pull the latest changes from master/default origin branch.
        '''
        raise NotImplemented('Must implement `pull_n_update()`')

    def revert(self, file):
        '''
        Revert and forget all changes to `file`.
        '''
        raise NotImplemented('Must implement `revert()`')

    def ignore(self, pattern, add, ignore_file=None):
        '''
        if `add` equals `True`, append `pattern` to the ignore file.
        Else try to remove it from the ignore file.
        '''
        if ignore_file is None:
            raise NotImplemented('Must implement `ignore()` and call super with `ignore_file` specified.')

        ignore_file = os.path.join(self.path, ignore_file)

        if not os.path.exists(ignore_file):
            warnings.warn('Not found, creating %s' % ignore_file)
            open(ignore_file, 'w').close()

        with open(ignore_file, 'r+') as f:
            lines = [l.strip('\n') for l in f if l]
            write_out = False
            if not add:
                if pattern in lines:
                    lines.remove(pattern)
                    write_out = True
            else:
                if not pattern in lines:
                    lines.append(pattern)
                    write_out = True

            if write_out:
                f.truncate(0)
                for l in lines:
                    f.write(l+'\n')
                f.flush()

        return lines

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