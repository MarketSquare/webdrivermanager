#!/usr/bin/env python
DOIT_CONFIG = {'default_tasks': []}

def task_tests():
    return {
        'actions': ['python test/test_acceptance.py']
    }

def task_coverage():
    return {
        'actions': ['coverage run test/test_acceptance.py']
    }

def task_cleandist():
    return {
        'actions': ['rm -rf dist report output .coverage*']
    }

def task_dist():
    return {
        'actions': ['python setup.py sdist']
    }

def task_release():
    return {
        'actions': ['twine upload -r pypi dist/webdrivermanager*.tar.gz']
    }


if __name__ == '__main__':
    import doit
    doit.run(globals())
