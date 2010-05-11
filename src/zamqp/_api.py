import pickle
import uuid
from threading import Thread
import amqplib.client_0_8 as amqp

EXCHANGE = "zamqp.broadcast.fanout"

client_uuid = str(uuid.uuid1())

class AMQPProps(object):
    
    def __init__(self, queue, host='localhost', user='guest', password='guest',
                 ssl=False, exchange=EXCHANGE, type='fanout', realm='/data',
                 mode='r'):
        self.queue = queue
        self.host = host
        self.user = user
        self.password = password
        self.ssl = ssl
        self.exchange = exchange
        self.type = type
        self.realm = realm
        self.mode = mode

class AMQPConnection(object):

    def __init__(self, props):
        self.props = props
        self.connection = amqp.Connection(props.host,
                                          userid=props.user,
                                          password=props.password,
                                          ssl=props.ssl)
    
    @property
    def channel(self):
        if hasattr(self, '_channel'):
            return self._channel
        props = self.props
        read = props.mode == 'r'
        write = props.mode == 'w'
        channel = self.connection.channel()
        channel.access_request(props.realm, active=True, read=read, write=write)
        channel.exchange_declare(props.exchange, type=props.type,
                                 durable=False, auto_delete=False)
        if read:
            channel.queue_declare(props.queue, durable=False,
                                  exclusive=True, auto_delete=True)
            channel.queue_bind(props.queue, props.exchange, props.queue)
        self._channel = channel
        return channel
    
    def close(self):
        self.connection.close()

class AMQPProducer(object):
    
    def __init__(self, props):
        props.mode = 'w'
        self.connection = AMQPConnection(props)

    def __call__(self, message):
        channel = self.connection.channel
        message = amqp.Message(pickle.dumps(message))
        channel.basic_publish(message, EXCHANGE, '')
    
    def close(self):
        self.connection.close()

class AMQPConsumer(object):
    
    def __init__(self, props, callback):
        queue = '%s_%s' % (props.queue, client_uuid)
        props = AMQPProps(queue, host=props.host, user=props.user,
                          password=props.password, ssl=props.ssl)
        self.connection = AMQPConnection(props)
        self.callback = callback
    
    def perform(self, message):
        message = pickle.loads(message.body)
        self.callback(message)

    def run(self):
        channel = self.connection.channel
        props = self.connection.props
        channel.basic_consume(props.queue, callback=self.perform,
                              no_ack=True)
        while channel.callbacks:
            try:
                channel.wait()
            except AttributeError:
                # XXX: figure out how to to interrupt waiting clean.
                pass
    
    def close(self):
        self.connection.close()

class AMQPThread(Thread):
    
    consumer = None
    
    def run(self):
        self.consumer.run()
    
    def close(self):
        try:
            self.consumer.close()
        except IOError:
            pass