from enum import Enum


class DEVICES(Enum):
    ESP8266 = 1      # if you use an ESP8266 over WiFi
    PI = 2           # if you use a Raspberry Pi as a standalone unit
    BLINKSTICK = 3   # if you use a BlinkstickPro is connected to this PC
