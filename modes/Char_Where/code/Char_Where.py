from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# disable mayor and zero diverters for this mode - ie always return Right Ramp to left flipper.

# Character Mode - "Where's Jack?" Multiball                                                                                                                           Page 15
# 
# Brief Description
# Simple 3-Ball multiball with a jackpot shot which needs to be relit once collected 
# and can be made super by completing other shots first.
# 
# Scenario
# Nobody in Halloween Town knows where Jack's gone off to, but then, 
# Jack's on his way back anyways so it's not a big deal.
# 
# Details
# Once started, the ball count is brought up to 3 and three of the major shots will light up, 
# one as a jackpot (always the right ramp), as well as two random shots as super qualifiers. 
# If you hit the two super qualifiers first, the jackpot shot will become a super jackpot, 
# but you must make it within 7 seconds or else it will time out, go back to a regular jackpot, 
# and two major shots will relight to qualify for a super. Once a jackpot or super jackpot is made, 
# the major shots will unlight and you must spell JACK to qualify another jackpot as well as the 
# super modifiers. The mode is completed simply by being started.
# 
# Scoring
# 1st Qualifying Shot                50,000
# 2nd Qualifying Shot                100,000
# 3rd Qualifying Shot                250,000
# Jackpot                            5,000,000
# Next Jackpot Increase              2,500,000
# Super Jackpot                      20,000,000
# Next Super Increase                10,000,000
# 
# Lighting
# The jackpot shot flashes yellow on the triangle only while the super qualifiers flash cyan 
# on their triangles. If you qualify a super, the jackpot will now flash white, both
# on the triangle and the circle. When the jackpot needs to be re-qualified, the JACK lights 
# will flash yellow and will go solid when one is hit. Once all are solid they will
# flash rapidly as the jackpot and super qualifier shots relight.
# 
# Difficulty Adjustments
# Very Easy    Only one shot to qualify super for 10 seconds, only need to hit one JACK standup to relight jackpots
# Easy         Two shots to qualify super for 10 seconds, only need to hit one JACK standup to relight jackpots
# Normal       Two shots to qualify super for 7 seconds, need to hit all four JACK standups to relight jackpots
# Hard         Three shots to qualify super for 7 seconds, need to hit all four JACK standups to relight jackpots
# Very Hard    Three shots to qualify super for 5 seconds, need to hit all four JACK standups to relight jackpots

class Char_Where(Mode):

    def mode_init(self):
        self.log.info('char_where mode_init')

    def mode_start(self, **kwargs):
        self.log.info('char_where mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.player.char_where_mayor_value = 50000
        self.player.char_where_basic_ramp_value = 10000
        self.player.char_where_jackpots_made = 0
        self.player.char_where_jackpot_base = 5000000
        self.player.char_where_jackpot_value = self.player.char_where_jackpot_base
        self.player.char_where_jackpot_jackinc = 100000
        self.player.char_where_jackpot_inc = 1000000        
        self.player.char_where_super_jackpots_made = 0
        self.player.char_where_super_jackpot_base = 20000000
        self.player.char_where_super_jackpot_value = self.player.char_where_super_jackpot_base
        self.player.char_where_super_jackpot_jackinc = 500000
        self.player.char_where_super_jackpot_inc = 5000000     
        self.player.char_where_jack_letter_value = 5000     
        self.player.char_where_jackpot_qualified = 0
        self.player.char_where_super_qualified = 0
        self.player.char_where_super_qualified_timeout = 7000
        self.player.char_where_score = 0
        self.player.char_where_jacks = 0
        self.player.char_where_state = 0            
        
        self.add_mode_event_handler("major_0_singlestep_unlit_hit", self.major_0)
        self.add_mode_event_handler("major_7_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_7a_singlestep_unlit_hit", self.major_7)
        
        self.add_mode_event_handler('jack_standups_wheres_jack_lit_complete', self.handle_jack_complete)
        self.add_mode_event_handler('lrampstandup_left_wheres_jack_unlit_hit', self.handle_j_lit)
        self.add_mode_event_handler('lrampstandup_right_wheres_jack_unlit_hit', self.handle_a_lit)
        self.add_mode_event_handler('rrampstandup_left_wheres_jack_unlit_hit', self.handle_c_lit)
        self.add_mode_event_handler('rrampstandup_right_wheres_jack_unlit_hit', self.handle_k_lit)
        
        self.add_mode_event_handler('balldevice_trough_ball_enter', self.ball_drained)
        self.add_mode_event_handler('door_switch_to_narrow', self.hide_slide)    
        self.add_mode_event_handler('oogie_switch_to_narrow', self.hide_slide)
        self.add_mode_event_handler("char_resume_and_show", self.resume_and_show)
        self.add_mode_event_handler("char_pause_and_hide", self.remove_all_widgets)          
        self.char_where_start()
        self.msg = 1
        self.ticks_msg = self.ticks                    


    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_where_messages")  
        self.machine.events.post('char_where_hide_slide')

        
    def char_where_start(self):
        self.log.info("char_where_start")
        if (self.player.char_where_state == 0):
            self.ticks = 0 #this one counts up
            self.player.char_where_shot_made = 0
            self.player.char_where_state = 1
            self.player.char_where_jacks = 0
            self.machine.events.post("char_where_music_start")
            self.machine.events.post('disable_combos')
            for x in range(0, 2):
                bip = self.machine.game.balls_in_play             
                if bip < 6:
                    self.machine.game.balls_in_play = bip+1
                    self.machine.playfield.add_ball(1, player_controlled=False)
                    self.log.info("BIP="+str(self.machine.game.balls_in_play))
                    self.log.info("BOP="+str(self.machine.playfield._balls))   
            self.machine.events.post('add_a_ball_start')
            self.machine.events.post('enable_the_mb_ball_save')   
            self.ticks_msg = self.ticks
            self.player.char_timer_ispaused = 0
            self.delay.add(name="char_where_slide_delay", ms=5000, callback=self.hide_slide)
            self.machine.events.post("ob_pause_and_hide")
            self.machine.events.post("doors_pause_and_hide")                        
            #set mayor arrow
            self.machine.events.post('arrow_change', led_num=0, script_name="blue", mode_name="char_Where", action="add")
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         
           

    def resume_and_show(self, **kwargs):   
        if (self.player.Doors_state == 0 and self.player.OB_Gate_current_mode_state == 0):
            if self.player.char_where_state > 0:
                self.machine.events.post("char_where_show_slide")            

           
    def hide_slide(self, **kwargs):   
        if (self.player.Doors_state != 0 or self.player.OB_Gate_current_mode_state != 0):
            self.remove_all_widgets()      
        self.delay.add(name="char_where_ticker", ms=500, callback=self.ticker)            
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         
        self.machine.events.post('show_where_msg_1')        

            
    def ticker(self):
        self.log.info("char_where - 500ms ticks " +str(self.ticks))
        self.delay.add(name="char_where_ticker", ms=500, callback=self.ticker)        
        if self.player.char_timer_ispaused == 0:
            self.ticks += 1;
            if self.ticks_msg-self.ticks < -3:
                self.msg += 1
                self.ticks_msg = self.ticks
                if self.msg > 4: 
                    self.msg = 1
                self.machine.events.post('show_where_msg_'+str(self.msg))


    def char_where_stop(self):
        if self.player.char_where_state == 1:
            self.log.info("char_where over")        
            self.machine.events.post('char_where_music_stop')
            self.machine.events.post('char_where_hide_slide')                        
            self.machine.events.post("stop_all_character_messages")
            self.machine.events.post('char_mode_stopped', char_state="complete", char_mode="Where")
            self.player.char_where_state = 2 #completed
            self.machine.events.post('char_jack_completed')                                            
            self.clear_shots()
            self.machine.events.post('enable_combos')
            self.machine.events.post('add_a_ball_stop')
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         


    def ball_drained(self, **kwargs):
        if self.player.char_where_state == 1:
            self.log.info("char_where - ball drained")
            self.log.info("char_where - balls in play "+str(self.machine.game.balls_in_play))
            if self.machine.game.balls_in_play <= 2:
                if self.player.ball_save_active == 0:
                    #there is only 1 ball on playfield, end multiball
                    self.log.info("char_where - Where's Jack MB over")
                    self.char_where_stop()
                else:
                    self.log.info( "char_where multiball - ball drained - but ball save is running" )
            else:
                self.log.info( "char_where multiball - ball drained - more than 2 BIP" )            
                            
 
    def handle_j_lit(self, **kwargs):
        self.log.info('char_where - handle_j_lit')
        if self.player.char_where_state == 1:        
            self.machine.events.post('say_jack_letter_hit')
            self.increase_jackpot()

            
    def handle_a_lit(self, **kwargs):
        self.log.info('char_where - handle_a_lit')
        if self.player.char_where_state == 1:        
            self.machine.events.post('say_jack_letter_hit')
            self.increase_jackpot()

            
    def handle_c_lit(self, **kwargs):
        self.log.info('char_where - handle_c_lit')
        if self.player.char_where_state == 1:        
            self.machine.events.post('say_jack_letter_hit')
            self.increase_jackpot()

            
    def handle_k_lit(self, **kwargs):
        self.log.info('char_where - handle_k_lit')
        if self.player.char_where_state == 1:        
            self.machine.events.post('say_jack_letter_hit')
            self.increase_jackpot()

            
    def increase_jackpot(self):
        self.player.char_where_jackpot_value += self.player.char_where_jackpot_jackinc
        self.player.score += self.player.char_where_jack_letter_value
        self.player.char_where_score += self.player.char_where_jack_letter_value
        
        
    def handle_jack_complete(self, **kwargs):
        if self.player.char_where_state == 1:  
            self.log.info('char_where - jack completed')            
            if (self.player.char_where_super_qualified == 1 or self.player.char_where_jackpot_qualified == 1):
                self.machine.events.post('char_where_jack_complete')                        	
                self.log.info('char_where - make it a super jackpot! for 7 seconds')        
                self.player.char_where_super_qualified = 1
                self.player.char_where_jackpot_qualified = 0
                #set ramp arrow
                self.machine.events.post('arrow_change', led_num=7, script_name="cyan", mode_name="char_Where", action="remove")            
                self.machine.events.post('arrow_change', led_num=7, script_name="red", mode_name="char_Where", action="add")
                self.delay.remove('char_where_super_qualified_timeout')
                self.delay.add(name="char_where_super_qualified_timeout", ms=self.player.char_where_super_qualified_timeout, callback=self.timeout_super)
            else:
                self.log.info('char_where - not qualified yet, inc super jackpot')                    
                self.player.char_where_super_jackpot_value += self.player.char_where_super_jackpot_jackinc
                self.machine.events.post('char_where_jack_complete2')
            self.player.score += self.player.char_where_jack_letter_value * 4
            self.player.char_where_score += self.player.char_where_jack_letter_value

                
    def timeout_super(self):
        self.log.info('char_where - super timed out')
        if self.player.char_where_super_qualified == 1:
            self.player.char_where_super_qualified = 0
            #remove super 
            self.machine.events.post('arrow_change', led_num=7, script_name="red", mode_name="char_Where", action="remove")
            #relight mayor
            self.machine.events.post('arrow_change', led_num=0, script_name='blue', mode_name="char_Where", action="add")                        

            
    def major_0(self, **kwargs):
        self.log.info('char_where - mayor hit')
        if self.player.char_where_state == 1:
            if self.player.char_where_jackpot_qualified == 0:
                if self.player.char_where_super_qualified == 0:
                    self.log.info('char_where - enable ramp jackpot')                
                    #qualify ramp jackpot                            
                    self.score = self.player.char_where_mayor_value * 4 * self.player.multiplier_shot_value_list[0]
                    self.player.char_where_jackpot_qualified = 1
                    self.machine.events.post('arrow_change', led_num=7, script_name='cyan', mode_name="char_Where", action="add")
                    #clear the mayor arrow
                    self.machine.events.post('arrow_change', led_num=0, script_name='blue', mode_name="char_Where", action="remove")                        
                    self.machine.events.post('char_where_mayor_hit1')
                else:
                    #ramp is already qualified for SUPER
                    self.score = self.player.char_where_mayor_value * self.player.multiplier_shot_value_list[0]
                    self.log.info('char_where - ramp super already')                                    
                    self.machine.events.post('char_where_mayor_hit3')
            else:
                #ramp is already qualified 
                self.score = self.player.char_where_mayor_value * 2 * self.player.multiplier_shot_value_list[0]
                self.log.info('char_where - ramp jackpot already')                                                    
                self.machine.events.post('char_where_mayor_hit2')                
            self.player.score += self.score
            self.player.char_where_score += self.score
       

    def major_7(self, **kwargs):
        self.log.info('char_where - ramp shot')
        if self.player.char_where_state == 1:
            self.score = 0
            self.log.info('char_where - ramp hit')
            self.delay.remove('char_where_qualifier_timeout')
            if self.player.char_where_super_qualified == 1:
                #super jackpot
                self.score = self.player.char_where_super_jackpot_value * self.player.multiplier_shot_value_list[7]
                self.player.char_where_super_jackpots_made += 1
                self.log.info('char_where - super jackpot')
                self.machine.events.post('char_where_sjackpot_hit')
                self.player.char_where_super_jackpot_value += self.player.char_where_super_jackpot_inc                
                self.player.char_where_super_qualified = 0                
                self.player.score += self.score
                self.player.char_where_score += self.score
                self.machine.events.post('arrow_change', led_num=7, script_name="red", mode_name="char_Where", action="remove")                
            elif self.player.char_where_jackpot_qualified == 1:            
                #regular jackpot 
                self.score = self.player.char_where_jackpot_value * self.player.multiplier_shot_value_list[7]
                self.player.char_where_jackpots_made += 1
                self.log.info('char_where - jackpot')
                self.machine.events.post('char_where_jackpot_hit')
                self.player.char_where_jackpot_value += self.player.char_where_jackpot_inc
                self.player.char_where_jackpot_qualified = 0                
                self.player.score += self.score
                self.player.char_where_score += self.score
                self.machine.events.post('arrow_change', led_num=7, script_name="cyan", mode_name="char_Where", action="remove")                        
            else:            
                #no jackpot  (mayor first!)
                self.score = self.player.char_where_basic_ramp_value * self.player.multiplier_shot_value_list[7]
                self.player.char_where_jackpot_value += self.player.char_where_jackpot_inc
                self.log.info('char_where - basic ramp value')
                self.machine.events.post('char_where_ramp_hit')
                self.player.score += self.score
                self.player.char_where_score += self.score
          

    def clear_shots(self):
        if self.player.char_where_super_qualified == 1:
            #clear super
            self.machine.events.post('arrow_change', led_num=7, script_name="red", mode_name="char_Where", action="remove")
        else:
            if self.player.char_where_jackpot_qualified == 1:
                #clear reg jackpot
                self.machine.events.post('arrow_change', led_num=7, script_name="cyan", mode_name="char_Where", action="remove")        
            else:
                #clear mayor
                self.machine.events.post('arrow_change', led_num=0, script_name="blue", mode_name="char_Where", action="remove")                    

                
    def mode_stop(self, **kwargs):
        self.log.info('char_where_mode_stop')
        self.char_where_stop()


