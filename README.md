# Alerta Charm

![GitHub Action CI badge](https://github.com/huntdatacenter/alerta-charm/workflows/ci/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Alerta juju charm provides Alerta service with web UI.

# Overview

Alerta accepts alerts from the standard sources like Syslog, SNMP, Prometheus, Nagios, Zabbix, Sensu and netdata. Any monitoring tool that can trigger a URL request can be integrated easily. Anything that can be scripted can also send alerts using the command-line tool. There is already a Python SDK and other SDKs are in the pipeline.

## Usage

This charm does not require relations, because so far there is no support in grafana, or nagios charms, therefore it can be deployed separately and then configured manually with any of supported sources:

```
juju deploy cs:~huntdatacenter/alerta
```

Charm provides http relation for the web UI which can be related to nginx or haproxy:

```
juju deploy juju deploy cs:haproxy haproxy-alerta
juju add-relation haproxy-alerta alerta
```

## Development

Here are some helpful commands to get started with development and testing:

```
$ make help
lint                 Run linter
build                Build charm
deploy               Deploy charm
upgrade              Upgrade charm
force-upgrade        Force upgrade charm
test-xenial-bundle   Test Xenial bundle
test-bionic-bundle   Test Bionic bundle
push                 Push charm to stable channel
clean                Clean .tox and build
help                 Show this help
```

## Links

- https://alerta.io/
- https://docs.alerta.io/en/latest/gettingstarted/tutorial-1-deploy-alerta.html#step-3-customisation
