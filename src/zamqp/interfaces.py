# Copyright 2009, BlueDynamics Alliance - http://bluedynamics.com
# GNU General Public License Version 2 or later

from zope.interface import Interface, Attribute

class IAMQPEvent(Interface):
    """AMQP Event interface.
    """
    
    name = Attribute(u"Name of the event.")
    data = Attribute(u"Payload of the event.")

class ISerializer(Interface):
    """Serializer interface for AMQP Events.
    
    A serializer is registered as an adapter for a specific zope event.
    """
    
    def __call__():
        """Serialize Event to AMQP.
        """

class IDeserializer(Interface):
    """Deserializer interface for AMQP Events.
    
    A deserializer is registered as an adapter for an AMQP event by name.
    """
    
    def __call__():
        """Deserialize Event from AMQP.
        """