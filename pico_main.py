import time
from machine import Pin
statusled = Pin(0, Pin.OUT)
pumpoutlet = Pin(2, Pin.OUT)
valve = Pin(1, Pin.OUT)
sensor = Pin(3, Pin.IN)
sensorstate = False
ontme = 5
offtme = 2

pumptime = 150

pumpison = False
valveison = False
starttime = time.time()
resevoirtime = time.time()
valveofftime = time.time()
longtime = time.time()
lasttime = starttime
currenttick = time.ticks_ms()
heartbeattick = currenttick
heartbeatduration = 200 # in milliseconds
#led.on()
#led.off()

def heartbeat() :
    
    global heartbeattick, currenttick, heartbeatduration
   
    if ((currenttick - heartbeattick) > heartbeatduration) :
        heartbeattick = currenttick
        statusled.toggle()
        #print(currenttime)
        
    #print(currenttick - heartbeattime)

# Initialize the pump and valve to off 
pumpoutlet.off()
valve.off()



valve.off()
pumpoutlet.on()
time.sleep(1)
pumpoutlet.off()

valve.on()
time.sleep(1)
valve.off()



print("testing")

while (True) :
    
    #time.sleep(1)
    
    #gets snapshot of current time in seconds and ms
    currenttime = time.time()
    currenttick = time.ticks_ms()
    
    #run heartbeat function to flash LED if needed 
    heartbeat()
    
    #if(((currenttime - longtime) > 20)):
    #     sensor.value(1)
    #    print("sensor should be on")
    #    time.sleep(1)
    
    #if (sensor.value() == 1 ):
    #    print("sensor is on")
    
    #checks to see if the sensor just turned on and if it was previously off 
    if ( (sensor.value() == 1) and (sensorstate == False)) :
           print("turn the pump on")
           #Take snapshot of start time and
           #Change the current state of the sensor to indicate if its on
           #Also turns on pump 
           starttime = time.time()
           sensorstate = True
           pumpoutlet.on()
           pumpison = True
           time.sleep(1)
          
           
    #If the pump has been on for more then 5 seconds then open valve
    if ( (currenttime - starttime > 5) and
         (pumpison == True) and
         (valveison == False) and
         (sensorstate == True)
       ):
        valve.on()
        print("pump is on")
        valveison = True
    
    # to see if sensor just turned off and if it was previously on 
    if ( (sensor.value() == 0) and
         (sensorstate == True)
       ) :
           #takeing snapshot of resevoir time
           # Change the current state of the sensor to indicate if its off
           resevoirtime = time.time()
           sensorstate = False
    
    #checking if the pump has been running for 45+ seconds if so it shuts the valve off
    # takes snapshot 
    if ((currenttime - resevoirtime > pumptime) and
        (valveison == True) and
        (sensorstate ==  False) and 
        (pumpison == True)):
        valve.off()
        valveison = False
        valveofftime = time.time()
  
    # if the time since the valve shut is greater then 2 seconds it shuts the pump off 
    if ((currenttime - valveofftime > 2) and
        (pumpison == True) and
        (sensorstate ==  False) and
        (valveison == False)):
        pumpoutlet.off()
        print("pump is off")
        pumpison = False
 
 # EOF
 
