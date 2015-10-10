# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 16:36:26 2011

@author: ProfMobius
@version: v0.1
"""

import os
import logging


def whereis(filename, rootdir,blacklist=[]):
    if not os.path.exists(rootdir):
        return None
    logging.info('> Searching for %s in %s', filename, rootdir)
    results = []
    for path, _, filelist in os.walk(rootdir):
        for x in blacklist:
            if x in path:
                pass
        if filename in filelist:
            results.append(path)
    if results == []:
        return None
    return results
