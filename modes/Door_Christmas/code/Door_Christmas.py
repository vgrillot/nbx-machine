from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Door_Christmas 
# Hinterlands Door Mode - "Naughty or Nice?" Multiball                                                                                                              Page 29
#
# Brief Description
# This multiball mode always has one shot lit for a few points and another 
# lit for a lot of points. When you make either, they both change to different shots.
#
# Scenario
# Santa's having a rather hard time figuring out who's been naughty or nice in 
# Halloween Town. You need to help him out!
#
# Details
# This is a 2-ball multiball which, unlike most multiballs in the game, 
# is not completed simply by starting it. During this multiball mode, two major shots, 
# selected at random, will be lit. One will be lit green for nice, the other red for 
# naughty. Shooting the green shot will award lots more points than shooting the red shot.
# Once you hit either of them though, BOTH will change to different major shots. 
# You must make three nice shots or three naughty shots to complete the mode, scoring 
# either a Nice Jackpot or a Naughty Jackpot. The interesting dichotomy of this mode is 
# that the Naughty Jackpot is actually worth more than the Nice Jackpot, but the
# naughty shots are worth significantly less than the nice shots. Once either jackpot 
# is awarded both the nice and naughty counters reset, meaning you need three of
# either again to score another jackpot. Scoring either jackpot also completes the mode.
#
# Scoring
# Nice Shots Base Value               1,000,000
# Nice Shots Increment                100,000
# Naughty Shots Base Value            200,000
# Naughty Shots Increment             20,000
# Nice Jackpot                        4,000,000
# Naughty Jackpot                     7,500,000
#
# Lighting
# Nice shots flash a green triangle while naughty shots flash a red triangle. 
# When either shot is ready for a jackpot it will also flash its circle.
#
# Difficulty Adjustments
# Very Easy        2 Shots for Jackpot
# Easy             2 Shots for Jackpot
# Normal           3 Shots for Jackpot
# Hard             3 Shots for Jackpot
# Very Hard        4 Shots for Jackpot

class Door_Christmas(Mode):

    def mode_init(self):
        self.log.info('Door_Christmas Multiball mode_init')

    def mode_start(self, **kwargs):
        self.log.info('Door_Christmas Multiball mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.player.door_christmas_running = 0
        self.nice_shot_score_base = 1000000
        self.nice_shot_score_inc = 100000
        self.nice_shot_score_jackpot = 4000000
        self.nice_shot_total = 0
        self.naughty_shot_score_base = 200000
        self.naughty_shot_score_inc = 2000
        self.naughty_shot_score_jackpot = 7500000
        self.naughty_shot_total = 0
        self.nice = 0
        self.naughty = 1
        self.player.door_christmas_score = 0
        self.player.door_christmas_nice_score = 0  
        self.player.door_christmas_nice_jackpot = 0
        self.player.door_christmas_naughty_score = 0  
        self.player.door_christmas_naughty_jackpot = 0
        self.ticks = 0
        self.add_mode_event_handler('balldevice_trough_ball_enter', self.ball_drained)
        self.player.door_christmas_shotlist = [
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
        self.add_mode_event_handler('rollover_lanes_santa_lights_lit_complete', self.handle_santa_complete)            
        self.add_mode_event_handler("major_0_singlestep_unlit_hit", self.major_0)
        self.add_mode_event_handler("major_1_singlestep_unlit_hit", self.major_1)
        self.add_mode_event_handler("major_2_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_2a_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_3_singlestep_unlit_hit", self.major_3)
        self.add_mode_event_handler("major_4_singlestep_unlit_hit", self.major_4)
        self.add_mode_event_handler("major_5_singlestep_unlit_hit", self.major_5)
        self.add_mode_event_handler("major_5a_singlestep_unlit_hit", self.major_5)
        self.add_mode_event_handler("major_6_singlestep_unlit_hit", self.major_6)
        self.add_mode_event_handler("major_6a_singlestep_unlit_hit", self.major_6)
        self.add_mode_event_handler("major_7_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_7a_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_8_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("major_8a_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("major_9_singlestep_unlit_hit", self.major_9)
        self.add_mode_event_handler('door_switch_to_narrow', self.switch_to_narrow)        
        self.add_mode_event_handler('door_switch_to_wide', self.switch_to_wide)
        self.add_mode_event_handler("doors_resume_and_show", self.reshow_screen)
        self.add_mode_event_handler("doors_pause_and_hide", self.remove_all_widgets)          
        self.start_multiball()
        self.msg = 1
        

    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_christmas_messages")  
        self.machine.events.post('remove_christmas_slide_narrow')
        self.machine.events.post('remove_christmas_slide_wide')
        self.machine.events.post('remove_christmas_slide_full')
        

    def reshow_screen(self, **kwargs):   
        if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        


    def start_multiball(self):
        if (self.player.door_christmas_running == 0):
            self.log.info("Started the Holiday Christmas Multiball mode")
            self.set_shots()
            bip = self.machine.game.balls_in_play             
            if bip < 6:
                self.machine.game.balls_in_play = bip+1
                self.machine.playfield.add_ball(1, player_controlled=False)
            self.player.door_christmas_running = 1
            self.machine.events.post('holiday_christmas_music_start')
            self.machine.events.post('santa_now_who_could_that_be')
            self.machine.events.post('disable_combos')
            self.machine.events.post('add_a_ball_start')
            self.machine.events.post('enable_the_mb_ball_save')   
            self.machine.events.post('show_christmas_slide_full')   
            self.machine.events.post('char_pause_and_hide')
            self.machine.events.post("ob_pause_and_hide") 
            self.player.door_timer_ispaused = 0
            self.delay.add(name="show_full_christmas_intro_remover", ms=5000, callback=self.show_screen)

            
    def show_screen(self, **kwargs):
        self.log.info( "5 seconds passed, show narrow or wide" )
        #self.ticks_msg = self.ticks        
        self.delay.add(name="holiday_christmas_ticker", ms=500, callback=self.ticker)
        if self.player.door_timer_ispaused == 0:        
            self.machine.events.post("char_resume_and_show")
            self.machine.events.post("ob_resume_and_show")         
            self.reshow_screen()        
            if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                self.machine.events.post('show_christmas_msg_1_n')                
            else:
                self.machine.events.post('show_christmas_msg_1')              

            
    def ticker(self):
        self.log.info("door_christmas - 500ms ticks ")
        if self.player.door_christmas_running == 1:
            self.delay.add(name="door_christmas_ticker", ms=500, callback=self.ticker)
        if self.player.door_timer_ispaused == 0:
            self.ticks += 1
            if self.ticks % 4 == 0:
                self.msg = 1
                if self.nice_shot_total > 0:
                    self.msg = 2  #shoot for nice
                if self.naughty_shot_total > 0:
                    self.msg = 3  #shoot for naughty
                if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                    self.machine.events.post('show_christmas_msg_'+str(self.msg)+'_n')            
                else:
                    self.machine.events.post('show_christmas_msg_'+str(self.msg))            
        
        
    def switch_to_narrow(self, **kwargs):   
        self.remove_all_widgets()
        self.machine.events.post('show_christmas_slide_narrow')

        
    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()
        self.machine.events.post('show_christmas_slide_wide')

        
    def set_shots(self):
        #pick 2 random shots set one to red, one to green
        for x in range(0, 10):
            self.player.door_christmas_shotlist[x]["state"] = "off"
        self.nice = random.randint(0,9)
        self.naughty = random.randint(0,9)
        while (self.naughty == self.nice):
            self.naughty = random.randint(0,9)
        self.player.door_christmas_shotlist[self.naughty]["state"] = "red"
        self.player.door_christmas_shotlist[self.nice]["state"] = "green"
        self.set_shot_lights()


    def set_shot_lights(self):
        for x in range(0, 10):
            state = self.player.door_christmas_shotlist [x]["state"]
            if state != 'off':
                led = self.player.door_christmas_shotlist [x]["led"]
                self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="Door_Christmas", action="add")


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


    def handle_shot(self, shot):
        self.log.info(("shot: " +str(shot)))
        if self.player.door_christmas_running == 1:
            if self.player.door_christmas_shotlist[shot]["state"] == "red":
                if self.naughty_shot_total < 2:
                    self.score = self.naughty_shot_score_base
                    self.score *= self.player.multiplier_shot_value_list[shot] # 1X, 2X or 3X
                    self.naughty_shot_score_base += self.naughty_shot_score_inc
                    self.naughty_shot_total += 1
                    self.nice_shot_total = 0
                    self.player.door_christmas_naughty_score = self.score 
                    self.machine.events.post('remove_christmas_messages')
                    self.ticks = 0
                    if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                        self.machine.events.post('show_christmas_naughty_score_collected'+'_n')
                    else:
                        self.machine.events.post('show_christmas_naughty_score_collected')
                    self.player["score"] += (self.score)
                    self.player.door_christmas_score += (self.score)
                else:
                    self.naughty_shot_score_base += self.naughty_shot_score_inc
                    self.score = self.naughty_shot_score_jackpot
                    self.score *= self.player.multiplier_shot_value_list[shot] # 1X, 2X or 3X                    
                    self.naughty_shot_total = 0
                    self.nice_shot_total = 0
                    self.player.door_christmas_naughty_jackpot = self.score 
                    self.machine.events.post('remove_christmas_messages')
                    self.ticks = 0
                    if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                        self.machine.events.post('show_christmas_naughty_jackpot_collected'+'_n')
                    else:
                        self.machine.events.post('show_christmas_naughty_jackpot_collected')
                    self.player["score"] += (self.score)
                    self.player.door_christmas_score += (self.score)                    
                led = self.player.door_christmas_shotlist [shot]["led"]                    
                self.machine.shows["sc_naughty_out"].play(show_tokens=dict(leds=led), speed=8.0, loops=3)							
                self.clear_shots()
                self.set_shots()
            if self.player.door_christmas_shotlist[shot]["state"] == "green":
                if self.nice_shot_total < 2:
                    self.score = self.nice_shot_score_base
                    self.score *= self.player.multiplier_shot_value_list[shot] # 1X, 2X or 3X                    
                    self.nice_shot_score_base += self.nice_shot_score_inc
                    self.nice_shot_total += 1
                    self.naughty_shot_total = 0
                    self.player.door_christmas_nice_score = self.score
                    self.machine.events.post('remove_christmas_messages')
                    self.ticks = 0
                    if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                        self.machine.events.post('show_christmas_nice_score_collected'+'_n')
                    else:
                        self.machine.events.post('show_christmas_nice_score_collected')
                    self.player["score"] += (self.score)
                    self.player.door_christmas_score += (self.score)                                        
                else:
                    self.nice_shot_score_base += self.nice_shot_score_inc
                    self.score = self.nice_shot_score_jackpot
                    self.score *= self.player.multiplier_shot_value_list[shot] # 1X, 2X or 3X                    
                    self.nice_shot_total = 0
                    self.naughty_shot_total = 0
                    self.player.door_christmas_nice_jackpot = self.score 
                    self.machine.events.post('remove_christmas_messages')
                    self.ticks = 0
                    if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                        self.machine.events.post('show_christmas_nice_jackpot_collected'+'_n')
                    else:
                        self.machine.events.post('show_christmas_nice_jackpot_collected')
                    self.player["score"] += (self.score)
                    self.player.door_christmas_score += (self.score)                                        
                led = self.player.door_christmas_shotlist [shot]["led"]                    
                self.machine.shows["sc_nice_out"].play(show_tokens=dict(leds=led), speed=8.0, loops=3)							
                self.clear_shots()                    
                self.set_shots()


    def handle_santa_complete(self, **kwargs):
        self.log.info("handle_santa_complete")
        if self.player.door_christmas_running == 1:        
            #spot the next nice/naughty shot!
            if self.naughty_shot_total > 0:
                self.handle_shot(self.naughty)
            elif self.nice_shot_total > 0:
                self.handle_shot(self.nice)
            else:
                if random.randint(0,9) > 4:
                    self.handle_shot(self.naughty)
                else:
                    self.handle_shot(self.nice)

        
    def clear_shots(self):
        for x in range(0, 10):
            state = self.player.door_christmas_shotlist [x]["state"]
            if state != 'off':
                led = self.player.door_christmas_shotlist [x]["led"]
                self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="Door_Christmas", action="remove")                        
                self.player.door_christmas_shotlist[x]["state"] = "off"



    def ball_drained(self, **kwargs):
        if self.player.door_christmas_running == 1:
            self.log.info("Holiday Christmas multiball - ball drained")
            if self.player.ball_save_active == 0:            
                if self.machine.game.balls_in_play <= 2:
                    #there is only 1 ball on playfield, end multiball
                    self.door_christmas_stop()
                else:
                    self.log.info( "Christmas - MB - ball drained - more than 2 BIP" )            
            else:
                self.log.info( "Christmas - MB - ball drained - but ball save is running" )


    def door_christmas_stop(self):
        if self.player.door_christmas_running == 1:
            self.player.door_christmas_running = 2          
            self.machine.events.post('holiday_christmas_music_stop')
            self.log.info("door_christmas over")
            self.machine.events.post('holiday_mode_stopped', state="complete")
            self.clear_shots()
            self.machine.events.post('enable_combos')
            self.machine.events.post('add_a_ball_stop')
        self.machine.events.post('remove_christmas_messages')
        self.machine.events.post('remove_christmas_narrow')
        self.machine.events.post('remove_christmas_wide')
        self.machine.events.post('oogie_switch_to_wide')
        self.machine.events.post("char_resume_and_show")


    def mode_stop(self, **kwargs):
        self.log.info('Holiday Christmas mode_stop')
        self.door_christmas_stop()
        self.clear_shots()

