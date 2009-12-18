# Copyright 2009, BlueDynamics Alliance - http://bluedynamics.com
# GNU General Public License Version 2 or later

from zope.interface import implements
from interfaces import IAMQPEvent

class AMQPEvent(object):
    implements(IAMQPEvent)