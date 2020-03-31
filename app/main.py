from config import WIFI_SSID, WIFI_PASS, RELAY_PIN, DELAY
from time import sleep
from machine import Pin, reset
import esp
import time
import network
import socket
import uasyncio as asyncio


def connect_wifi():
    print("Connecting to " + WIFI_SSID)
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(WIFI_SSID, WIFI_PASS)
    while station.isconnected() == False:
        pass

    ifcfg = station.ifconfig()
    ip = ''
    if len(ifcfg) > 0:
        ip = ifcfg[0]

    print('wifi connected')
    return ip


def web_page():
    html = """
<html>
    <head>
        <title>Door opener</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            html { font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
            h1{color: #0F3376; padding: 2vh;}
            p{font-size: 1.5rem;}
            .button{display: inline-block; background-color: #336699; border: none; border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
            #spinner {opacity: 0;}

.loader,
.loader:after {
  border-radius: 50%;
  width: 10em;
  height: 10em;
}
.loader {
  margin: 60px auto;
  font-size: 10px;
  position: relative;
  text-indent: -9999em;
  border-top: 1.1em solid rgba(51,102,153, 0.2);
  border-right: 1.1em solid rgba(51,102,153, 0.2);
  border-bottom: 1.1em solid rgba(51,102,153, 0.2);
  border-left: 1.1em solid #336699;
  -webkit-transform: translateZ(0);
  -ms-transform: translateZ(0);
  transform: translateZ(0);
  -webkit-animation: load8 1.1s infinite linear;
  animation: load8 1.1s infinite linear;
}
@-webkit-keyframes load8 {
  0% {
    -webkit-transform: rotate(0deg);
    transform: rotate(0deg);
  }
  100% {
    -webkit-transform: rotate(360deg);
    transform: rotate(360deg);
  }
}
@keyframes load8 {
  0% {
    -webkit-transform: rotate(0deg);
    transform: rotate(0deg);
  }
  100% {
    -webkit-transform: rotate(360deg);
    transform: rotate(360deg);
  }
}



        </style>
        <script>
           function clickAndDisable(link) {
             link.onclick = function(event) { event.preventDefault(); }
             link.style.display = "none"
             document.getElementById("spinner").style.opacity = 100
           }
        </script>
    </head>
    <body>
        <h1>Door opener</h1>
        <p><a href="/open" onclick="clickAndDisable(this)">
            <button class="button">Open</button>
        </a></p>
        <div id="spinner" class="loader">Loading...</div>
    </body>
</html>"""

    return html


def res_redirect(writer):
    yield from writer.awrite("""HTTP/1.1 303 See Other
Location: /
Connection: close

""")
    yield from writer.aclose()


def res_ok(writer):
    yield from writer.awrite("""HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

""" + web_page())
    yield from writer.aclose()


def serve(reader, writer, pin):

    request = str((yield from reader.read()))

    if len(request) == 0:
        return res_ok(writer)

    lines = request.split("\\r\\n")
    if len(lines) == 0:
        return await res_ok(writer)
    line0 = lines[0]
    lines = None

    parts = line0.split(" ")
    if len(parts) < 3:
        return await res_ok(writer)

    method, path, _ = parts
    print('%s %s' % (str(method), str(path)))

    if path == "/open":
        print("Open relay")
        pin.on()
        sleep(DELAY)
        pin.off()
        print("Closed relay")
        return await res_redirect(writer)

    if path == "/":
        return await res_ok(writer)

    await res_redirect(writer)


def run():

    print('Disabling access point')
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(False)

    ip = connect_wifi()
    print('Starting service on http://%s' % ip)

    pin = Pin(RELAY_PIN, Pin.OUT)
    pin.off()

    loop = asyncio.get_event_loop()
    try:
        loop.call_soon(
            asyncio.start_server(
                lambda r, w: serve(r, w, pin), "0.0.0.0", 80
            )
        )
        loop.run_forever()
    except Exception as err:
        print(err)
    finally:
        loop.close()
        reset()


if __name__ == '__main__':
    run()
