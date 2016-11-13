# gicomm Scriptlet for Nightmare

from mpf.core.scriptlet import Scriptlet
#from mpf.core.timing import Timer
from mpf.core.rgb_color import RGBColor
from mpf.core.delays import DelayManager
import random
import math

class Gicomm(Scriptlet):

    def on_load(self):
        self.command = 255
        self.r = random.randint(50,150)
        self.g = random.randint(50,150)
        self.b = random.randint(50,150)

        self.pr = random.randint(50,150)
        self.pg = random.randint(50,150)
        self.pb = random.randint(50,150)
        
        self.rd = random.randint(-1,1)*random.randint(0,4)
        self.gd = random.randint(-1,1)*random.randint(0,4)
        self.bd = random.randint(-1,1)*random.randint(0,4)
        self.delay = DelayManager(self.machine.delayRegistry)

        self.machine.switch_controller.add_switch_handler(
            'doctor_sw', self.switchmode2)
        self.machine.switch_controller.add_switch_handler(
            'mystery_sw', self.switchmodeR)

        self.delay.add(name='change_gi_lights', ms=2000, callback=self.timetochange)
        self.machine.events.add_handler('set_gi_x_ready', self.dofast_x_ready)
        self.machine.events.add_handler('set_gi_2x', self.dofast_2x)
        self.machine.events.add_handler('set_gi_3x', self.dofast_3x)
        self.machine.events.add_handler('set_gi_col', self.set_col)
        self.machine.events.add_handler('set_gi_col_pulse', self.set_col_pulse)        
        

        self.machine.events.add_handler('gi_random', self.switchmode2)

    def switchmodeR(self, **kwargs):
        self.command = 253

    def switchmode2(self, **kwargs):
        self.log.info('GI - set random colour')
        self.command=255
        self.r = random.randint(0,20)*10
        self.g = random.randint(10,20)*10
        self.b = random.randint(0,20)*10
        if (random.randint(0,100) > 90):
            self.rd = random.randint(-1,1)*random.randint(2,6)
        if (random.randint(0,100) > 90):
            self.gd = random.randint(-1,1)*random.randint(2,6)
        if (random.randint(0,100) > 90):
            self.bd = random.randint(-1,1)*random.randint(2,6)

    def timetochange(self): 
        if self.command == 255:
            if self.r < 0 or self.r > 255:
                self.r = self.r - self.rd
                self.rd = -self.rd
            if (random.randint(0,100) > 95):
                self.rd = random.randint(-1,1)*random.randint(1,4)
            self.g = self.g + self.gd
            if self.g < 0 or self.g > 255:
                self.g = self.g - self.gd
                self.gd = -self.gd
            if (random.randint(0,100) > 95):
                self.gd = random.randint(-1,1)*random.randint(1,4)
            self.b = self.b + self.bd
            if self.b < 0 or self.b > 255:
                self.b = self.b - self.bd
                self.bd = -self.bd
            if (random.randint(0,100) > 95):
                self.bd = random.randint(-1,1)*random.randint(1,4)
            self.set_all_LED(self.r, self.g, self.b)

        if self.command == 253:
            i = random.randint(0,22)
            r = random.randint(0,20)*10
            g = random.randint(0,20)*10
            b = random.randint(0,20)*10
            self.set_single_LED(i, r, g, b)
        #replace 2000 with 50
        self.delay.add(name='change_gi_lights', ms=2000, callback=self.timetochange)
        
        

    def set_col(self, red, green, blue):
        self.set_all_LED(red, green, blue)

    def set_col_pulse(self, red, green, blue):
        self.set_all_LED_pulse(red, green, blue)

    def dofast_x_ready(self):
        self.set_all_LED(0, 180, 0)

    def dofast_2x(self):
        self.set_all_LED(0, 0, 180)

    def dofast_3x(self):
        self.set_all_LED(180, 0, 180)


    def set_all_LED(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        self.rd = 0
        self.gd = 0
        self.bd = 0
        for i in range(1, 24):
           lname = 'grb_gi_' + str(i)
           self.machine.leds[lname ].color([g,r,b], 0, 1, 1)

    def set_all_LED_pulse(self, r, g, b):
        self.pr = r
        self.pg = g
        self.pb = b
        for i in range(1, 24):
           lname = 'grb_gi_' + str(i)
           self.machine.leds[lname ].color([g,r,b], 0, 1, 1)

    def set_single_LED(self,i, r, g, b):
        lname = 'grb_gi_' + str(i+1)
        self.machine.leds[lname ].color([g,r,b], 0, 1, 1)
    
