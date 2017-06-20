#!/usr/bin/env python2.7

# Grab an environmental variable
def get_env_var(var):
    import os
    if os.environ.get(var):
        return os.environ.get(var)

# Get password from environmental variable or prompt for input
def get_password(password_var=None):
    import getpass, os

    if password_var:
    	if get_env_var(password_var):
        	return get_env_var(password_var)
    return getpass.getpass('Password:')
