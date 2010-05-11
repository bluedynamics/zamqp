import pickle
import uuid
from threading import Thread
import amqplib.client_0_8 as amqp

EXCHANGE = "zamqp.broadcast.fanout"

client_uuid = str(uuid.uuid1())

class AMQPProps(object):
    
    def __init__(self,
                 queue,
                 host='localhost',
                 user='guest',
                 password='guest',
                 ssl=False,
                 exchange=EXCHANGE):
        self.queue = queue
        self.host = host
        self.user = user
        self.password = password
        self.ssl = ssl
        self.exchange = exchange

class AMQPConnection(object):

    def __init__(self, mode, props):
        self.mode = mode
        self.props = props
        self.channel = None
        self.connect()
    
    def connect(self):
        read = self.mode == 'r'
        write = self.mode == 'w'
        props = self.props
        conn = amqp.Connection(props.host,
                               userid=props.user,
                               password=props.password,
                               ssl=props.ssl)
        ch = conn.channel()
        ch.access_request('/data', active=True, read=read, write=write)
        ch.exchange_declare(props.exchange, 'fanout',
                            durable=False, auto_delete=False)
        if read:
            qname, n_msgs, n_consumers = ch.queue_declare(
                props.queue, durable=False, exclusive=True, auto_delete=True)
            ch.queue_bind(props.queue, props.exchange, props.queue)
        self.channel = ch
    
    def close(self):
        self.channel.close()
        self.channel = None

class AMQPProducer(object):
    
    def __init__(self, props):
        self.connection = AMQPConnection('w', props)

    def __call__(self, message):
        channel = self.connection.channel
        message = amqp.Message(pickle.dumps(message))
        channel.basic_publish(message, EXCHANGE, '')

class AMQPConsumer(object):
    
    def __init__(self, props, callback):
        queue = '%s_%s' % (props.queue, client_uuid)
        props = AMQPProps(queue, host=props.host, user=props.user,
                          password=props.password, ssl=props.ssl)
        self.connection = AMQPConnection('w', props)
        self.callback = callback
    
    def perform(self, message):
        message = pickle.loads(message.body)
        self.callback(message)

    def run(self):
        channel = self.connection.channel
        props = self.connection.props
        channel.basic_consume(props.queue, callback=self.perform, no_ack=True)
        while channel.callbacks:
            channel.wait()

    def close(self):
        self.connection.close()

class AMQPThread(Thread):
    
    def __init__(self, props, callback):
        Thread.__init__(self)
        self.consumer = AMQPConsumer(props, callback)
    
    def run(self):
        self.consumer.run()
    
    def close(self):
        self.consumer.close()