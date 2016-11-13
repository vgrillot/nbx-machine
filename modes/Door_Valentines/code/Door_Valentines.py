from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Door_Valentines 
# Hinterlands Door Mode - "Love is in the Air"
# 
# Brief Description
# You must get a certain number of points off the spinner. 
# To help out, the more lit shots you clear the more valuable the spinner gets.
# 
# Scenario
# Cupid is out and about in Halloween Town trying to figure out how to make 
# the denizens fall in love. He figures just shoot as many arrows as he can!
# 
# Details
# The goal of this mode is to score 5,000,000 points off of the spinner alone within 45 seconds. 
# However, the base value of the spinner in this mode is only 10,000,
# thus without a shot multiplier this would take 500 spins. However, all of the other 
# major shots and many of the standups (JACK, Doctor, LSB and Mystery) start
# flashing pink at a moderate speed. When you hit one of these flashing shots 
# or standups it will unlight and increase the spinner value. The idea is to hit lots of
# different things to get the spinner value up, then go for spinner shots to clear the 
# 5,000,000 much more easily! The spinner value will double if at least 16 of the 18 pink shots
# are cleared!
# 
# Scoring
# Base Spinner Value                         10,000 / spin
# Increase per Shot/Standup Cleared          25,000 / spin
# Maximum Potential Spinner Value            920,000 / spin (450,000+10,000) x2 for having all 18 pink shots cleared)
# 
# Lighting
# The spinner will flash yellow on the triangle for most of the mode 
# but will flash a white triangle and circle if all 18 pink shots are cleared. 
# Each shot lit to increase the spinner value will flash pink.
# 
# Difficulty Adjustments
# Very Easy         60 Seconds, Target Score of 3,000,000
# Easy              50 Seconds, Target Score of 4,000,000
# Normal            45 Seconds, Target Score of 5,000,000
# Hard              40 Seconds, Target Score of 6,000,000
# Very Hard         35 Seconds, Target Score of 7,000,000

class Door_Valentines(Mode):

    def mode_init(self):
        self.log.info('Door_Valentines mode_init')

    def mode_start(self, **kwargs):
        self.log.info('Door_Valentines mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.ticks = 0
        self.player.door_valentines_running = 0
        self.player.door_valentines_spin_score = 0
        self.player.door_valentines_spin_value = 0
        self.player.door_valentines_base_ticks = 90  #90 = 45 seconds
        self.player.door_valentines_timeleft = int(self.player.door_valentines_base_ticks/2)        
        self.player.door_valentines_spin_value_pts = 10000
        self.player.door_valentines_score_needed = 3000000
        self.player.door_valentines_show_handles = [0] * 20          
        self.player.door_valentines_shotlist = [
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

            ,{"led":"rgb_lramp_ldiamond", "state":"off"}
            ,{"led":"rgb_lramp_rdiamond", "state":"off"}
            ,{"led":"rgb_lock_rect", "state":"off"}
            ,{"led":"rgb_shock_rect", "state":"off"}
            ,{"led":"rgb_barrel_rect", "state":"off"}
            ,{"led":"rgb_mystery_rect", "state":"off"}
            ,{"led":"rgb_rramp_ldiamond", "state":"off"}
            ,{"led":"rgb_rramp_rdiamond", "state":"off"}
            ,{"led":"rgb_doctor_rect", "state":"off"}
            ]
        self.add_mode_event_handler('sw_sally', self.spin)
        self.add_mode_event_handler("major_0_singlestep_unlit_hit", self.major_0)
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
        self.add_mode_event_handler('sw_bugbashtarget1', self.bug_hit1)
        self.add_mode_event_handler('sw_bugbashtarget2', self.bug_hit2)
        self.add_mode_event_handler('sw_bugbashtarget3', self.bug_hit3)
        self.add_mode_event_handler('sw_bugbashtarget4', self.bug_hit4)
        self.add_mode_event_handler('sw_bugbashtarget5', self.bug_hit5)
        self.add_mode_event_handler('sw_bugbashtarget9', self.bug_hit9)
        self.add_mode_event_handler('sw_bugbashtarget10', self.bug_hit10)
        self.add_mode_event_handler('sw_bugbashtarget11', self.bug_hit11)
        self.add_mode_event_handler('sw_bugbashtarget12', self.bug_hit12)
        self.add_mode_event_handler("extend_door_time", self.extend_time)  
        self.add_mode_event_handler('door_switch_to_narrow', self.switch_to_narrow)        
        self.add_mode_event_handler('door_switch_to_wide', self.switch_to_wide)   
        self.add_mode_event_handler("doors_resume_and_show", self.reshow_screen)
        self.add_mode_event_handler("doors_pause_and_hide", self.remove_all_widgets)                  
        self.valentines_start()
        self.msg = 1
        self.ticks_msg = self.ticks

        
    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_valentines_messages")  
        self.machine.events.post('remove_valentines_slide_narrow')
        self.machine.events.post('remove_valentines_slide_wide')
        self.machine.events.post('remove_valentines_slide_full')
        
        
    def reshow_screen(self, **kwargs):   
        self.log.info("reshow_screen")    
        if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        
        
        
    def valentines_start(self):
        self.log.info("holiday valentines start")
        if (self.player.door_valentines_running == 0):
            self.ticks = self.player.door_valentines_base_ticks
            self.player.door_valentines_timeleft = int(self.player.door_valentines_base_ticks/2)
            self.player.door_valentines_spin_value_pts = 10000
            self.player.door_valentines_score_needed = 3000000
            self.player.door_valentines_spin_score = 0
            self.player.door_valentines_spin_value = 0
            self.set_shots()
            self.player.door_valentines_running = 1
            self.machine.events.post("holiday_valentines_music_start")
            self.machine.events.post('show_valentines_slide_full')
            self.machine.events.post('char_pause_and_hide')
            self.machine.events.post("ob_pause_and_hide")
            self.player.door_timer_ispaused = 0
            self.delay.add(name="show_full_valentines_intro_remover", ms=5000, callback=self.show_screen)

            
    def show_screen(self, **kwargs):
        self.log.info( "5 seconds passed, show narrow or wide" )
        self.ticks_msg = self.ticks
        self.delay.add(name="holiday_valentines_ticker", ms=500, callback=self.ticker)        
        if self.player.door_timer_ispaused == 0:        
            self.machine.events.post("char_resume_and_show")
            self.machine.events.post("ob_resume_and_show")         
            self.player.door_timer_ispaused = 0
            self.reshow_screen()        
            if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                self.machine.events.post('show_valentines_msg_1_n')                
            else:
                self.machine.events.post('show_valentines_msg_1')                                  

            
    def ticker(self):
        self.log.info("Door_Valentines - 500ms ticks " + str(self.ticks))
        self.player.door_valentines_timeleft = int(self.ticks/2)        
        if self.player.door_valentines_running == 1:
            self.delay.add(name="holiday_valentines_ticker", ms=500, callback=self.ticker)
        if self.player.door_timer_ispaused == 0:
            self.ticks -= 1;
            if self.ticks <= 0:
                self.valentines_stop()
            else:
                if  self.ticks_msg-self.ticks > 3:
                    self.msg += 1
                    self.ticks_msg = self.ticks
                    if self.msg > 3: 
                        self.msg = 1    
                    if self.ticks > 2:                
                        if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                            self.machine.events.post('show_valentines_msg_'+str(self.msg)+'_n')   
                        else:
                            self.machine.events.post('show_valentines_msg_'+str(self.msg))   

                
    def switch_to_narrow(self, **kwargs): 
        self.remove_all_widgets()   
        self.machine.events.post('show_valentines_slide_narrow')
        
        
    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()       
        self.machine.events.post('show_valentines_slide_wide')

            
    def extend_time(self, time, **kwargs):
        self.log.info("door_valentines - time extended " +str(time))
        self.ticks += time*2;
        self.ticks_msg += time*2;        
        self.player.door_valentines_timeleft = int(self.ticks/2)
        

    def valentines_stop(self):
        if self.player.door_valentines_running == 1:
            self.machine.events.post('holiday_valentines_music_stop')
            self.log.info("holiday valentines over")
            if self.player.door_valentines_spin_score >= self.player.door_valentines_score_needed:
                self.machine.events.post('holiday_mode_stopped', state="complete")
                self.player.door_valentines_running = 2 #completed
            else:
                self.machine.events.post('holiday_mode_stopped', state="incomplete")
                self.player.door_valentines_running = 0 #ready to start again
            self.reset_shots()
        self.log.info("valentines stop - posting remove events")            
        self.machine.events.post('remove_valentines_messages')
        self.machine.events.post('remove_valentines_narrow')
        self.machine.events.post('remove_valentines_wide')
        self.machine.events.post('oogie_switch_to_wide')
        self.machine.events.post("char_resume_and_show")


    def set_shots(self):
        for x in range(0, 19):
            self.player.door_valentines_shotlist[x]["state"] = "pink"
        self.player.door_valentines_shotlist[1]["state"] = "pink"
        self.set_shot_lights()


    def set_shot_lights(self):
        for x in range(10, 19):
            if self.player.door_valentines_show_handles[x] != 0:
                self.player.door_valentines_show_handles[x].stop()
                self.player.door_valentines_show_handles[x] = 0
        for x in range(10, 19):
            state = self.player.door_valentines_shotlist[x]["state"]
            led = self.player.door_valentines_shotlist[x]["led"]
            script_name = "sc_"+state
            self.player.door_valentines_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)			 
        for x in range(0, 10):
            state = self.player.door_valentines_shotlist[x]["state"]
            led = self.player.door_valentines_shotlist[x]["led"]
            self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="Door_Valentines", action="add")

            
    def major_0(self, **kwargs):
        self.handle_shot(0)
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
    def bug_hit1(self, **kwargs):
        self.handle_shot(10)
    def bug_hit2(self, **kwargs):
        self.handle_shot(11)
    def bug_hit3(self, **kwargs):
        self.handle_shot(12)
    def bug_hit4(self, **kwargs):
        self.handle_shot(13)
    def bug_hit5(self, **kwargs):
        self.handle_shot(14)
    def bug_hit9(self, **kwargs):
        self.handle_shot(15)
    def bug_hit10(self, **kwargs):
        self.handle_shot(16)
    def bug_hit11(self, **kwargs):
        self.handle_shot(17)
    def bug_hit12(self, **kwargs):
        self.handle_shot(18)


    def handle_shot(self, shot):
        if self.player.door_valentines_running == 1:
            if self.player.door_valentines_shotlist[shot]["state"] == "pink":
                self.player.door_valentines_spin_value += 1
                #self.machine.events.post('arrow_change', led_num=shot, script_name="pink", mode_name="Door_Valentines", action="remove")                        
                self.player.door_valentines_shotlist[shot]["state"] = "off"
                if shot > 9:
                    #self.machine.light_controller.stop_script(key="holiday_valentines_"+str(shot))
                    #led = self.player.door_valentines_shotlist[shot]["led"]
                    #script_name = "sc_off"
                    #self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=1)
                    if self.player.door_valentines_show_handles[shot] != 0:
                      self.player.door_valentines_show_handles[shot].stop()
                      self.player.door_valentines_show_handles[shot] = 0
                else:
                    #it's an arrow, remove pink light
                    self.machine.events.post('arrow_change', led_num=shot, script_name="pink", mode_name="Door_Valentines", action="remove")
                if self.player.door_valentines_spin_value >= 16:
                    if self.player.door_valentines_shotlist[1]["state"] != "white":
                        self.player.door_valentines_shotlist[1]["state"] = "white"
                        self.machine.events.post('arrow_change', led_num=1, script_name="pink", mode_name="Door_Valentines", action="remove")
                        self.machine.events.post('arrow_change', led_num=1, script_name="white", mode_name="Door_Valentines", action="add")
                #calc how much each spin is worth
                self.score = 10000+self.player.door_valentines_spin_value*25000
                self.score *= self.player.multiplier_shot_value_list[1] # 1X, 2X or 3X 
                if self.player.door_valentines_spin_value >= 16:
                    self.score *= 2   #2X if at least 16 pink targets are hit
                self.player.door_valentines_spin_value_pts = self.score
                self.player.score += self.score 


    def spin(self, **kwargs):
        if self.player.door_valentines_running == 1:
            self.score = 10000+self.player.door_valentines_spin_value*25000
            self.score *= self.player.multiplier_shot_value_list[1] # 1X, 2X or 3X 
            if self.player.door_valentines_spin_value >= 16:
                self.score *= 2   #2X if at least 16 pink targets are hit
            self.player.door_valentines_spin_score += self.score
            self.player.score += self.score 
            self.machine.events.post('valentines_spin_score_increased', 
                    value=self.player.door_valentines_spin_score )


    def reset_shots(self):
        for x in range(0, 10):
            state = self.player.door_valentines_shotlist[x]["state"]
            if state != 'off':
                self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="Door_Valentines", action="remove")                        
                self.player.door_valentines_shotlist[x]["state"] = "off"

        for x in range(10, 19):
            if self.player.door_valentines_show_handles[x] != 0:
                self.player.door_valentines_show_handles[x].stop()
                self.player.door_valentines_show_handles[x] = 0
            self.player.door_valentines_shotlist[x]["state"] = "off"
            led = self.player.door_valentines_shotlist[x]["led"]
            self.machine.shows["sc_off"].play(show_tokens=dict(leds=led), speed=8.0, loops=1)


    def mode_stop(self, **kwargs):
        self.log.info('Door_Valentines mode_stop')
        self.valentines_stop()

        