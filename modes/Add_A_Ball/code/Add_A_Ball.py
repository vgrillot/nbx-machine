from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Add-a-Ball is slightly different. 
# When in any multiball, the mystery target will be solid green. 
#
# Hit it once to make it start flashing, then again to clear it and light the
# graveyard shot with a green triangle. Hitting the graveyard now will start to 
# display the mystery award sequence, but a giant pinball will fall on the bag of toys,
# pushing the sleigh and Santa out of the display area and showing "Add-a-Ball" text. 
# Afterwards, the mystery shot no longer functions for the duration of the multiball.
# Also, if you start a multiball with the mystery award lit, the graveyard 
# shot immediately lights for an add-a-ball.

class Add_A_Ball(Mode):

    def mode_init(self):
        self.log.info('Add_A_Ball mode_init')


    def mode_start(self, **kwargs):
        self.log.info('Add_A_Ball mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.player.add_a_ball_state = 0
        self.lowend = 100
        self.add_a_ball_show_handles = [0] * 2
        self.add_mode_event_handler('sw_mystery', self.mystery_hit)
        self.add_mode_event_handler('sw_grave', self.gravestone_hit)        
        self.add_mode_event_handler('sw_saucer', self.jack_saucer_hit) 
        self.add_mode_event_handler('add_a_ball_start', self.reset) 
        self.do_setup()
        
        
    def do_setup(self, **kwargs):
        if self.player.mystery_state == 1:
            #mystery-grave was already lit, skip to state 3
            self.player.add_a_ball_state = 3
            self.light_grave()
        else:
            self.light_mystery()

            
    def reset(self, **kwargs):
        #if we got another MB started, relight mystery for add-a-ball, if we had already claimed it
        if self.player.add_a_ball_state == 4:
            self.player.add_a_ball_state = 0
            self.light_mystery()


    def light_mystery(self, **kwargs):
        if self.player.add_a_ball_state == 0:
            self.player.add_a_ball_state = 1
            self.log.info("Add_A_Ball - MB started")
            #turn the mystery target green
            led = "rgb_mystery_rect"
            script_name = "sc_green_solid"
            self.add_a_ball_show_handles[0] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)			


    def mystery_hit(self, **kwargs):
        self.log.info('Add_A_Ball - mystery hit')
        if self.player.add_a_ball_state == 1:
            self.machine.events.post('addaball_mystery1')        
            self.player.add_a_ball_state = 2
            self.log.info("Add_A_Ball - Mystery hit")
            if self.add_a_ball_show_handles[0] != 0:
                self.add_a_ball_show_handles[0].stop()
                self.add_a_ball_show_handles[0] = 0
            #turn the mystery target green flash
            led = "rgb_mystery_rect"
            script_name = "sc_green_flash"
            self.add_a_ball_show_handles[0] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=6.0, loops=3)						
        elif self.player.add_a_ball_state == 2:
            self.player.add_a_ball_state = 3
            self.log.info("Add_A_Ball - Mystery hit 2nd time")
            if self.add_a_ball_show_handles[0] != 0:
                self.add_a_ball_show_handles[0].stop()
                self.add_a_ball_show_handles[0] = 0
            self.light_grave()
            self.machine.events.post('addaball_mystery2')                    
        else:
            self.machine.events.post('addaball_mystery3')                
            self.lowend += 100

    def light_grave(self):          
        #light the grave target purple
        self.machine.events.post('arrow_change', led_num=6, script_name="purple", mode_name="add_a_ball", action="add")


    def gravestone_hit(self, **kwargs):
        if self.player.add_a_ball_state == 3:
            self.log.info('Add_A_Ball - gravestone hit')        
            self.award_ball()
        elif self.player.add_a_ball_state == 4:    
            if self.player.LSB_MB_running == 0:
                if self.lowend > 5000:
                    self.lowend = 5000
                self.pts = random.randint(self.lowend,5000) * 100
                self.pts *= self.player.multiplier_shot_value_list[6]                        
                self.player["score"] += self.pts
                self.player.jackpoints = self.pts
                self.machine.events.post('jack_random_points')
            #self.delay.add(name="delayed_saucer_eject", ms=2000, callback=self.eject_saucer_ball)

            
    def jack_saucer_hit(self, **kwargs):
        if self.player.add_a_ball_state == 3:
            self.log.info('Add_A_Ball - jack saucer hit')
            self.award_ball()                
            self.delay.add(name="delayed_saucer_eject", ms=3000, callback=self.eject_saucer_ball)
        elif self.player.add_a_ball_state == 4:
            if self.player.LSB_MB_running == 0:
                if self.lowend > 5000:
                    self.lowend = 5000
                self.pts = random.randint(self.lowend,5000) * 100
                self.pts *= self.player.multiplier_shot_value_list[6]                        
                self.player["score"] += self.pts
                self.player.jackpoints = self.pts
                self.machine.events.post('jack_random_points')
            self.delay.add(name="delayed_saucer_eject", ms=1000, callback=self.eject_saucer_ball)


    def eject_saucer_ball(self):
        self.machine.coils['jackkickout'].pulse()                


    def award_ball(self):
        self.player.add_a_ball_state = 4
        self.machine.events.post('arrow_change', led_num=6, script_name="purple", mode_name="add_a_ball", action="remove")        
        led = "rgb_grave_arrow"
        script_name = "sc_white_flash"
        self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=3)
        bip = self.machine.game.balls_in_play 
        if bip < 6:
            self.machine.game.balls_in_play = bip+1
            self.machine.playfield.add_ball(1, player_controlled=False)
            self.machine.events.post('show_addaball')            
            self.log.info("BIP="+str(self.machine.game.balls_in_play))
            self.log.info("BOP="+str(self.machine.playfield._balls))   
        else:
            self.log.info('Add_A_Ball - 6 balls in play, TODO pts?')


    def mode_stop(self, **kwargs):
        self.player.add_a_ball_state = 0
        self.log.info('Add_A_Ball mode_stop')
        self.machine.events.post('arrow_change', led_num=6, script_name="purple", mode_name="add_a_ball", action="remove")        
        if self.add_a_ball_show_handles[0] != 0:
            self.add_a_ball_show_handles[0].stop()
            self.add_a_ball_show_handles[0] = 0
