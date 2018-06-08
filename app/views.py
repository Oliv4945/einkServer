# -*- coding: utf-8 -*-
from flask import Response
from app import app
from PIL import Image
from random import random
import binascii
import json
import requests


def imageToByteArray(imageName, blackThreshold):
    """ Convert an image to a Waveshare compatible byte array

        :imageName:      'path/name' to the image
        :blackThreshold: Threshold of R+G+B colors to consider a black pixel

        :return: {
                    'image': bytearray(imageName),
                    'w': Image width
                    'h': Image height
                 }
    """
    # Open image & load it
    im = Image.open(imageName)
    pix = im.load()
    # Create resulting byte array
    buffer = bytearray((im.size[0] // 8) * im.size[1])
    i = 0
    # Loop on image
    for y in range(im.size[1]):
        # 8 by 8 as 1 bit = 1 pixel in resulting array
        for x in range(im.size[0] // 8):
            byte = 0
            for bit in range(8):
                pixel = pix[x * 8 + bit, y]
                if pixel[0] + pixel[1] + pixel[2] > blackThreshold:
                    byte |= (1 << (7-bit))
            # print('i: {}, x: {}, y: {} - {} - 0x{:02x}'.format(i,x*8+bit,y,pixel[0] + pixel[1] + pixel[2],byte))
            buffer[i] = byte
            i += 1
        # print('Line {}/{} - 0x{:02x}'.format(y+1, im.size[1], byte))
    # print('Image:', buffer)
    return {
            'image': buffer,
            'w': im.size[0],
            'h': im.size[1]
           }


@app.route('/weather', methods=['GET'])
def index():
    """ Return index template

        :return: Index template
    """
    # Black threshold (255*3)/2
    data = imageToByteArray('test.png', 382)
    data['image'] = binascii.hexlify(data['image']).decode('utf8')
    data['x'] = int(random() * 200)
    data['y'] = int(random() * 50)
    resp = Response(json.dumps(data))
    resp.headers['content-type'] = 'application/json'
    return resp
