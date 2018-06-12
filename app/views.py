# -*- coding: utf-8 -*-
from flask import Response
from app import app
from wand.color import Color
from wand.drawing import Drawing
from wand.font import Font
from wand.image import Image
from random import random
import binascii
import json
import requests


def tileWeather(data, tileSize, imgWidth, textSize):
    """ Convert an image to a Waveshare compatible byte array

        :data:      Forecast data {'temperature': 20.0, 'icon': 'shra', 'weather': 'Rain', 'clouds': 76, 'dt_txt': '2018-06-11 15:00:00'}

        :return: {
                    'image': bytearray(imageName),
                    'w': Image width
                    'h': Image height
                 }
    """
    with Image( width=tileSize[0], height=tileSize[1], background=Color('white')) as tile:
        with Image(filename='ressources/weather/{}.svg'.format(data['icon'])) as img:
            imgHeight = int(imgWidth/img.width*img.height)
            img.resize(imgWidth, imgHeight)
            # Paste icon
            tile.composite(img, int((tileSize[0]-imgWidth)/2), 0)
            tile.font = Font(
                path = 'virtualenv/lib/python3.4/site-packages/pygame/freesansbold.ttf',
                color = Color('black'),
                size = textSize
                )
            # Add temperature
            tile.caption(
                    '{}°C'.format(data['temperature']),
                    top = int(imgHeight + (tileSize[1]-imgHeight-textSize)/2),
                    width = tileSize[0],
                    gravity = 'south'
                    )
            # Cloud bargraph
            cloudBarH = int(tileSize[1] * data['clouds'] / 100)
            with Drawing() as draw:
                draw.rectangle(
                        top = tileSize[1] - cloudBarH,
                        height = cloudBarH,
                        left = 0,
                        right = int(tileSize[0] * 3/100)
                    )
                draw(tile)
        with tile.convert('png') as tbc:
            tbc.save(filename='test.png')
        return imageToByteArray(tile)
    return {}


def imageToByteArray(img):
    """ Convert an image to a Waveshare compatible byte array

        :img:      Wand image

        :return: {
                    'image': bytearray(imageName),
                    'w': Image width
                    'h': Image height
                 }
    """
    bufferIndex = 0
    byteIndex = 0
    byte = 0
    # Create resulting byte array
    buffer = bytearray((img.width // 8) * img.height*2)
    for row in img:
        for col in row:
            if (col.red != col.green) or (col.red != col.blue) or (col.blue != col.green):
                print('Col: {}  -  {}-{}-{}-{}'.format(col, col.red, col.green, col.blue, col.alpha))
            if col.red + col.green + col.blue > 2:
                byte |= (1 << (7-byteIndex))
            byteIndex += 1
            if byteIndex == 8:
                byteIndex = 0
                buffer[bufferIndex] = byte
                bufferIndex += 1
                byte = 0
                # print(bufferIndex)

    return {
            'image': buffer,
            'w': img.width,
            'h': img.height
        }

    with Image(filename=imageName) as img:
        if newSize:
            # TODO - Enter X, compute Y to keep scale. Only X must be multiple of 8
            img.resize(newSize[0], newSize[1])

        # Create resulting byte array
        buffer = bytearray((img.width // 8) * img.height*2)

        for row in img:
            for col in row:
                # print('Col: {}  -  alpha: {}'.format(col, col.alpha_int8))
                if col.alpha < 0.2:
                    byte |= (1 << (7-byteIndex))
                byteIndex += 1
                if byteIndex == 8:
                    byteIndex = 0
                    buffer[bufferIndex] = byte
                    bufferIndex += 1
                    byte = 0
                    # print(bufferIndex)

        return {
                'image': buffer,
                'w': img.width,
                'h': img.height
            }
    return {}

@app.route('/weather', methods=['GET'])
def index():
    """ Return index template

        :return: Index template
    """
    data = imageToByteArray('ressources/weather/tsra.svg', (104,104))
    data['image'] = binascii.hexlify(data['image']).decode('utf8')
    data['x'] = int(random() * 200)
    data['y'] = int(random() * 50)
    # print('data:', data)
    resp = Response(json.dumps(data))
    resp.headers['content-type'] = 'application/json'
    return resp
