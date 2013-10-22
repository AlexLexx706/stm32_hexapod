#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from __future__ import division
from visual import * 
import multiprocessing
import numpy


#модель ноги
class MyFrame(frame):
    def __init__(self, **args):
        frame.__init__(self, **args)
    
    def get_matrix(self):
        #найдём все фреймы.
        grob_matrix = numpy.identity(4)
        grob_matrix[:3, 0] = self.axis
        grob_matrix[:3, 1] = self.up
        grob_matrix[:3, 2] = cross(self.axis, self.up)
        grob_matrix[:3, 3] = self.pos

        cur_frame = self.frame
     
        while cur_frame is not None:
            cur_matrix = numpy.identity(4)
            cur_matrix[:3, 0] = cur_frame.axis
            cur_matrix[:3, 1] = cur_frame.up
            cur_matrix[:3, 2] = cross(cur_frame.axis, cur_frame.up)
            cur_matrix[:3, 3] = cur_frame.pos
            grob_matrix = numpy.dot(cur_matrix, grob_matrix)
            
            cur_frame = cur_frame.frame

        return grob_matrix
    
    def frame_to_world(self, frame_pos):
        return vector(numpy.dot(self.get_matrix(), (frame_pos[0],
                                                    frame_pos[1],
                                                    frame_pos[2],
                                                    1.0))[:3])
        
    def world_to_frame(self, world_pos):
        m = self.get_matrix()
        pos = world_pos - m[:3, 3]
        return vector(numpy.dot(m.T, (pos[0], pos[1], pos[2], 0.))[:3])


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
                                     axis=(0, -1),
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
                             size=(20, 58.5, 2),
                             pos=vector(0, -19.25, 25.5),
                             color=(1, 0, 0))

        self.b_3_box_2 = box(frame=self.b_3,
                             size=(20, 58.5, 2),
                             pos=vector(0, -19.25, -25.5),
                             color=(1, 0, 0))

        self.b_3_box_3 = box(frame=self.b_3,
                             size=(20, 4, 53.7),
                             pos=vector(0, -47, 0),
                             color=(1, 0, 0))

        self.b_3_box_4 = box(frame=self.b_3,
                             size=(26.5, 66.5, 25),
                             pos=vector(-1.9, -81.75, 0),
                             color=(1, 0, 0))

        #4
        self.b_4 = MyFrame(frame=self.b_3, pos=(0, -95))

        self.b_4_celinder = cylinder(frame=self.b_4,
                                     pos=(0, 0, -29.6),
                                     axis=(0, 0, 1),
                                     radius=8,
                                     length=59.1,
                                     color=(0, 1, 0))

        self.b_4_box_1 = box(frame=self.b_4,
                             size=(20, 43.5, 2),
                             pos=(6.14, 10.2, 25.5),
                             axis=rotate((1, 0, 0),
                                         angle=-31.29/180. * pi,
                                         axis=(0, 0, 1)),
                             color=(0, 1, 0))

        self.b_4_box_2 = box(frame=self.b_4,
                             size=(20, 43.5, 2),
                             pos=(6.14, 10.2, -25.5),
                             axis=rotate((1, 0, 0),
                                         angle=-31.29/180. * pi,
                                         axis=(0, 0, 1)),
                             color=(0, 1, 0))

        self.b_4_box_3 = box(frame=self.b_4,
                             size=(20, 4, 53.7),
                             pos=(16.75, 27.25, 0.0),
                             axis=rotate((1, 0, 0),
                                         angle=-31.29/180. * pi,
                                         axis=(0, 0, 1)),
                             color=(0, 1, 0))

        self.b_4_box_3 = box(frame=self.b_4,
                             size=(25, 92.48, 25),
                             pos=(7.44, 64.86, 0.0),
                             axis=rotate((1, 0, 0),
                                         angle=18.39/180. * pi,
                                         axis=(0, 0, 1)),
                             color=(0, 1, 0))

        #5.
        self.b_5 = MyFrame(frame=self.b_4,
                           pos=(0, 90.05))

        self.b_5_celinder = cylinder(frame=self.b_5,
                                     pos=(0, 0, -29.6),
                                     axis=(0, 0, 1),
                                     radius=8,
                                     length=59.1,
                                     color=(0, 0, 1))
                                        
        self.b_5_box_1 = box(frame=self.b_5,
                             size=(39.5, 20, 2),
                             pos=(-9.75, 0, 25.5),
                             color=(0, 0, 1))

        self.b_5_box_2 = box(frame=self.b_5,
                             size=(39.5, 20, 2),
                             pos=(-9.75, 0, -25.5),
                             color=(0, 0, 1))

        self.b_5_box_3 = box(frame=self.b_5,
                             size=(2, 20, 53.7),
                             pos=(-28.5, 0, 0),
                             color=(0, 0, 1))

        self.b_5_box_4 = box(frame=self.b_5,
                             size=(55.5, 10, 10),
                             pos=(-57.25, 0, 0),
                             color=(0, 0, 1))
        
        self.set_angle_0(0.0)
        self.set_angle_1(pi)
        self.set_angle_2(0.0)
        self.set_angle_3(pi / 2.0 - (18.40 / 180.) * pi)

    def set_angle_0(self, in_angle):
        border = pi / 2.0
        if in_angle >= border:
            in_angle = border
        elif in_angle < -border:
            in_angle = border
        
        sub_angle = in_angle - self.angle_0

        if sub_angle != 0.0:
            self.angle_0 = in_angle
            self.b_2.rotate(angle=sub_angle, axis=(0, 1, 0))

            if self.cmd_queue is not None:
                self.cmd_queue.put((self.group_index,
                                    3,
                                    (pi - (in_angle + border)) / pi))

    def set_angle_1(self, in_angle):
        if in_angle >= pi:
            in_angle = pi
        elif in_angle < 0.0:
            in_angle = 0.0

        sub_angle = self.angle_1 - in_angle

        if sub_angle != 0.0:
            self.angle_1 = in_angle
            self.b_3.rotate(angle=sub_angle, axis=(0, 0, 1))
            
            if self.cmd_queue is not None:
                self.cmd_queue.put((self.group_index, 2, in_angle / pi))
        
    def set_angle_2(self, in_angle):
        offset = 18.40 / 180. * pi
        
        if in_angle >= pi + offset:
            in_angle = pi + offset
        elif in_angle < offset:
            in_angle = offset
        
        sub_angle = self.angle_2 - in_angle

        if sub_angle != 0.0:
            self.angle_2 = in_angle
            self.b_4.rotate(angle=sub_angle, axis=(0, 0, 1))

            if self.cmd_queue is not None:
                self.cmd_queue.put((self.group_index, 1, (in_angle - offset) / pi))

    def set_angle_3(self, in_angle):
        offset = 18.40 / 180. * pi

        if in_angle >= pi - offset:
            in_angle = pi - offset
        elif in_angle < -offset:
            in_angle = -offset
        
        sub_angle = self.angle_3 - in_angle
        
        if sub_angle != 0.0:
            self.angle_3 = in_angle
            self.b_5.rotate(angle=sub_angle, axis=(0, 0, 1))

            if self.cmd_queue is not None:
                self.cmd_queue.put((self.group_index, 0, (in_angle + offset) / pi))
    
    def get_end_pos_angles(self, end_pos, angle1):
        a = 85.0
        c = mag(self.b_5.pos)
        k = mag(self.b_4.pos)

        end1 = [-k * math.sin(angle1), -k * math.cos(angle1)]
        b = math.sqrt(math.pow((end_pos[0] - end1[0]), 2) +
                      math.pow((end_pos[1] - end1[1]), 2))

        cos_alfa1 = (b * b + c * c - a * a) / (2 * b * c)

        if cos_alfa1 <= 1.0:
            alfa1 = math.acos(cos_alfa1)
            betta = math.acos((a * a + c * c - b * b) / (2 * a * c))
        else:
            alfa1 = 0.0
            betta = pi

        angle3 = betta - math.pi / 2.0
       
        n = math.sqrt(end_pos[0] * end_pos[0] + end_pos[1] * end_pos[1])
        alfa2 = math.acos((b * b + k * k - n * n) / (2 * b * k))
        
        #определим знак угла.
        if dot((end1[1], -end1[0]), end_pos) >= 0:
            angle2 = alfa1 - alfa2
        else:
            angle2 = alfa1 + alfa2
        
        return (angle1, angle2, angle3)

    def set_angles(self, angles):
        self.set_angle_1(angles[0])
        self.set_angle_2(angles[1])
        self.set_angle_3(angles[2])

    def set_pos(self, end_pos, angle1):
        #1. найдём угол поворота плоскости b_2 относиельно b_1 и знак угла
        v1 = self.b_1.world_to_frame(end_pos) - self.b_2.pos
        v1.y = 0.0

        b_2_angle = diff_angle(v1, (-1, 0, 0))
        b_2_angle = b_2_angle if dot(v1, (0, 0, 1)) >= 0. else -b_2_angle
        self.set_angle_0(b_2_angle)

        #2. перевод end_pos в координаты p_3
        b_3_g_pos = self.b_2.world_to_frame(end_pos) - self.b_3.pos
        self.set_angles(self.get_end_pos_angles(b_3_g_pos, angle1))

        self.end_pos = end_pos


class Pauk:
    def __init__(self, cmd_queue=None):
        self.f_1 = MyFrame()
        
        self.f_2 = MyFrame(frame=self.f_1)
        self.f_2.rotate(axis=(0, 1, 0), angle=-pi / 4.0)
        
        self.base_box = box(frame=self.f_2,
                            size=(50, 40, 50))
        
        self.legs = []
        self.legs.append(Leg({"pos": (25, 20 - 13.7, 0), "axis": (-1, 0, 0),
                              "frame": self.f_2}, cmd_queue, 0))

        self.legs.append(Leg({"pos": (-25, 20 - 13.7, 0), "axis": (1, 0, 0),
                              "frame": self.f_2}, cmd_queue, 1))

        self.legs.append(Leg({"pos": (0, 20 - 13.7, 25.), "axis": (0, 0, -1),
                              "frame": self.f_2}, cmd_queue, 2))

        self.legs.append(Leg({"pos": (0, 20 - 13.7, -25.), "axis": (0, 0, 1),
                              "frame": self.f_2}, cmd_queue, 3))
        self.time = 0.0
        
        self.base_height = 60
        self.leg_len = 110
        self.leg_angle = pi * 0.8

        for id, point in enumerate(self.get_init_legs_points()):
            self.legs[id].set_pos(point, self.leg_angle)

        self.can_move = True
        self.first_step = True

        self.move_direction = vector(0, 0, 0)
        self.move_time = 0.0
        self.move_angle = 0.0
        self.angle = 0.0

    def set_angle(self, angle):
        da = angle - self.angle
        
        if da != 0.0:
            self.f_1.rotate(angle=da, axis=self.f_1.up)
            self.angle = angle
    
    def get_angle(self):
        return self.angle
            
    def get_init_legs_points(self):
        res = []
        for leg in self.legs:
            pos = self.f_1.world_to_frame(leg.b_2.frame_to_world((0, 0, 0)))
            pos.y = 0
            pos = pos + norm(pos) * self.leg_len + vector(0, -1, 0) * self.base_height
            res.append(pos)
        return res

    def get_data_by_time(self, animation, time):
        if len(animation) == 0:
            return vector(0, 0, 0)
        elif len(animation) == 1:
            return vector(animation[0][1])
        else:
            if time < animation[0][0]:
                return animation[0][1]
            elif time >= animation[-1][0]:
                return animation[-1][1]

            for i in range(1, len(animation)):
                if animation[i][0] >= time:
                    return vector(animation[i-1][1]) + (vector(animation[i][1]) - vector(animation[i-1][1])) *\
                            (time - animation[i-1][0]) / (animation[i][0] - animation[i-1][0])
 
    def set_next_move(self, direction, angle, time):
        if not self.can_move:
            self.move_direction = direction
            self.move_angle = angle
            self.move_time = time
            self.can_move = True

    #сделать шиг в заданном направление за заданное время.
    def update(self, rate=30.0):
        #разрешено движение.
        if self.can_move:
            #рассчёт анимации ног.
            if self.first_step:
                max_up = 80
                leg_move_time = self.move_time / 4.0
                dt = 0.0

                #инимация перемещения
                if self.move_angle == 0:
                    #определим последовательность ног
                    sequence = [0, 1, 2, 3]
                    dot_x = dot(self.f_1.axis, self.move_direction)
                    dot_z = dot(vector(-self.f_1.axis.z,
                                       self.f_1.axis.y,
                                       self.f_1.axis.x),
                                self.move_direction)
                    
                    if dot_x >= 0.0 and dot_z >= 0.0:
                        sequence = [0, 1, 2, 3]
                    elif dot_x < 0.0 and dot_z >= 0.0:
                        sequence = [2, 3, 0, 1]
                    elif dot_x < 0.0 and dot_z < 0.0:
                        sequence = [1, 0, 3, 2]
                    else:
                        sequence = [3, 2, 1, 0]

                    #создание набора анимации
                    for id in sequence:
                        leg = self.legs[id]
                        leg.anim = [(0.0 + dt, vector(leg.end_pos)),
                                    (leg_move_time / 2.0 + dt, (leg.end_pos + self.move_direction / 2) + self.f_1.up * max_up),
                                    (leg_move_time + dt, (leg.end_pos + self.move_direction))]
                        dt = dt + leg_move_time

                    self.body_pos_anim = [(0.0, vector(self.f_1.pos)), (self.move_time, self.f_1.pos + self.move_direction)]
                    self.body_angle_anim = [(0.0, vector(self.angle, 0.0, 0.0))]
                    self.first_step = False
                    self.time = 0.0
                    self.max_time = self.move_time
                else:
                    #определим последовательность ног
                    for id in [0, 1, 2, 3]:
                        leg = self.legs[id]
                        new_pos_1 = self.f_1.pos + rotate(vector=(leg.end_pos - self.f_1.pos),
                                                          angle=self.move_angle / 2,
                                                          axis=self.f_1.up)

                        new_pos_2 = self.f_1.pos + rotate(vector=(leg.end_pos - self.f_1.pos),
                                                          angle=self.move_angle,
                                                          axis=self.f_1.up)

                        leg.anim = [(0.0 + dt, vector(leg.end_pos)),
                                    (leg_move_time / 2.0 + dt, new_pos_1 + self.f_1.up * max_up),
                                    (leg_move_time + dt, new_pos_2)]
                        dt = dt + leg_move_time

                    self.body_pos_anim = [(0.0, vector(self.f_1.pos))]
                    self.body_angle_anim = [(0.0, vector(self.angle, 0.0, 0.0)),
                                            (self.move_time, vector(self.angle + self.move_angle, 0.0, 0.0))]
                    
                    self.first_step = False
                    self.time = 0.0
                    self.max_time = self.move_time

            self.time = self.time + 1.0 / rate
            
            #анимация тела
            self.f_1.pos = self.get_data_by_time(self.body_pos_anim, self.time)
            self.set_angle(self.get_data_by_time(self.body_angle_anim, self.time)[0])

            #анимация ног
            for leg in self.legs:
                leg.set_pos(self.get_data_by_time(leg.anim, self.time), self.leg_angle)

            #проверка конца анимации.
            if self.time >= self.max_time:
                self.can_move = False
                self.first_step = True

            
def servo_process(cmd_queue):
    from protocol.protocol import Protocol
    protocol = Protocol('com4')
    
    while 1:
        cmd = cmd_queue.get()
        if cmd is None:
            break
        group, servo, value = cmd
        
        protocol.move_servo(group, servo, value)
    
if __name__ == '__main__':
    #координаты
    x_arrow = arrow(pos=(0, 0, 0), axis=(1, 0, 0), length=100, shaftwidth=1, fixedwidth = True, color=color.red)
    x_arrow = arrow(pos=(0, 0, 0), axis=(0, 1, 0), length=100, shaftwidth=1, fixedwidth = True, color=color.green)
    x_arrow = arrow(pos=(0, 0, 0), axis=(0, 0, 1), length=100, shaftwidth=1, fixedwidth = True, color=color.blue)
    
    #создадим процесс отсылки комманд.
    cmd_queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=servo_process,  args=(cmd_queue,))
    proc.start()
    
    #leg = Leg(cmd_queue, None, 0, 1)
    pauk = Pauk(cmd_queue)

    can_move = False
    move_camera = False
    camera_pos = None
    offset = None
    
    scene.autoscale = 0
    key_masks = {}

    def mousedown(event):
        if not event.shift:
            global can_move
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
            pass
        elif move_camera:
            global camera_pos
            dv = event.pos - camera_pos
            scene.center = scene.center - dv
            camera_pos = event.pos

    def key_down_hendler(evt):
        global key_masks
        key_masks[evt.key] = True

    def key_up_hendler(evt):
        global key_masks
        key_masks[evt.key] = False
        print evt.key
        
    scene.bind('keydown', key_down_hendler)
    scene.bind('keyup', key_up_hendler)
   
    scene.bind('mousedown', mousedown)
    scene.bind('mouseup', mouseup)
    scene.bind('mousemove', mousemove)
    
    while True:
        rate(30)
        pauk.update()
        
        direction = vector(0, 0, 0)
        angle = 0.0
        
        if "up" in key_masks and key_masks["up"]:
            direction = direction + vector(0, 0, -120)

        if "down" in key_masks and key_masks["down"]:
            direction = direction + vector(0, 0, 120)

        if "left" in key_masks and key_masks["left"]:
            direction = direction + vector(-120, 0, 0)

        if "right" in key_masks and key_masks["right"]:
            direction = direction + vector(120, 0, 0)

        if "a" in key_masks and key_masks["a"]:
            angle = angle + 0.5

        if "d" in key_masks and key_masks["d"]:
            angle = angle - 0.5
            
        if abs(direction) != 0 or angle != 0:
            pauk.set_next_move(direction, angle, 1.5)
