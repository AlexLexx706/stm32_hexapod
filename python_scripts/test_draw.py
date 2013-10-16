# -*- coding: utf-8 -*-
import sys
import pygame
import math

pygame.init() 

#create the screen
window = pygame.display.set_mode((640, 480)) 

#draw a line - see http://www.pygame.org/docs/ref/draw.html for more 
pygame.draw.line(window, (255, 255, 255), (0, 0), (30, 50))

#draw it to the screen
pygame.display.flip() 



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



#input handling (somewhat boilerplate code):
while True: 
    for event in pygame.event.get(): 
      if event.type == pygame.QUIT: 
          sys.exit(0) 
      else: 
          print event
    window.fill((0, 0, 0))
    
    
    center = (500,500)
    a = 85.0
    c = 90.05
    k = 95.0
    angle1 = 160. / 180. * math.pi
    pos = [-140., 0.0] #конечная точка
    res = calc_angles(a, c, k, angle1, pos)
    
    end1 = (center[0])

    pygame.draw.line(window, (255, 255, 255), (0, 0), (30, 50))
    pygame.display.flip()
