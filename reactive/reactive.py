#!/usr/bin/env python

import json
import os
import stat
import subprocess

from charmhelpers.contrib.templating.contexts import juju_state_to_yaml
# from charmhelpers.contrib.ansible import apply_playbook
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
            'service_port': config.get('port'),
            'plugin_slack': config.get('slack'),
            'plugins': get_list('plugins'),
            'environments': get_list('environments'),
            'settings': get_settings()
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
            'service_port': config.get('port'),
            'plugin_slack': config.get('slack'),
            'plugins': get_list('plugins'),
            'environments': get_list('environments'),
            'settings': get_settings()
        }
    )
    close_port(config.get('port'))


@hook('start')
def start():
    apply_playbook(
        playbook='ansible/playbook.yaml',
        tags=['install'],
        extra_vars={
            'service_port': config.get('port'),
            'plugin_slack': config.get('slack'),
            'plugins': get_list('plugins'),
            'environments': get_list('environments'),
            'settings': get_settings()
        }
    )
    open_port(config.get('port'))
    status_set('active', 'ready')


@hook('config-changed')
def config_changed():
    apply_playbook(
        playbook='ansible/playbook.yaml',
        tags=['config'],
        extra_vars={
            'service_port': config.get('port'),
            'plugin_slack': config.get('slack'),
            'plugins': get_list('plugins'),
            'environments': get_list('environments'),
            'settings': get_settings()
        }
    )
    open_port(config.get('port'))
    status_set('active', 'ready')


@hook('upgrade-charm')
def upgrade_charm():
    remove_state('alerta.version')
    remove_state('alerta.installed')
    status_set('active', 'ready')


def apply_playbook(playbook, tags=None, extra_vars=None):
    tags = tags or []
    tags = ",".join(tags)
    juju_state_to_yaml(
        '/etc/ansible/host_vars/localhost', namespace_separator='__',
        allow_hyphens_in_keys=False, mode=(stat.S_IRUSR | stat.S_IWUSR))

    # we want ansible's log output to be unbuffered
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = "1"
    call = [
        'ansible-playbook',
        '-c',
        'local',
        playbook,
    ]
    if tags:
        call.extend(['--tags', '{}'.format(tags)])
    if extra_vars:
        call.extend(['--extra-vars', json.dumps(extra_vars)])
    subprocess.check_call(call, env=env)


def get_settings():
    try:
        used = [
            'SIGNUP_ENABLED', 'AUTH_REQUIRED', 'SECRET_KEY',
            'ALLOWED_ENVIRONMENTS', 'COLOR_MAP', 'SEVERITY_MAP',
            'PLUGINS', 'SECRET_KEY'
        ]
        settings = {}
        for item in config.get('settings').split(','):
            try:
                k, v = [
                    x.strip().strip('"').strip("'").strip()
                    for x in item.split('=', 1)
                ]
                if len(k) and len(v) and k not in used:
                    try:
                        value = int(v)
                    except Exception:
                        value = "'{}'".format(v)
                    settings[k] = value
                else:
                    log('Missing key or value in setting', level="ERROR")
                    raise Exception('Missing')
            except Exception:
                log('Cannot parse setting "{}"'.format(item), level="ERROR")
    except Exception:
        log('Cannot parse settings string', level="ERROR")
        settings = {}
    return settings


def get_list(config_key):
    try:
        response = config.get(config_key).split(',')
        response = ", ".join(['"{}"'.format(
            x.strip().strip('"').strip("'").strip()
        ) for x in response])
        # response = "'{}'".format(response)
    except Exception:
        response = ''
    return response
