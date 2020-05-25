# Arduino-Monitoring-Console

This program uses a "server" program running on a Linux or Windows PC and a "cilent" program running on an Arduino to display system
CPU, RAM, and GPU usage as percentages on analogue panel metres. It 

### Installing

The file arduino_rom/arduino_rom.ino should be opened in the Arduino IDE and uploaded to the Arduino. Pins should be connected to the Arduino as indicated:
 - CPU panel metre from pin 11 to ground
 - GPU panel metre from pin 9 to ground
 - RAM panel metre from pin 10 to ground
 - Microphone mute switch should be connected to pin 2 with a pull-down (or pull-up) resistor so that your 'on' position will give a value of high and your 'off' position will give a value of low
 
You should install the following Python libraries:
 - pyserial
 - psutil
 - [GPUtil](https://github.com/anderskm/gputil)

There is no ui on the PC side for now, so you must manually set the serial ports at the top of console_controller.py based on the port that the Arduino IDE gives
 
### Running
##### Linux
With your Arduino connected, run console_controller.py with the following command:
`python console_controller.py`
##### Windows
With your Arduino connected, double-click on Launch, or run the following command:
`python console_controller.py`
