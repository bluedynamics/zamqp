import pickle
import uuid
from threading import Thread
import amqplib.client_0_8 as amqp
import zope.event

EXCHANGE = "zamqp.broadcast.fanout"

class AMQPProps(object):
    
    def __init__(self, host='localhost', user='guest', password='guest',
                 ssl=False, exchange=EXCHANGE, type='fanout', realm='/data'):
        self.host = host
        self.user = user
        self.password = password
        self.ssl = ssl
        self.exchange = exchange
        self.type = type
        self.realm = realm

class AMQPConnection(object):

    def __init__(self, queue, props, mode='w'):
        self.queue = queue
        self.props = props
        self.mode = mode
        self.connection = amqp.Connection(props.host,
                                          userid=props.user,
                                          password=props.password,
                                          ssl=props.ssl)
    
    @property
    def channel(self):
        if hasattr(self, '_channel'):
            return self._channel
        read, write = self.mode == 'r', self.mode == 'w'
        props = self.props
        channel = self.connection.channel()
        channel.access_request(props.realm, active=True, read=read, write=write)
        channel.exchange_declare(props.exchange, type=props.type,
                                 durable=False, auto_delete=False)
        if read:
            channel.queue_declare(self.queue, durable=False,
                                  exclusive=True, auto_delete=True)
            channel.queue_bind(self.queue, props.exchange, self.queue)
        self._channel = channel
        return channel
    
    def close(self):
        self.connection.close()

class AMQPProducer(object):
    
    def __init__(self, queue, props):
        self.connection = AMQPConnection(queue, props)
        self.props = props

    def __call__(self, message):
        channel = self.connection.channel
        message = amqp.Message(pickle.dumps(message))
        channel.basic_publish(message, self.props.exchange, '')
    
    def close(self):
        self.connection.close()

class AMQPConsumer(object):
    
    def __init__(self, queue, props, callback):
        id = str(uuid.uuid1())
        self.queue = '%s_%s' % (queue, id)
        self.connection = AMQPConnection(self.queue, props, 'r')
        self.callback = callback
    
    def perform(self, message):
        message = pickle.loads(message.body)
        self.callback(message)

    def run(self):
        channel = self.connection.channel
        props = self.connection.props
        channel.basic_consume(self.queue, callback=self.perform,
                              no_ack=True)
        while channel.callbacks:
            try:
                channel.wait()
            except AttributeError, e:
                # XXX: figure out how to to interrupt waiting clean.
                pass
    
    def close(self):
        self.connection.close()

class AMQPThread(Thread):
    
    def __init__(self, consumer):
        self.consumer = consumer
        Thread.__init__(self)
    
    def run(self):
        self.consumer.run()
    
    def close(self):
        try:
            self.consumer.close()
        except IOError:
            pass

class AMQPEventCallback(object):
    
    def __call__(self, payload):
        zope.event.notify(payload)

class AMQPEvent(object):
    
    def __init__(self, queue, props, payload):
        self.queue = queue
        self.props = props
        self.payload = payload

def amqp_trigger(event):
    if not isinstance(event, AMQPEvent):
        return
    producer = AMQPProducer(event.queue, event.props)
    producer(event.payload)
    producer.close()

zope.event.subscribers.append(amqp_trigger)