# Copyright (c) 2017 Adafruit Industries
# Author: Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import json
import os
import subprocess
import time

import RPi.GPIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import NBX_OLED

RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setwarnings(False)
RPi.GPIO.setup(4, RPi.GPIO.OUT)
RPi.GPIO.output(4, True)
# Raspberry Pi pin configuration:
RST = None  # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Beaglebone Black pin configuration:
# RST = 'P9_12'
# Note the following are only used with SPI:
# DC = 'P9_15'
# SPI_PORT = 1
# SPI_DEVICE = 0

# 128x32 display with hardware I2C:
disp = NBX_OLED.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Note you can change the I2C address by passing an i2c_address parameter like:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

# Alternatively you can specify an explicit I2C bus number, for example
# with the 128x32 display you would use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)

# 128x32 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# 128x64 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# Alternatively you can specify a software SPI implementation by providing
# digital GPIO pin numbers for all the required display pins.  For example
# on a Raspberry Pi with the 128x32 display you might use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, sclk=18, din=25, cs=22)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
# font = ImageFont.load_default()
# cn_font = ImageFont.truetype('JetBrainsMono.ttf', 8, encoding='utf-8')

en_font = ImageFont.load_default()


# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)

def fan():
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    cmd = "cat /sys/class/thermal/thermal_zone0/temp"
    tmp_core = int(subprocess.check_output(cmd, shell=True))
    upper = int(45 if os.getenv("upper") is None else os.getenv("upper")) * 1000
    lower = int(42 if os.getenv("lower") is None else os.getenv("lower")) * 1000
    if tmp_core > upper:
        RPi.GPIO.output(4, True)
    if tmp_core < lower:
        RPi.GPIO.output(4, False)


def call_net():
    sleep_time = 0.2
    tx_cmd1 = "ifconfig br-lan | grep 'TX packets' | awk '{print $5}'"
    tx1 = subprocess.check_output(tx_cmd1, shell=True)
    time.sleep(sleep_time)
    tx_cmd2 = "ifconfig br-lan | grep 'TX packets' | awk '{print $5}'"
    tx2 = subprocess.check_output(tx_cmd2, shell=True)
    up = check_unit(parse(tx2, tx1), sleep_time)

    rx_cmd1 = "ifconfig br-lan | grep 'RX packets' | awk '{print $5}'"
    rx1 = subprocess.check_output(rx_cmd1, shell=True)
    time.sleep(sleep_time)
    rx_cmd2 = "ifconfig br-lan | grep 'RX packets' | awk '{print $5}'"
    rx2 = subprocess.check_output(rx_cmd2, shell=True)
    download = check_unit(parse(rx2, rx1), sleep_time)
    return 'U:' + up + ' ' + 'D:' + download


def parse(speed2, speed1):
    return int(str(speed2.decode('utf-8').strip()).strip('b')) - int(str(speed1.decode('utf-8').strip()).strip('b'))


def check_unit(difference, sleep_time):
    result = difference / sleep_time / 1024
    return '{:.1f}'.format(int(result / 1024)) + ' m/s' if result > 1024 else '{:.1f}'.format(int(result)) + ' k/s'


def page_one():
    cmd = "ifconfig br-lan | awk '{print $2}' | awk 'NR==2'"
    ip = subprocess.check_output(cmd, shell=True)
    now = time.strftime("%Y-%m-%d %H:%M", time.localtime())

    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, top), str(now), font=en_font, fill=255)
    draw.text((x, top + 12), "IP: " + str(ip.decode('utf8').strip()).strip('b'), font=en_font, fill=255)
    draw.text((x, top + 24), call_net(), font=en_font, fill=255)

    disp.image(image)
    disp.display()
    time.sleep(1)


def page_two():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    cmd = "top -bn1 | grep load | awk '{printf (\"CPU:%.2f\", $(NF-2))}'"
    cpu = subprocess.check_output(cmd, shell=True)
    cmd = "cat /sys/class/thermal/thermal_zone0/temp"
    tmp_core = int(subprocess.check_output(cmd, shell=True))
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB (%s)\", $3,$2,$5}'"
    disk = subprocess.check_output(cmd, shell=True)
    cmd = "free -m | awk 'NR==2{printf \"Mem: %.1f/%.1fG (%.1f%%)\", $3/1000,$2/1000,$3*100/$2 }'"
    mem = subprocess.check_output(cmd, shell=True)

    draw.text((x, top), str(cpu.decode('utf8').strip()).strip('b') + " CT:" + '{:.2f}°'.format(tmp_core / 1000),
              font=en_font,
              fill=255)
    draw.text((x, top + 12), str(mem.decode('utf8').strip()).strip('b'), font=en_font, fill=255)  # "T:" +
    draw.text((x, top + 24), str(disk.decode('utf8').strip()).strip('b'), font=en_font, fill=255)

    disp.image(image)
    disp.display()
    time.sleep(1)


lock = True
while True:
    fan()
    if lock:
        page_one()
        lock = False
    else:
        page_two()
        lock = True
