# zero Diverter Scriptlet for Nightmare

from mpf.core.scriptlet import Scriptlet
from mpf.core.delays import DelayManager
import random
import math

class ZeroDiverter(Scriptlet):

    def on_load(self):
        self.delay = DelayManager(self.machine.delayRegistry)
        self.enabled = 0
        self.machine.switch_controller.add_switch_handler(
            'rampreturnl_sw', self.open_diverter)
        self.machine.events.add_handler('zero_disable_diverter', self.disable_diverter)
        self.machine.events.add_handler('zero_enable_diverter', self.enable_diverter)

    def enable_diverter(self, **kwargs):
        self.enabled = 1

    def disable_diverter(self, **kwargs):
        self.enabled = 0

    def open_diverter(self):
        if self.enabled == 1:
            self.machine.coils['zerodiverter'].enable()
            self.delay.add(name='zero_close_diverter', ms=3000, callback=self.close_diverter)
            self.log.info("Activate - Zero Diverter")
            self.enabled = 0  #one time use, needs to be reset from zero_enable_diverter event

    def close_diverter(self):
        self.machine.coils['zerodiverter'].disable()

    def disable(self):
        self.close_diverter()

