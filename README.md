# Setup

### Prereqs

Ensure python 3.6 is installed (check using `python3 -V`).

Install `easy_install`.

Install `pip`.

### Setup

VirtualEnv is a way to create isolated Python environments for every project and VirtualEnvWrapper "wraps" the virtualenv API to make it more user friendly.

```
pip install pip --upgrade
pip install virtualenv
pip install virtualenvwrapper
```

To complete the virtualenv setup process, put the following in you ~/.bash_profile

```
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```

### Create virtual environment

Run the following in the root folder of the cloned repo:

```
mkvirtualenv job-bilby --python=python3
workon job-bilby
pip install pip --upgrade
pip install -r requirements.txt
```

To deactivate the virtual environment, use `deactivate`.

**NOTE** This guide will be amended to include database creation, migration etc, and to flesh out install steps if required.
