# -*- coding: utf-8 -*-
from flask import Response
from app import app
from wand.image import Image
from random import random
import binascii
import json
import requests


def imageToByteArray(imageName, newSize=None):
    """ Convert an image to a Waveshare compatible byte array

        :imageName:      'path/name' to the image

        :return: {
                    'image': bytearray(imageName),
                    'w': Image width
                    'h': Image height
                 }
    """
    bufferIndex = 0
    byteIndex = 0
    byte = 0

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
