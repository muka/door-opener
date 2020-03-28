
from config import WIFI_SSID, WIFI_PASS, RELAY_PIN, DELAY
import socket
import network
import time
import esp
from machine import Pin
from time import sleep


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


def http_server():

    pin = Pin(RELAY_PIN, Pin.OUT)
    pin.off()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)

    lock = False

    while True:

        conn, addr = s.accept()

        request = conn.recv(1024)
        request = str(request)

        if len(request) == 0:
            continue

        lines = request.split("\\r\\n")
        if len(lines) == 0:
            continue
        line0 = lines[0]
        lines = None

        parts = line0.split(" ")
        if len(parts) < 3:
            continue

        method, path, http_ver = parts
        print('%s - %s %s' % (str(addr[0]), str(method), str(path)))

        if path.find("open") > -1:
            if not lock:
                lock = True
                print("Open relay")
                pin.on()
                sleep(DELAY)
                pin.off()
                print("Closed relay")
                lock = False
            else:
                print("Locked..")

            conn.send('HTTP/1.1 303 See Other\n')
            conn.send('Location: /\n')
            conn.send('Connection: close\n\n')

            continue

        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        response = web_page()
        conn.sendall(response)
        conn.close()


def run():
    ip = connect_wifi()
    print('Starting service on http://%s' % ip)
    http_server()


if __name__ == '__main__':
    run()
