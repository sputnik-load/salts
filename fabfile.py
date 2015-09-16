# -*- coding: utf-8 -*-
import re
import datetime
from fabric.api import put, env, run, cd, sudo, lcd, local, settings, get

#import logging
#logging.basicConfig(level=logging.DEBUG)

env.hosts = ['salt-dev.dev.ix.km']
DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"

_TPLS = {
    '#PROJECT_NAME#': lambda: 'salts_prj',
    '#PROJECT_ROOT#': lambda: '/usr/local/salts',
    '#HOSTNAME#': lambda: env.host_string,
}


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


def deploy(reload_=True):
    remote_dir = _my_replace('#PROJECT_ROOT#')
    sudo(_my_replace('mkdir -p "#PROJECT_ROOT#"'))
    sudo(_my_replace('chown suhov.uwsgi -R "#PROJECT_ROOT#"'))
    sudo(_my_replace('chmod g+rwX -R "#PROJECT_ROOT#"'))
    put('salts', remote_path=remote_dir)
    put('salts_prj', remote_path=remote_dir)
    put('templates', remote_path=remote_dir)
    put('static/favicon.ico', remote_path=remote_dir+"/static/")
    with settings(warn_only=True):
        put('*.py', remote_path=remote_dir)
        # put('*.sh', remote_path=remote_dir)
    with cd(remote_dir):
        run('chmod +x manage.py')
 #       run('chmod +x *.sh')

    put('conf', remote_path=remote_dir)
    _my_replace_in_remote_file('#PROJECT_ROOT#/conf/uwsgi.ini.sample', '#PROJECT_ROOT#/conf/uwsgi.ini')
    _my_replace_in_remote_file('#PROJECT_ROOT#/conf/nginx.conf.sample', '#PROJECT_ROOT#/conf/nginx.conf')

    if reload_:
        reload_svc()


def install_req():
#    sudo('yum install -y uwsgi uwsgi-plugin-python supervisor')
#    sudo('yum install -y MySQL-python mysql-connector-python python-pip')
#    sudo('pip install -U pip setuptools')
#    sudo('pip install -U paramiko pycrypto django django-debug-toolbar south fabric celery django-celery flower' +
#         'requests jsonfield amqp amqplib kombu five django-audit-log')

#    sudo('yum install -y uwsgi uwsgi-plugin-python')
    sudo('yum install -y python27 python27-tools python27-devel python27-libs uwsgi-plugin-python27')

    sudo('curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python2.7 get-pip.py')
    sudo('yum install -y python-ldap')
    sudo('bash -c "PATH=$PATH:/usr/pgsql-9.4/bin/ pip2.7 install psycopg2"')
    sudo('pip2.7 install django django-debug-toolbar django-audit-log jsonfield django-auth-ldap slumber')  # slumber - для вызова rest api


def _setup_django():
    sudo(_my_replace('ln -fs #PROJECT_ROOT#/conf/uwsgi.ini /etc/uwsgi/#HOSTNAME#.ini'))
    sudo(_my_replace('ln -fs #PROJECT_ROOT#/conf/nginx.conf /etc/nginx/conf.d/#HOSTNAME#.conf'))
    # TODO: manage.py installstatic
    with cd(_my_replace("#PROJECT_ROOT#")):
        run("python manage.py collectstatic --noinput")


def setup():
    deploy(False)
    _setup_django()
    reload_svc()


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

def backup_files():
    with cd(_my_replace('#PROJECT_ROOT#')):
        archive = '/tmp/salts-{ts}.tar.bz2'.format(ts=get_ts())
        sudo('tar --exclude "./media/results/*" --exclude "*.bz2" -zcvf "{archive}" .'.format(archive=archive))
        get(archive)
        remote_rm(archive)

def backup_database():
    with cd(_my_replace('#PROJECT_ROOT#')):
        archive = '/tmp/salts-{ts}.sql.gz'.format(ts=get_ts())
        sudo('sudo -u postgres pg_dump salts | gzip > "{archive}"'.format(archive=archive))
        get(archive)
        remote_rm(archive)

def backup_results():
    with cd(_my_replace('#PROJECT_ROOT#')):
        archive = '/tmp/salts-results-{ts}.tar.bz2'.format(ts=get_ts())
        sudo('tar -zcvf "{archive}" ./media/results/'.format(archive=archive))
        get(archive)
        remote_rm(archive)

def backup():
    backup_database()
    backup_files()

def backup_all():
    backup_database()
    backup_files()
    backup_results()
