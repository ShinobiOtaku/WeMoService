#!/usr/bin/env python
import argparse
import sys
import pika
import UpdateLightCommand

from ouimeaux.environment import Environment
from ouimeaux.utils import matcher
from ouimeaux.signals import receiver, statechange, devicefound
from datetime import datetime


def mainloop(name):
    matches = matcher(name)
    queueName = 'HUECOMMANDS'
    channel = None
    def connect():
        global channel
        global queue
        print "Connecting to RabbitMQ"
        connection = pika.BlockingConnection(pika.ConnectionParameters(
               '54.69.168.245'))
        channel = connection.channel()
        channel.queue_declare(queue=queueName)
        print "Connected to RabbitMQ"

    def postState():
        global channel
        
        print "motion detected ", datetime.now().time()
        
        #TODO: this should be posting events, not commands, but this works for now...
        if channel is not None:
            channel.basic_publish(exchange='',
                      routing_key=queueName,
                      body=buildMessage("5").SerializeToString())
            channel.basic_publish(exchange='',
                      routing_key=queueName,
                      body=buildMessage("6").SerializeToString())
            channel.basic_publish(exchange='',
                      routing_key=queueName,
                      body=buildMessage("7").SerializeToString())
            print "message posted"
        
    def buildMessage( id ):
        m = UpdateLightCommand.UpdateLightCommand()
        m.is_on = True
        m.msg_version = 1
        m.light_id = id
        m.rgb_red = 255
        m.rgb_green = 255
        m.rgb_blue = 255
        return m
    
    @receiver(devicefound)
    def found(sender, **kwargs):
        if matches(sender.name):
            print "Found device:", sender.name
            connect()

    @receiver(statechange)
    def motion(sender, **kwargs):
        if matches(sender.name) and kwargs.get('state'):
            postState()

    env = Environment(with_cache=False)
    try:
        env.start()
        env.discover(10)
        env.wait()
    except (KeyboardInterrupt, SystemExit):
        print "Goodbye!"
        sys.exit(0)


if __name__ == "__main__":
    mainloop("Hallway motion")
