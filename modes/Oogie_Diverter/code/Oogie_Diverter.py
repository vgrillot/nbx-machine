from mpf.core.mode import Mode

from mpf.core.delays import DelayManager

#Oogie_Diverter

class Oogie_Diverter(Mode):

    def mode_init(self):
        self.log.info('Oogie_Diverter mode_init')

        
    def mode_start(self, **kwargs):
        self.log.info('Oogie_Diverter mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.oogieloopmode = 0
        self.add_mode_event_handler('turn_on_oogie_loop_mode', self.loopmode_on)
        self.add_mode_event_handler('turn_off_oogie_loop_mode', self.loopmode_off)        
        self.add_mode_event_handler('sw_oogiecw', self.timedactivate_5s)
        self.add_mode_event_handler('sw_oogieccw', self.deactivate_5s)
        self.add_mode_event_handler('sneakinloop_opt_active', self.timedactivate_5s)
        self.add_mode_event_handler('sw_oogiedivertertrap', self.settle_time)        


    def settle_time(self, **kwargs):
        self.log.info("Oogie_Diverter - delay 1 second confirm ball trap")
        self.delay.add(name='ball_trap_delay', ms=1000, callback=self.timedactivate_2s)
        
        
    def loopmode_on(self, **kwargs):
        self.activate()
        self.oogieloopmode = 1

        
    def loopmode_off(self, **kwargs):
        self.oogieloopmode = 0
        self.machine.coils['oogieloopdiverter'].disable()        


    def activate(self, **kwargs):
        self.log.info('Oogie Diverter - activate')
        self.machine.coils['oogieloopdiverter'].enable()

        
    def timedactivate_2s(self, **kwargs):
        self.log.info('Oogie Diverter - 1s still trapped?')
        if self.machine.switch_controller.is_active('oogiedivertertrap_opt'):        
            self.machine.coils['oogieloopdiverter'].enable()
            self.delay.add(name='deactivate_2s_delay', ms=2000, callback=self.deactivate)

        
    def timedactivate_5s(self, **kwargs):
        self.log.info('Oogie Diverter - 5s enable')
        self.machine.coils['oogieloopdiverter'].enable()        
        if self.oogieloopmode == 0:
            self.delay.add(name='deactivate_5s_delay', ms=5000, callback=self.deactivate_5s)


    def deactivate_5s(self, **kwargs):        
        self.log.info('Oogie Diverter - deactivate after 5s')    
        #don't shut off if in loop mode
        if self.oogieloopmode == 0:
            self.machine.coils['oogieloopdiverter'].disable()
        

    def deactivate(self, **kwargs):        
        self.log.info('Oogie Diverter - deactivate')    
        self.machine.coils['oogieloopdiverter'].disable()

        
    def mode_stop(self, **kwargs):
        self.log.info('Oogie_Diverter mode_stop')
        self.delay.remove('deactivate_2s_delay')                
        self.delay.remove('deactivate_5s_delay')        
        self.deactivate()        
        
        

    


        
