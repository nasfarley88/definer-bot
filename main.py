#!/usr/bin/env python3
import asyncio
import telepot
import logging
from telepot.delegate import per_chat_id
from telepot.async.delegate import create_open

from definer_bot import DefinerBot

# User config (keys etc.)
import config

logging.basicConfig(level=logging.DEBUG)

bot = telepot.async.DelegatorBot(config.TG_KEY, [
    (per_chat_id(), create_open(DefinerBot, timeout=60)),
])

loop = asyncio.get_event_loop()
loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
