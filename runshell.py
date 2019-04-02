#!env/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess
import tempfile

reload(sys)
sys.setdefaultencoding('utf8')

def run_command(command, cwd):
    t0 = time.time()
    std_out_temp = tempfile.TemporaryFile(mode='w+t')
    err_out_temp = tempfile.TemporaryFile(mode='w+t')
    os_env = os.environ.copy()
    proc = subprocess.Popen(command,
                     cwd=cwd,
                     shell=True,
                     stdout=std_out_temp.fileno(),
                     stderr=err_out_temp.fileno(),
                     bufsize=0,
                     env=os_env,
                     close_fds=True,
                     executable='/bin/sh')
    spent = time.time() - t0
    print '[shell]:' + command + ' spent: ' + str(spent)
    proc.wait()
    std_out_temp.seek(0)
    err_out_temp.seek(0)
    return proc.returncode, std_out_temp.read(), err_out_temp.read()

if __name__ == '__main__':
    run_command('git checkout develop','/Users/shimingwei/Desktop/gitLvmama/ios_kit/LvmmKit')