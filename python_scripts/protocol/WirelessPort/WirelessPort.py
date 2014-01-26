# -*- coding: utf-8 -*-
from serial import Serial
import struct
import threading
import sys

class Port:
    TranssmitPacket = 0
    Echo = 1

    def __init__(self, port, baudrate=57600):
        self.serial = Serial(port=port, baudrate=baudrate, timeout=10)
    
    def send_data(self, data):
        packet = struct.pack("<BB", self.TranssmitPacket, len(data)) + data
        self.serial.write(packet)
        data = self.serial.read(3)

        if len(data) == 0:
            return

        type, size, res = struct.unpack("<BBB", data)
        return res

    def echo(self, data):
        packet = struct.pack("<BB", self.Echo, len(data)) + data
        self.serial.write(packet)

        type, size = struct.unpack("<BB", self.serial.read(2))
        return self.serial.read(size)

if __name__ == '__main__':
    import time
    p = Port(port="com6", baudrate=115200)
    
    start_time = time.time()
    common_size = 0
    errors_count = 0
    data = "1"*8
    

    while(1):
        res = p.send_data(data)
        print res
        #time.sleep(1111111)
        
        if res:
            common_size = common_size + len(data)
        else:
            errors_count = errors_count + 1
       
        if time.time() > start_time + 10:
            print "speed: {0} byte/sec".format(common_size/(time.time() - start_time))
            print "errors: {0}".format(errors_count)
            errors_count = 0
            common_size = 0
            start_time = time.time()
            
            
            
        #time.sleep(5)

    
