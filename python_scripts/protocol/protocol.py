# -*- coding: utf-8 -*-
from serial import Serial
import struct

class Protocol:
    CMD_ECHO = 0
    CMD_SET_SEVO_POS = 1
    CMD_SET_SEVOS_RANGES = 2
    CMD_ADD_ANIMATION = 3
    CMD_CLEAR_ANIMATION = 4
    CMD_START_ANIMATIONS = 5
    CMD_STOP_ANIMATIONS = 6
    CMD_GET_SEVOS_RANGES = 7
    CMD_GET_SEVO_POS = 8

    def __init__(self, port_name="com8", baudrate=115200):
        self.serial = Serial(port=port_name, baudrate=baudrate)
    
    def echo(self, data):
        self.serial.write(struct.pack("<BB", len(data), self.CMD_ECHO) + data)
        return self.serial.read(2+len(data))[2:]
        
    def move_servo(self, group_id, servo_id, value):
        data = struct.pack("<BBf", group_id, servo_id, value)
        self.serial.write(struct.pack("<BB", len(data), self.CMD_SET_SEVO_POS) + data)
        return struct.unpack("<B", self.serial.read(3)[2:])[0]
    
    def set_group_params(self, group_id, period, resolution, ranges):
        data = struct.pack("<BfB", group_id, period, resolution) + "".join([struct.pack("<ff", r[0], r[1]) for r in ranges])
        self.serial.write(struct.pack("<BB", len(data), self.CMD_SET_SEVOS_RANGES) + data)
        return struct.unpack("<B", self.serial.read(3)[2:])[0]

    def get_group_params(self, group_id):
        self.serial.write(struct.pack("<BBB", 1, self.CMD_GET_SEVOS_RANGES, group_id))
        size, cmd = struct.unpack("<BB", self.serial.read(2))
        data = self.serial.read(size)
        print "data len:", len(data)

        if size == 1:
            return None
        else:
            res = list(struct.unpack("<BfB", data[1: 7]))
            data = data[7:]
            res.append([struct.unpack("<ff", data[i * 8: i * 8 + 8]) for i in range(4)])
            return res

                
            
        


if __name__ == '__main__':
    import time
    p = Protocol()
    
    while 1:
        #print p.echo("1234")
        #time.sleep(2)
        #print p.move_servo(0,0,0.3)
        #time.sleep(2)
        #print p.set_group_params(0, 150., 223, [[0,1], [0.8, 3],[0,1],[0,1]])
        #time.sleep(2)
        params = p.get_group_params(1)
        print p.set_group_params(*params)
        time.sleep(2)