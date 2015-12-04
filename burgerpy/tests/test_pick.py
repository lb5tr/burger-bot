import pytest
import simplejson as json
from burgerpy.modules.pick import PickModule
from burgerpy.tests.mocks import AMQPMock, ConfigMock


def test_simple():
    cm = ConfigMock()
    am = AMQPMock()
    pm = PickModule(config=cm, amqp_iface=am)

    msg = {
        'content': 'pick one of those',
        'channel': 'channel',
        'from': 'user',
        'source' : 'reply.to'
    }

    msg = pm.on_pick(None, None, None, json.dumps(msg))

    assert(msg['message'] == 'user: pick < those < of < one')
    assert(msg['command'] == 'msg')
    assert(msg['user'] == 'channel')

