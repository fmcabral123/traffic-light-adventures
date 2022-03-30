# For CircuitPython 7.x  boards
import board
import neopixel
import time
import asyncio
import digitalio
import keypad
import usb_cdc

# "Simulation" time granularity
timeInterval = 1.0
travelTicksCar = 3   # How many ticks for a car to get popped from the queue
travelTicksPed = 5   # How many ticks for a pedestrian to cross 4 lanes

# "Simulation" max crossing queue lengths
maxQueueLenPed = 4     # 4 "pedestrians" per crossing
maxQueueLenLong = 4    # 4 cars per long crossing (including long turns)
maxQueueLenMed = 2     # 2 cars per medium crossing
maxQueueLenShort = 1   # 1 car per short crossing

# Pixel color order: GRB
colorRed = (0, 10, 0)
colorOrange = (6, 10, 0)
colorGreen = (10, 0, 2)

# Factors for score calculation
A = 2
B = 2
C = 1

# Define the 16 WS2812 RGB modules connected to digital pin 52
pixels = neopixel.NeoPixel(board.D52, 16, pixel_order=neopixel.RGB)

# Contains the lane information, used for vehicles and pedestrians
class Lane:
    def __init__(self, name, turnModulus, isPedXing):
        self.name = name
        self.actorQueue = []
        self.hungerLevel = 0
        self.turnModulus = turnModulus  # Naive, modulus-based way to determine if this actor is going primary path (non-zero modulus) or turning (zero modulus)
        self.state = 0                  # 0 = stop, 1 = go, 2 = caution
        self.isPedXing = isPedXing      # True = use travelTicksPed, False = use travelTicksCar

    def show(self):
        #print("L {0}: len {1}, wait {2}".format(self.name, len(self.actorQueue), self.waitingTime()))
        print("{0}, {1}, ".format(len(self.actorQueue), self.waitingTime()), end = "")

    def volume(self):
        return len(self.actorQueue)

    # Returns mean waiting time in seconds
    def waitingTime(self):
        # Avoid division by zero
        if len(self.actorQueue) > 0:
            now = time.time()   # Time now
            runningTotal = 0.0
            for carTime in self.actorQueue:
                runningTotal += now - carTime

            return runningTotal / len(self.actorQueue)
        
        else:
            # Empty queue: zero wait time
            return 0.0
    
    def tick(self):
        # Do this twice?
        # If queue is not empty
        #   If state is go:
        #       pop an actor out
        count = 2
        while count > 0:
            if len(self.actorQueue) > 0:
                if self.state > 0:
                    # Does this lane have actors that can turn?
                    if self.turnModulus > 1:
                        # If this actor is supposed to run (timestamp mod turnModulus > 0) and
                        #   the crossing queue is "cleared" in 2-ish ticks, let it cross
                        if (self.actorQueue[0] % self.turnModulus >= 0) and (time.time() % 2 == 0):
                            self.actorQueue.pop(0)
                    
                    # Lane only has one direction allowed                
                    else:
                        self.actorQueue.pop(0)
                        self.hungerLevel = 0
            else:
                break
            
            count -= 1

class Junction:
    def __init__(self, mainLaneEW2, mainLaneEW1, mainLaneWE1, mainLaneWE2, subLaneS1, subLaneS2, pedLaneW, pedLaneE, pedLaneS):
        self.phase = -1

        self.mainLaneEW2 = mainLaneEW2
        self.mainLaneEW1 = mainLaneEW1
        self.mainLaneWE1 = mainLaneWE1
        self.mainLaneWE2 = mainLaneWE2
        self.subLaneS1 = subLaneS1
        self.subLaneS2 = subLaneS2

        self.pedLaneW = pedLaneW
        self.pedLaneE = pedLaneE
        self.pedLaneS = pedLaneS

        self.phase = 0
        self.changePhaseTimer = 30

    def setPhase(self, phase):
        # Sets the phase, triggers the lane settings, and sets the LEDs
        if phase >= 0 and phase <= 5:
            #print("***** setPhase {0} *****".format(phase))
            self.phase = phase

            # pixels[] indices:
            # 0 is westbound, straight
            # 1 is westbound, straight and turn south
            # 2 is eastbound, straight
            # 3 is eastbound, straight and turn south
            # 4 is gap
            # 5 is pedestrian north-south, west-side
            # 6 is pedestrian north-south, east-side
            # 7 is gap
            # 8 is south road, westbound and eastbound
            # 9 is south road, eastbound
            # 10 is gap
            # 11 is pedestrian east-west, south-side

            if phase == 0:
                self.mainLaneEW2.state = 1
                self.mainLaneEW2.hungerLevel = 0
                pixels[0] = colorGreen

                self.mainLaneEW1.state = 1
                self.mainLaneEW1.hungerLevel = 0
                pixels[1] = colorGreen

                self.mainLaneWE1.state = 1
                self.mainLaneWE1.hungerLevel = 0
                pixels[2] = colorGreen

                self.mainLaneWE2.state = 1
                self.mainLaneWE2.hungerLevel = 0
                pixels[3] = colorGreen

                self.pedLaneW.state = 0
                self.pedLaneW.hungerLevel += 1
                pixels[5] = colorRed

                self.pedLaneE.state = 0
                self.pedLaneE.hungerLevel += 1
                pixels[6] = colorRed

                self.subLaneS1.state = 0
                self.subLaneS1.hungerLevel += 1
                self.subLaneS2.state = 0
                self.subLaneS2.hungerLevel += 1
                pixels[8] = colorRed
                pixels[9] = colorRed

                self.pedLaneS.state = 1
                self.pedLaneS.hungerLevel = 0
                pixels[11] = colorGreen

            elif phase == 1:
                self.mainLaneEW2.state = 1
                self.mainLaneEW2.hungerLevel = 0
                pixels[0] = colorGreen

                self.mainLaneEW1.state = 1
                self.mainLaneEW1.hungerLevel = 0
                pixels[1] = colorGreen

                self.mainLaneWE1.state = 1
                self.mainLaneWE1.hungerLevel = 0
                pixels[2] = colorGreen

                self.mainLaneWE2.state = 1
                self.mainLaneWE2.hungerLevel = 0
                pixels[3] = colorGreen

                self.pedLaneW.state = 0
                self.pedLaneW.hungerLevel += 1
                pixels[5] = colorRed

                self.pedLaneE.state = 0
                self.pedLaneE.hungerLevel += 1
                pixels[6] = colorRed

                self.subLaneS1.state = 0
                self.subLaneS1.hungerLevel += 1
                self.subLaneS2.state = 0
                self.subLaneS2.hungerLevel += 1
                pixels[8] = colorRed
                pixels[9] = colorRed

                self.pedLaneS.state = 0
                self.pedLaneS.hungerLevel += 1
                pixels[11] = colorRed

            elif phase == 2:
                self.mainLaneEW2.state = 2
                self.mainLaneEW2.hungerLevel += 1
                pixels[0] = colorOrange

                self.mainLaneEW1.state = 2
                self.mainLaneEW1.hungerLevel += 1
                pixels[1] = colorOrange

                self.mainLaneWE1.state = 2
                self.mainLaneWE1.hungerLevel += 1
                pixels[2] = colorOrange

                self.mainLaneWE2.state = 2
                self.mainLaneWE2.hungerLevel += 1
                pixels[3] = colorOrange

                self.pedLaneW.state = 0
                self.pedLaneW.hungerLevel += 1
                pixels[5] = colorRed

                self.pedLaneE.state = 0
                self.pedLaneE.hungerLevel += 1
                pixels[6] = colorRed

                self.subLaneS1.state = 0
                self.subLaneS1.hungerLevel += 1
                self.subLaneS2.state = 0
                self.subLaneS2.hungerLevel += 1
                pixels[8] = colorRed
                pixels[9] = colorRed

                self.pedLaneS.state = 0
                self.pedLaneS.hungerLevel += 1
                pixels[11] = colorRed

            elif phase == 3:
                self.mainLaneEW2.state = 0
                self.mainLaneEW2.hungerLevel += 1
                pixels[0] = colorRed

                self.mainLaneEW1.state = 0
                self.mainLaneEW1.hungerLevel += 1
                pixels[1] = colorRed

                self.mainLaneWE1.state = 0
                self.mainLaneWE1.hungerLevel += 1
                pixels[2] = colorRed

                self.mainLaneWE2.state = 0
                self.mainLaneWE2.hungerLevel += 1
                pixels[3] = colorRed

                self.pedLaneW.state = 1
                self.pedLaneW.hungerLevel = 0
                pixels[5] = colorGreen

                self.pedLaneE.state = 1
                self.pedLaneE.hungerLevel = 0
                pixels[6] = colorGreen
                
                self.subLaneS1.state = 1
                self.subLaneS1.hungerLevel = 0
                self.subLaneS2.state = 1
                self.subLaneS2.hungerLevel = 0
                pixels[8] = colorGreen
                pixels[9] = colorGreen

                self.pedLaneS.state = 0
                self.pedLaneS.hungerLevel += 1
                pixels[11] = colorRed

            elif phase == 4:
                self.mainLaneEW2.state = 0
                self.mainLaneEW2.hungerLevel += 1
                pixels[0] = colorRed

                self.mainLaneEW1.state = 0
                self.mainLaneEW1.hungerLevel += 1
                pixels[1] = colorRed

                self.mainLaneWE1.state = 0
                self.mainLaneWE1.hungerLevel += 1
                pixels[2] = colorRed

                self.mainLaneWE2.state = 0
                self.mainLaneWE2.hungerLevel += 1
                pixels[3] = colorRed

                self.pedLaneW.state = 0
                self.pedLaneW.hungerLevel += 1
                pixels[5] = colorRed

                self.pedLaneE.state = 0
                self.pedLaneE.hungerLevel += 1
                pixels[6] = colorRed
                
                self.subLaneS1.state = 1
                self.subLaneS1.hungerLevel = 0
                self.subLaneS2.state = 1
                self.subLaneS2.hungerLevel = 0
                pixels[8] = colorGreen
                pixels[9] = colorGreen

                self.pedLaneS.state = 0
                self.pedLaneS.hungerLevel += 1
                pixels[11] = colorRed
            
            elif phase == 5:
                self.mainLaneEW2.state = 0
                self.mainLaneEW2.hungerLevel += 1
                pixels[0] = colorRed

                self.mainLaneEW1.state = 0
                self.mainLaneEW1.hungerLevel += 1
                pixels[1] = colorRed

                self.mainLaneWE1.state = 0
                self.mainLaneWE1.hungerLevel += 1
                pixels[2] = colorRed

                self.mainLaneWE2.state = 0
                self.mainLaneWE2.hungerLevel += 1
                pixels[3] = colorRed

                self.pedLaneW.state = 0
                self.pedLaneW.hungerLevel += 1
                pixels[5] = colorRed

                self.pedLaneE.state = 0
                self.pedLaneE.hungerLevel += 1
                pixels[6] = colorRed
                            
                self.subLaneS1.state = 2
                self.subLaneS1.hungerLevel += 1
                self.subLaneS2.state = 2
                self.subLaneS2.hungerLevel += 1
                pixels[8] = colorOrange
                pixels[9] = colorOrange

                self.pedLaneS.state = 0
                self.pedLaneS.hungerLevel += 1
                pixels[11] = colorRed

            pixels.show()

    def rebalanceLanes(self, sLane, stLane):
        # Allows cars to change lanes if the straight lane is emptier (< 1/4) compared to the straight + turn lane
        if len(sLane.actorQueue) < len(stLane.actorQueue) / 4:
            # Only shift lanes if going straight (timestamp % self.turnModulus == 0),
            # and only those past the last car in lane1,
            # and until the lanes are roughtly the same length
            index = len(sLane.actorQueue)
            while index < len(stLane.actorQueue) and len(sLane.actorQueue) < len(stLane.actorQueue):
                # Is this car going straight?
                if stLane.actorQueue[index] % stLane.turnModulus == 0:
                    # Pop it to the other lane
                    sLane.actorQueue.append(stLane.actorQueue.pop(index))  
                else:
                    index += 1              

    def tick(self):
        now = time.time()
        #print("Time: {0}".format(now))
        #print("Phase: {0}".format(self.phase))
        #print("Phase Countdown: {0}".format(self.changePhaseTimer))

        # Redo printing for easy reading as CSV
        print("{0}, {1}, {2}, ".format(now, self.phase, self.changePhaseTimer), end = "")

        # Rebalance the lanes
        self.rebalanceLanes(self.mainLaneEW2, self.mainLaneEW1)
        self.rebalanceLanes(self.mainLaneWE1, self.mainLaneWE2)
        self.rebalanceLanes(self.subLaneS2, self.subLaneS1)

        # Main simulation section logic. Very naive assumptions on how to process crossings.
        #
        # For each lane:
        #   Call their tick() methods
        self.mainLaneEW2.tick()
        self.mainLaneEW2.show()

        self.mainLaneEW1.tick()
        self.mainLaneEW1.show()

        self.mainLaneWE1.tick()
        self.mainLaneWE1.show()

        self.mainLaneWE2.tick()
        self.mainLaneWE2.show()

        self.subLaneS1.tick()
        self.subLaneS1.show()

        self.subLaneS2.tick()
        self.subLaneS2.show()

        self.pedLaneW.tick()
        self.pedLaneW.show()

        self.pedLaneE.tick()
        self.pedLaneE.show()

        self.pedLaneS.tick()
        self.pedLaneS.show()

        print("-")

        # Calculate phase 0 and phase 3 scores
        P0Vol = sum((self.mainLaneWE1.volume(), self.mainLaneWE2.volume(), self.mainLaneEW1.volume(), self.mainLaneEW2.volume(), self.pedLaneS.volume()))
        P3Vol = sum((self.subLaneS1.volume(), self.subLaneS2.volume(), self.pedLaneW.volume(), self.pedLaneE.volume()))
        P0WT = sum((self.mainLaneWE1.waitingTime(), self.mainLaneWE2.waitingTime(), self.mainLaneEW1.waitingTime(), self.mainLaneEW2.waitingTime(), self.pedLaneS.waitingTime()))
        P3WT = sum((self.subLaneS1.waitingTime(), self.subLaneS2.waitingTime(), self.pedLaneW.waitingTime(), self.pedLaneE.waitingTime()))
        P0HL = self.mainLaneWE1.hungerLevel
        P3HL = self.subLaneS1.hungerLevel
        
        scores = [sum((A * P0Vol, B * P0WT, C * P0HL / 4)),
                  sum((A * P3Vol, B * P3WT, C * P3HL / 2))]

        # Do the state change checks after time has expired
        if self.changePhaseTimer <= 0:
            if self.phase == 0:
                if scores[0] > scores[1]:
                    #self.setPhase(0)
                    self.changePhaseTimer = 30  # Add 30 more seconds to phase 1
                else:
                    self.setPhase(1)
                    self.changePhaseTimer = 5
            
            elif self.phase == 1:
                self.setPhase(2)
                self.changePhaseTimer = 2
            
            elif self.phase == 2:
                self.setPhase(3)
                self.changePhaseTimer = 30
            
            elif self.phase == 3:
                if scores[1] > scores[0]:
                    self.changePhaseTimer = 30  # Add 30 more seconds to phase 3
                else:
                    self.setPhase(4)
                    self.changePhaseTimer = 5
            
            elif self.phase == 4:
                self.setPhase(5)
                self.changePhaseTimer = 2

            elif self.phase == 5:
                self.setPhase(0)
                self.changePhaseTimer = 30

        else:
            # Tick downwards
            self.changePhaseTimer -= 1

async def intPinLane(pin, lane):
    # Physical pin inputs to GND (low or False) correspond with a vehicle or person entering the lane
    with keypad.Keys((pin,), value_when_pressed = False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.pressed:
                    lane.actorQueue.append(time.time())
                    #print("+A {0}".format(lane.name))

            await asyncio.sleep(0)

def readSerialRaw():
    # Reads the incoming sent data through the console serial port
    byteCount = usb_cdc.console.in_waiting
    text = ""
    if byteCount:
        text = usb_cdc.console.read(byteCount).decode("utf-8")
    return text


def processText(serialBuffer, lanes):
    #Gets the 9 bits saved in hexadecimal text sent through console serial port
    try:
        value = int(serialBuffer, 16)
        bitMask = 0b100000000   # 9-bit mask, starting with the 9th bit
        for lane in lanes:
            if value & bitMask: # If the bit at that position is 1, add an actor to the lane
                lane.actorQueue.append(time.time())
                #print("+A {0}".format(lane.name))
            
            bitMask >>= 1       # Move the bit mask one place to the right to get the next bit

    except:
        # Because it's not hexadecimal
        pass

async def intSerialLane(lanes):
    # Event handler for incoming serial data
    serialBuffer = ""
    while True:
        serialBuffer += readSerialRaw()
        if serialBuffer.endswith("\n"):
            serialBuffer = serialBuffer[:-1]    # Remove newline character
            processText(serialBuffer, lanes)
            serialBuffer = ""

        await asyncio.sleep(0)

async def loop(junction):
    # Main program loop
    while True:
        junction.tick()
        await asyncio.sleep(timeInterval)

# Contains the initialization bits
async def setup():
    # Define lanes (name, isPriority, isPedXing)
    V_EW_2 = Lane("VE > W  ", 1, False)   # 100% westbound
    V_EW_1 = Lane("VE > W/S", 2, False)   # 50% westbound, 50% turning south
    V_WE_1 = Lane("VW > E  ", 1, False)   # 100% eastbound
    V_WE_2 = Lane("VW > E/S", 2, False)   # 50% eastbound, 50% turning south
    V_SX_1 = Lane("VS > W/E", 5, False)   # 80% westbound, 20% eastbound
    V_SE_2 = Lane("VS > E  ", 1, False)   # All eastbound

    P_W    = Lane("PX West ", 1, True)
    P_E    = Lane("PX East ", 1, True)
    P_S    = Lane("PX South", 1, True)

    lanes = [P_W, P_E, P_S, V_WE_1, V_WE_2, V_EW_1, V_EW_2, V_SX_1, V_SE_2]

    # Define junction with lanes
    junction = Junction(V_EW_2, V_EW_1, V_WE_1, V_WE_2, V_SX_1, V_SE_2, P_W, P_E, P_S)
    junction.setPhase(0)

    # Assign lanes to interruptable digital pins
    intV_EW_2 = asyncio.create_task(intPinLane(board.D12, V_WE_1))
    intV_EW_1 = asyncio.create_task(intPinLane(board.D11, V_WE_2))
    intV_WE_1 = asyncio.create_task(intPinLane(board.D10, V_EW_1))
    intV_WE_2 = asyncio.create_task(intPinLane(board.D9, V_WE_2))
    intV_SX_1 = asyncio.create_task(intPinLane(board.D8, V_SX_1))
    intV_SE_2 = asyncio.create_task(intPinLane(board.D7, V_SE_2))

    intP_NS_W = asyncio.create_task(intPinLane(board.D6, P_W))
    intP_NS_E = asyncio.create_task(intPinLane(board.D5, P_E))
    intP_WE_S = asyncio.create_task(intPinLane(board.D4, P_S))

    # Periodic tasks
    loopFunc = asyncio.create_task(loop(junction))
    serialFunc = asyncio.create_task(intSerialLane(lanes))

    # Set up asynchronous task execution
    await asyncio.gather(intV_WE_1, intV_WE_2, intV_EW_1, intV_EW_2, intV_SX_1, intV_SE_2, intP_NS_W, intP_NS_E, intP_WE_S, loopFunc, serialFunc)

# Call the setup() function asynchronously
asyncio.run(setup())