# burger - AMQP based IRC bot

## Key goals

* simple to extend
* live feature updates
* easy to setup

## Requirements

* rabbitmq
* mongodb

## Development

* `$ cd burger-bot/`
* `$ virtaulenv .`
* `$ . bin/activate`
* `$ pip install -r dist/requirements-common.txt`
* `$ docker-compose up -d`
* then run `src/python_modules/gateway.py` module and any other desired one
