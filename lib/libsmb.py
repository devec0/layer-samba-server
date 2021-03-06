import subprocess
import fileinput

from charmhelpers.core import (
    hookenv,
)
from configobj import ConfigObj


class SambaHelper():
    def __init__(self):
        self.charm_config = hookenv.config()
        self.config_file = "/etc/samba/smb.conf"
        self.smb_config = ConfigObj(self.config_file)

    def reload_config(self):
        self.smb_config = ConfigObj(self.config_file, raise_errors=True)

    def save_config(self):
        self.smb_config.write()
        subprocess.check_call(['systemctl', 'restart', 'smbd.service', 'nmbd.service'])

    def clean_example_config(self):
        for line in fileinput.input(self.config_file, inplace=True):
            if line.startswith("#") or line.startswith(";"):
                continue
            if '\n' == line:
                continue
            print(line, end='')

    def update_config(self):
        if self.charm_config['smb-shares']:
            for entry in self.charm_config['smb-shares'].split(','):
                share, path = entry.split(':')
                self.smb_config[share] = {}
                self.smb_config[share]['path'] = path
                if self.charm_config['smb-browsable']:
                    self.smb_config[share]['browsable'] = 'yes'
                else:
                    self.smb_config[share]['browsable'] = 'no'
                if self.charm_config['smb-guest']:
                    self.smb_config[share]['guest ok'] = 'yes'
                else:
                    self.smb_config[share]['guest ok'] = 'no'
                if self.charm_config['smb-read-only']:
                    self.smb_config[share]['read only'] = 'yes'
                else:
                    self.smb_config[share]['read only'] = 'no'
                self.smb_config[share]['create mask'] = self.charm_config['smb-create-mask']
        if self.charm_config['smb-custom']:
            for num, share in enumerate(self.charm_config['smb-custom'].split(';')):
                share_name = 'custom-' + str(num)
                self.smb_config[share_name] = {}
                for setting in share.split(','):
                    key, value = setting.split('=')
                    self.smb_config[share_name][key] = value
        for section in self.smb_config.keys():
            sections = ['global']
            if self.charm_config['smb-shares']:
                for entry in self.charm_config['smb-shares'].split(','):
                    share, path = entry.split(':')
                    sections.append(share)
            if self.charm_config['smb-custom']:
                sections.extend(['custom-{}'.format(i) for i, dummy in enumerate(self.charm_config['smb-custom'].split(';'))])
            if section not in sections:
                del self.smb_config[section]

