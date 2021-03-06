from charms.reactive import (
    when_not,
    set_state,
    when,
)
from charmhelpers.core import (
    hookenv,
)
from charmhelpers import fetch

from libsmb import SambaHelper

smb = SambaHelper()


@when_not('samba-server.installed')
def install_samba_server():
    hookenv.status_set('maintenance', 'installing samba server')
    fetch.apt_update()
    fetch.apt_install(['samba'])
    smb.clean_example_config()
    smb.reload_config()
    smb.update_config()
    smb.save_config()
    hookenv.status_set('active', 'Samba server is ready')
    set_state('samba-server.installed')


@when('config.changed', 'samba-server.installed')
def update_exports():
    smb.update_config()
    # smb.save_config()
    hookenv.log("Config file written", hookenv.INFO)
