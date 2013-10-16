# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import pyqtSlot, pyqtSignal
from protocol.protocol import Protocol
import json

class ServoControl(QtGui.QFrame):
    value_changed_signal = pyqtSignal(int, float)
    
    def __init__(self, name, value, index, parent=None):
        QtGui.QFrame.__init__(self, parent)
        uic.loadUi("ServoControl.ui", self)
        
        self.index = index
        self.label.setText(name)
        self.slider.setValue(self.slider.minimum() + (self.slider.maximum() - self.slider.minimum()) * value)
        self.spin_box.setValue(value)

    @pyqtSlot(int)
    def on_slider_valueChanged(self, value):
        old_state = self.spin_box.blockSignals(True)
        self.spin_box.setValue(value / float(self.slider.maximum()))
        self.spin_box.blockSignals(old_state)
        self.value_changed_signal.emit(self.index, self.spin_box.value())
        
    @pyqtSlot(float)
    def on_spin_box_valueChanged(self, value):
        old_state = self.slider.blockSignals(True)
        self.slider.setValue(self.slider.maximum() * value)
        self.slider.blockSignals(old_state)

        self.value_changed_signal.emit(self.index, self.spin_box.value())
    
    def get_value(self):
        return self.spin_box.value()
    
    def set_value(self, value):
        self.spin_box.setValue(value)
        
    def get_index(self):
        return self.index
        
class RangeControl(QtGui.QFrame):
    value_changed_signal = pyqtSignal(int, float, float)
    
    def __init__(self, text, index,  min, max, parent=None):
        QtGui.QFrame.__init__(self, parent)
        uic.loadUi("RangeControl.ui", self)
        
        self.index = index
        self.label.setText(text)
        self.spin_box_min.setValue(min)
        self.spin_box_max.setValue(max)

    @pyqtSlot(float)
    def on_spin_box_min_valueChanged(self, value):
        self.value_changed_signal.emit(self.index, self.spin_box_min.value(), self.spin_box_max.value())
        
    @pyqtSlot(float)
    def on_spin_box_max_valueChanged(self, value):
        self.value_changed_signal.emit(self.index, self.spin_box_min.value(), self.spin_box_max.value())
        
    def get_value(self):
        return (float(self.spin_box_min.value()), float(self.spin_box_max.value()))
    
    def set_value(self, min, max):
        self.spin_box_min.setValue(float(min))
        self.spin_box_max.setValue(float(max))

    def get_index(self):
        return self.index

class GroupFrame(QtGui.QFrame):
    servo_value_changed_signal = pyqtSignal(int, int, float)
    range_value_changed_signal = pyqtSignal(int, int, float, float)

    resolution_changed_signal = pyqtSignal(int, int)
    period_changed_signal = pyqtSignal(int, float)
    setup_signal = pyqtSignal(int)
    load_signal = pyqtSignal(int)
    
    def __init__(self, parent=None):
        QtGui.QGroupBox.__init__(self, parent)
        uic.loadUi("GroupFrame.ui", self)

    def load_config(self, config, index):
        self.servos = []
        self.ranges = []
       
        self.index = index

        self.spin_box_resolution.setValue(config["resolution"])
        self.spin_box_period.setValue(config["period"])

        for index, conf in enumerate(config["controlls"]):
            servo_controll = ServoControl(u"серво_{0}".format(index), conf["value"], index)
            servo_controll.value_changed_signal.connect(self.onServo_value_changed)
            self.vertical_layout_servos.addWidget(servo_controll)
            
            range_controll = RangeControl(u"предел_{0}".format(index), index, conf["min"], conf["max"])
            range_controll.value_changed_signal.connect(self.onRange_value_changed)
            self.vertical_layout_ranges.addWidget(range_controll)

            self.servos.append(servo_controll)
            self.ranges.append(range_controll)

    def get_servos(self):
        return sefl.servos

    def get_ranges(self):
        return self.ranges
        
    def get_ranges_data(self):
        return (float(self.spin_box_period.value()),
                int(self.spin_box_resolution.value()),
                [v.get_value() for v in self.ranges])

    def set_ranges_data(self, data):
        self.spin_box_period.setValue(data[1])
        self.spin_box_resolution.setValue(data[2])
        for range_value, control in zip(data[3], self.ranges):
            control.set_value(range_value[0], range_value[1])
                
    def set_servos_data(self, data):
        for index, value in enumerate(data):
            self.servos[index].set_value(value)
    
    def get_servos_data(self):
        return [v.get_value() for v in self.servos]

    def get_index(self):
        return self.index
    
    def onServo_value_changed(self, servo_id, value):
        self.servo_value_changed_signal.emit(self.index, servo_id, value)

    def onRange_value_changed(self, servo_id, min, max):
        self.range_value_changed_signal.emit(self.index, servo_id, min, max)
        
    @pyqtSlot(int)
    def on_spin_box_resolution_valueChanged(self, resolution):
        self.resolution_changed_signal.emit(self.index, resolution)

    @pyqtSlot(float)
    def on_spin_box_period_valueChanged(self, period):
        self.period_changed_signal.emit(self.index, period)

    def on_push_button_set_clicked(self):
        self.setup_signal.emit(self.index)
    
    def on_push_button_load_clicked(self):
        self.load_signal.emit(self.index)


if __name__ == '__main__':
    import sys

    from PyQt4 import QtGui, uic, QtCore
    from mainwindow import MainWindow
    import json

    app = QtGui.QApplication(sys.argv)
    
    config = json.loads(open("config.json", "rb").read())
    
    widget = GroupFrame()
    widget.load_config(config["groups"][0])
    widget.show()
    widget.get_ranges_data()
    
    sys.exit(app.exec_())  
