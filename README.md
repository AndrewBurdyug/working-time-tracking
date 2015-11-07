### Django project folders

+ */deploy/configs*
    contains Jinja2 templates for Nginx, uWSGI, Systemctl

+ */deploy/requirements.txt*
    contains python modules which are used in project

+ */fabfile.py*
    contains instruction for project deploy, update, restart services, etc

+ */config.ini*
    it is a main config file of project, it contains all info about
    how project will run in system: system user account, system paths(document root, log files, etc),
    many different services options which are variable from username etc

+ */static*
    standart Django "static" folder, it contains static files(css, js, fonts, images),
    a content will be overwritten by the django collectstatic command

+ */media*
    standart Django "media" folder, it contains media files(txt, pdf): reports and invoices

+ */locale*
    a folder for where Django looks for translation files

## Deploy

### preinstall operations

Project is working on Python3, but for deploy/publish changes you should install locally:
Python 2 and latest versions of Fabric, Jinja2

Setup virtual environment:

```shell
$ mkdir ~/envs
$ virtualenv -p python2 ~/envs/py2
$ . ~/envs/py2/bin/activate
(py2)$ pip install -U pip setuptools Fabric Jinja2 configparser==3.3.0.post2
```

Clone project, create your personal config and change default settings:

```shell
(py2)$ git clone ssh://git@gitlab.server.com/work-time-tracking.git
(py2)$ cd work-time-tracking
(py2)$ cp config.ini.example config.ini
```
__ DO NOT FORGET change default settings in config.ini __

### you can use Docker(optionally):

Install Docker, Weave(https://github.com/weaveworks/weave),
pull Ubuntu 15.10 image and run wktime docker container, example:

```shell
(py2)$ docker pull ubuntu:15.10
(py2)$ fab docker_run_ct
[localhost] local: weave launch -iprange 192.168.2.0/24
d1e8a3cded7a2df92556a93194380b214c2b38989b1fbd5e9c6af2c704f45565
[localhost] local: weave run 192.168.2.100/24 -ti --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro --name=wktime --hostname=wktime.local ubuntu:15.10 /bin/bash
39531e8b6e59bc8024cd9719bd5f725ed4b8757be2c2b92209a3760144a4e218
[localhost] local: sudo ip addr a 192.168.2.251/24 dev weave

Done.
(py2)$ echo "192.168.2.100 wktime.local" >> /etc/hosts
(py2)$ ping -c 2 wktime.local
PING wktime.local (192.168.2.100) 56(84) bytes of data.
64 bytes from wktime.local (192.168.2.100): icmp_seq=1 ttl=64 time=0.139 ms
64 bytes from wktime.local (192.168.2.100): icmp_seq=2 ttl=64 time=0.062 ms

--- wktime.local ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 999ms
rtt min/avg/max/mdev = 0.062/0.100/0.139/0.039 ms
```

then install and run SSH server inside this docker container,
add to /root/.ssh/authorized_keys your public SSH key,
go to the next section "deployment"

### deployment

After setup virtual environment with Fabric and Jinja2,
you can deploy project on clean Ubuntu 15.10 lts system,
just run this command under virtual environment:

```shell
(py2)$ fab deploy:dev
```

or for new production deployment(please do not forget change config.ini):

```shell
(py2)$ fab deploy:live
```

start all system services(Nginx, uWSGI backend, redis etc):

```shell
(py2)$ fab restart_services
```

open 'http://wktime.local/admin/' (or other wktime URL - depend on your settings in config.ini) in your browser, that's all!


__ DO NOT FORGET set the value of csrftoken cookie to your cookie_csrftoken, otherwise you get 403 HTTP Forbidden error! __



__Developer/Sysadmin:__

2015, Andrew Burdyug
