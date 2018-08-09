#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: "venv_util.py"
# Created: "Ter, 23 Jun 2015 11:02:12 -0300 (kassick)"
# Updated: "Ter, 23 Jun 2015 11:07:31 -0300 (kassick)"
# $Id$
# Copyright (C) 2015, Rodrigo Virote Kassick <rvkassick@inf.ufrgs.br>

import os.path
import sys
def exec_full(filepath):
    import os
    global_namespace = {
        "__file__": filepath,
        "__name__": "__main__",
        }
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), global_namespace)

def venv_dir(file, envname):
    """
    Returns `basename file`/envname
    """

    env_dir = os.path.join(os.path.dirname(os.path.realpath(file)),
                       envname)

    return env_dir

def activate_env(env_dir):
    if os.path.exists(env_dir):
        print("Activating venv in %s" % env_dir)
        activate_this = os.path.join(env_dir,
                                    'bin/activate_this.py')
        exec_full(activate_this)

__all__ = [ 'exec_full', 'venv_dir', 'activate_env' ]
