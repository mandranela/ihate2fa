from amqtt.broker import Broker


config = {
    "listeners": {
        "default": {
            "max-connections": 50000,
            "type": "tcp",
        },
        "my-tcp-1": {
            "bind": "127.0.0.1:8081",
        },
    },
    "topic-check": {
        "enabled": False,
    },
    "timeout-disconnect-delay": 60,
}


async def broker_coro():
    broker = Broker(config)
    return broker
