from hashlib import sha1

import pika
import json
import simplejson as json


def compose_fail_to_kick(user):
    return {
        "command": "msg",
        "user": user,
        "message": "sage who?"
    }

def compose_kick(user, channel):
    return {
        "command": "kick",
        "channel": channel,
        "user": user,
        "reason": ":^)"
    }

def send_result(msg):
    channel.basic_publish(
        exchange='bus',
        routing_key='burger.outbound.send',
        body=json.dumps(msg))

def callback(ch, method, properties, body):
    data = json.loads(body)
    words = data["content"].split(' ')

    msg = None
    if len(words) == 0:
        msg = compose_fail_to_kick(data["channel"])
    else:
        msg = compose_kick(words[0], data["channel"])

    send_result(msg)


params = pika.ConnectionParameters(host='localhost')
connection = pika.BlockingConnection(params)
channel = connection.channel()
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.exchange_declare(exchange='bus', exchange_type='topic')
channel.queue_bind(exchange='bus',
                   queue=queue_name,
                   routing_key="burger.command.sage")

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()
