import gc
import webrepl
import network
import ujson as json
import uos as os

webrepl.start()
ap_if = network.WLAN(network.AP_IF)
ap_setup_file = "accesspoint.json"

if ap_setup_file in os.listdir():
    # Start the access point.
    if not ap_if.active():
        ap_if.active(True)
    with open(ap_setup_file, "r") as f:
        access_point = json.load(f)
        ap_if.config(
            essid=access_point["essid"], 
            channel=access_point["channel"],
            password=access_point["password"])
else:
    if ap_if.active():
        ap_if.active(False)

sta_if = network.WLAN(network.STA_IF)
sta_setup_file = "networks.json"
if sta_setup_file in os.listdir():
    with open(sta_setup_file, "r") as f:
        network_data = json.load(f)
    if not sta_if.active():
        sta_if.active(True)
    available_networks = sta_if.scan()
    for network in available_networks:
        network_name = network[0].decode()
        if not sta_if.isconnected():
            for network in network_data:
                if network_name == network["essid"]:
                    try:
                        network_config = network["static_ip"]
                        network_config = tuple(network_config)
                    except KeyError:
                        pass
                    else:
                        sta_if.ifconfig(network_config)
                    sta_if.connect(network_name, network["password"])
        else:
            break
    identity_file = "identity.json"
    if identity_file in os.listdir():
        with open(identity_file, "r") as f:
            identity = json.load(f)
        location = identity.get("location")
        if location is not None:

            sta_if.config(dhcp_hostname=location.lower().replace(" ","_"))
else:
    if sta_if.active():
        sta_if.active(True)
gc.collect()
