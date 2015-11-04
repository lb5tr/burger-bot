from python_common import Module, Config
from datetime import datetime

import simplejson as json
import pymongo
import re


CONFIG = Config()


class LoggerModule(Module):
    def __init__(self, mongo_client):
        super(LoggerModule, self).__init__()
        self.mongo_client = mongo_client
        self.backlog_lines = 50
        self.grep_lines = 15

    def on_message(self, ch, method, properties, body):
        data = json.loads(body)
        origin = data["channel"]
        db = self.mongo_client.logger_module[origin]
        db.insert_one(data)

    def date_string(self, stamp):
        return datetime.fromtimestamp(stamp).strftime('%Y/%m/%d %H:%M:%S')

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
            self.send_result(self.compose_msg(
                dest,
                "%s [%s] <%s> %s" % (
                    msg["channel"],
                    self.date_string(msg["timestamp"]),
                    msg["from"],
                    msg["content"])))

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
            {"content":
             {"$regex": regex,
              "$options": options}}).limit(self.grep_lines).sort([("$natural", -1)])
        self.send_collection(origin, logs)


mongo_client = pymongo.MongoClient(CONFIG.mongo_host, CONFIG.mongo_port)
lm = LoggerModule(mongo_client)
lm.listen("burger.msg", lm.on_message)
lm.listen("burger.command.backlog", lm.on_backlog)
lm.listen("burger.command.greplog", lm.on_greplog)
lm.run()
