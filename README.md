django-commit
=============

Commit and push changes made to all editable (pip install -e) packages with a django management command.

Installation
------------

Run `pip install django-commit` to install and add `django_commit` to your `INSTALLED_APPS`

Usage
-----

To commit and push all changes in all edible applications:

    ./manage.py ci "Your commit message"

To commit and push a single Django app:

    ./manage.py ci "Your commit message" cms
  
To view a diff of all current changes:

    ./manage.py ci --diff
  
To view a diff of a single Django app:

    ./manage.py ci --diff cms
  
To pull and update all remote changes:

    ./manage.py pup
    
To pull and update remote changes of a single Django app:

    ./manage.py pup cms
