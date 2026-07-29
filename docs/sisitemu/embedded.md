# Embedded Development Guide

## Overview

SISITEMU's embedded platform (`ibyinjijwe`) provides abstractions for MCUs,
GPIO, SPI, I2C, UART, PWM, ADC, interrupts, and RTOS primitives.

## Supported Targets

- ARM Cortex-M0, M3, M4, M7
- ESP32
- AVR (Arduino)

## GPIO

```python
from sisitemu.ibyinjijwe import GPIOController, GPIOPinMode

gpio = GPIOController()
gpio.set_mode(13, GPIOPinMode.OUTPUT)
gpio.write(13, True)
value = gpio.read(12)
```

## I2C

```python
from sisitemu.ibyinjijwe import I2CBus

i2c = I2CBus(bus_id=1, frequency=100000)
data = i2c.read(0x76, 0x00, 2)
i2c.write(0x76, 0x01, b"\x00")
```

## RTOS

```python
from sisitemu.ibyinjijwe import RTOS, RTOSConfig, RTOSTask

rtos = RTOS(RTOSConfig(max_tasks=16))

def blink_task():
    while True:
        gpio.toggle(13)
        rtos.delay(500)

task = RTOSTask(name="blink", fn=blink_task, priority=1)
rtos.create_task(task)
rtos.start()
```

## Flashing

```bash
isoko sisitemu embedded flash --port /dev/ttyUSB0 --firmware firmware.bin
isoko sisitemu embedded monitor --port /dev/ttyUSB0 --baud 115200
```
