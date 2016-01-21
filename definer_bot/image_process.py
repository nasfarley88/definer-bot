import asyncio
import logging
import requests
import pickle                   # TODO replace with dataset
import random
from PIL import Image, ImageFont, ImageDraw, ImageFilter

from io import BytesIO

import config


@asyncio.coroutine
def get_images_from_pixabay(search_term="sad"):
    """Gets images from pixabay.

    Implements basic caching with pickle.

    """
    # TODO get requests to do the replacing and such
    urld_search_term = search_term.replace(' ', '+')

    try:
        search_response = pickle.load(open(urld_search_term+".p", "rb"))
    except:
        # TODO check this response is correct, returns right json etc.
        search_response = requests.get((
            "https://pixabay.com/api/?key="+
            config.PIXABAY_KEY+
            "&q="+
            urld_search_term+
            "&image_type=photo"))
        pickle.dump(search_response, open(urld_search_term+".p", "wb"))

    return search_response.json()

@asyncio.coroutine
def open_random_image_from_json(json):
    # TODO chose random from page, not from 0 to 9th item
    logging.debug("Choosing random image.")
    url = json['hits'][random.randint(0,9)]['webformatURL']
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    return img

@asyncio.coroutine
def process_img_for_tg(img, max_dim=(800, 800), blur_radius=2, brightness=0.8):
    logging.debug("Resizing image")
    img.thumbnail(max_dim, Image.ANTIALIAS)
    logging.debug("Blurring image")
    img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    logging.debug("Changing brightness of image by "+str(brightness))
    img = img.point(lambda p: p*brightness)

    logging.debug("Returning image after processing")
    return img

@asyncio.coroutine
def add_text_to_img(img, word, definition="undefined", color=(225,225,225)):
    draw = ImageDraw.Draw(img)
    
    word_font = ImageFont.truetype(config.FONT_LOCATION, 96)
    draw.text(
        (img.width/2-word_font.getsize(word)[0]/2,
        img.height/2-word_font.getsize(word)[1]),
        word,
        color,
        font=word_font,
    )

    definition_font_size = 48
    definition_font = ImageFont.truetype(config.FONT_LOCATION,
                                         definition_font_size)
    while(definition_font.getsize(definition)[0] > 4*img.width/5):
        definition_font_size -= 1
        definition_font = ImageFont.truetype(config.FONT_LOCATION,
                                             definition_font_size)

    draw.text(
        (img.width/2-definition_font.getsize(definition)[0]/2,
        # img.height/2+definition_font.getsize(definition)[1]),
         img.height/2+definition_font_size/2),
        definition,
        color,
        font=definition_font,
    )

    return img
