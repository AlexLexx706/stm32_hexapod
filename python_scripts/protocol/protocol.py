# -*- coding: utf-8 -*-
#from serial import Serial
from WirelessPort.WirelessPort import Port
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

    def __init__(self, port_name, baudrate):
        self.serial = Port(port=port_name, baudrate=baudrate)
    
    def echo(self, data):
        #self.serial.write(struct.pack("<BB", len(data), self.CMD_ECHO) + data)
        #return self.serial.read(2+len(data))[2:]
        return None
        
    def move_servo(self, group_id, servo_id, value):
        print "group_id:{0} servo_id:{1} value:{2}".format(group_id, servo_id, value)
        data = struct.pack("<BBf", group_id, servo_id, value)
        return self.serial.send_data(struct.pack("<BB", len(data), self.CMD_SET_SEVO_POS) + data)
        
        #return struct.unpack("<B", self.serial.read(3)[2:])[0]
    
    def set_group_params(self, group_id, period, resolution, ranges):
        #print "group_id:{0} period:{1} resolution:{2} ranges:{3}".format(group_id, period, resolution, ranges)
        data = struct.pack("<BfH", group_id, period, resolution) + "".join([struct.pack("<ff", r[0], r[1]) for r in ranges])
        self.serial.send_data(struct.pack("<BB", len(data), self.CMD_SET_SEVOS_RANGES) + data)
        #return struct.unpack("<B", self.serial.read(3)[2:])[0]
        return None

    def get_group_params(self, group_id):
        return None
        # self.serial.write(struct.pack("<BBB", 1, self.CMD_GET_SEVOS_RANGES, group_id))
        # size, cmd = struct.unpack("<BB", self.serial.read(2))
        # data = self.serial.read(size)
        # print "data len:", len(data)

        # if size == 1:
            # return None
        # else:
            # res = list(struct.unpack("<BfH", data[1: 8]))
            # data = data[8:]
            # res.append([struct.unpack("<ff", data[i * 8: i * 8 + 8]) for i in range(4)])
            # return res

            
if __name__ == '__main__':
    import time
    import math
    p = Protocol(port_name="com6", baudrate=115200)
    
    while 1:
        #print "echo: ", p.echo("1234")
        #time.sleep(2)
        print "move_servo: ", p.move_servo(0,0, (math.cos(time.time()) + 1) / 2.0)
        
        
        #time.sleep(2)
        #print "set_group_params: ", p.set_group_params(0, 150., 223, [[0,1], [0.8, 3],[0,1],[0,1]])
        #time.sleep(2)
        #params = p.get_group_params(1)
        #print "get_group_params, set_group_params: ", p.set_group_params(*params)
        #time.sleep(2)