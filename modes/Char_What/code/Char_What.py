from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random
     
# Character Mode - "What's This?" Frenzy                                                                                                                           Page 14
# 
# Brief Description
# 30 Second timed frenzy mode where almost all switches award points. Hitting any of the JACK targets increases the frenzy value. You must reach a target score to
# complete the frenzy and progress towards "Deliver the Presents".
# 
# Scenario
# Jack's fallen through the Christmas Town door in the Hinterlands and is wondering what everything is.
# 
# Details
# To help Jack discover the magic of Christmas Town you must shoot everything! The base value for every switch starts at 40,000, but hitting any of the JACK
# standups increases this value by 5,000. The mode only lasts 30 seconds and you must score at least 2,000,000 to complete and end the mode.
# 
# Scoring
# Frenzy Base Value                 40,000
# Increments to Base Value          5,000 / each
# 
# Lighting
# The lighting in this mode is mostly just festive and fun and meant to distract the player. The JACK targets will be flashing yellow and will ALL flash green briefly when
# one is hit to indicate the increase in the frenzy value.
# 
# Difficulty Adjustments
# Very Easy         40 Seconds - Goal of 1,000,000 Points
# Easy              35 Seconds - Goal of 1,500,000 Points
# Normal            30 Seconds - Goal of 2,000,000 Points
# Hard              30 Seconds - Goal of 2,500,000 Points
# Very Hard         25 Seconds - Goal of 3,000,000 Points

class Char_What(Mode):

    def mode_init(self):
        self.log.info('char_what mode_init')

    def mode_start(self, **kwargs):
        self.log.info('char_what mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.char_what_started == 0:
            #once per game only
            self.player.char_what_started = 1
            self.player.char_what_running = 0
            self.player.char_what_base_ticks = 60 #30 seconds
        self.player.char_shared_timeleft = 30
        self.ticks = self.player.char_what_base_ticks
        self.player.char_what_Jacks = 0
        self.player.char_what_score = 0
        self.player.char_what_value = 0        
        self.player.char_what_shotlist = [
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
            ,{"led":"rgb_bug_1", "state":"off"}
            ,{"led":"rgb_bug_2", "state":"off"}
            ,{"led":"rgb_bug_3", "state":"off"}
            ,{"led":"rgb_mystery_rect", "state":"off"}
            ,{"led":"rgb_rramp_ldiamond", "state":"off"}
            ,{"led":"rgb_rramp_rdiamond", "state":"off"}
            ,{"led":"rgb_doctor_rect", "state":"off"}
            ]
        self.player.what_show_handles = [0] * 25            
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
        self.add_mode_event_handler('sw_bugbashtarget1', self.bug_hit1)
        self.add_mode_event_handler('sw_bugbashtarget2', self.bug_hit2)
        self.add_mode_event_handler('sw_bugbashtarget3', self.bug_hit3)
        self.add_mode_event_handler('sw_bugbashtarget4', self.bug_hit4)
        self.add_mode_event_handler('sw_bugbashtarget5', self.bug_hit5)
        self.add_mode_event_handler('sw_bugbashtarget6', self.bug_hit6)
        self.add_mode_event_handler('sw_bugbashtarget7', self.bug_hit7)
        self.add_mode_event_handler('sw_bugbashtarget8', self.bug_hit8)
        self.add_mode_event_handler('sw_bugbashtarget9', self.bug_hit9)
        self.add_mode_event_handler('sw_bugbashtarget10', self.bug_hit10)
        self.add_mode_event_handler('sw_bugbashtarget11', self.bug_hit11)
        self.add_mode_event_handler('sw_bugbashtarget12', self.bug_hit12)
        self.add_mode_event_handler("extend_char_time", self.extend_time)
        self.add_mode_event_handler('door_switch_to_narrow', self.hide_slide)    
        self.add_mode_event_handler('oogie_switch_to_narrow', self.hide_slide)
        self.add_mode_event_handler("char_resume_and_show", self.resume_and_show)
        self.add_mode_event_handler("char_pause_and_hide", self.remove_all_widgets)          
        self.char_what_start()
        self.msg = 1
        self.ticks_msg = self.ticks         


    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_what_messages")  
        self.machine.events.post('char_what_hide_slide')


    def char_what_start(self):
        self.log.info("char_what_start")
        if (self.player.char_what_running != 1):  #not running
            self.player.char_what_running = 1          
            self.ticks = self.player.char_what_base_ticks
            #self.player.char_what_needed = 1000000
            self.player.char_what_value = 40000
            self.player.char_what_score = 0
            self.player.char_what_Jacks = 0
            self.set_shots()
            self.ticks_msg = self.ticks            
            #self.machine.events.post("mode_base_stop_music")                        
            self.machine.events.post("char_what_music_start")
            self.machine.events.post("char_show_timer")
            self.machine.events.post('show_what_msg_1')
            self.machine.events.post("ob_pause_and_hide")
            self.machine.events.post("doors_pause_and_hide")          
            self.delay.add(name="char_what_ticker", ms=500, callback=self.ticker)
            self.player.char_timer_ispaused = 0
            self.delay.add(name="char_what_slide_delay", ms=5000, callback=self.hide_slide)
           

    def resume_and_show(self, **kwargs):   
        if (self.player.Doors_state == 0 and self.player.OB_Gate_current_mode_state == 0):
            if self.player.char_what_running > 0:
                self.machine.events.post("char_what_show_slide")            


    def hide_slide(self, **kwargs):   
        if (self.player.Doors_state != 0 or self.player.OB_Gate_current_mode_state != 0):
            self.remove_all_widgets()      
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         

            
    def extend_time(self, time, **kwargs):
        self.log.info("char_what - time extended " +str(time))
        self.ticks += time*2;
        self.ticks_msg += time*2;        
        self.player.char_shared_timeleft = int(self.ticks/2)
        
            
    def ticker(self):
        self.log.info("char_what - 500ms ticks " +str(self.ticks))
        self.player.char_shared_timeleft = int(self.ticks/2)
        self.delay.add(name="char_what_ticker", ms=500, callback=self.ticker)
        if self.player.char_timer_ispaused == 0:
            self.ticks -= 1;
            if self.ticks <= 0:
                self.char_what_stop()
            else:
                if  self.ticks_msg-self.ticks > 3:
                    self.msg += 1
                    self.ticks_msg = self.ticks
                    if self.msg > 3: 
                        self.msg = 1
                    self.machine.events.post('show_what_msg_'+str(self.msg))
            
            
    def char_what_stop(self):
        if self.player.char_what_running == 1:
            self.machine.events.post('char_what_music_stop')
            self.machine.events.post('char_what_hide_slide')                        
            self.machine.events.post("char_hide_timer")
            self.machine.events.post("stop_all_character_messages")
            self.log.info("char_what over")
            self.machine.events.post('char_mode_stopped', char_state="complete", char_mode="What")
            self.player.char_what_running = 2 #completed
            self.reset_shots()
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         


    def set_shots(self):
        for x in range(0, 22):
            self.player.char_what_shotlist[x]["state"] = "white"
        self.set_shot_lights()


    def set_shot_lights(self):
        for x in range(10, 22):
            state = self.player.char_what_shotlist[x]["state"]
            led = self.player.char_what_shotlist[x]["led"]
            script_name = "sc_"+state
            if self.player.what_show_handles[x] != 0:
                self.player.what_show_handles[x].stop()
            self.player.what_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)						
        for x in range(0, 10):
            state = self.player.char_what_shotlist[x]["state"]
            led = self.player.char_what_shotlist[x]["led"]
            self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="char_What", action="add")


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
    def bug_hit1(self, **kwargs):
        #self.handle_shot(10)
        self.jack_hit(10)
    def bug_hit2(self, **kwargs):
        #self.handle_shot(11)
        self.jack_hit(11)        
    def bug_hit3(self, **kwargs):
        self.handle_shot(12)
    def bug_hit4(self, **kwargs):
        self.handle_shot(13)
    def bug_hit5(self, **kwargs):
        self.handle_shot(14)
    def bug_hit6(self, **kwargs):
        self.handle_shot(15)
    def bug_hit7(self, **kwargs):
        self.handle_shot(16)
    def bug_hit8(self, **kwargs):
        self.handle_shot(17)
    def bug_hit9(self, **kwargs):
        self.handle_shot(18)
    def bug_hit10(self, **kwargs):
        #self.handle_shot(19)
        self.jack_hit(19)        
    def bug_hit11(self, **kwargs):
        #self.handle_shot(20)
        self.jack_hit(20)        
    def bug_hit12(self, **kwargs):
        self.handle_shot(21)


    def handle_shot(self, shot):
        if self.player.char_what_running == 1:
            if shot == 7:
                #right ramp - increase the value (10, 20 or 30 jacks)
                self.player.char_what_Jacks += (10*self.player.multiplier_shot_value_list[shot])
                self.player.char_what_value = 40000+self.player.char_what_Jacks*5000            
                self.log.info('char_what - rooftop ramp  -value at - ' + str(self.player.char_what_value))            
                self.machine.events.post("char_what_value_increased_ramp")
            self.score = self.player.char_what_value
            if shot < 10:
                self.score *= self.player.multiplier_shot_value_list[shot] # 1X, 2X or 3X 
            self.player.char_what_score += self.score
            self.player.score += self.score
            self.log.info('char_what - score - ' + str(self.score)) 
            nb = random.randint(1,3)
            self.machine.events.post('say_whats_this_'+str(nb))                       


    def jack_hit(self, shot, **kwargs):
        if self.player.char_what_running == 1:    	
            self.player.char_what_Jacks += 1
            self.player.char_what_value = 40000+self.player.char_what_Jacks*5000            
            self.log.info('char_what - JACK letter hit - value at - ' + str(self.player.char_what_value))
            self.machine.events.post("char_what_value_increased")
            self.score = self.player.char_what_value
            self.player.char_what_score += self.score
            self.player.score += self.score
            self.log.info('char_what - score - ' + str(self.score)) 

            
    def reset_shots(self):
        for x in range(0, 10):
            self.player.char_what_shotlist[x]["state"] = "off"
            script_name = "white"
            self.machine.events.post('arrow_change', led_num=x, script_name=script_name, mode_name="char_What", action="remove")                        
        for x in range(10, 22):
            self.player.char_what_shotlist[x]["state"] = "off"
            #stop currently playing show
            if self.player.what_show_handles[x] != 0:
                self.player.what_show_handles[x].stop()
                self.player.what_show_handles[x] = 0


    def mode_stop(self, **kwargs):
        self.log.info('char_what mode_stop')
        self.char_what_stop()
        self.reset_shots()


