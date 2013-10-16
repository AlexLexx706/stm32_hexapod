# -*- coding: utf-8 -*-
import math
import time
from protocol import Protocol

#размеры в миллиметрах, углы в радианах
a = 85.0
c = 90.05
k = 95.0
#angle1 = math.pi * 0.95
angle1 = 150./180. * math.pi
pos = [-140., 0.0] #конечная точка


def calc_angles(a, c, k, angle1, pos):
    end1 = [-k * math.sin(angle1), -k * math.cos(angle1)]
    b = math.sqrt( math.pow((pos[0] - end1[0]), 2) + math.pow((pos[1] - end1[1]), 2) )
    alfa1 = math.acos( (b*b + c*c - a*a) / (2 * b * c) )
    betta = math.acos( (a*a + c*c - b*b) / (2 * a *c) )
    angle3 = betta - math.pi / 2.0
    n = math.sqrt( pos[0] * pos[0] + pos[1] * pos[1] )
    alfa2 = math.acos( (b*b + k*k - n*n) / ( 2 * b * k) )
    angle2 = alfa1 + alfa2
    
    return (angle1, angle2 - (18.19 / 180. * math.pi), angle3)


    
    
    
count = 0.0
proto = Protocol('com4')

while 1:
    count = count + 0.1
    #pos = (((math.cos(count) + 1.0) / 2.0) * (-120.0) - 100.0, 0.0)
    pos = [-140., 0.0]
    
    res = calc_angles(a, c, k, angle1, pos)
    proto.move_servo(0, 2, res[0]/math.pi)
    proto.move_servo(0, 1, res[1]/math.pi)
    proto.move_servo(0, 0, res[2]/math.pi)
    

    #for id, value in enumerate(res):
    #    proto.move_servo(0, id, value/math.pi)

    time.sleep(0.01)
    print "pos:{0} angle1:{1} angle2:{2} angle3:{3}".format(pos, res[0]/math.pi * 180., res[1]/math.pi * 180., res[2]/math.pi * 180.)


