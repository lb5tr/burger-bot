from hashlib import sha1

import pika
import json


def compose_response(msg, result):
    return {
        "content": "%s: %s" % (msg["from"], result),
        "from": msg["from"],
        "channel": msg["channel"]
    }


def send_result(msg):
    channel.basic_publish(
        exchange='bus',
        routing_key='burger.outbound.send',
        body=json.dumps(msg))


def pick(words):
    r = sorted(map(lambda word: (word, sha1(word).hexdigest()), words))
    r = map(lambda t: t[0], r)
    return ' < '.join(r)


def callback(ch, method, properties, body):
    data = json.loads(body)
    words = data["content"].split(' ')
    result = pick(words)
    msg = compose_response(data, result)
    send_result(msg)


params = pika.ConnectionParameters(host='localhost')
connection = pika.BlockingConnection(params)
channel = connection.channel()
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='bus',
                   queue=queue_name,
                   routing_key="burger.command.pick")

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()
