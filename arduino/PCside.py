import serial
import random
import time

random.seed(time.time())

port = serial.Serial(port = "COM4", baudrate = 9600, bytesize = 8, timeout = 1, stopbits = serial.STOPBITS_ONE)
outFile = "C:\\usr\\src\\output.txt"

port.flush()

with open(outFile, "w") as f:
    while True:
        try:
            data = port.readline().decode("utf-8")
            print(data, end="")
            f.write(data)
            
            # Add zero to two random actors after a cycle
            if data.startswith("-"):
                count = random.randint(0, 2)
                while count > 0:
                    out = hex(random.randint(1, 511))[2:] + "\n"
                    print("PC >>> {0}".format(out))
                    port.write(out.encode("utf-8"))
                    count -= 1
                    time.sleep(0.15)


        except KeyboardInterrupt:
            break

port.close()