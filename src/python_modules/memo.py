from python_common import Config, Module
import simplejson as json
import pymongo
import datetime

CONFIG = Config()

class Memo(object):
    @staticmethod
    def parse(memo_from, content):
        words = content.split()
        if len(words) < 2:
            return None

        memo = {
            "memo_to":  words[0],
            "memo_from": memo_from,
            "content" : ' '.join(words[1:]),
            "date" : datetime.datetime.now(),
            "sent": False
            }

        return memo


class MemoModule(Module):

    def __init__(self, name, routing_keys, mongo_client):
        super(MemoModule, self).__init__(name, routing_keys)
        self.mongo_client = mongo_client

    def check_msg(self, data):
        db = self.mongo_client.memo_module.memos
        msg_origin = data["channel"]
        msg_from = data["from"]

        for memo in db.find({"memo_to": msg_from, "sent": False}):
            msg = "%s: Memo from %s : %s" % (
                memo["memo_to"],
                memo["memo_from"],
                memo["content"])
            msg = self.compose_msg(msg_origin, msg)
            db.update_one(memo, { "$set": {"sent": True}})
            self.send_result(msg)

    def add_memo(self, data):
        db = self.mongo_client.memo_module.memos
        content = data["content"]
        msg_origin = data["channel"]
        memo_from = data["from"]

        memo = Memo.parse(memo_from, content)

        msg = "usage - ,memo <user> <memo-content>"
        if memo:
            msg = "Created memo for %s" % memo["memo_to"]
            db.insert_one(memo)

        result = self.compose_msg(msg_origin, msg)
        self.send_result(result)


    def on_message(self, ch, method, properties, body):
        data = json.loads(body)
        if method.routing_key == 'burger.command.memo':
            self.add_memo(data)
        elif method.routing_key == 'burger.msg':
            self.check_msg(data)

mongo_client = pymongo.MongoClient(CONFIG.mongo_host, CONFIG.mongo_port)
mm = MemoModule("memo", ["burger.command.memo", "burger.msg"], mongo_client)
mm.run()
