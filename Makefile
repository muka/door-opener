
TAG ?= latest
FW ?= esp8266-20191220-v1.12.bin

setup: clean deps download

clean:
	rm -rf ./venv ./*.bin ./webrepl_cli ./pyboard

deps:
	sudo echo
	virtualenv -p python3 ./venv
	./venv/bin/pip3 install -r requirements.txt
	cd venv/ && git clone https://github.com/micropython/webrepl.git
	echo "./venv/bin/python venv/webrepl/webrepl_cli.py \$@" > webrepl_cli
	cd venv && wget https://raw.githubusercontent.com/micropython/micropython/master/tools/pyboard.py
	echo "./venv/bin/python ./venv/pyboard.py -b 115200 --device /dev/ttyUSB0 \$@" > pyboard
	chmod +x ./webrepl_cli ./pyboard
	sudo apt install -y picocom

download:
	wget https://micropython.org/resources/firmware/${FW}

reset:
	./venv/bin/esptool.py --port /dev/ttyUSB0 erase_flash

write/nodemcu:
	./venv/bin/esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 ${FW}

repl:
	picocom /dev/ttyUSB0 -b115200

webrepl:
	xdg-open http://micropython.org/webrepl

mqtt-server:
	docker run --rm --name mqtt_server -d -p 1883:1883 eclipse-mosquitto

docker/build:
	docker build . -t opny/micropython

docker/push:
	docker push opny/micropython:${TAG}
