# Example plugin routing rules file

import logging
import traceback


LOG = logging.getLogger('alerta.plugins.routing')


def rules(alert, plugins, config):

    if 'slack' not in plugins:
        return plugins.values(), config

    try:
        # Filter Nagios notifications
        if any(alert.value.startswith(x) for x in ['1/4', '2/4', '3/4']):
            LOG.debug('ROUTING: Rejecting alert for dispatch {} {} {}'.format(
                alert.resource, alert.status, alert.value
            ))
            return [plugins[k] for k in plugins.keys() if k != 'slack'], config
        else:
            LOG.debug('ROUTING: Passing alert for dispatch {} {} {}'.format(
                alert.resource, alert.status, alert.value
            ))
            return plugins.values(), config
    except Exception as e:
        LOG.error('ROUTING: Exception formatting payload: {}\n{}'.format(
            e, traceback.format_exc()
        ))
        return plugins.values(), config
