from setuptools import setup # pragma: no cover 

setup(
  name='Django Commit',
  version='0.1',
  py_modules=['django_commit'],
  cmdclass={'upload':lambda x:None},
  install_requires=[
    'django',
    'pip>=6'
  ],
)# pragma: no cover 
