from python_common import Module, Config
from datetime import datetime

import simplejson as json
import pymongo


CONFIG = Config()


class LoggerModule(Module):
    def __init__(self, mongo_client):
        super(LoggerModule, self).__init__()
        self.mongo_client = mongo_client
        self.lines = 15

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
        backlog = db.find().sort([("$natural", -1)]).limit(self.lines)

        self.send_collection(data["from"], backlog)

    def send_collection(self, dest, collection):
        results = []
        for msg in collection:
            results = [msg] + results

        for msg in results:
            self.send_result(self.compose_msg(
                dest,
                "[%s] <%s> %s" % (
                    self.date_string(msg["timestamp"]),
                    msg["from"],
                    msg["content"])))

    def on_greplog(self, ch, method, properties, body):
        data = json.loads(body)
        origin = data["channel"]
        db = self.mongo_client.logger_module[origin]

        words = data["content"].split()
        options = ''

        if not words:
            self.send_result(
                self.compose_msg(
                    origin,
                    "usage - ,greplog <regex> [options]"))
            return

        regex = words[0]

        if len(words) >= 2:
            options = words[1]

        logs = db.find(
            {"content":
             {"$regex": regex,
              "$options": options}}).limit(self.lines).sort([("$natural", -1)])
        self.send_collection(origin, logs)


mongo_client = pymongo.MongoClient(CONFIG.mongo_host, CONFIG.mongo_port)
lm = LoggerModule(mongo_client)
lm.listen("burger.msg", lm.on_message)
lm.listen("burger.command.backlog", lm.on_backlog)
lm.listen("burger.command.greplog", lm.on_greplog)
lm.run()
