import os
import atexit
from zamqp import (        
    AMQPEventCallback,
    AMQPConsumer,
    AMQPThread,
)
import logging
logger = logging.getLogger('zamqp')

event_consumer = None

def cleanup():
    """Close event consumer if running.
    """
    from zamqp import runner
    logger.info('Cleanup event consumer')
    if runner.event_consumer:
        try:
            runner.event_consumer.close()
            logger.info('Event consumer closed')
        except Exception, e:
            logger.error('Error while closing event consumer: %s' % str(e))
        return
    logger.info('No event consumer found, Skipping...')

atexit.register(cleanup)

def create_consumer(props, queue):
    """Create AMQP consumer thread for event notification.
    
    Returns wether starting consumer thread was successful or not.
    
    ``props``:
        AMQPProps instance
    
    ``queue``:
        Queue name
    """
    cleanup()
    from zamqp import runner
    try:
        logger.info('Starting event consumer')
        callback = AMQPEventCallback()
        consumer = AMQPThread(AMQPConsumer(queue, props, callback))
        consumer.start()
        runner.event_consumer = consumer
        return True
    except Exception, e:
        logger.error('AMQP Error: %s %s' % (str(e.__class__), str(e)))
        return False