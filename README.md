# E-ink image server
Easy to configure image saver for E-Paper dislays

## Description
The server is answering a JSON to each of its endpoints with the corresponding image encoded for the E-ink screen.
It can send back (X,Y) coordinate to offload all heavy computation from the micro-controler.

## Install
```
# wand-py might be different regarding the OS
apt-get install libmagickwand-dev libmagickcore-6.q16-2-extra
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage
* In debug mode just use `./run.py`
* In prod mode use a WSIG interface

## Credits
* Weather images by [Matthew Petroff](https://cdn6.mpetroff.net/wp-content/uploads/2012/09/weather-icons.zip)