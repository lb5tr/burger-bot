from python_common import Module, Config
from datetime import datetime

import simplejson as json
import pymongo


CONFIG = Config()

class LoggerModule(Module):
    def __init__(self, mongo_client):
        super(LoggerModule, self).__init__()
        self.mongo_client = mongo_client

    def on_message(self, ch, method, properties, body):
        data = json.loads(body)
        origin = data["channel"]
        db = self.mongo_client.logger_module[origin]
        db.insert_one(data)

    def date_string(self, stamp):
        return datetime.fromtimestamp(stamp).strftime('%Y/%m/%d %H:%M:%S')

    def on_backlog(self, ch, method, properties, body):
        data = json.loads(body)
        words = data["content"].split()
        origin = data["channel"]
        lines = 15
        db = self.mongo_client.logger_module[origin]

        backlog = db.find().sort([("$natural", -1)]).limit(lines)

        results = []
        for msg in backlog:
            results = [msg] + results

        for msg in results:
            self.send_result(self.compose_msg(msg["from"],
                                              "[%s] <%s> %s" % (
                                                  self.date_string(msg["timestamp"]),
                                                  msg["from"],
                                                  msg["content"])))



mongo_client = pymongo.MongoClient(CONFIG.mongo_host, CONFIG.mongo_port)
lm = LoggerModule(mongo_client)
lm.listen("burger.msg", lm.on_message)
lm.listen("burger.command.backlog", lm.on_backlog)
lm.run()
