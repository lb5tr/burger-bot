from burgerpy.common import Module, Config
from datetime import datetime

import simplejson as json
import pymongo
import re


class Event(object):
    @staticmethod
    def format_event(msg):
        event_type = msg["event_type"]
        events = ["privmsg", "joined", "userJoined", "userLeft", "userKicked"]
        if event_type not in events:
            raise IndexError

        return getattr(Event, 'format_%s' % event_type)(msg)

    @staticmethod
    def date_string(stamp):
        return datetime.fromtimestamp(stamp).strftime('%Y/%m/%d %H:%M:%S')

    @staticmethod
    def format_userEvent(event, msg):
        return "%s [%s] user %s %s" % (
            msg["channel"],
            Event.date_string(msg["timestamp"]),
            msg["user"],
            event)

    @staticmethod
    def format_privmsg(msg):
        return "%s [%s] <%s> %s" % (
            msg["channel"],
            Event.date_string(msg["timestamp"]),
            msg["from"],
            msg["content"])

    @staticmethod
    def format_joined(msg):
        return "%s [%s] joined" % (
            msg["channel"],
            Event.date_string(msg["timestamp"]))

    @staticmethod
    def format_userJoined(msg):
        return Event.format_userEvent('joined', msg)

    @staticmethod
    def format_userLeft(msg):
        return Event.format_userEvent('left', msg)

    @staticmethod
    def format_userKicked(msg):
        return Event.format_userEvent('has been kicked', msg)


class LoggerModule(Module):
    def __init__(self, config, mongo_client):
        super(LoggerModule, self).__init__(config)
        self.mongo_client = mongo_client
        self.backlog_lines = 50
        self.grep_lines = 15

    def on_message(self, ch, method, properties, body):
        data = json.loads(body)
        if "channel" not in data:
            return None

        match = re.match('^burger\.([a-zA-Z]+)(\.|$)', method.routing_key)
        if match == None:
            #log it
            return

        event_type = match.group(1)
        data["event_type"] = event_type
        origin = data["channel"]
        db = self.mongo_client.logger_module[origin]
        db.insert_one(data)


    def on_backlog(self, ch, method, properties, body):
        data = json.loads(body)
        origin = data["channel"]
        db = self.mongo_client.logger_module[origin]
        backlog = db.find().sort([("$natural", -1)]).limit(self.backlog_lines)

        self.send_collection(data["from"], backlog)

    def send_collection(self, dest, collection):
        results = []
        for msg in collection:
            results = [msg] + results

        for msg in results:
            try:
                event = Event.format_event(msg)
                self.send_result(self.compose_msg(dest, event))
            except IndexError:
                continue

    def respond_with_usage(self, origin):
        self.send_result(self.compose_msg(
            origin,
            "usage - ,greplog /<regex>/options"))

    def on_greplog(self, ch, method, properties, body):
        data = json.loads(body)
        origin = data["channel"]
        db = self.mongo_client.logger_module[origin]

        content = data["content"]
        matches = re.match('^[ ]*\/(.*)\/([imxs]*)[ ]*$', content)

        if matches is None:
            self.respond_with_usage(origin)
            return

        regex = matches.group(1)
        options = matches.group(2)

        logs = db.find(
            {"event_type": "privmsg",
             "content":
             {"$regex": regex,
              "$options": options}}).limit(self.grep_lines).sort([("$natural", -1)])
        self.send_collection(data["from"], logs)


if __name__ == "__main__":
    config = Config()
    mongo_client = pymongo.MongoClient(config.mongo_host, config.mongo_port)
    lm = LoggerModule(config, mongo_client)
    lm.listen("burger.command.backlog", lm.on_backlog)
    lm.listen("burger.command.greplog", lm.on_greplog)
    lm.listen("burger.#", lm.on_message)
    lm.run()
