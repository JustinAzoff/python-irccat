# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
from twisted.protocols.basic import LineReceiver
import logging

# system imports
import time, sys

class BasicLineReceiver(LineReceiver):
    delimiter = "\n"
    def lineReceived(self, line):
        self.factory.bot.bot.send(line.rstrip())

class LineToBotFactory(protocol.ServerFactory):
    protocol = BasicLineReceiver

    def __init__(self, bot):
        self.bot = bot

class ircCatBot(irc.IRCClient):
    """A logging IRC bot."""
    
    nickname = "twistedbot"
    password = "apassword"
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.factory.bot=self
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("irccat")
        self.logger.info("[connected at %s]" % 
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.info("[disconnected at %s]" % 
                        time.asctime(time.localtime(time.time())))

    def send(self, line):
        self.logger.info("Sending: %s" % line)
        self.msg("#log", line)

    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.logger.info("[I have joined %s]" % channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        pass

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        pass

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        pass

    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'


class ircCatBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    # the class of the protocol to build when new connection is made
    protocol = ircCatBot

    def __init__(self, channel):
        self.channel = channel

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # initialize logging
    # create factory protocol and application
    f = ircCatBotFactory("#log")

    # connect factory to this host and port
    reactor.connectTCP("irc.example.com", 6667, f)

    line_to_bot = LineToBotFactory(f)

    reactor.listenTCP(5000, line_to_bot)

    # run bot
    reactor.run()
