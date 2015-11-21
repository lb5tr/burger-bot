import pika
import simplejson as json

from time import time
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, task, protocol
from twisted.words.protocols import irc
from burgerpy.common import Config

CONFIG = Config()


class IRC(irc.IRCClient):

    def __init__(self, factory):
        self.factory = factory
        self.nickname = factory.config.irc_nick
        self.realname = factory.config.irc_nick

    def dispatch(self, command, msg):
        self.commands_sent -= 1
        command_params = {
            "topic": ["channel", "topic"],
            "kick": ["channel", "user", "reason"],
            "join": ["channel", "key"],
            "leave": ["channel", "reason"],
            "say": ["channel", "say"],
            "msg": ["user", "message"],
            "notice": ["user", "message"]
        }
        params = {}

        for p in command_params[command]:
            if p in msg:
                params[p] = msg[p].encode('utf-8')
            else:
                return

        getattr(self, command)(**params)

    @defer.inlineCallbacks
    def on_outbound_command(self, queue_object):
        self.commands_sent += 1
        op, tag = queue_object
        ch, method, prop, body = yield op.get()
        msg = json.loads(body)
        command = msg["command"]
        commands_whitelist = ["topic",
                              "kick",
                              "join",
                              "leave",
                              "say",
                              "msg",
                              "notice"]

        if command in commands_whitelist:
            reactor.callLater(self.commands_sent, self.dispatch, command, msg)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def signedOn(self):
        self.commands_sent = 0
        for channel in self.factory.config.irc_channels:
            self.join(channel)

        self.factory.amqp.start_outbound_queue(self.on_outbound_command)

    def get_command(self, msg):
        if msg == "":
            raise LookupError('empty message')

        first_word = msg.split(' ')[0]

        if self.is_command(first_word):
            return first_word[1:]

        return False

    def emit(self, key, data):
        data["timestamp"] = int(time())
        self.factory.amqp.channel.basic_publish(exchange='bus', routing_key=key, body=json.dumps(data))

    def is_command(self, word):
        return word[0] == self.factory.config.command_character

    def get_command_params(self, msg):
        return ' '.join(msg.split(' ')[1:])

    def joined(self, channel):
        self.emit('burger.joined', {"channel": channel})

    def left(self, channel):
        self.emit('burger.left', {"channel": channel})

    def noticed(self, user, channel, message):
        self.emit('burger.noticed', {"user": user, "channel": channel, "message": message})

    def modeChanged(self, user, channel, set, modes, args):
        self.emit('burger.modeChanaged', {"user": user, "channel": channel, "set": set, "modes": modes, "args": args})

    def kickedFrom(self, channel, kicker, message):
        self.emit('burger.kickedFrom', {"channel": channel, "kicker": kicker, "message": message})

    def nickChanaged(self, nick):
        self.emit('burger.nickChanaged', {"nick": nick})

    def userJoined(self, user, channel):
        self.emit('burger.userJoined', {"user": user, "channel": channel})

    def userLeft(self, user, channel):
        self.emit('burger.userLeft', {"user": user, "channel": channel})

    def userQuit(self, user, quitMessage):
        self.emit('burger.userQuit', {"user": user, "quitMessage": quitMessage})

    def userKicked(self, kickee, channel, kicker, message):
        self.emit('burger.userKicked', {"kickee": kickee, "channel": channel, "kicker": kicker, "message": message})

    def userRenamed(self, oldname, newname):
        self.emit('burger.userRenamed', {"oldname": oldname, "newname": newname})

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]

        to_send = {
            "from": user,
            "channel": channel,
            "content": msg,
        }

        command = self.get_command(msg)
        self.emit('burger.privmsg', to_send)

        if command:
            to_send["content"] = self.get_command_params(msg)
            routing_key = "burger.command.%s" % command
            self.emit(routing_key, to_send)

    def irc_unknown(self, prefix, command, params):
        channel = params[1]
        allowed_channels = self.factory.config.irc_allowed_channels
        if command == "INVITE" and channel in allowed_channels:
            self.join(channel)


class IRCFactory(protocol.ClientFactory):
    def __init__(self, config, amqp):
        self.config = config
        self.amqp = amqp

    def buildProtocol(self, addr):
        p = IRC(self)
        print "irc built"
        return p

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()


class AMQP(object):
    @defer.inlineCallbacks
    def setup(self, conn):
        self.conn = conn
        self.channel = yield self.conn.channel()
        self.exchange = yield self.channel.exchange_declare(
            exchange="bus",
            exchange_type='topic')

        self.outbound_queue = yield self.channel.queue_declare(
            queue="outbound",
            exclusive=True)

        yield self.channel.queue_bind(
            exchange='bus',
            queue=self.outbound_queue.method.queue,
            routing_key='burger.outbound.send')

    @defer.inlineCallbacks
    def start_outbound_queue(self, callback):
        qo = yield self.channel.basic_consume(
            consumer_callback=callback,
            queue=self.outbound_queue.method.queue)

        l = task.LoopingCall(callback, qo)
        l.start(0.01)


def on_error(error, er):
    print 'error!', error, er


def on_close():
    print 'close!'


if __name__ == "__main__":
    amqp = AMQP()
    factory = IRCFactory(CONFIG, amqp)
    params = pika.ConnectionParameters(CONFIG.amqp_server, CONFIG.amqp_port)
    conn = twisted_connection.TwistedConnection(parameters=params,
                                                on_open_callback=amqp.setup,
                                                on_open_error_callback=on_error,
                                                on_close_callback=on_close)
    reactor.connectTCP(CONFIG.irc_server,
                       CONFIG.irc_port,
                       factory)
    reactor.run()
