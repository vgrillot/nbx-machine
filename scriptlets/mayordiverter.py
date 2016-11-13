# mayorDiverter Scriptlet for Nightmare

from mpf.core.scriptlet import Scriptlet
from mpf.core.delays import DelayManager
#from mpf.core.timing import Timer

import random
import math

class mayorDiverter(Scriptlet):

    def on_load(self):
        self.delay = DelayManager(self.machine.delayRegistry)
        self.enabled = 1
        self.happy = 1
        self.machine.switch_controller.add_switch_handler('rrampgate_sw', self.open_diverter)
        
        self.machine.events.add_handler('mayor_disable_diverter', self.disable_diverter)
        self.machine.events.add_handler('mayor_enable_diverter', self.enable_diverter)
        self.machine.events.add_handler('mayor_spin_1', self.set_sad)
        self.machine.events.add_handler('mayor_spin_2', self.set_happy)
        self.set_happy()

    def enable_diverter(self):
        self.enabled = 1

    def disable_diverter(self):
        self.enabled = 0

    def set_happy(self):
        self.happy = 1
        self.log.info('Mayor sad')  
        self.machine.servos.servo_mayor.go_to_position(0)

    def set_sad(self):
        self.happy = 0
        self.log.info('Mayor happy')            
        self.machine.servos.servo_mayor.go_to_position(1)

    def open_diverter(self):
        if self.enabled ==1 and self.happy == 1:
            if self.machine.game:
                self.machine.coils['mayordiverter'].enable()
            self.delay.add(name='mayor_close_diverter', ms=5000, callback=self.close_diverter)
            self.log.info("Activate - Mayor Diverter")

    def close_diverter(self):
        self.machine.coils['mayordiverter'].disable()
        self.log.info("Deactivate - Mayor Diverter")

    def disable(self):
        self.close_diverter()


