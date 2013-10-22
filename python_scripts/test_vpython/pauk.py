# -*- coding: utf-8 -*-
from __future__ import division
from visual import * 
from my_frame import MyFrame
from leg import Leg


class Pauk:
    def __init__(self, cmd_queue=None):
        self.f_1 = MyFrame()
        
        self.f_2 = MyFrame(frame=self.f_1, pos=(0, -20, 0))
        self.f_2.rotate(axis=(0, 1, 0), angle=-pi / 4.0)
        
        self.base_box = box(frame=self.f_2,
                            size=(50, 40, 50),
                            color=(1, 0, 0))
        
        self.legs = []
        self.legs.append(Leg({"pos": (25, 20 - 13.7, 0), "axis": (-1, 0, 0), "frame": self.f_2}, cmd_queue, 0))
        self.legs.append(Leg({"pos": (-25, 20 - 13.7, 0), "axis": (1, 0, 0), "frame": self.f_2}, cmd_queue, 1))
        self.legs.append(Leg({"pos": (0, 20 - 13.7, 25.), "axis": (0, 0, -1), "frame": self.f_2}, cmd_queue, 2))
        self.legs.append(Leg({"pos": (0, 20 - 13.7, -25.), "axis": (0, 0, 1), "frame": self.f_2}, cmd_queue, 3))
        self.time = 0.0
        
        self.base_height = 120
        self.set_pos((0, self.base_height, 0))
        self.leg_len = 160

        for id, point in enumerate(self.get_init_legs_points()):
            self.legs[id].set_pos(point)

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
            pos = norm(pos) * self.leg_len + vector(0, -1, 0) * self.base_height
            print pos
            res.append(self.f_1.frame_to_world(pos))
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
                                 (time - animation[i-1][0]) / (animation[i][0] - animation[i - 1][0])
 
    def set_next_move(self, direction, angle, time):
        if not self.can_move:
            self.move_direction = self.f_1.frame_to_world(direction) - self.f_1.pos
            self.move_angle = angle
            self.move_time = time
            self.can_move = True
            
    def get_leg_by_obj(self, obj):
        for leg in self.legs:
            if leg.has_obj(obj):
                return leg
        return None
    
    def is_body(self, obj):
        return obj is self.base_box
        
    def get_pos(self):
        return self.f_1.pos
    
    def set_pos(self, pos):
        self.f_1.pos = pos

    #сделать шиг в заданном направление за заданное время.
    def update(self, rate=30.0):
        #разрешено движение.
        if self.can_move:
            #рассчёт анимации ног.
            if self.first_step:
                max_up = 20
                leg_move_time = self.move_time / 4.0
                dt = 0.0

                #инимация перемещения
                if self.move_angle == 0:
                    #определим последовательность ног
                    sequence = [0, 1, 2, 3]
                    dot_x = dot(self.f_1.axis, self.move_direction)
                    dot_z = dot(vector(-self.f_1.axis.z, self.f_1.axis.y, self.f_1.axis.x), self.move_direction)
                    
                    if dot_x >= 0.0 and dot_z >= 0.0:
                        sequence = [0, 1, 2, 3]
                    elif dot_x < 0.0 and dot_z >= 0.0:
                        sequence = [2, 3, 0, 1]
                    elif dot_x < 0.0 and dot_z < 0.0:
                        sequence = [1, 0, 3, 2]
                    else:
                        sequence = [3, 2, 1, 0]

                    #ходьба 1
                    if 1:
                        #создание набора анимации
                        for id in sequence:
                            leg = self.legs[id]
                            leg.anim = [(0.0 + dt, vector(leg.get_pos())),
                                        (leg_move_time / 2.0 + dt, (leg.get_pos() + self.move_direction / 2) + self.f_1.up * max_up),
                                        (leg_move_time + dt, (leg.get_pos() + self.move_direction))]
                            dt = dt + leg_move_time

                        self.body_pos_anim = [(0.0, vector(self.get_pos())),
                                              (self.move_time, self.get_pos() + self.move_direction)]

                        self.body_angle_anim = [(0.0, vector(self.angle, 0.0, 0.0))]
                        self.first_step = False
                        self.time = 0.0
                        self.max_time = self.move_time
                    #ходьба 2
                    else:
                        dt = self.move_time / 2
                        
                        leg = self.legs[sequence[0]]
                        leg.anim = [(0.0, vector(leg.get_pos())),
                                    (dt / 2, (leg.get_pos() + self.move_direction / 2 + self.f_1.up * max_up)),
                                    (dt, (leg.get_pos() + self.move_direction))]

                        leg = self.legs[sequence[1]]
                        leg.anim = [(0.0, vector(leg.get_pos())),
                                    (dt / 2, (leg.get_pos() + self.move_direction / 2 + self.f_1.up * max_up)),
                                    (dt, (leg.get_pos() + self.move_direction))]
                                    
                        leg = self.legs[sequence[2]]
                        leg.anim = [(dt, vector(leg.get_pos())),
                                    (dt + dt / 2.0, (leg.get_pos() + self.move_direction / 2 + self.f_1.up * max_up)),
                                    (dt + dt, (leg.get_pos() + self.move_direction))]

                        leg = self.legs[sequence[3]]
                        leg.anim = [(dt, vector(leg.get_pos())),
                                    (dt + dt / 2.0, (leg.get_pos() + self.move_direction / 2 + self.f_1.up * max_up)),
                                    (dt + dt, (leg.get_pos() + self.move_direction))]

                        dt = self.move_time / 4
                        dv = self.move_direction / 4
                        dv_left = rotate(dv, angle=pi / 2,   axis=self.f_1.up)
                        dv_rigth = rotate(dv, angle=-pi / 2, axis=self.f_1.up)
                        
                        self.body_pos_anim = [(dt * 0, self.get_pos()),
                                              (dt * 1, self.get_pos() + dv * 1 + dv_left + self.f_1.up * max_up),
                                              (dt * 2, self.get_pos() + dv * 2),
                                              (dt * 3, self.get_pos() + dv * 3 + dv_rigth + self.f_1.up * max_up),
                                              (dt * 4, self.get_pos() + dv * 4)]

                        self.body_angle_anim = [(0.0, vector(self.angle, 0.0, 0.0))]
                        self.first_step = False
                        self.time = 0.0
                        self.max_time = self.move_time
                        
                else:
                    #определим последовательность ног
                    for id in [0, 1, 2, 3]:
                        leg = self.legs[id]
                        new_pos_1 = self.get_pos() + rotate(vector=(leg.get_pos() - self.get_pos()),
                                                            angle=self.move_angle / 2,
                                                            axis=self.f_1.up)

                        new_pos_2 = self.get_pos() + rotate(vector=(leg.get_pos() - self.get_pos()),
                                                            angle=self.move_angle,
                                                            axis=self.f_1.up)

                        leg.anim = [(0.0 + dt, vector(leg.get_pos())),
                                    (leg_move_time / 2.0 + dt, new_pos_1 + self.f_1.up * max_up),
                                    (leg_move_time + dt, new_pos_2)]

                        dt = dt + leg_move_time

                    self.body_pos_anim = [(0.0, vector(self.get_pos()))]
                    self.body_angle_anim = [(0.0, vector(self.angle, 0.0, 0.0)),
                                            (self.move_time, vector(self.angle + self.move_angle, 0.0, 0.0))]
                    
                    self.first_step = False
                    self.time = 0.0
                    self.max_time = self.move_time

            self.time = self.time + 1.0 / rate
            
            #анимация тела
            self.set_pos(self.get_data_by_time(self.body_pos_anim, self.time))
            self.set_angle(self.get_data_by_time(self.body_angle_anim, self.time)[0])

            #анимация ног
            for leg in self.legs:
                leg.set_pos(self.get_data_by_time(leg.anim, self.time))

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

    
def togglecubecolor(evt):
    choice = t1.GetSelection()
    print choice


def get_mouse_pos():
    choice = t1.GetSelection()

    #0 - плоскость камеры
    if choice == 0:
        return scene.mouse.pos
    #плоскость X
    elif choice == 1:
        return scene.mouse.project(normal=(1, 0, 0), point=(0, 0, 0))
    #плоскость Y
    elif choice == 2:
        return scene.mouse.project(normal=(0, 1, 0), point=(0, 0, 0))
    #плоскость Z
    return scene.mouse.project(normal=(0, 0, 1), point=(0, 0, 0))

if __name__ == '__main__':
    import wx
    import multiprocessing

    L = 320
    d = 20

    w = window(width=2 * (L + window.dwidth),
               height=L + window.dheight + window.menuheight,
               menus=True, title='Widgets')

    scene = display(window=w,
                    x=d,
                    y=d,
                    width= L - 2 * d,
                    height=L - 2 * d,
                    forward=-vector(0, 1, 2))

    p = w.panel

    t1 = wx.RadioBox(p,
                     pos=(d + L, d),
                     size=(150, L- 2 * d),
                     choices=[u'плоскость камеры',
                              u'плоскость X',
                              u'плоскость Y',
                              u'плоскость Z'],
                     style=wx.RA_SPECIFY_ROWS)
    
    t1.Bind(wx.EVT_RADIOBOX, togglecubecolor)



    #координаты
    x_arrow = arrow(pos=(0, 0, 0), axis=(1, 0, 0), length=100, shaftwidth=1, fixedwidth = True, color=color.red)
    x_arrow = arrow(pos=(0, 0, 0), axis=(0, 1, 0), length=100, shaftwidth=1, fixedwidth = True, color=color.green)
    x_arrow = arrow(pos=(0, 0, 0), axis=(0, 0, 1), length=100, shaftwidth=1, fixedwidth = True, color=color.blue)
    b = box(size=(1000, 1, 1000), pos=(0, -0.5, 0))
    
    #создадим процесс отсылки комманд.
    cmd_queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=servo_process,  args=(cmd_queue,))
    proc.start()
    
    #leg = Leg(cmd_queue, None, 0, 1)
    pauk = Pauk(cmd_queue)

    move_camera = False
    camera_pos = None
    offset = None
    
    scene.autoscale = 0
    key_masks = {}
    selected_obj = None
    selected_obj_color = None

    def mousedown(event):
        if not event.shift:
            global selected_obj
            global selected_obj_color
            global pauk
            global offset

            selected_obj = scene.mouse.pick
            
            if selected_obj is not None:
                selected_obj_color = selected_obj.color
                selected_obj.color = (1, 1, 1)

                leg = pauk.get_leg_by_obj(selected_obj)

                #выбор обьекта
                if leg is not None:
                    offset = leg.get_pos() - get_mouse_pos()
                elif pauk.is_body(selected_obj):
                    offset = pauk.get_pos() - get_mouse_pos()
        else:
            global move_camera
            global camera_pos

            move_camera = True
            camera_pos = event.pos

    def mouseup():
        global move_camera
        move_camera = False
        
        global selected_obj
        global selected_obj_color
        
        if selected_obj is not None:
            selected_obj.color = selected_obj_color
            selected_obj = None

    def mousemove(event):
        global move_camera
        global offset

        if selected_obj is not None:
            leg = pauk.get_leg_by_obj(selected_obj)
            
            if leg is not None:
                leg.set_pos(get_mouse_pos() + offset)
            elif pauk.is_body(selected_obj):
                legs_pos = [l.get_pos() for l in pauk.legs]
                pauk.set_pos(get_mouse_pos() + offset)
                
                for pos, l in zip(legs_pos, pauk.legs):
                    l.set_pos(pos)
                    
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
        
        if "w" in key_masks and key_masks["w"]:
            direction = direction + vector(0, 0, 120)

        if "s" in key_masks and key_masks["s"]:
            direction = direction + vector(0, 0, -120)

        if "a" in key_masks and key_masks["a"]:
            angle = angle + 0.5

        if "d" in key_masks and key_masks["d"]:
            angle = angle - 0.5
            
        if abs(direction) != 0 or angle != 0:
            pauk.set_next_move(direction, angle, 1)
