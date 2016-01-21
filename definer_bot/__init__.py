import asyncio
import telepot

class DefinerBot(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(DefinerBot, self).__init__(seed_tuple, timeout)

    @asyncio.coroutine
    def on_message(self, msg):
        yield from self.sender.sendMessage(msg['text'])
