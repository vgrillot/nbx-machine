# Oogie Magnet Scriptlet for Nightmare

from mpf.core.scriptlet import Scriptlet
from mpf.core.delays import DelayManager


class OogieMagnet(Scriptlet):

    def on_load(self):
        self.firedattick = 0
        self.delay = DelayManager(self.machine.delayRegistry)
        self.machine.switch_controller.add_switch_handler(
            'oogiebanktrap_opt', self.activate)
        self.machine.switch_controller.add_switch_handler(
            'subwayoogie_sw', self.deactivate)

    def enable(self):
        self.machine.switch_controller.add_switch_handler(
            'oogiebanktrap_opt', self.activate)
        self.machine.switch_controller.add_switch_handler(
            'subwayoogie_sw', self.deactivate)

    def disable(self):
        self.deactivate()
        self.machine.switch_controller.remove_switch_handler(
            'oogiebanktrap_opt', self.activate)
        self.machine.switch_controller.remove_switch_handler(
            'subwayoogie_sw', self.deactivate)

    def activate(self):
        self.currenttick = self.machine.clock.get_time()  #returns a float in seconds  eg 32.124366
        self.log.info("Oogie Magnet Opto - now: " + str(self.currenttick) +" prev "+ str(self.firedattick))
        if self.currenttick - self.firedattick > 3: 
            self.machine.coils['oogiemagnet'].enable()
            #don't stay on more than 2 seconds
            self.delay.add(name='disable_oogie_magnet', ms=2000, callback=self.deactivate)
            self.firedattick = self.currenttick
            self.log.info("Oogie Magnet ON - max 2s - tick: " + str(self.firedattick))
        else:
            self.log.info("Oogie Magnet - pulse for 24ms")        
            self.machine.coils['oogiemagnet'].pulse(24)

    def deactivate(self):
        self.log.info( "Oogie Magnet OFF" )
        self.machine.coils['oogiemagnet'].disable()
        
