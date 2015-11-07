import collections
from configparser import ConfigParser, ExtendedInterpolation


class Config(collections.MutableMapping):
    """ Custom class of mappings, it read data from INI file and
        if some of options have role suffixes, it will return
        appropriate role option(role suffix will stripped), example config.ini:

        [Main]
        debug_dev = true
        debug_live = false

        In [1]: from fabfile import Config

        In [2]: cfg =  Config('config.ini', 'live')

        In [3]: cfg.items()
        Out[3]: [(u'Main', [(u'debug', u'false')])]

        In [4]: {x[0]:dict(x[1]) for x in cfg.items() if isinstance(x, tuple)}
        Out[4]: {u'Main': {u'debug': u'false'}}


        NOTICE: config options are based on username, so you should further
        re-define in this way:
            config.read_dict({'System': {'user': 'joe', 'group': 'joe'}})
    """
    def __init__(self, config_ini_path, role):
        """ Standard init method, role should be 'dev' or 'live'"""
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        if not self.config.read(config_ini_path):
            raise IOError('not found "%s"' % config_ini_path)
        self.reflect(role)

    def __delitem__(self, key):
        """ NotImplemented, normally we should not want delete options """
        raise NotImplemented

    def __setitem__(self, key, value):
        """ NotImplemented, all options should be setup in config.ini file """
        raise NotImplemented

    def __getitem__(self, key):
        """ Return option of section if key like "Section:option",
            otherwise return section options
        """
        if key.find(':') > 0:
            section, option = key.split(':')
            if self.config.has_option(section, option + '_' + self.role):
                return self.config.get(section, option + '_' + self.role)
            if self.config.has_option(section, option):
                return self.config.get(section, option)
            return
        return [(x[0].replace(self.role_suf, ''), x[1])
                for x in self.config.items(key)
                if not x[0].endswith(self.anti_role_suf)]

    def __len__(self):
        """ Return len of keys - number of sections """
        return len(self.config.sections())

    def __iter__(self):
        """ Return iterator over keys - iterator over sections """
        for section in self.config.sections():
            yield section

    def get_context(self):
        return {x[0]: dict(x[1]) for x in self.items() if isinstance(x, tuple)}

    def reflect(self, role):
        """ Reflect the role to config file, role should be 'dev' or 'live' """
        if role not in ('dev', 'live'):
            raise Exception('bad role, use "dev" or "live"')
        self.role = role
        self.anti_role_suf = '_live' if role == 'dev' else '_dev'
        self.role_suf = '_' + role
