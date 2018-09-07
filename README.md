# Vial

A micropython web server targetting the NodeMCU/esp8266 chips.


ESP8266 doesn't come with a web framework. So I had to repurpose the http_webserver example
script to control the GPIO pins.

## Example usage
- To make pin 2 output and switch it on, send get request to http://*ip-address-of-nodemcu*/write/2/on
- To read from pin 2 with PULL_UP, send get request to http://*ip-address-of-nodemcu*/read/2?pull=up
- To measure from dht, http://*ip-address-of-nodemcu*/measure/2 (Returns two number separated by a comma)

## To Do
- Return json instead of text
- Confirm if the read process is not errenous

### Just so that I remember what I did
- Connect to nodemcu using picocom or micropython webrepl
- After nodemcu boots up, it will run boot.py followed by main.py
- You can send files to nodemcu as well using webrepl
- I have a raspberry pi zero which runs a single page webpage which sends ajax calls to this nodemcu
- since the pi zero runs pihole as well, i've set it up such that it runs on port 5000
- the webserver will start as soon as the pi zero is started (crontab @reboot)


## DS18x20 Output

```
    query: GET /measure/4?type=ds18b20

```

```
    Response: 
    {
        'temperatures': [
            [
                {
                    'id': '0xc30316b1c398ff28',
                    'temperature': 28.6875
                },
                {
                    'id': '0xf70024984322ef28',
                    'temperature': 27.9375
                },
                {
                    'id': '0x65000e98431b8f28',
                    'temperature': 28.875
                },
                {
                    'id': '0x8000219843054328',
                    'temperature': 28.1875
                },
                {
                    'id': '0x2f00219843053228',
                    'temperature': 27.25
                }]
            ],
        'unit': 'celsius'
    }

```