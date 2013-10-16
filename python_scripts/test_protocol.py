# -*- coding: utf-8 -*-
from protocol import Protocol
import time

proto = Protocol('com4')

while 1:
    #1. тест echo
    for i in range(2):
        proto.echo()
        time.sleep(1)
    
    for i in range(180):
        proto.move_servo(3, i)
        time.sleep(0.1)
