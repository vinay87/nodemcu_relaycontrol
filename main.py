import usocket as socket
import ujson as json
import machine, time

"""
http 1.1 response rules
    A Status-line

    Zero or more header (General|Response|Entity) fields followed by CRLF

    An empty line (i.e., a line with nothing preceding the CRLF) 
    indicating the end of the header fields

    Optionally a message-body

"""

CONTENT_JSON = """HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Response Status Code -> 200 OK
Access-Control-Allow-Methods: GET, POST
Content-Type application-json; charset=utf-8
Connection: Close
Response Body:

%s
"""

CONTENT_HTML = """HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Response Status Code -> 200 OK
Access-Control-Allow-Methods: GET, POST
Content-Type: text/html; charset=utf-8
Connection: Close
Response Body:

%s
"""

def parse_req(my_request):
    """Function to pass the url and return the path
    
    url = /write/PIN/on
    """
    my_request = str(my_request)
    request_items = my_request.strip().split('\r\n')
    url = None
    path = ""
    param_pairs = []
    for item in request_items:
        if 'GET' in item.upper():
            url = item.split()[1]
            if '?' in url: 
                url, params = url.split('?', 1)
            else:
                params = []
            url = url.split('/')
            url = [x.lower() for x in url if x != ""]
            if params:
                param_pairs = [p.split('=') for p in  params.split('&')]
            else:
                param_pairs = []
        # TODO: Implement other HTTP commands.
    param_dict = {key.lower():value.lower() for [key, value] in param_pairs}
    return url, param_dict

def exec_req(url, param_dict):
    """Function to execute the request
    This function executes the parsed request.

    Arguments:
        url: list, separated by /.
            So if a user comes to http://example.domain.com/read/1
            this argument is ["read","1"]
        
        param_dict: dictionary, of the parameters that are sent to the server.

        
    """
    print("URL:", url, param_dict)
    if len(url) == 0:
        with open("identity.json", "r") as f:
            identity = json.load(f)
        return """<html>
                <head>
                    <title>NodeMCU</title>
                </head>
                <body>
                    <b>Location: {}</b>
                </body>
            </html>
            """.format(identity["location"])
    elif url[0] == 'write':
        pin_id = int(url[1])
        try:
            pin = machine.Pin(pin_id, machine.Pin.OUT)
        except:
            return {"status": "Error, pin value {} is inaccessible".format(pin_id)}
        else:
            if url[2] == 'on':
                pin.on()
                return {"status": "Pin {} is on".format(str(pin_id))}
            elif url[2] == 'off':
                pin.off()
                return {"status": "Pin {} is off".format(str(pin_id))}
            else:
                return {"status": "{} is not a valid input for pin {} status".format(url[3], pin_id)}
    elif url[0] == 'read':
        try:
            pin_id = int(url[1])
            if "pull" in param_dict.keys():
                pull = param_dict["pull"]
            else:
                pull = None
            if pull == "up":
                pull = machine.Pin.PULL_UP
            elif pull == "down":
                pull = machine.Pin.PULL_DOWN
            pin = machine.Pin(pin_id, machine.Pin.IN, pull) #todo
            return {"value": pin.value()}
        except:
            return {
                "Status": "Error"
                }
    elif url[0] == "measure":
        pin_id = int(url[1])
        measurement_type = param_dict.get("type")
        if measurement_type is None:
            return {"status": "measurement type is required in the query arguments!"}
        elif measurement_type.lower() == "dht11":
            # /measure/PIN_ID?type="dht11"
            try:
                import dht
                d = dht.DHT11(machine.Pin(pin_id))
                d.measure()
                return {"temperature": d.temperature(),  "humidity": d.humidity()}
            except:
                return {"Status": "Error"}
        elif measurement_type.lower() == "ds18b20":
            # /measure/PIN_ID?type=ds18b20
            import onewire, ds18x20
            temperatures = []
            try:
                dat = machine.Pin(pin_id)
                ds = ds18x20.DS18X20(onewire.OneWire(dat))
                roms = ds.scan()
                ds.convert_temp()
                time.sleep_ms(750)
                temperatures = []
                for rom in roms:
                    temperature = ds.read_temp(rom)
                    address = hex(int.from_bytes(rom, "little"))
                    temperatures.append({"id":address, "temperature": round(temperature, 4)})
            except Exception as e:
                return {
                    "status":"{} error while attempting to measure ds18b20 temperature!".format(repr(e))
                    }
            return {
                "temperatures": [
                    temperatures
                ],
                "unit": "celsius"}
        else:
            return {
                "status": "{} measurement not implemented.".format(measurement_type.lower())
                }
    elif url[0] == "whoami":
        with open("identity.json", "r") as f:
            identity = json.load(f)
        return identity
    else:
        return {"Status": "No Action"}
    

def main(micropython_optimize=False):
    s = socket.socket()

    # Binding to all interfaces - 
    # server will be accessible to other hosts!
    ai = socket.getaddrinfo("0.0.0.0", 80)
    print("Bind address info:", ai)
    addr = ai[0][-1]
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print("Listening, connect your browser to http://<this_host>")

    counter = 0
    while True:
        res = s.accept()
        client_sock = res[0]
        client_addr = res[1]
        print("Client address:", client_addr)
        print("Client socket:", client_sock)
        if not micropython_optimize:
            client_stream = client_sock.makefile("rwb")
        else:
            client_stream = client_sock

        req = client_stream.readline()
        print("Incoming Request: {}" .format(req))
        my_request = req
        print("Headers:")
        while True:
            # Read request headers
            h = client_stream.readline()
            if h == b"" or h == b"\r\n":
                break
            print(h)
            my_request = my_request + h
        print(my_request)
        url, param_dict = parse_req(my_request)
        #print(url)
        out = exec_req(url, param_dict)
        #out = "URL: {}, PARAM: {}".format(str(url), str(param_dict))
        if isinstance(out, dict):
            response = CONTENT_JSON % out
        else:
            response = CONTENT_HTML % out
        # HTTP protocol needs CRLF in the response.
        if "\r\n" not in response:
            response=response.replace("\n","\r\n")
        response = response.encode("bytes")
        client_stream.write(response)
        client_stream.close()
        print(response)
        if not micropython_optimize:
            client_sock.close()

main()
