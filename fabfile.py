#!/usr/bin/env python2
import os
import datetime
import cStringIO
from config import Config
from jinja2 import Environment, FileSystemLoader
from fabric.api import env, run, put, prefix, prompt, cd, sudo, local, \
    execute

cfg = Config('config.ini', os.environ.get('WKTIME_INSTANCE_ROLE', 'dev'))


def setup_env(root_priv=False):
    def setup_env(func):
        def wrapped(*args, **kwargs):
            env.effective_roles = [cfg.role]
            if root_priv:
                env.host_string = '%s@%s' % (
                    cfg['System:super_user'], cfg['Main:ssh'])
            else:
                env.host_string = '%s@%s' % (
                    cfg['System:user'], cfg['Main:ssh'])
            env.user = cfg['System:user']
            func(*args, **kwargs)
        return wrapped
    return setup_env


@setup_env(root_priv=True)
def upgrade_os_and_install_system_packages():
    if cfg['System:os'] == 'ubuntu':
        system_packages = (
            # system wide packages: python, Redis, etc:
            'python3', 'python3-dev', 'python3-pip', 'python3-venv',
            'wget', 'git', 'sudo', 'unzip', 'gettext',
            'redis-server', 'sqlite3',
            # libs:
            'libmysqlclient-dev', 'libjpeg8-dev', 'libpng-dev', 'zlib1g-dev',
            'libfreetype6-dev', 'libxml2-dev', 'libxslt1-dev', 'libpcre3-dev',
            # special for PIL:
            'libjbig0', 'liblcms2-2', 'libtiff5', 'libwebp5', 'libwebpmux1',
            # special for nginx:
            'libgeoip1',
        )

        # upgrade OS and install all needed software:
        with prefix('export DEBIAN_FRONTEND=noninteractive'):
            run('apt-get update -q -y && apt-get upgrade -q -y ')
            run('apt-get install %s -q -y' % ' '.join(system_packages))

            # use custom ngnix with geoip:
            run('wget -q http://pkg.chalenge.tk/'
                'nginx_1.8.0-1~trusty_amd64.deb -P /usr/src')
            run('dpkg -i /usr/src/nginx_1.8.0-1~trusty_amd64.deb')

    if cfg['System:os'] == 'arch':
        # Not yet implemented...
        pass


@setup_env(root_priv=True)
def create_project_user():
    home = cfg['System:home']
    user = cfg['System:user']

    run('mkdir -pv {home} && useradd -s /bin/bash -d {home} -m {user}'.format(
        **locals()))

    # add user to sudoers:
    if cfg['System:os'] == 'ubuntu':
        file_content = cStringIO.StringIO(
            '{user}  ALL=NOPASSWD: /usr/sbin/service nginx reload\n'.format(
                **locals()))
    if cfg['System:os'] == 'arch':
        file_content = cStringIO.StringIO(
            '{user}  ALL=NOPASSWD: /usr/bin/systemctl reload nginx\n'.format(
                **locals()))

    put(local_path=file_content, remote_path='/etc/sudoers.d/{user}'.format(
        **locals()))

    # add your SSH keys to user SSH authorized_keys:
    run('mkdir {home}/.ssh'.format(**locals()))
    run('chown -R {user}:{user} {home}'.format(**locals()))
    run('cp /root/.ssh/authorized_keys {home}/.ssh'.format(**locals()))


@setup_env()
def post_create_user_actions():
    run('pyvenv py3')

    # hint for auto activation virtualenv:
    file_content = cStringIO.StringIO('source ~/py3/bin/activate')
    put(local_path=file_content, remote_path='~/.bash_profile')

    run('ssh-keygen -t rsa -f ~/.ssh/id_rsa -P ""')
    run('cat ~/.ssh/id_rsa.pub')
    if cfg['Git:server'].find(':') >= 0:
        server, port = cfg['Git:server'].split(':')
        run('ssh-keyscan -p {port} "{git_server}" >>~/.ssh/known_hosts'.format(
            git_server=server, port=port))
    else:
        run('ssh-keyscan "{git_server}" >> ~/.ssh/known_hosts'.format(
            git_server=cfg['Git:server']))

    prompt('Please add ssh key to GitLab Deploy Keys for all project repos'
           ' and hit enter')


@setup_env()
def clone_all_git_repos():
    remote = cfg['Git:repo_path']
    run('git clone -q {remote} -b master ~/src'.format(**locals()))


@setup_env()
def create_user_extra_dirs():
    run('mkdir -pv ~/{logs,backups}')
    run('mkdir -pv ~/src/media/{invoices,reports}')
    run('mkdir -pv ~/src/deploy/build')


@setup_env()
def update_configs():
    project_configs = (
        'uwsgi.ini', 'nginx_vhost.conf', 'uwsgi_systemctl.service',
        'local_settings.py', 'logrotate.conf'
    )
    jinja_env = Environment(trim_blocks=True, lstrip_blocks=True,
                            loader=FileSystemLoader('deploy/configs'))
    for project_cfg in project_configs:
        template = jinja_env.get_template(project_cfg)
        file_content = cStringIO.StringIO()
        file_content.write(template.render(cfg.get_context()) + '\n')
        put(local_path=file_content,
            remote_path='~/src/deploy/build/{config}'
            .format(config=project_cfg))


@setup_env()
def install_python_requirements():
    run('pip install -q -U pip setuptools')
    run('pip install -q -r ~/src/deploy/requirements.txt')


@setup_env(root_priv=True)
def create_links_to_project_configs():
    home = cfg['System:home']
    run('ln -sf ' + home + '/src/deploy/build/nginx_vhost.conf '
        '/etc/nginx/conf.d/nginx_wktime_vhost.conf')
    run('ln -sf ' + home + '/src/deploy/build/uwsgi.ini ' +
        home + '/uwsgi.ini')
    run('ln -sf ' + home +
        '/src/deploy/build/uwsgi_systemctl.service '
        '/etc/systemd/system/uwsgi-wktime.service')
    run('ln -sf ' + home +
        '/src/deploy/build/local_settings.py ' + home +
        '/src/local_settings.py')


@setup_env()
def syncdb():
    with cd('~/src'):
        run('./manage.py syncdb')


@setup_env()
def migrate():
    with cd('~/src'):
        run('./manage.py migrate')


@setup_env()
def collectstatic():
    with cd('~/src'):
        run('./manage.py collectstatic --noinput')


@setup_env()
def makemessages():
    with cd('~/src'):
        run('./manage.py makemessages -a -d djangojs -l en')
        run('./manage.py makemessages -a -l en')


@setup_env()
def compilemessages():
    with cd('~/src'):
        run('./manage.py compilemessages')


@setup_env(root_priv=True)
def autostart_services_enable():
    # run('systemctl enable nginx')
    # run('systemctl enable redis')
    # run('systemctl enable uwsgi-wktime')
    pass


@setup_env(root_priv=True)
def add_to_logrotate_project_config():
    run('cp -f {home}/src/deploy/build/logrotate.conf '.format(
        home=cfg['System:home']) +
        '/etc/logrotate.d/wktime')
    run('chown root:root /etc/logrotate.d/wktime')
    run('chmod 644 /etc/logrotate.d/wktime')


@setup_env(root_priv=True)
def restart_services(service='all'):
    #  Docker Ubuntu 15.10 container still does not working properly
    #  with systemd, so we still use SystemV init scripts:
    if cfg['System:os'] == 'ubuntu':
        if service == 'redis' or service == 'all':
            run('service redis-server restart')
        if service == 'nginx' or service == 'all':
            run('service nginx restart')
        if service == 'uwsgi' or service == 'all':
            execute(restart_uwsgi)

    if cfg['System:os'] == 'arch':
        if service == 'redis' or service == 'all':
            run('systemctl restart redis')
        if service == 'nginx' or service == 'all':
            run('systemctl restart nginx')
        if service == 'uwsgi' or service == 'all':
            run('systemctl restart uwsgi-wktime')


@setup_env()
def restart_uwsgi():
    run('if [ -f /tmp/uwsgi-{user}.pid ]; then '.format(
        user=cfg['System:user']) +
        'uwsgi --stop /tmp/uwsgi-$USER.pid; fi; uwsgi ~/uwsgi.ini')


def deploy(role):
    cfg.reflect(role)

    execute(upgrade_os_and_install_system_packages)
    execute(create_project_user)
    execute(post_create_user_actions)
    execute(clone_all_git_repos)
    execute(create_user_extra_dirs)
    execute(update_configs)
    execute(install_python_requirements)
    execute(create_links_to_project_configs)
    execute(restart_services, 'redis')
    execute(syncdb)
    execute(migrate)
    execute(collectstatic)
    execute(makemessages)
    execute(compilemessages)
    execute(autostart_services_enable)
    execute(add_to_logrotate_project_config)


# Custom hints, not related to deploy:
# ====================================

@setup_env()
def reload_frontend():
    if cfg['System:os'] == 'ubuntu':
        sudo('service nginx reload', shell=False)
    if cfg['System:os'] == 'arch':
        sudo('systemctl reload nginx', shell=False)


@setup_env()
def reload_backend():
    file_name = cfg['uWSGI:chdir'] + '/' + cfg['uWSGI:wsgi_file']
    run('touch ' + file_name, shell=False)


@setup_env()
def reload_project():
    reload_backend()
    reload_frontend()


@setup_env()
def tail_logs():
    run('tail -f logs/*.log')


@setup_env()
def remove_pyc():
    run('find ~/src/ -type f -name "*.pyc" -delete')


@setup_env()
def reset_changes():
    with cd('~/src'):
        run('git clean -fd -e deploy/build && git checkout -- . && git pull')


def create_patch(branch=None):
    if branch is None:
        branch = ''
    local('git add . && git diff --cached {branch} > '
          '/tmp/__changes.patch'.format(**locals()))


@setup_env()
def save_dump():
    timestamp = datetime.datetime.now().strftime('%Y.%m.%d-%H.%M.%S')
    filename = 'dump-{timestamp}.sql'.format(**locals())
    with cd('~/src'):
        run('sqlite3 db.sqlite3 .dump > ~/backups/{filename}'.format(
            **locals()))


@setup_env()
def publish_changes():
    execute(reset_changes)
    execute(save_dump)
    execute(create_patch)
    put(local_path='/tmp/__changes.patch', remote_path='/tmp/__changes.patch')
    with cd('~/src'):
        run('git apply /tmp/__changes.patch')
    execute(reload_project)


@setup_env()
def update():
    execute(save_dump)
    execute(reset_changes)
    execute(update_configs)
    execute(create_links_to_project_configs)
    execute(install_python_requirements)
    execute(remove_pyc)
    execute(migrate)
    execute(collectstatic)
    execute(makemessages)
    execute(compilemessages)
    execute(reload_project)


def docker_run_ct():
    local('weave launch -iprange 192.168.2.0/24')
    local('weave run 192.168.2.100/24 -ti --privileged '
          '-v /sys/fs/cgroup:/sys/fs/cgroup:ro --name=wktime '
          '--hostname=wktime.local ubuntu:15.10 /bin/bash')
    local('sudo ip addr a 192.168.2.251/24 dev weave')


def docker_start_ct():
    local('weave launch -iprange 192.168.2.0/24')
    local('weave start 192.168.2.100/24 wktime')
    local('sudo ip addr a 192.168.2.251/24 dev weave')
