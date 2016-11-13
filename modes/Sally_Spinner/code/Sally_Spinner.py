from mpf.core.mode import Mode

class Sally_Spinner(Mode):

# runs on MPF boot when the mode is read in and set up.
    def mode_init(self):
        self.log.info('Sally_Spinner mode_init')

    def mode_start(self, **kwargs):
        if self.player.sally_spinner_started == 0:
            self.player.sally_spinner_started = 1 
            self.player.sally_spins = 0
            self.player.sally_spins_soups = 1
            self.player.sally_spins_qualify = 1
        self.player.sally_spinner_value = 1
        self.spinsforsoup = 50 
        self.spinsforqualify = 20
        self.stopped = 1
        self.log.info( 'Sally_spinner mode_start')
        self.add_mode_event_handler('sw_sally', self.spin)
        #get notified when spinner stops spinning
        self.machine.switch_controller.add_switch_handler('spinner_sw', self.spinner_stopped, state=0, ms=250)

        
    def spinner_stopped(self, **kwargs):
        self.log.info( 'Sally_spinner stopped')
        if self.machine.game:  # in case this happens after the last ball drained and game ended
            if self.machine.game.player:  #in case this happened after the ball drained
                self.machine.events.post('spinner_stopped', value=self.player.sally_spins)
                self.stopped = 1
                

    def spin(self, **kwargs):
        self.log.info( 'Sally_spinner spin' )
        #don't count them if in soup hurry up 
        if self.player.soup_hurry_state == 0:
            self.player.sally_spins += 1*self.player.sally_spinner_value*self.player.multiplier_shot_value_list[1] 
            if self.player.sally_spins >= (self.spinsforsoup*self.player.sally_spins_soups):
                self.player.sally_spins_soups += 1
                self.machine.events.post('start_soup_hurryup')
            if self.player.sally_spins >= (self.spinsforqualify*self.player.sally_spins_qualify):
                self.player.sally_spins_qualify += 1
                self.machine.events.post('sally_spin_qualify')   
        if self.stopped == 1:
            self.stopped = 0
            if (self.player.char_state == 0 and self.player.Doors_state == 0):
                self.machine.events.post('sw_sally_start')                   



    def mode_stop(self, **kwargs):
        self.log.info( 'Sally_spinner mode_stop')
        self.machine.switch_controller.remove_switch_handler('spinner_sw', self.spinner_stopped, state=0, ms=100)
