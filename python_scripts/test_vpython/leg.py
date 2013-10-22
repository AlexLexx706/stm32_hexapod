#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from __future__ import division
from visual import * 
from my_frame import MyFrame
import multiprocessing


class Leg:
    def __init__(self, b_1_settings=None, cmd_queue=None, group_index=1):
        self.angle_0 = 0.0
        self.angle_1 = 0.0
        self.angle_2 = 0.0
        self.angle_3 = 0.0

        self.cmd_queue = cmd_queue                            
        self.group_index = group_index

        #1
        if b_1_settings is not None:
            self.b_1 = MyFrame(**b_1_settings)
        else:
            self.b_1 = MyFrame()

        self.b_1_box_1 = box(frame=self.b_1,
                            size=(63, 2, 40),
                            pos=(-31.5, 12.69, 0),
                            axis=(1, 0, 0))

        self.b_1_box_2 = box(frame=self.b_1,
                            size=(63, 2, 40),
                            pos=(-31.5, -39.02, 0),
                            axis=(1, 0, 0))


        self.b_1_box_3 = box(frame=self.b_1,
                            size=(2, 53.71, 40),
                            pos=(-1, -13.17, 0),
                            axis=(1, 0, 0))

        #2 
        self.b_2 = MyFrame(frame=self.b_1,
                                pos=(-53, 0, 0))

        self.b_2_celinder = cylinder(frame=self.b_2,
                                        pos=(0, 16.1),
                                        axis=(0,-1),
                                        radius=8,
                                        length=63)
        
        self.b_2_box_1 = box(frame=self.b_2,
                            size=(61.5, 43.61, 26.5),
                            pos=(9.25, -13.21, -1.75),
                            axis=(1, 0, 0))

        self.b_2_box_2 = box(frame=self.b_2,
                            size=(28.81, 60, 43.6),
                            pos=(-35.9, -4.99, -0.3),
                            axis=(1, 0, 0))
        
        #3
        self.b_3 = MyFrame(frame=self.b_2,
                         pos=(-35, -14.99, 0))

        self.b_3_celinder = cylinder(frame=self.b_3,
                                        pos=(0, 0, -29.6),
                                        axis=(0, 0, 1),
                                        radius=8,
                                        length=59.1,
                                        color=(1, 0, 0))

        self.b_3_box_1 = box(frame=self.b_3,
                          size=(42, 20, 2),
                          pos=vector(-11, 0, 25.85),
                          color=(1, 0, 0))

        self.b_3_box_2 = box(frame=self.b_3,
                          size=(42, 20, 2),
                          pos=vector(-11, 0, -25.85),
                          color=(1, 0, 0))        

        self.b_3_box_3 = box(frame=self.b_3,
                          size=(2, 20, 53.7),
                          pos=vector(-31, 0, 0),
                          color=(1, 0, 0))

        self.b_3_box_4 = box(frame=self.b_3,
                          size=(68, 25, 25),
                          pos=vector(-(32 + 34), 0, 0),
                          color=(1, 0, 0))                          

        #4.
        self.b_4 = MyFrame(frame=self.b_3,
                            pos=(-(32 + 34 + 14), 0, 0))

        self.b_4_celinder = cylinder(frame=self.b_4,
                                        pos=(0, 0, -29.6),
                                        axis=(0, 0, 1),
                                        radius=8,
                                        length=59.1,
                                        color=(0, 0, 1))
                                        
        self.b_4_box_1 = box(frame=self.b_4,
                            size=(39.5, 20, 2),
                            pos=(-9.75, 0, 25.5),
                            color=(0, 0, 1))

        self.b_4_box_2 = box(frame=self.b_4,
                            size=(39.5, 20, 2),
                            pos=(-9.75, 0, -25.5),
                            color=(0, 0, 1))

        self.b_4_box_3 = box(frame=self.b_4,
                            size=(2, 20, 53.7),
                            pos=(-28.5, 0, 0),
                            color=(0, 0, 1))

        self.b_4_box_4 = box(frame=self.b_4,
                            size=(55.5, 10, 10),
                            pos=(-57.25, 0, 0),
                            color=(0, 0, 1))
    
    def has_obj(self, obj):
        return obj is self.b_4_box_4

        if obj in self.b_1.objects:
            return True
        if obj in self.b_2.objects:
            return True
        if obj in self.b_3.objects:
            return True
        if obj in self.b_4.objects:
            return True
        return False
                          
    def set_angle_0(self, in_angle):
        border = pi / 2.0
        if in_angle >= border:
            in_angle = border
        elif in_angle < -border:
            in_angle = border
        
        sub_angle = in_angle - self.angle_0

        if sub_angle != 0.0:
            self.angle_0 = in_angle
            self.b_2.rotate(angle=sub_angle, axis=(0,1,0))

            if self.cmd_queue is not None:
                self.cmd_queue.put((self.group_index, 2, (pi - (in_angle + border)) / pi))


    def set_angle_1(self, in_angle):
        sub_angle = in_angle - self.angle_1

        if sub_angle != 0.0:
            self.angle_1 = in_angle
            self.b_3.rotate(angle=sub_angle, axis=(0,0,1))
            
            if self.cmd_queue is not None:
                offset = 140 / 180 * pi 
                self.cmd_queue.put((self.group_index, 1, (offset - in_angle) / pi))
        
       

    def set_angle_2(self, in_angle):
        sub_angle = in_angle - self.angle_2

        if sub_angle != 0.0:
            self.angle_2 = in_angle
            self.b_4.rotate(angle=sub_angle, axis=(0,0,1))

            if self.cmd_queue is not None:
                offset = 122 / 180 * pi            
                self.cmd_queue.put((self.group_index, 0, (offset - in_angle) / pi))
    
    def calc_angles(self, end_pos):
        a = mag(self.b_4.pos)
        b = 85.0
        c = mag(end_pos)
        c = c if c <= a + b else a + b
        
        alfa_1 = math.acos((a * a + c * c - b * b) / (2 * a * c))
        alfa_2 = pi - (math.acos((b * b + a * a - c * c) / (2 * b * a)))
        
        betta = diff_angle((end_pos[0], end_pos[1]), (-1,0))

        if dot((end_pos[0], end_pos[1]), (0, -1)) >= 0:
            betta = betta - alfa_1
        else:
            betta = -betta - alfa_1

        return (betta, alfa_2)

    def set_pos(self, end_pos):
        #1. найдём угол поворота плоскости b_2 относиельно b_1 и знак угла
        v1 = self.b_1.world_to_frame(end_pos) - self.b_2.pos
        v1.y = 0.0

        b_2_angle = diff_angle(v1, (-1, 0, 0))
        b_2_angle = b_2_angle if dot(v1, (0, 0, 1)) >= 0. else -b_2_angle

        #2. перевод end_pos в координаты b_3
        b_3_g_pos = self.b_2.world_to_frame(end_pos) - self.b_3.pos
        angles = self.calc_angles(b_3_g_pos)

        self.set_angle_0(b_2_angle)
        self.set_angle_1(angles[0])
        self.set_angle_2(angles[1])

    def get_pos(self):
        return self.b_4.frame_to_world((-85.0, 0, 0))
    

def servo_process(cmd_queue):
    from protocol.protocol import Protocol
    protocol = Protocol('com4')
    
    while 1:
        cmd = cmd_queue.get()
        if cmd is None:
            break
        group, servo, value = cmd
        
        protocol.move_servo(0, servo, value)
        protocol.move_servo(1, servo, value)
        protocol.move_servo(2, servo, value)
        protocol.move_servo(3, servo, value)
    
if __name__ == '__main__':
    #координаты
    x_arrow = arrow(pos=(0,0,0), axis=(1,0,0), length=100, shaftwidth=1, fixedwidth = True, color=color.red)
    x_arrow = arrow(pos=(0,0,0), axis=(0,1,0), length=100, shaftwidth=1, fixedwidth = True, color=color.green)
    x_arrow = arrow(pos=(0,0,0), axis=(0,0,1), length=100, shaftwidth=1, fixedwidth = True, color=color.blue)

    cmd_queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=servo_process,  args=(cmd_queue,))    
    proc.start()
    
    leg = Leg(cmd_queue=cmd_queue, group_index=0)
    
    
    can_move = False
    move_camera = False
    camera_pos = None
    offset = None


    
    scene.autoscale=0

    def mousedown(event):
        if  event.shift == False:
            global can_move
            global offset
            can_move = True
        else:
            global move_camera
            global camera_pos

            move_camera = True
            camera_pos = event.pos

    def mouseup():
        global can_move
        can_move = False
        global move_camera
        move_camera = False

    def mousemove(event):
        global can_move
        global move_camera
        global offset

        if can_move:
            leg.set_pos(scene.mouse.project(normal=vector(0,0,1)))
            pass
        elif move_camera:
            global camera_pos
            dv = event.pos - camera_pos
            scene.center = scene.center - dv
            camera_pos = event.pos
    
    scene.bind('mousedown', mousedown)
    scene.bind('mouseup', mouseup)
    scene.bind('mousemove', mousemove)
    
    while True:
        rate(30)
 