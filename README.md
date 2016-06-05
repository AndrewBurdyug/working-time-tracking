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
(py2)$ git clone git@github.com:AndrewBurdyug/working-time-tracking.git
(py2)$ cd work-time-tracking
(py2)$ cp config.ini.example config.ini
```
__DO NOT FORGET change default settings in config.ini__

### you can use Docker(optionally):

Install Docker, Weave(https://github.com/weaveworks/weave),
pull Ubuntu 15.10 image and run wktime docker container, example:

```shell
(py2)$ docker pull ubuntu:15.10
(py2)$ fab docker_run_ct
70938076b50e97f3c32960082471c3d774fb856a549ca0024c38c908b7d17785
[localhost] local: docker run --net=wktime_nw --ip=172.31.1.1 -ti --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro --name=wktime --hostname=wktime.local ubuntu:15.10 /bin/bash
root@wktime:/#
```

now you should install ssh server and make deploy into this local VM:

```shell
root@wktime:/# apt-get update && apt-get install -y openssh-server && service ssh start
```

```shell
(py2)$ echo "172.31.1.1 wktime.local" | sudo tee --append /etc/hosts
(py2)$ ping -c 2 wktime.local
PING wktime.local (172.31.1.1) 56(84) bytes of data.
64 bytes from wktime.local (172.31.1.1): icmp_seq=1 ttl=64 time=0.085 ms
64 bytes from wktime.local (172.31.1.1): icmp_seq=2 ttl=64 time=0.086 ms

--- wktime.local ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 999ms
rtt min/avg/max/mdev = 0.085/0.085/0.086/0.009 ms
```

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


__DO NOT FORGET set up the value of auth cookie, otherwise you get 403 HTTP Forbidden error!__



__Developer/Sysadmin:__

2015, Andrew Burdyug
