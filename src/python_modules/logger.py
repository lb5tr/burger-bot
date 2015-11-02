from python_common import Module, Config
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

    def on_backlog(self, ch, method, properties, body):
        data = json.loads(body)
        words = data["content"].split()
        origin = data["channel"]
        lines = 15
        db = self.mongo_client.logger_module[origin]

        backlog = db.find().sort([("$natural", -1)]).limit(lines).sort([("$natural", 1)])

        print backlog
        for msg in backlog:
            self.send_result(self.compose_msg(origin,
                                              "<%s > %s" % (msg["from"], msg["content"])))



mongo_client = pymongo.MongoClient(CONFIG.mongo_host, CONFIG.mongo_port)
lm = LoggerModule(mongo_client)
lm.listen("burger.msg", lm.on_message)
lm.listen("burger.command.backlog", lm.on_backlog)
lm.run()
