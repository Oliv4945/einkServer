# E-ink image server
Easy to configure image saver for E-Paper dislays

## Description
The server is answering a JSON to each of its endpoints with the corresponding image encoded for the E-ink screen.
It can send back (X,Y) coordinate to offload all heavy computation from the micro-controler.

## Install
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage
* In debug mode just use `./run.py`
* In prod mode use a WSIG interface

