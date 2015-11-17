![travis status](https://travis-ci.org/kubov/burger-bot.svg)

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
* `$ virtualenv .`
* `$ . bin/activate`
* `$ pip install -r burgerpy/dist/requirements-common.txt`
* `$ docker-compose up -d`
* then run `python -m burgerpy.modules.gateway` module and any other desired one
