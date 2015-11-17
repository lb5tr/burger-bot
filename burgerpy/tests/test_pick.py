import pytest
import simplejson as json
from burgerpy.modules import pick

class ConfigMock():
    base_dir = '.'

class AMQPMock():
    def listen(self, key, callback, name, exchange):
        print 'listen mock called!'

    def send_result(self, exhange, routing_key, msg):
        msg = json.loads(msg)

        assert(msg['message'] == 'user: pick < those < of < one')
        assert(msg['command'] == 'msg')
        assert(msg['user'] == 'channel')

def test_one():
    cm = ConfigMock()
    am = AMQPMock()
    pm = pick.PickModule(config=cm, amqp_iface=am)

    msg = {
        'content': 'pick one of those',
        'channel': 'channel',
        'from' : 'user'
    }

    pm.on_pick(None, None, None, json.dumps(msg))

