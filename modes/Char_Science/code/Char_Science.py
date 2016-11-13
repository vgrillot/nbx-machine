from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Character Mode - "The Scientific Method" Multiball
# 
# Brief Description
# Special multiball played instead of "Where's Jack?" 
# if all other character modes are completed before trying to start "Science's Jack?" for your first time. 
# The goal is to make randomly selected major shots, then get the ball into the graveyard for a jackpot.
#
# Scenario
# Jack is up in his tower trying to figure out what makes Christmas so special. 
# He needs to experiment with various things to discover the answers he seeks.
# 
# Details
# When this mode begins, the ball count is brought up to 2, the gravestone is reset, 
# and two major shots (excluding the graveyard) will be selected at random. 
# Add-a-Ball is disabled for this multiball. When you shoot a lit major shot, 
# it will be cleared. Once all major shots are cleared, the gravestone can be knocked down 
# and entering the Graveyard will award a jackpot. Attempting to shoot the graveyard without 
# a jackpot lit will reset the gravestone immediately. You can upgrade the
# jackpot into a super jackpot by spelling JACK entirely after the jackpot is lit 
# but before collecting it. Once a jackpot is collected, the ball count will increase by 1, 
# a 10 second ball saver will be activated, and the number of major shots you need to clear 
# for the next jackpot to light will also be one higher. You can get the ball count all
# the way up to 5, though the number of major shots to clear can go as high as 7. 
# Once no more balls are added no more ball saver time will be awarded. The mode is
# completed simply by being started.
# 
# Scoring
# Lit Major Shot                       200,000
# Jackpot                              10,000,000
# Next Jackpot Increase                1,000,000
# Super Jackpot                        25,000,000
# Next Super Increase                  5,000,000
# 
# Lighting
# The major shots flash yellow triangles. 
# When the jackpot is ready the graveyard shot will flash a yellow triangle and the 
# JACK lights will flash cyan. When you hit a JACK standup the light will go solid. 
# If all JACK lights are completed they will rapidly flash white for a moment and the 
# graveyard shot will flash white on both the triangle and circle.
# 
# Difficulty Adjustments
# Very Easy         1 Major Shot Initially to Light Jackpot, Maximum Ball Count of 5, Ball Saver 30 sec Initial, 15 sec Additional
# Easy              2 Major Shots Initially to Light Jackpot, Maximum Ball Count of 5, Ball Saver 30 sec Initial, 15 sec Additional
# Normal            2 Major Shots Initially to Light Jackpot, Maximum Ball Count of 5, Ball Saver 20 sec Initial, 10 sec Additional
# Hard              2 Major Shots Initially to Light Jackpot, Maximum Ball Count of 4, Ball Saver 15 sec Initial, 7 sec Additional
# Very Hard         3 Major Shots Initially to Light Jackpot, Maximum Ball Count of 4, Ball Saver 15 sec Initial, 7 sec Additional

class Char_Science(Mode):

    def mode_init(self):
        self.log.info('char_science mode_init')

    def mode_start(self, **kwargs):
        self.log.info('char_science mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.player.char_science_jackpots_made = 0
        self.player.char_science_jackpots_base = 5000000
        self.player.char_science_jackpots_inc = 2500000
        self.player.char_science_super_jackpots_made = 0
        self.player.char_science_super_jackpots_base = 20000000
        self.player.char_science_super_jackpots_inc = 10000000
        self.player.char_science_qualifier_value = 100000
        self.player.char_science_shot_index = [0,0,0,0,0,0,0,0,0,0]        
        self.player.char_science_shots_to_qualify = 2
        self.player.char_science_shots_qualified = 0
        self.player.char_science_jackpot_qualified = 0
        self.player.char_science_super_qualified = 0            
        self.player.char_science_score = 0
        self.player.char_science_state = 0            
        self.player.char_science_shotlist = [
            {"led":"rgb_mayor_arrow", "state":"off"}
            ,{"led":"rgb_lorbit_arrow", "state":"off"}
            ,{"led":"rgb_lramp_arrow", "state":"off"}
            ,{"led":"rgb_leftloop_arrow", "state":"off"}
            ,{"led":"rgb_oogie_cw_arrow", "state":"off"}
            ,{"led":"rgb_oogie_ccw_arrow", "state":"off"}
            ,{"led":"rgb_grave_arrow", "state":"off"}
            ,{"led":"rgb_rramp_arrow", "state":"off"}
            ,{"led":"rgb_rorbit_arrow", "state":"off"}
            ,{"led":"rgb_soup_arrow", "state":"off"}
            ]
        self.add_mode_event_handler("major_0_singlestep_unlit_hit", self.major_0)
        self.add_mode_event_handler("major_1_singlestep_unlit_hit", self.major_1)
        self.add_mode_event_handler("major_2_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_2a_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_3_singlestep_unlit_hit", self.major_3)
        self.add_mode_event_handler("major_4_singlestep_unlit_hit", self.major_4)
        self.add_mode_event_handler("major_5_singlestep_unlit_hit", self.major_5)
        self.add_mode_event_handler("major_5a_singlestep_unlit_hit", self.major_5)
        self.add_mode_event_handler("major_6_singlestep_unlit_hit", self.handle_gravestone)
        self.add_mode_event_handler("major_6a_singlestep_unlit_hit", self.handle_saucer)
        self.add_mode_event_handler("major_7_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_7a_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_8_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("major_8a_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("major_9_singlestep_unlit_hit", self.major_9)
        self.add_mode_event_handler('jack_standups_science_jack_lit_complete', self.handle_jack_complete)
        self.add_mode_event_handler('lrampstandup_left_science_jack_unlit_hit', self.handle_j_lit)
        self.add_mode_event_handler('lrampstandup_right_science_jack_unlit_hit', self.handle_a_lit)
        self.add_mode_event_handler('rrampstandup_left_science_jack_unlit_hit', self.handle_c_lit)
        self.add_mode_event_handler('rrampstandup_right_science_jack_unlit_hit', self.handle_k_lit)
        self.add_mode_event_handler('balldevice_trough_ball_enter', self.ball_drained)
        self.add_mode_event_handler('door_switch_to_narrow', self.hide_slide)    
        self.add_mode_event_handler('oogie_switch_to_narrow', self.hide_slide)
        self.add_mode_event_handler("char_resume_and_show", self.resume_and_show)
        self.add_mode_event_handler("char_pause_and_hide", self.remove_all_widgets)          
        self.char_science_start()
        self.msg = 1
        self.ticks_msg = self.ticks                    


    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_science_messages")  
        self.machine.events.post('char_science_hide_slide')
        

    def char_science_start(self):
        self.log.info("char_science_start")
        if (self.player.char_science_state == 0):
            self.player.char_science_state = 1        	
            self.ticks = 0 #this one counts up
            self.set_shots()
            self.player.char_science_score = 0            
            self.player.char_science_shots_qualified = 0
            self.player.char_science_jackpot_qualified = 0
            self.player.char_science_super_qualified = 0            
            self.machine.events.post("char_science_music_start")
            self.machine.events.post('disable_combos')
            self.add_a_ball()
            self.machine.events.post('enable_the_mb_ball_save')               
            self.delay.add(name="char_science_ticker", ms=500, callback=self.ticker)
            self.machine.events.post('show_science_msg_1')
            self.ticks_msg = self.ticks
            self.player.char_timer_ispaused = 0            
            self.delay.add(name="char_science_slide_delay", ms=5000, callback=self.hide_slide)
            self.machine.events.post("ob_pause_and_hide")
            self.machine.events.post("doors_pause_and_hide")
           

    def resume_and_show(self, **kwargs):   
        if (self.player.Doors_state == 0 and self.player.OB_Gate_current_mode_state == 0):
            if self.player.char_science_state > 0:
                self.machine.events.post("char_science_show_slide")            


    def hide_slide(self, **kwargs):   
        if (self.player.Doors_state != 0 or self.player.OB_Gate_current_mode_state != 0):
            self.machine.events.post("char_science_hide_slide")   
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         
            
           
    def ticker(self):
        self.log.info("char_science - 500ms ticks " +str(self.ticks))
        self.delay.add(name="char_science_ticker", ms=500, callback=self.ticker)
        if self.player.char_timer_ispaused == 0:
            self.ticks += 1;
            if self.ticks_msg-self.ticks < -3:
                self.msg += 1
                self.ticks_msg = self.ticks
                if self.msg > 4: 
                    self.msg = 1
                self.machine.events.post('show_science_msg_'+str(self.msg))


    def char_science_stop(self):
        if self.player.char_science_state == 1:
            self.machine.events.post('char_science_music_stop')
            self.machine.events.post('char_science_hide_slide')            
            self.log.info("char_science over")
            if self.player.char_science_shot_made > 0:
                self.machine.events.post('char_mode_stopped', char_state="complete", char_mode="Science")
                self.player.char_science_state = 2 #completed
            else:
                self.machine.events.post('char_mode_stopped', char_state="incomplete", char_mode="Science")
                self.player.char_science_state = 0 #ready to start again
            self.reset_shots()
            self.machine.events.post('enable_combos')
            self.machine.events.post('add_a_ball_stop')
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         


    def ball_drained(self, **kwargs):
        if self.player.char_science_state == 1:
            self.log.info("char_science - ball drained")
            self.log.info("char_science - balls in play "+str(self.machine.game.balls_in_play))
            if self.machine.game.balls_in_play <= 2:
                if self.player.ball_save_active == 0:
                    #there is only 1 ball on playfield, end multiball
                    self.log.info("char_science - Science's Jack MB over")
                    self.char_science_stop()
                else:
                    self.log.info( "char_science multiball - ball drained - but ball save is running" )
            else:
                self.log.info( "char_science multiball - ball drained - more than 2 BIP" )            
                

    def set_shots(self):
        for x in range(0, 10):
            self.player.char_science_shotlist[x]["state"] = "off"
            self.player.char_science_shot_index[x] = 0
        self.player.char_science_shots_to_qualify
        if self.player.char_science_jackpot_qualified == 1:
            self.player.char_science_shotlist[6]["state"] = "yellow"
            if self.player.char_science_super_qualified == 1:
                self.player.char_science_shotlist[6]["state"] = "white"
        shots_set = 0
        while (shots_set < self.player.char_science_shots_to_qualify):
            potential_shot = random.randint(0,9)
            self.log.info('char_science - trying - ' + str(potential_shot)) 
            if potential_shot != 6:
                if self.player.char_science_shot_index[potential_shot] != 1:
                    self.player.char_science_shot_index[potential_shot] = 1
                    self.player.char_science_shotlist[potential_shot]["state"] = "blue"                    
                    self.log.info('char_science - qualifier shot - ' + str(potential_shot)) 
                    shots_set += 1
        self.set_shot_lights()


    def set_shot_lights(self):
        for x in range(0, 10):
            state = self.player.char_science_shotlist[x]["state"]
            if state != 'off':
                led = self.player.char_science_shotlist[x]["led"]
                self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="char_science", action="add")

			
    def major_0(self, **kwargs):
        self.handle_shot(0)
    def major_1(self, **kwargs):
        self.handle_shot(1)
    def major_2(self, **kwargs):
        self.handle_shot(2)
    def major_3(self, **kwargs):
        self.handle_shot(3)
    def major_4(self, **kwargs):
        self.handle_shot(4)
    def major_5(self, **kwargs):
        self.handle_shot(5)
    def major_6(self, **kwargs):
        self.handle_shot(6)
    def major_7(self, **kwargs):
        self.handle_shot(7)
    def major_8(self, **kwargs):
        self.handle_shot(8)
    def major_9(self, **kwargs):
        self.handle_shot(9)

 
    def handle_j_lit(self, **kwargs):
        if self.player.char_science_state == 1:  
            if self.player.char_science_jackpot_qualified == 1:
                self.log.info('char_science - handle_j_lit')
                self.machine.events.post('say_Oww')


    def handle_a_lit(self, **kwargs):
        if self.player.char_science_state == 1:  
            if self.player.char_science_jackpot_qualified == 1:
                self.log.info('char_science - handle_a_lit')
                self.machine.events.post('say_Oww')


    def handle_c_lit(self, **kwargs):
        if self.player.char_science_state == 1:  
            if self.player.char_science_jackpot_qualified == 1:
                self.log.info('char_science - handle_c_lit')
                self.machine.events.post('say_Oww')


    def handle_k_lit(self, **kwargs):
        if self.player.char_science_state == 1:  
            if self.player.char_science_jackpot_qualified == 1:
                self.log.info('char_science - handle_k_lit')
                self.machine.events.post('say_Oww')

        
    def handle_jack_complete(self):
        if self.player.char_science_state == 1:  
            if self.player.char_science_jackpot_qualified == 1:
                self.player.char_science_super_qualified = 1
                self.log.info('char_science - super jackpot ready')


    def handle_shot(self, shot):
        self.log.info('char_science - handle_shot')    	
        if self.player.char_science_state == 1:
            self.score = 0
            state = self.player.char_science_shotlist[shot]["state"]
            #not lit, skip it
            if state != "off":
                self.log.info('char_science - qualifier hit')
                #qualifier
                self.player.char_science_shots_qualified += 1
                self.player.char_science_shotlist[shot]["state"] = "off"
                self.score = self.player.char_science_qualifier_value * self.player.char_science_shots_qualified 
                self.score *= self.player.multiplier_shot_value_list[shot] # 1X, 2X or 3X                 
                self.player.score += self.score
                self.player.char_science_score += self.score
                if self.player.char_science_shots_qualified == self.player.char_science_shots_to_qualify:
                    self.player.char_science_jackpot_qualified = 1
                    self.log.info('char_science - jackpot ready')
                self.set_shot_lights()
                
                
    def handle_gravestone(self, **kwargs):
        self.log.info('char_science - grave hit')
        if self.player.char_science_state == 1:
            if self.player.char_science_jackpot_qualified == 1:
                #keep it down, jackpot ready
                self.score = self.player.char_science_qualifier_value * self.player.char_science_shots_qualified 
                self.score *= self.player.multiplier_shot_value_list[6] # 1X, 2X or 3X                 
                self.player.score += self.score
                self.player.char_science_score += self.score
            else:
                #pop it back up            
                self.player.score += 10
                self.log.info('char_science - grave not ready 10 pts')
                        
            
    def handle_saucer(self, **kwargs):           
        self.log.info('char_science - saucer hit')    	 
        if self.player.char_science_state == 1:
            if self.player.char_science_jackpot_qualified != 1:
                #kick it out
                self.player.score += 1110
                self.log.info('char_science - saucer not ready 1110 pts')
            else:
                if self.player.char_science_super_qualified == 1:
                    #super jackpot
                    self.score = self.player.char_science_super_jackpots_base
                    self.score += self.player.char_science_super_jackpots_inc*self.player.char_science_super_jackpots_made
                    self.score *= self.player.multiplier_shot_value_list[6] # 1X, 2X or 3X 
                    self.player.score += self.score
                    self.player.char_science_score += self.score
                    self.player.char_science_super_jackpots_made += 1
                    self.log.info('char_science - super jackpot')
                    self.machine.events.post('char_science_sjackpot_hit')
                    self.machine.events.post('char_science_score_change')
                else:
                    #regular jackpot                	  	
                    self.score = self.player.char_science_jackpots_base
                    self.score += self.player.char_science_jackpots_inc*self.player.char_science_jackpots_made
                    self.score *= self.player.multiplier_shot_value_list[6] # 1X, 2X or 3X 
                    self.player.score += self.score
                    self.player.char_science_score += self.score
                    self.player.char_science_jackpots_made += 1
                    self.log.info('char_science - jackpot')
                    self.machine.events.post('char_science_jackpot_hit')
                    self.machine.events.post('char_science_score_change')
                self.player.char_science_shotlist[6]["state"] = "off"
                self.player.char_science_shots_qualified = 0
                self.player.char_science_shot_made += 1
                self.set_shot_lights()
                self.player.char_science_shots_to_qualify += 1
                if self.player.char_science_shots_to_qualify > 9:
                   self.player.char_science_shots_to_qualify = 9
                self.set_shots()
                self.add_a_ball()
                
                	  
    def add_a_ball(self):
        bip = self.machine.game.balls_in_play             
        if bip < 6:
            self.machine.game.balls_in_play = bip + 1
            self.machine.playfield.add_ball(1, player_controlled=False)


    def reset_shots(self):
        for x in range(0, 10):
            state = self.player.char_science_shotlist[x]["state"]
            if state != 'off':
                led = self.player.char_science_shotlist[x]["led"]
                self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="char_science", action="remove")
                self.player.char_science_shotlist[x]["state"] = "off"


    def mode_stop(self, **kwargs):
        self.log.info('char_science_mode_stop')
        self.char_science_stop()


        
