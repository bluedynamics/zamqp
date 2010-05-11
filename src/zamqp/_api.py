import pickle
import os
import uuid
import logging
import amqplib.client_0_8 as amqp
from time import (
    time,
    strftime,
    localtime,
)

EXCHANGE = "zamqp.broadcast.fanout"

client_uuid = str(uuid.uuid1())

class AMQPProps(object):
    
    def __init__(self, queue, host='localhost', user='guest',
                 password='guest', ssl=False):
        self.queue = queue
        self.host = host
        self.user = user
        self.password = password
        self.ssl = ssl

class AMQPConnection(object):

    def __init__(self, mode, queue_name, props):
        self.mode = mode
        self.props = props
        read = mode == 'r'
        write = mode == 'w'
        conn = amqp.Connection(props.host,
                               userid=props.user,
                               password=props.password,
                               ssl=props.ssl)
        ch = conn.channel()
        ch.access_request('/data', active=True, read=read, write=write)
        ch.exchange_declare(EXCHANGE, 'fanout',
                            durable=False, auto_delete=False)
        if read:
            qname, n_msgs, n_consumers = ch.queue_declare(
                props.queue, durable=False, exclusive=True, auto_delete=True)
            ch.queue_bind(props.queue, EXCHANGE, props.queue)
        self.channel = ch
    
    def close(self):
        self.channel.close()

#>>> from threading import Thread
#    >>> from zodict.locking import TreeLock
#    >>> class TestThread(Thread):
#    ...     def run(self):
#    ...         self._waited = False
#    ...         while dummy._waiting:
#    ...             self._waited = True
#    ...             time.sleep(3)
#    ...         lock = TreeLock(dummy)
#    ...         lock.acquire()
#    ...         dummy._waiting = True
#    ...         time.sleep(1)
#    ...         dummy._waiting = False
#    ...         lock.release()
#
#    >>> t1 = TestThread()
#    >>> t2 = TestThread()
#    >>> t1.start()
#    >>> t2.start()

class Producer(object):
    
    def __init__(self, props):
        self.connection = AMQPConnection('w', props)
        self.ch = setup_amqp('w', queue_name="logger")

    def message(self, message):
        self.ch.basic_publish(amqp.Message(pickle.dumps(message)), my_exchange, "")

class Consumer():
    def __init__(self, callback_function=None):
        self.ch = setup_amqp('r',queue_name="logger_"+my_uuid)
        self.callback_function = callback_function
    
    def callback(self, msg):
        message = pickle.loads(msg.body)
        if(self.callback_function):
            self.callback_function(message)

    def consume_forever(self):
        self.ch.basic_consume("logger_"+my_uuid, callback=self.callback, no_ack=True)
        while self.ch.callbacks:
            self.ch.wait()

    def close(self):
        self.ch.close()