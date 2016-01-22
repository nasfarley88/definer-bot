import asyncio
import logging
import telepot
import tempfile
import re

import dataset

from . import image_process

class DefinerBot(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(DefinerBot, self).__init__(seed_tuple, timeout)

    @asyncio.coroutine
    def on_message(self, msg):
        # yield from self.sender.sendMessage(msg['text'])
        if msg['text'] == "/randomimage":
            yield from self.send_random_image(msg)
        elif re.findall(r'(?i)(/define)(@[a-z_]+bot)?', msg['text']):
            no_to_create_match = re.findall(r'(\d+)', msg['text'])
            if no_to_create_match:
                yield from self.create_image(msg, no_to_create=int(no_to_create_match[0]))
            else:
                yield from self.create_image(msg)

    @asyncio.coroutine
    def send_random_image(self, msg, word="word", definition="definition", emotion="sad"):
        json = yield from image_process.get_images_from_pixabay(emotion)
        img = yield from image_process.open_random_image_from_json(
            json)
        img = yield from image_process.process_img_for_tg(img)
        img = yield from image_process.add_text_to_img(
            img,
            word,
            definition)

        with tempfile.NamedTemporaryFile(suffix=".png") as f:
            logging.debug("Saving image to temporary file.")
            img.save(f.name)

            # Must be opened with 'open' so it's the right type
            #
            # Not sure if tempfile should open differently or telepot
            # should accept different buffers
            with open(f.name, "rb") as q:
                yield from self.sender.sendPhoto(q)

    @asyncio.coroutine
    def create_image(self, msg, no_to_create=1):
        hide_keyboard = {'hide_keyboard': True}
        try:
            yield from self.sender.sendMessage("What's the word, hummingbird?")
            self.listener.set_options(timeout=60)
            response = yield from self.listener.wait()
            word = response['text']
            yield from self.sender.sendMessage("But what does it _mean_?",
                                            parse_mode="Markdown")
            response = yield from self.listener.wait()
            definition = response['text']
            show_keyboard = {
                'keyboard': [
                    ["happy", "sad"],
                    ["angry", "destroyed"],
                ],
                'one_time_keyboard': True}

            yield from self.sender.sendMessage("What's the emotion behind this word?\n(You can also type out your own emotion.)",reply_markup=show_keyboard)
            response = yield from self.listener.wait()
            emotion = response['text']
            yield from self.sender.sendMessage("Let me see what I can find...", reply_markup=hide_keyboard)

            # Create image
            for i in range(no_to_create):
                yield from self.send_random_image(msg, word, definition, emotion)
        except telepot.helper.WaitTooLong as e:
            yield from self.sender.sendMessage("Why'd you leave me hanging?", reply_markup=hide_keyboard)
            yield from self.send_random_image(msg, "rejection", "because bots have feelings too", "sad")

                                           
