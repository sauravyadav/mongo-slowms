__author__ = "Saurav Yadav"
from fabric.api import *
from fabric.colors import *
from functools import wraps
from fabric.network import needs_host
import time
import os

#env.reject_unknown_hosts = True
env.disable_known_hosts = True

env.user = 'root'
env.password = 'XXXXXXXXXXXXX'
env.port = '22'
env.colorize_errors = True

mongologfile = "/var/log/mongodb/mongod.log"

# Add the Replica details here ##
env.roledefs = {
    'PP': { 'hosts' : ['X.X.X.X'], 'rname' : 'PP' },
    'PROD1': { 'hosts' : ['X.X.X.X', 'X.X.X.X'], 'rname' : 'PROD1' },
    'PROD2': { 'hosts' : ['X.X.X.X','X.X.X.X','X.X.X.X'], 'rname' : 'PROD2' },
}

Role = env.roles[0]
env.roledefs['all'] = [h for r in env.roledefs.values() for h in r]

timestr = time.strftime("%Y%m%d")
remote_mkdir = "mkdir -p /tmp/%s/" % (timestr)
remote_dirname = "/tmp/%s/mongo.log" % (timestr)
cp_op = "cat %s  > %s"  % (mongologfile,remote_dirname)
local_dir = "/tmp/%s/%s/" % (env.roledefs[Role]['rname'],timestr)
local_mkdir = "mkdir -p %s" % (local_dir)
output_dir = "/tmp/%s/" % (env.roledefs[Role]['rname'])
output_mkdir = "mkdir -p %s" % (output_dir)
clearfile = "echo ' '>"

def runs_final(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if env.host_string == env.roledefs[Role]['hosts'][0]:
            return func(*args, **kwargs)
        else:
            return None
    return decorated

def copylogfile():
    print(green("copylogfile task ............"))
    run(remote_mkdir)
    with settings(warn_only=True):
        run(cp_op)
    local(local_mkdir)
    local(output_mkdir)
    get(remote_dirname, local_dir+"/mongo.log"+"."+env.host)
    with settings(warn_only=True):
            run(clearfile+" "+mongologfile)
            run(clearfile+" "+remote_dirname)
    print(blue("Triggering onefile Tasks ...................."))
    onefile()

def onefile():
    print(green("Generating single file ............................"))
    op = 'cat %smongo.log.%s >> %smongo-all.log' % (local_dir, env.host_string, output_dir)
    local(op)

@task
def getdata():
        RemoveOldFile()
        print(blue("Triggering copylogfile Tasks ....."))
        copylogfile()

@runs_final
def RemoveOldFile():
        filename = "%smongo-all.log" % (output_dir)
        print "This is Awesome !!"+filename
        os.remove(filename)