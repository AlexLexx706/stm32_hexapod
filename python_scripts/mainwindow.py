# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import pyqtSlot
from protocol.protocol import Protocol
import json
import frames

class MainWindow(QtGui.QMainWindow):
    CONCRETE = 0
    BRICK = 1
    
    def __init__(self, parent=None):
        super(QtGui.QWidget, self).__init__(parent)
        uic.loadUi("main_window.ui", self)
        self.protocol = Protocol(port_name="com6", baudrate=115200)

        self.config = json.loads(open("config.json", "rb").read())

        self.played = False
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.setInterval(2)
        self.timer.timeout.connect(self.onTimeout)
        self.settings = QtCore.QSettings("AlexLexx", "servo_animator")

        self.spinBox_max_time.setValue(10.0);
        self.doubleSpinBox_speed.setValue(1.0);
        self.checkBox_load_last_anamation.setChecked(self.settings.value("load_last_anamation", True).toPyObject())
        self.checkBox_enable_servo.setChecked(self.settings.value("enable_servo", False).toPyObject())
        self.checkBox_enable_auto_save.setChecked(self.settings.value("enable_auto_save", False).toPyObject())
        
        #создадим сервы
        self.groups = []
        for index, conf in enumerate(self.config["groups"]):
            frame = frames.GroupFrame(self)
            frame.load_config(conf, index)
            self.tab.addTab(frame, conf["name"])

            frame.servo_value_changed_signal.connect(self.on_servo_value_changed_signal)
            frame.range_value_changed_signal.connect(self.on_range_value_changed_signal)
            frame.resolution_changed_signal.connect(self.on_resolution_changed_signal)
            frame.period_changed_signal.connect(self.on_period_changed_signal)
            frame.setup_signal.connect(self.on_setup_ranges)
            frame.load_signal.connect(self.on_load_ranges)
            self.groups.append(frame)

        self.time_window_pos = 0.0
        self.time_window_size = self.spinBox_max_time.value()

        self.listWidget.addAction(self.action_remove)
        self.listWidget.addAction(self.action_create)
        self.listWidget.addAction(self.action_copy)
        self.listWidget.addAction(self.action_insert)

        self.copied_data = None

        if self.checkBox_load_last_anamation.isChecked():
            
            file_name = self.settings.value("last_animation_file", "").toPyObject()

            if file_name != "":
                self.load_from_file(file_name)
        
    def on_servo_value_changed_signal(self, group_id, servo_id, value):
        if self.checkBox_enable_servo.isChecked():
            self.protocol.move_servo(group_id, servo_id, value)

    def on_setup_ranges(self, group_id):
        if self.checkBox_enable_servo.isChecked():
            data = self.groups[group_id].get_ranges_data()
            self.protocol.set_group_params(group_id, data[0], data[1], data[2])
    
    def on_load_ranges(self, group_id):
        if self.checkBox_enable_servo.isChecked():
            self.groups[group_id].set_ranges_data(self.protocol.get_group_params(group_id))

    def on_range_value_changed_signal(self, group_id,  servo_id, min, max):
        self.config["groups"][group_id]["controlls"][servo_id]["min"] = min
        self.config["groups"][group_id]["controlls"][servo_id]["max"] = max
        
        if self.checkBox_enable_config_modification.isChecked():
            open("config_new.json", "wb").write(json.dumps(self.config, indent=1))
    
    def on_resolution_changed_signal(self, group_id, resolution):
        self.config["groups"][group_id]["resolution"] = resolution

        if self.checkBox_enable_config_modification.isChecked():
            open("config_new.json", "wb").write(json.dumps(self.config, indent=1))
        
    def on_period_changed_signal(self, group_id, period):
        self.config["groups"][group_id]["period"] = period

        if self.checkBox_enable_config_modification.isChecked():
            open("config_new.json", "wb").write(json.dumps(self.config, indent=1))
    
    @pyqtSlot("int")
    def on_checkBox_load_last_anamation_stateChanged(self, state):
        self.settings.setValue("load_last_anamation", state)
        
    @pyqtSlot("int")
    def on_checkBox_enable_servo_stateChanged(self, state):
        self.settings.setValue("enable_servo", state)
        
    @pyqtSlot("int")
    def on_checkBox_enable_auto_save_stateChanged(self, state):
        self.settings.setValue("enable_auto_save", state)
        
    @pyqtSlot("bool")
    def on_action_save_as_triggered(self, state):
        file_name = QtGui.QFileDialog.getSaveFileName(None, u"Сохранить в файл", "anim.json", "Animation(*.json)")

        if file_name != "":
            self.save_to_file(file_name)
    
    @pyqtSlot("bool")
    def on_action_save_triggered(self, state):
        last_file = self.settings.value("last_animation_file", "").toPyObject()

        if last_file != "":
            self.save_to_file(last_file)
        else:
            self.on_action_save_as_triggered(True)

    @pyqtSlot("bool")
    def on_action_load_triggered(self, state):
        fileName = QtGui.QFileDialog.getOpenFileName(None, u"открыть файл", "anim.json", "Animation(*.json)")

        if fileName != "":
            self.load_from_file(fileName)

    @pyqtSlot()
    def onTimeout(self):
        self.set_cur_time((self.spinBox_cur_time.value() + (self.timer.interval() / 1000.) * self.doubleSpinBox_speed.value()))


    @pyqtSlot("bool")
    def on_action_copy_triggered(self, state):
        self.copied_data = self.get_data_by_time(self.get_cur_time())

    @pyqtSlot("bool")
    def on_action_insert_triggered(self, state):
        if self.copied_data is not None:
            self.create_frame(self.get_cur_time(), self.copied_data)

            if self.checkBox_enable_auto_save.isChecked():
                self.on_action_save_triggered(True)
   
    @pyqtSlot('double')
    def on_doubleSpinBox_speed_valueChanged(self, value):
        self.settings.setValue("animation_speed", value)
        
        if self.checkBox_enable_auto_save.isChecked():
            self.on_action_save_triggered(True)
            
    @pyqtSlot("bool")
    def on_action_create_triggered(self, state):
        #поверим сеществования фрейма в данном времени
        self.create_frame(self.get_cur_time(), self.get_cur_data())

        if self.checkBox_enable_auto_save.isChecked():
            self.on_action_save_triggered(True)
            

    @pyqtSlot("bool")
    def on_action_remove_triggered(self, state):
        row = self.listWidget.currentRow()
        if row != -1:
            self.listWidget.takeItem(row)

            if self.checkBox_enable_auto_save.isChecked():
                self.on_action_save_triggered(True)

    @pyqtSlot('double')
    def on_spinBox_cur_time_valueChanged(self, time):
        data = self.get_data_by_time(time)

        if data is not None:
            for index, values in enumerate(data):
                self.groups[index].set_servos_data(values)

        
        if time >= self.time_window_pos and time < self.time_window_pos + self.time_window_size:
            old_state = self.horizontalSlider_cur_time.blockSignals(True)
            self.horizontalSlider_cur_time.setValue((time - self.time_window_pos) /
                self.time_window_size * self.horizontalSlider_cur_time.maximum())
            self.horizontalSlider_cur_time.blockSignals(old_state)
        

    @pyqtSlot('double')
    def on_spinBox_max_time_valueChanged(self, value):
        print "on_spinBox_max_time_valueChanged(value:{0})".format(value)
        if value < self.get_max_animation_time():
            value = self.get_max_animation_time()
            self.spinBox_max_time.setValue(value)
        
        self.spinBox_cur_time.setMaximum(value)
        self.time_window_size = value

        if self.checkBox_enable_auto_save.isChecked():
            self.on_action_save_triggered(True)
        
        
    
    @pyqtSlot('int')
    def on_listWidget_currentRowChanged(self, row):
        if row != -1:
            item = self.listWidget.item(row)

            time = item.data(QtCore.Qt.UserRole).toDouble()[0]
            data = item.data(QtCore.Qt.UserRole + 1).toPyObject()
            self.set_cur_time(time)
            
            for index, values in enumerate(data):
                self.groups[index].set_servos_data(values)

    @pyqtSlot()
    def on_pushButton_start_stop_clicked(self):
        if not self.played:
            self.groupBox_settings.setEnabled(False)
            self.frame_time_settings.setEnabled(False)
            self.pushButton_start_stop.setText(u"Стоп")
            self.played = True
            self.timer.start()
        else:
            self.played = False
            self.groupBox_settings.setEnabled(True)
            self.frame_time_settings.setEnabled(True)
            self.pushButton_start_stop.setText(u"Пуск")
            self.timer.stop()
    
    @pyqtSlot('int')
    def on_horizontalSlider_cur_time_valueChanged(self, value):
        time = (value / float(self.horizontalSlider_cur_time.maximum())) * self.time_window_size + self.time_window_pos
        self.spinBox_cur_time.setValue(time)


    def get_cur_time(self):
        return float(self.spinBox_cur_time.value())
    
    def set_cur_time(self, time):
        self.spinBox_cur_time.setValue(time % self.spinBox_max_time.value())

    def save_to_file(self, file_name):
        res = {"animation":[]}

        for i in range(self.listWidget.count()):
            time = self.listWidget.item(i).data(QtCore.Qt.UserRole).toDouble()[0]
            data = self.listWidget.item(i).data(QtCore.Qt.UserRole+1).toPyObject()
            res["animation"].append({"time":time, "data":data})
        
        res["speed"] = self.doubleSpinBox_speed.value()
        res["max_time"] = self.spinBox_max_time.value()
        
        open(file_name, "wb").write(json.dumps(res))
        self.settings.setValue("last_animation_file", file_name)
        
    def load_from_file(self, file_name):
        try:
            data = json.loads(open(file_name, "rb").read())
            print data

            state = self.doubleSpinBox_speed.blockSignals(True)
            self.doubleSpinBox_speed.setValue(data["speed"])
            self.doubleSpinBox_speed.blockSignals(state)
            
            #state = self.spinBox_max_time.blockSignals(True)
            self.spinBox_max_time.setValue(data["max_time"])
            #self.spinBox_max_time.blockSignals(state)

            self.listWidget.clear()
            
            for item in data["animation"]:
                self.create_frame(float(item["time"]), item["data"])

            self.settings.setValue("last_animation_file", file_name)
        except:
            pass
      
                   
    def get_max_animation_time(self):
        if self.listWidget.count():
            return self.listWidget.item(self.listWidget.count() - 1).text().toDouble()[0]
        return 0.0


    def get_frame_byte_time(self, time):
        for i in range(self.listWidget.count()):
            if  self.listWidget.item(i).data(QtCore.Qt.UserRole).toDouble()[0] == time:
                return self.listWidget.item(i)
        return None
    
    def get_cur_data(self):
        return [g.get_servos_data() for g in self.groups]

    def create_frame(self, time, data):
        item = self.get_frame_byte_time(time)

        if item is None:
            item = QtGui.QListWidgetItem()
            item.setText(QtCore.QString.number(time))
            
            item.setData(QtCore.Qt.UserRole, time)
            item.setData(QtCore.Qt.UserRole + 1, data)

            #вставим в нужное место
            for i in range(self.listWidget.count()):
                if time < self.listWidget.item(i).data(QtCore.Qt.UserRole).toDouble()[0]:
                    self.listWidget.insertItem(i, item)
                    break
            else:
                self.listWidget.addItem(item)
        else:
            item.setData(QtCore.Qt.UserRole + 1, data)
        self.listWidget.setCurrentItem(item)
    
    def get_data_by_time(self, time):
        #найдём граничные фреймы.
        borders = self.get_borders(time)

        #вычислим промежуточное значение углов
        if borders is not None:
            start_time, end_time = borders[0]

            if time == start_time:
                self.listWidget.setCurrentItem(borders[1][0])

            dt = float(time - start_time)/float(end_time - start_time)

            left_border = borders[1][0].data(QtCore.Qt.UserRole + 1).toPyObject()
            right_border = borders[1][1].data(QtCore.Qt.UserRole + 1).toPyObject()

                
            result = []
            for first_group, last_group in zip(left_border, right_border):
                group_data = [first + (last - first) * dt for first, last in zip(first_group, last_group)]
                result.append(group_data)
            return result

        return self.get_cur_data()
    
    def get_borders(self, time):
        for i in range(self.listWidget.count() - 1):
            cur_time = self.listWidget.item(i).data(QtCore.Qt.UserRole).toDouble()[0]
            next_time = self.listWidget.item(i + 1).data(QtCore.Qt.UserRole).toDouble()[0]

            if cur_time <= time and next_time > time:
                return ((cur_time, next_time), (self.listWidget.item(i), self.listWidget.item(i + 1)))
        return None
