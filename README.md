# door-opener

An electric door opener with nodemcu.

For the hardware setup see https://opny.cc/door-opener-project

## Setup

1. Prepare the environment `make setup`
2. install micropython on your nodemcu
   **WARNING** this will flash your nodemcu, review the `Makefile` and ensure everything is good to go!

   `make reset write/nodemcu`

3. Create a file `./app/config.py` and set your configurations. See `./app/config.example.py`
4. Install the firmware

  ```sh
  ./pyboard -f cp ./app/main.py
  ./pyboard -f cp ./app/config.py
  ./pyboard -f cp ./app/boot.py
  ```

## License

Apache 2.0
