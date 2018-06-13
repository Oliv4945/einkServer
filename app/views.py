# -*- coding: utf-8 -*-
from config import API_KEY_HASS, API_KEY_OWM, SERVER_URL
from flask import Response, request
from app import app
from wand.color import Color
from wand.drawing import Drawing
from wand.font import Font
from wand.image import Image
from random import random
import binascii
import datetime
import json
import requests

# Global variable, shared between fonctions
screen = []


def tileFloorplanFromHass():
    data = [
            {'entityId': 'sensor.bedroom_temperature',            'x': 65, 'y': 12},
            {'entityId': 'sensor.bedroomnoe_temperature',         'x': 5,  'y': 69  },
            {'entityId': 'sensor.biviers_outside_temperature',    'x': 167, 'y': 8 },
            {'entityId': 'sensor.biviers_livingroom_temperature', 'x': 138, 'y': 51  },
           ]
    
    headers = {'x-ha-access': API_KEY_HASS,
           'content-type': 'application/json'
           }
    with Image(filename='ressources/floorplan.png') as tile:
        tile.font = Font(
            path = 'virtualenv/lib/python3.4/site-packages/pygame/freesansbold.ttf',
            color = Color('black'),
            size = 14
            )
        # Fetch data and display them
        for room in data:
            r = requests.get('{}/api/states/{}'.format(SERVER_URL, room['entityId']), headers=headers)
            if r.status_code == 200:
                r = r.json()
                room['state'] = r['state']
                room['unit']  = r['attributes']['unit_of_measurement']
                # Add values
                tile.caption(
                    '{}{}'.format(r['state'],r['attributes']['unit_of_measurement']),
                    left = room['x'],
                    top  = room['y']
                    )
        with tile.convert('png') as tbc:
            tbc.save(filename='tileHass.png')
        # Display it
        return imageToByteArray(tile)
    return {}


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
            # cloudBarH = int(tileSize[1] * data['clouds'] / 100)
            # with Drawing() as draw:
            #     draw.rectangle(
            #             top = tileSize[1] - cloudBarH,
            #             height = cloudBarH,
            #             left = 0,
            #             right = int(tileSize[0] * 3/100)
            #         )
            #     draw(tile)
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
            # if (col.red != col.green) or (col.red != col.blue) or (col.blue != col.green):
            #     print('Col: {}  -  {}-{}-{}-{}'.format(col, col.red, col.green, col.blue, col.alpha))
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


def fillForecastFromOWM(data):
    """ Return a dict of forecast values
    
        :data: Input OpenWeatherMap data
        :return: {'dt_txt': '2018-06-11 15:00:00', 'clouds': 76, 'temperature': 20.0, 'weather': 'Rain'}
    """
    iconConv = {
                    '01d': 'skc',
                    '02d': 'sct',
                    '03d': 'ovc',
                    '04d': 'ovc',
                    '09d': 'ra',
                    '10d': 'shra',
                    '11d': 'tsra',
                    '13d': 'sn',
                    '50d': 'fg',
    }
    return {
                'dt_txt': data['dt_txt'],
                'weather': data['weather'][0]['main'],
                'clouds': data['clouds']['all'],
                'temperature': round(data['main']['temp'], 1),
                'icon': iconConv[data['weather'][0]['icon']]
            }


def getWeatherFromOWM(cityCode, appId):
    r = requests.get('https://api.openweathermap.org/data/2.5/forecast?id={}&APPID={}&units={}'.format(cityCode, appId, 'metric'))
    r = r.json()
    # TODO - Error handling
    
    # Parse data for morning & afternoon
    forecast = {'am': None, 'pm': None}
    date = datetime.datetime.now()
    if date.hour > 9:
        dateAM = (date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        dateAM = date.strftime('%Y-%m-%d')
    if date.hour > 15:
        datePM = (date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        datePM = date.strftime('%Y-%m-%d')
    for item in r['list']:
        if '{} 09:00:00'.format(dateAM) in item['dt_txt']:
            forecast['am'] = fillForecastFromOWM(item)
        if '{} 15:00:00'.format(datePM) in item['dt_txt']:
            forecast['pm'] = fillForecastFromOWM(item)
    return forecast


@app.route('/page', methods=['GET'])
def page():
    index = request.args.get('index', default = None, type = int)
    # TODO - Error handling
    resp = Response(json.dumps(screen[index]))
    resp.headers['content-type'] = 'application/json'
    return resp


@app.route('/screen', methods=['GET'])
def index():
    """ Return index template

        :return: Index template
    """
    # Empty screen list
    del screen[:]
    # ****    Weather    ****
    forecast = getWeatherFromOWM(2994087, API_KEY_OWM)
    # print('WHEATHER - Forecast:', forecast)
    data = tileWeather(forecast['pm'], (104, 160), 104, 25)
    data['image'] = binascii.hexlify(data['image']).decode('utf8')
    data['x'] = 400-104-5
    data['y'] = 5
    data['index'] = 1
    screen.append(data)
    data = tileWeather(forecast['am'], (104, 160), 104, 25)
    data['image'] = binascii.hexlify(data['image']).decode('utf8')
    data['x'] = 400-104*2-5-10
    data['y'] = 5
    data['index'] = 2
    screen.append(data)
    # ****    HASS    ****
    data = tileFloorplanFromHass()
    data['image'] = binascii.hexlify(data['image']).decode('utf8')
    data['x'] = 10
    data['y'] = 170
    data['index'] = 3
    screen.append(data)
    print('Range:', [i for i in range(len(screen))])
    resp = Response(json.dumps([i for i in range(len(screen))]))
    resp.headers['content-type'] = 'application/json'
    return resp
