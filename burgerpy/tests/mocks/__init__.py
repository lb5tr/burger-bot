import simplejson as json


class ConfigMock(object):
    base_dir = '.'

class AMQPMock(object):
    def listen(self, key, callback, name, exchange):
        pass

    def send_result(self, exchange, routing_key, msg):
        msg = json.loads(msg)
        return msg

