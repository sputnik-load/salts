# -*- coding: utf-8 -*-
import re
import datetime
from os.path import abspath,dirname
from fabric.api import put, env, run, cd, sudo, lcd, local, settings, get, task

#import logging
#logging.basicConfig(level=logging.DEBUG)

DEFAULT_HOSTS = ['salt-dev.dev.ix.km']

def local_run(*args, **kwargs):
    return local(*args, shell="/bin/bash", capture=True, **kwargs)

if not env.hosts:
    env.hosts = DEFAULT_HOSTS

is_local = False

@task
def locally():
    global is_local
    is_local = True
    env.run = local_run

DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
PYTHON = 'python2.7'
PIP = 'pip2.7'

_TPLS = {
    '#PROJECT_NAME#': lambda: 'salts_prj',
    '#PROJECT_ROOT#': lambda: '/usr/local/salts',
    '#HOSTNAME#': lambda: env.host_string,
}


def _compare_ver(x, y):
    x_items = x.split(".")
    y_items = y.split(".")
    len_x = len(x_items)
    len_y = len(y_items)
    i = 0
    while True:
        if i < len_x and i < len_y:
            r = int(y_items[i])-int(x_items[i])
        else:
            return len_y - len_x
        if r:
            return r
        i += 1


def checkout_last_version():
    v = None
    fabfile_dir = dirname(abspath(env.fabfile))
    with cd(fabfile_dir):
        run("git fetch --tags")
        run("git pull")
        tags_out = run("git tag")
        if tags_out:
            tags = tags_out.split()
            tags.sort(cmp=_compare_ver)
            v = tags[0]
        if v:
            with open("version", "w") as ver_file:
                ver_file.write(v)
            run("git checkout %s ." % v)


def get_ts():
    return datetime.datetime.now().strftime(DATETIME_FORMAT)

def remote_rm(path):
        sudo('rm -f "{archive}"'.format(archive=path))

def _my_replace(str_):
    result = str_
    for key, val_func in _TPLS.items():
        result = result.replace(key, val_func())
    return result


def _my_replace_in_remote_file(src, dst):
    command = 'sed'
    for key, val_func in _TPLS.items():
        command = command + " -e 's/{0}/{1}/g'".format(re.escape(key), re.escape(val_func()))
    command = command + " '{0}' > '{1}'".format(_my_replace(src), _my_replace(dst))
    sudo(command)

@task
def deploy(reload_=True):
    checkout_last_version()
    remote_dir = _my_replace('#PROJECT_ROOT#')
    sudo(_my_replace('mkdir -p "#PROJECT_ROOT#"'))
    if not is_local:
        sudo(_my_replace('chown $(whoami).uwsgi -R "#PROJECT_ROOT#"'))
    else:
        print env.run("echo $(whoami)")
        sudo(_my_replace('chown $(whoami).$(whoami) -R "#PROJECT_ROOT#"'))
    sudo(_my_replace('chmod g+rwX -R "#PROJECT_ROOT#"'))
    put('salts', remote_path=remote_dir) # use_sudo=is_local
    put('salts_prj', remote_path=remote_dir)
    put('templates', remote_path=remote_dir)
    #put('js', remote_path=remote_dir+"/static/")
    #put('logfile', remote_path=remote_dir)
    #put('run_series.log', remote_path=remote_dir)
    put('static/favicon.ico', remote_path=remote_dir+"/static/")
    put('version', remote_path=remote_dir)
    with settings(warn_only=True):
        put('*.py', remote_path=remote_dir)

    put('conf', remote_path=remote_dir)
    _my_replace_in_remote_file('#PROJECT_ROOT#/conf/uwsgi.ini.sample', '#PROJECT_ROOT#/conf/uwsgi.ini')
    _my_replace_in_remote_file('#PROJECT_ROOT#/conf/uwsgi-krylov.ini.sample', '#PROJECT_ROOT#/conf/uwsgi-krylov.ini')
    _my_replace_in_remote_file('#PROJECT_ROOT#/conf/nginx.conf.sample', '#PROJECT_ROOT#/conf/nginx.conf')

    sudo('rm -rf /var/tmp/django_cache/*')

    with cd(_my_replace("#PROJECT_ROOT#")):
        env.run(PYTHON + " manage.py bower_install")
        env.run(PYTHON + " manage.py collectstatic --noinput")

    if reload_:
        reload_svc()

@task
def install_req():
#    sudo('yum install -y uwsgi uwsgi-plugin-python supervisor')
#    sudo('yum install -y MySQL-python mysql-connector-python python-pip')
#    sudo(PIP + ' install -U pip setuptools')
#    sudo(PIP + ' install -U paramiko pycrypto django django-debug-toolbar south fabric celery django-celery flower' +
#         'requests jsonfield amqp amqplib kombu five django-audit-log')

#    sudo('yum install -y uwsgi uwsgi-plugin-python')
    sudo('yum install -y python27 python27-tools python27-devel python27-libs uwsgi-plugin-python27')

    sudo('curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python2.7 get-pip.py')
    sudo('yum install -y python-ldap')
    sudo('bash -c "PATH=$PATH:/usr/pgsql-9.4/bin/ pip2.7 install psycopg2"')
    sudo(PIP + ' install django django-debug-toolbar django-audit-log jsonfield django-auth-ldap slumber')  # slumber - для вызова rest api


def _setup_django():
    sudo(_my_replace('ln -fs #PROJECT_ROOT#/conf/uwsgi.ini /etc/uwsgi/#HOSTNAME#.ini'))
    sudo(_my_replace('ln -fs #PROJECT_ROOT#/conf/uwsgi-krylov.ini /etc/uwsgi/uwsgi-krylov.ini'))
    sudo(_my_replace('ln -fs #PROJECT_ROOT#/conf/nginx.conf /etc/nginx/conf.d/#HOSTNAME#.conf'))
    # TODO: manage.py installstatic
    with cd(_my_replace("#PROJECT_ROOT#")):
        env.run(PYTHON + " manage.py bower_install")
        env.run(PYTHON + " manage.py collectstatic --noinput")

@task
def setup():
    deploy(False)
    _setup_django()
    reload_svc()

@task
def reload_svc():
    sudo('service nginx reload')
    # sudo('service supervisord reload')
    #sudo('supervisorctl restart all')
    sudo('service uwsgi reload')  # вообще, там сейчас стоит py-autoreload


def env_():
    sudo('env')


def test_():
    with cd('./tmp'):
        with lcd(run('pwd')):
            print local('pwd')

@task
def backup_files():
    with cd(_my_replace('#PROJECT_ROOT#')):
        archive = '/tmp/salts-{ts}.tar.gz'.format(ts=get_ts())
        sudo('tar --exclude "./media/results/*" --exclude "*.bz2" --exclude "*.zip" --exclude "*.gz" -zcvf "{archive}" .'.format(archive=archive))
        get(archive)
        remote_rm(archive)

@task
def backup_database():
    with cd(_my_replace('#PROJECT_ROOT#')):
        archive = '/tmp/salts-{ts}.sql.gz'.format(ts=get_ts())
        sudo('sudo -u postgres pg_dump salts | gzip > "{archive}"'.format(archive=archive))
        get(archive)
        remote_rm(archive)

@task
def backup_results():
    with cd(_my_replace('#PROJECT_ROOT#')):
        archive = '/tmp/salts-results-{ts}.tar.gz'.format(ts=get_ts())
        sudo('tar -zcvf "{archive}" ./media/results/'.format(archive=archive))
        get(archive)
        remote_rm(archive)

@task
def backup():
    backup_database()
    backup_files()

@task
def backup_all():
    backup_database()
    backup_files()
    backup_results()

