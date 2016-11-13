from mpf.core.mode import Mode
#from mpf.core.delays import DelayManager

# Extra_Ball

class Extra_Ball(Mode):

    def mode_start(self, **kwargs):
        self.log.info('EB - start')    	    
        self.player.extra_ball_collected +=1
        self.machine.events.post('EB_start_1')
        self.delay.add(name='EB_clear', ms=6500, callback=self.end_mode)
        self.delay.add(name='EB_sfx', ms=2000, callback=self.callout)        
        self.machine.events.post('char_pause_and_hide')
        self.machine.events.post('doors_pause_and_hide')
        self.machine.events.post('OB_pause_and_hide')
        self.player.extra_balls += 1

        
    def callout(self):
        self.log.info('EB - say something')     
        self.machine.events.post("EB_start_2")
        

    def end_mode(self):
        self.log.info('EB - end')     
        self.machine.events.post("char_resume_and_show")
        self.machine.events.post("doors_resume_and_show")
        self.machine.events.post("OB_resume_and_show")
        self.stop()

        
    def mode_stop(self, **kwargs):
        self.log.info('EB mode_stop')


