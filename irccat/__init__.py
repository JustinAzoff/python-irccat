# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
from twisted.protocols.basic import LineReceiver
import logging

# system imports
import time, sys

from irccat import util

class BasicLineReceiver(LineReceiver):
    delimiter = "\n"
    def lineReceived(self, line):
        self.factory.bot.bot.parse_and_send(line.rstrip())

class LineToBotFactory(protocol.ServerFactory):
    protocol = BasicLineReceiver

    def __init__(self, bot):
        self.bot = bot

class ircCatBot(irc.IRCClient):
    """A logging IRC bot."""
    
    def connectionMade(self):
        self.nickname = self.factory.nickname
        self.password = self.factory.password
        self.factory.bot=self

        irc.IRCClient.connectionMade(self)
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("irccat")
        self.logger.info("[connected at %s]" % 
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.info("[disconnected at %s]" % 
                        time.asctime(time.localtime(time.time())))

    def parse_and_send(self, line):
        self.logger.debug("Sending: %s" % line)
        targets, line = util.extract_targets(line)
        if not targets:
            targets = self.factory.default_channels
        for c in targets:
            if c == '#*':
                for c in self.factory.all_channels:
                    self.msg(c, line)
            else:
                self.msg(c, line)

    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        for c in self.factory.channels:
            self.join(c['name'],c.get('key'))

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

    def __init__(self, nickname, channels, password):
        self.nickname = nickname
        self.channels = channels
        self.password = password

        self.all_channels = [c['name'] for c in channels]
        self.default_channels = [c['name'] for c in channels if c.get('default')]

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


def runbot(config):

    # initialize logging
    # create factory protocol and application
    f = ircCatBotFactory(config['bot']['nick'], config['channels'], config['server']['password'])

    # connect factory to this host and port
    reactor.connectTCP(config['server']['address'], config['server']['port'], f)

    line_to_bot = LineToBotFactory(f)

    reactor.listenTCP(config['cat']['port'], line_to_bot, interface=config['cat']['ip'])

    # run bot
    reactor.run()

def botmain():
    import sys
    cfg_file = sys.argv[1]
    config = util.read_config(cfg_file)
    runbot(config)
