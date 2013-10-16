# -*- coding: utf-8 -*-
from protocol import Protocol
from ik.ik_leg import get_angles
import time
import math

class Animation:
    def __init__(self):
        self.dt  = 0.01
        self.cur_time = 1.0
        self.animation = [[0.0, [60.0, -130.0]],
                         [1.0, [160, -130.0]],
                         [2.0, [160, 140]],
                         [4.0, [160, -130.0]],
                         [7.0, [60.0, -130.0]]]
    
    def inc_time(self):
        if len(self.animation) == 0:
            self.cur_time = 0.0
        else:
            self.cur_time = self.cur_time + self.dt
            if ( self.cur_time > self.animation[-1][0]):
                self.cur_time = self.animation[0][0]

    def get_pos(self):
        if len(self.animation) == 0:
            return [0.0, 0.0]
        elif len(self.animation) == 1:
            return self.animation[0][1]
        else:
            for i in range(len(self.animation)-1):
                a1 = self.animation[i]
                a2 = self.animation[i + 1]
                
                if self.cur_time >= a1[0] and self.cur_time < a2[0]:
                    p1 = a1[1]
                    p2 = a2[1]
                    k = (self.cur_time - a1[0]) / (a2[0] - a1[0])
                    
                    return [p1[0] + (p2[0] - p1[0]) * k, p1[1] + (p2[1] - p1[1]) * k]

anim = Animation()
get_angles(anim.get_pos())
proto = Protocol('com4')

r = 80.
a = 0.0
d_a = math.pi / 180.
y = 60

while 1:
    #1. тест echo
    pos = [math.cos(a) * r  + 140, math.sin(a) * r  - y]
    #angles = get_angles(anim.get_pos())
    angles = get_angles(pos)
    proto.move_servo(2, angles[0])
    proto.move_servo(3, angles[1])

    anim.inc_time()
    #time.sleep(anim.dt)
    a = a + d_a
    r = (math.cos(a / 2.) + 1.) / 2. * 40.  +20
    y = (math.cos(a / 2.) + 1.) / 2. * 60 
    
