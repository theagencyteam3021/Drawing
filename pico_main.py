import time
from machine import Pin
status_led_pin = Pin(0, Pin.OUT)
pump_pin = Pin(2, Pin.OUT)
valve_pin = Pin(1, Pin.OUT)
sensor_pin = Pin(3, Pin.IN)

heartbeat_duration = 200 # in milliseconds
pump_spool_time = 2 # seconds? time.time()
pump_on_time = 150

start_time = time.time()
current_time = start_time
last_event_time = current_time
heartbeat_time = time.ticks_ms()
heartbeat_offset = 0

pump_pin.off()
valve_pin.off()

state = "wait_for_low_pressure"
# "wait_for_low_pressure"
# "wait_for_pump_on"
# "wait_for_high_pressure"
# "wait_for_time"
# "wait_for_pump_off"

def try_heartbeat():
    global heartbeat_time, heartbeat_duration, heartbeat_offset

    heartbeat_time = time.ticks_ms()
    if ((heartbeat_time - heartbeat_offset) > heartbeat_duration):
        heartbeat_offset = heartbeat_time
        status_led_pin.toggle()
        #print("Toggled")



while True:
    current_time = time.time()

    try_heartbeat()

    time_since_last_event = (current_time - last_event_time)

    if state == "wait_for_low_pressure":
        if sensor_pin.value() == 1:
            pump_pin.on()
            last_event_time = current_time
            state = "wait_for_pump_on"

    elif state == "wait_for_pump_on":
        if time_since_last_event > pump_spool_time:
            valve_pin.on()
            last_event_time = current_time
            state = "wait_for_high_pressure"

    elif state == "wait_for_high_pressure":
        if sensor_pin.value() == 0:
            last_event_time = current_time
            state = "wait_for_time"

    elif state == "wait_for_time":
        if time_since_last_event > pump_on_time:
            pump_pin.off()
            last_event_time = current_time
            state = "wait_for_pump_off"
    
    elif state == "wait_for_pump_off":
        if time_since_last_event > pump_spool_time:
            valve_pin.off()
            last_event_time = current_time
            state = "wait_for_low_pressure"
