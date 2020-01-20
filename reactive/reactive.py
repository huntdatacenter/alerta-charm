#!/usr/bin/env python

from charmhelpers.contrib.ansible import apply_playbook
from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import application_version_set
from charmhelpers.core.hookenv import close_port
from charmhelpers.core.hookenv import log
from charmhelpers.core.hookenv import open_port
from charmhelpers.core.hookenv import status_set
from charms.reactive import hook
from charms.reactive import remove_state
from charms.reactive import set_state
from charms.reactive import when
from charms.reactive import when_not

config = hookenv.config()


@when_not('alerta.version')
def set_version():
    try:
        with open(file='repo-info') as f:
            for line in f:
                if line.startswith('commit-short'):
                    commit_short = line.split(':')[-1].strip()
                    application_version_set(commit_short)
    except IOError:
        log('Cannot set application version. Missing repo-info.')
    set_state('alerta.version')


@when_not('alerta.installed')
def install_deps():
    status_set('maintenance', 'installing dependencies')
    apply_playbook(
        playbook='ansible/playbook.yaml',
        extra_vars={
            'service_port': config.get('port')
        }
    )
    open_port(config.get('port'))
    status_set('active', 'ready')
    set_state('alerta.installed')


@when('website.available')
def configure_website(website):
    open_port(config.get('port'))
    website.configure(port=config.get('port'))


# Hooks
@hook('stop')
def stop():
    apply_playbook(
        playbook='ansible/playbook.yaml',
        tags=['uninstall'],
        extra_vars={
            'service_port': config.get('port')
        }
    )
    close_port(config.get('port'))


@hook('start')
def start():

    apply_playbook(
        playbook='ansible/playbook.yaml',
        tags=['install'],
        extra_vars={
            'service_port': config.get('port')
        }
    )
    open_port(config.get('port'))
    status_set('active', 'ready')


@hook('upgrade-charm')
def upgrade_charm():
    remove_state('alerta.version')
    remove_state('alerta.installed')
    remove_state('alerta.configured')
    status_set('active', 'ready')
