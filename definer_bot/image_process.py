import asyncio
import tempfile
import logging
import requests
import pickle                   # TODO replace with dataset
import random
import os
import yaml
from PIL import Image, ImageFont, ImageDraw, ImageFilter

from io import BytesIO

import config

import dataset


@asyncio.coroutine
def get_images_from_pixabay(search_term="sad"):
    """Gets images from pixabay.

    Implements basic caching with pickle.

    """
    # TODO get requests to do the replacing and such
    urld_search_term = search_term.replace(' ', '+').lower()

    with dataset.connect(config.DBASE_LOCATION) as db:
        cache = db['json_cache']
        request_url = (
            "https://pixabay.com/api/?key="+
            config.PIXABAY_KEY+
            "&q="+
            urld_search_term+
            "&image_type=photo")

        cache_entry = cache.find_one(url=request_url)

        if cache_entry:
            search_response_json = yaml.load(
                open(os.path.join(config.CACHE_LOCATION,
                                  cache_entry['json_path']),
                                  "rb"))
        else:
            search_response = requests.get(request_url)
            search_response_json = search_response.json()
            f = tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".yaml",
                dir=config.CACHE_LOCATION,
                delete=False)
            yaml.dump(search_response_json, f)
            
            cache.insert(
                dict(
                    url=request_url, json_path=f.name.split('/')[-1]))

        # try:
        #     search_response = pickle.load(open(urld_search_term+".p", "rb"))
        # except:
        #     # TODO check this response is correct, returns right json etc.
        #     pickle.dump(search_response, open(urld_search_term+".p", "wb"))

    return search_response_json

@asyncio.coroutine
def open_random_image_from_json(json):
    # TODO chose random from page, not from 0 to 9th item
    logging.debug("Choosing random image.")
    hits = json['hits']
    url = random.choice(hits)['webformatURL']

    # Caching
    with dataset.connect(config.DBASE_LOCATION) as db:
        cache = db['image_cache']
        cache_entry = cache.find_one(url=url)

        # If there is a cache entry, open it. Otherwise, download it
        # and cache it.
        if cache_entry:
            logging.debug("Opening cached file.")
            try:
                f = open(
                    os.path.join(
                        config.CACHE_LOCATION,
                        cache_entry['image_filename']),
                    "rb")
                img = Image.open(f)
            except IOError as e:
                logging.warning("Removing invalid cache entry")
                cache.delete(url=url)
                # If there's an exception, call the function again
                return open_random_image_from_json(json)
        else:
            logging.debug("Fetching image file from web.")
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))

            # Not really a temporary file, more of a cache file
            f = tempfile.NamedTemporaryFile(
                suffix=".png",
                dir=config.CACHE_LOCATION,
                delete=False)
            img.save(f.name)
            cache.insert(dict(url=url, image_filename=f.name.split('/')[-1]))

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
