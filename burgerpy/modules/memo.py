from burgerpy.common import Config, Module
import simplejson as json
import pymongo
import datetime


class Memo(object):
    @staticmethod
    def parse(memo_from, content):
        words = content.split()
        if len(words) < 2:
            return None

        now = datetime.datetime.now()
        memo = {
            "memo_to":  words[0],
            "memo_from": memo_from,
            "content": ' '.join(words[1:]),
            "date": now,
            "sent": False
            }
        return memo

    @staticmethod
    def pager(memo):
        msg = "%s: Memo from %s created at %s: %s" % (
            memo["memo_to"],
            memo["memo_from"],
            memo["date"].strftime('%Y/%m/%d %H:%M:%S'),
            memo["content"])

        return msg


class MemoModule(Module):
    def __init__(self, config, mongo_client):
        super(MemoModule, self).__init__(config)
        self.mongo_client = mongo_client

    def get_unsent_memos(self, memo_to):
        db = self.mongo_client.memo_module.memos
        return db.find({"memo_to": memo_to, "sent": False})

    def set_memo_as_sent(self, memo):
        db = self.mongo_client.memo_module.memos
        db.update_one(memo, {"$set": {"sent": True}})

    def check_msg(self, data):
        msg_origin = data["channel"]
        msg_from = data["from"]

        for memo in self.get_unsent_memos(msg_from):
            self.set_memo_as_sent(memo)
            pager = Memo.pager(memo)
            msg = self.compose_msg(msg_origin, pager)
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

    def on_msg(self, ch, method, properties, body):
        data = json.loads(body)
        self.check_msg(data)

    def on_memo(self, ch, method, properties, body):
        data = json.loads(body)
        self.add_memo(data)

config = Config()
mongo_client = pymongo.MongoClient(config.mongo_host, config.mongo_port)
mm = MemoModule(config, mongo_client)
mm.listen("burger.command.memo", mm.on_memo)
mm.listen("burger.msg", mm.on_msg)
mm.run()
