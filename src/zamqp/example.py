#!/usr/bin/python

import sys
sys.path[0:0] = [
  '/home/rnix/workspace/mdb-backend/devsrc/zamqp/src',
  '/home/rnix/workspace/mdb-backend/eggs/amqplib-0.6.1-py2.6.egg',
]

def callback(message):
    print message
    
from zamqp import AMQPConsumer
from zamqp import AMQPThread
from zamqp import AMQPProps
props = AMQPProps('my_queue_name',
                  host='localhost',
                  user='guest',
                  password='guest',
                  ssl=False)

consumer = AMQPConsumer(props, callback)
amqpthread = AMQPThread()
amqpthread.consumer = consumer
amqpthread.start()

from zamqp import AMQPProducer
producer = AMQPProducer(props)
producer('1')
producer('2')
producer('3')

import time
time.sleep(1)

amqpthread.close()