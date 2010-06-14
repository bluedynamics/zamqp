Overview
========

``zamqp`` is aimed to broadcast messages and trigger events between python
instances via AMQP.

It is based on amqplib and provides consumer and producer implementations as
well as a mechanism to trigger zope events remotely.


Helper Classes
--------------

Create properties for AMQP connection.
::

    >>> from zamqp import AMQPProps
    >>> props = AMQPProps(host='localhost',
    ...                   user='guest',
    ...                   password='guest',
    ...                   ssl=False,
    ...                   exchange='zamqp.broadcast.fanout',
    ...                   type='fanout',
    ...                   realm='/data')

Create AMQP connection manually.
::
    
    >>> from zamqp import AMQPConnection
    >>> connection = AMQPConnection('zamqp_queue', props)

Access connection channel.
::

    >>> connection.channel


Consumer and producer
---------------------

Create consumer callback.
::

   >>> def callback(message):
   ...     pass # do anything with received message here

Create and start consumer thread.
::

    >>> from zamqp import AMQPConsumer
    >>> from zamqp import AMQPThread
    >>> consumer = AMQPConsumer('zamqp_queue', props, callback)
    >>> thread = AMQPThread(consumer)
    >>> thread.start()

Create producer and send a messages. Every python object which is serializable 
can be used as a message.
::

    >>> from zamqp import AMQPProducer
    >>> producer = AMQPProducer('zamqp_queue', props)
    >>> message = 'foo'
    >>> producer(message)


Trigger events
--------------

Create an event which should be triggered in the remote instance.
::

    >>> class MyEvent(object):
    ...     def __init__(self, name):
    ...         self.name = name

Create a listener for ``MyEvent``. This gets called when AMQP events are
received.
::

    >>> def my_listener(event):
    ...     if not isinstance(event, MyEvent):
    ...         return
    ...     # do something

    >>> import zope.event
    >>> zope.event.subscribers.append(my_listener) 

The default ``AMQPEventCallback`` just calls ``zope.event.notify`` with the
received payload, which is the serialized event, in this case an instance of
``MyEvent``.

Start our AMQP consumer for events.
::

    >>> exchange = 'zamqp.events.fanout'
    >>> queue = 'zamqp_events'
    >>> from zamqp import AMQPEventCallback
    >>> props = AMQPProps(exchange=exchange)
    >>> callback = AMQPEventCallback()
    >>> consumer = AMQPConsumer(queue, props, callback)
    >>> thread = AMQPThread(consumer)
    >>> thread.start()
    
Trigger ``MyEvent`` to AMQP channel. The previously started event consumer now
receives this event and triggers it locally in it's own interpreter.
::

    >>> from zamqp import AMQPEvent
    >>> event = AMQPEvent(queue, props, MyEvent('myevent'))
    >>> zope.event.notify(event)

Credits
=======

  -Robert Niederreiter <rnix@squarewave.at>

Changes
=======

1.0b1
-----

* make it work [rnix]