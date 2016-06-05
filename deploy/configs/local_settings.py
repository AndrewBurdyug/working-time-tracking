SECRET_KEY = '{{ Main.django_secret_key }}'

DEBUG = {{ Main.debug }}

ALLOWED_HOSTS = [ '{{ Nginx.server_name }}' ]

TIME_ZONE = '{{ Main.timezone }}'
