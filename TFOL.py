import json
import os
import subprocess
import time

import RPi.GPIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import psutil
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

# 128x32 display with hardware I2C:
disp = NBX_OLED.SSD1306_128_32(rst=RST)

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
en_font = ImageFont.load_default()


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


def net():
    net_io_counters = psutil.net_io_counters()
    # 获取当前时间戳
    start_time = time.time()
    # 获取当前接收和发送的字节数
    bytes_recv = net_io_counters.bytes_recv
    bytes_sent = net_io_counters.bytes_sent
    # 等待一段时间
    time.sleep(1)
    # 再次获取网络 I/O 计数器和当前时间戳
    net_io_counters = psutil.net_io_counters()
    end_time = time.time()
    # 计算接收和发送速率（MB/秒）
    d = (net_io_counters.bytes_recv - bytes_recv) / (end_time - start_time) / 1024
    u = (net_io_counters.bytes_sent - bytes_sent) / (end_time - start_time) / 1024
    return 'U:' + check_unit(u) + 'D: ' + check_unit(d)


def check_unit(data):
    return '{:.1f}'.format(int(data / 1024)) + ' m/s' if data > 1024 else '{:.1f}'.format(int(data)) + ' k/s'


def page_one():
    cmd = "ifconfig br-lan | awk '{print $2}' | awk 'NR==2' | awk -F ':' '{print $2}'"
    ip = subprocess.check_output(cmd, shell=True)
    now = time.strftime("%Y-%m-%d %H:%M", time.localtime())

    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, top), str(now), font=en_font, fill=255)
    draw.text((x, top + 12), "IP: " + str(ip.decode('utf8').strip()).strip('b'), font=en_font, fill=255)
    draw.text((x, top + 24), net(), font=en_font, fill=255)

    disp.image(image)
    disp.display()
    time.sleep(1)


def page_two():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    cpu_usage = str(psutil.cpu_percent()) + '%'
    tmp_core = int(subprocess.check_output("cat /sys/class/thermal/thermal_zone0/temp", shell=True))
    mem = psutil.virtual_memory()
    m = 'M: ' + f"{mem.used / (1024 ** 3):.1f}" + '/' + f"{mem.total / (1024 ** 3):.1f}" + 'G(' + str(
        psutil.virtual_memory().percent) + '%)'
    disk = psutil.disk_usage('/data')
    d = 'Disk: ' + f"{disk.used / (1024 ** 3):.1f}" + '/' + f"{disk.total / (1024 ** 3):.0f}" + 'G(' + str(
        psutil.virtual_memory().percent) + '%)'

    draw.text((x, top), str('CPU: ' + cpu_usage + " CT: " + '{:.1f}°'.format(tmp_core / 1000)), font=en_font, fill=255)
    draw.text((x, top + 12), m, font=en_font, fill=255)
    draw.text((x, top + 24), d, font=en_font, fill=255)

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

