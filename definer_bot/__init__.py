import asyncio
import logging
import telepot
import tempfile

from . import image_process

class DefinerBot(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(DefinerBot, self).__init__(seed_tuple, timeout)

    @asyncio.coroutine
    def on_message(self, msg):
        # yield from self.sender.sendMessage(msg['text'])
        if msg['text'] == "/randomimage":
            yield from self.send_random_image(msg)
        elif msg['text'] == "/define":
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
    def create_image(self, msg):
        yield from self.sender.sendMessage("What's the word, hummingbird?")
        self.listener.set_options(timeout=20)
        response = yield from self.listener.wait()
        word = response['text']
        yield from self.sender.sendMessage("But what does it _mean_?",
                                           parse_mode="Markdown")
        response = yield from self.listener.wait()
        definition = response['text']
        yield from self.sender.sendMessage("What's the emotion behind this word? (single word only)")
        response = yield from self.listener.wait()
        emotion = response['text']

        # Create image
        yield from self.send_random_image(msg, word, definition, emotion)
                                           
