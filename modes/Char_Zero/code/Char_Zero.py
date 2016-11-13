from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Character Mode - "Go Fetch!"                                                                                                                             Page 20
#
# Brief Description
# All major shots will blink.  Shoot one and it lights solid.  Repeat that shot for increasing jackpot
# Shoot a different shot and it resets.
# 
# Scenario
# Zero wants to play fetch, so Jack takes off one of his bones and tosses it out.
# 
# Details
# To complete this mode, all you have to do is make a major shot three times in a row. 
# Continue shooting same shot for more points.
# 
# Scoring
# 1st Major Shot                   500,000
# 2nd Major Shot                 1,000,000
# 3rd Major Shot                 2,000,000
# 4th Major Shot                 4,000,000
# 5th                            8,000,000
# 6th                           16,000,000
# 
# Lighting
# The major shots you need to make light the triangle orange.
# 
# Difficulty Adjustments
# Very Easy         Make 2 Major Shots, 40 Second Time Limit
# Easy              Make 3 Major Shots, 40 Second Time Limit
# Normal            Make 3 Major Shots, 30 Second Time Limit
# Hard              Make 3 Major Shots, 25 Second Time Limit
# Very Hard         Make 4 Major Shots, 25 Second Time Limit

class Char_Zero(Mode):

# runs on MPF boot when the mode is read in and set up.
    def mode_init(self):
        self.log.info('char_zero mode_init')

    def mode_start(self, **kwargs):
        self.log.info('char_zero mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.player.char_zero_base_ticks = 60 #60 = 30 seconds
        self.player.char_shared_timeleft = int(self.player.char_zero_base_ticks/2)
        self.player.char_zero_shots_needed = 2
        self.player.char_zero_shot_index = -1
        self.player.char_zero_completed = 0
        self.player.char_zero_state = 0            
        self.player.char_zero_shot_points = [100000,500000,1000000,2000000,4000000,8000000,16000000]            
        self.player.char_zero_next = 100000        
        self.player.char_zero_shots_made = 0
        self.add_mode_event_handler('sw_zero', self.ball_at_zero)
        self.player.char_zero_shotlist = [
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
        self.add_mode_event_handler("major_6_singlestep_unlit_hit", self.major_6)
        self.add_mode_event_handler("major_6a_singlestep_unlit_hit", self.major_6)
        self.add_mode_event_handler("major_7_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_7a_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_8_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("major_8a_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("major_9_singlestep_unlit_hit", self.major_9)
        self.add_mode_event_handler("extend_char_time", self.extend_time)
        self.add_mode_event_handler('door_switch_to_narrow', self.hide_slide)    
        self.add_mode_event_handler('oogie_switch_to_narrow', self.hide_slide)
        self.add_mode_event_handler("char_resume_and_show", self.resume_and_show)
        self.add_mode_event_handler("char_pause_and_hide", self.remove_all_widgets)          
        self.char_zero_start()
        self.msg = 1
        self.ticks_msg = self.ticks        
        self.add_mode_event_handler("loop_Fever2_played", self.music_track_2_played)
        self.add_mode_event_handler("loop_Fever3_played", self.music_track_3_played)
        self.add_mode_event_handler("loop_Fever4_played", self.music_track_4_played)        



    def music_track_2_played(self, **kwargs):     
        next_track = random.randint(2,4)
        self.machine.events.post("char_zero_music_loop_"+str(next_track))
        self.log.info('queue up next track '+str(next_track))

    def music_track_3_played(self, **kwargs):     
        next_track = random.randint(2,4)
        self.machine.events.post("char_zero_music_loop_"+str(next_track))
        self.log.info('queue up next track '+str(next_track))        

    def music_track_4_played(self, **kwargs):     
        next_track = random.randint(2,4)
        self.machine.events.post("char_zero_music_loop_"+str(next_track))
        self.log.info('queue up next track '+str(next_track))        


    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_zero_messages")  
        self.machine.events.post('char_zero_hide_slide')


    def char_zero_start(self):
        self.log.info("char_zero_start - state: "+str(self.player.char_zero_state))
        if (self.player.char_zero_state == 0):
            self.player.char_zero_state = 1          
            self.ticks = self.player.char_zero_base_ticks
            self.player.char_zero_score = 0
            self.player.char_zero_shots_made = 0
            self.set_shots()
            self.player.char_zero_shot_index = -1
            self.ticks_msg = self.ticks                 
            self.machine.events.post("mode_base_stop_music")            
            self.machine.events.post("char_zero_music_start")
            self.machine.events.post('show_zero_msg_1') 
            self.machine.events.post("char_show_timer")
            self.machine.events.post("ob_pause_and_hide")
            self.machine.events.post("doors_pause_and_hide")
            self.delay.add(name="char_zero_ticker", ms=500, callback=self.ticker)
            self.player.char_timer_ispaused = 0
            self.delay.add(name="char_zero_slide_delay", ms=5000, callback=self.hide_slide)


    def resume_and_show(self, **kwargs):   
        if (self.player.Doors_state == 0 and self.player.OB_Gate_current_mode_state == 0):
            if self.player.char_zero_state > 0:
                self.machine.events.post("char_zero_show_slide")            


    def hide_slide(self, **kwargs):   
        if (self.player.Doors_state != 0 or self.player.OB_Gate_current_mode_state != 0):
            self.remove_all_widgets() 
        self.log.info("char_zero - hide slide")            
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         


    def extend_time(self, time, **kwargs):
        self.log.info("char_zero - time extended " +str(time))
        self.ticks += time*2;
        self.ticks_msg += time*2;
        self.player.char_shared_timeleft = int(self.ticks/2)


    def ticker(self):
        self.log.info("char_zero - 500ms ticks " +str(self.ticks))
        self.player.char_shared_timeleft = int(self.ticks/2)
        self.delay.add(name="char_zero_ticker", ms=500, callback=self.ticker)
        if self.player.char_timer_ispaused == 0:
            self.ticks -= 1;
            if self.ticks <= 0:
                self.char_zero_stop()
            else:
                if  self.ticks_msg-self.ticks > 3:
                    self.msg += 1
                    self.ticks_msg = self.ticks
                    if self.msg > 3: 
                        self.msg = 1                 
                    self.machine.events.post('show_zero_msg_'+str(self.msg))            

            
    def char_zero_stop(self):
        if self.player.char_zero_state == 1:
            self.machine.events.post('char_zero_music_stop')
            self.machine.events.post('char_zero_hide_slide')            
            self.machine.events.post("char_hide_timer")
            self.machine.events.post("stop_all_character_messages")            
            self.log.info("char_zero over")
            if self.player.char_zero_completed:
                self.machine.events.post('char_mode_stopped', char_state="complete", char_mode="Zero")
                self.player.char_zero_state = 2 #completed
                self.machine.events.post('char_zero_completed')                
            else:
                self.machine.events.post('char_mode_stopped', char_state="incomplete", char_mode="Zero")
                self.player.char_zero_state = 0 #ready to start again
                self.machine.events.post('char_zero_failed')                
            self.clear_shots()
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         

            
    def set_shots(self):
        self.clear_shots()
        for x in range(0, 10):
            self.player.char_zero_shotlist[x]["state"] = "orange"
        self.set_shot_lights()


    def set_zero_shot(self):
        self.clear_shots()    	
        self.player.char_zero_shotlist[self.player.char_zero_shot_index]["state"] = "red"             
        self.set_shot_lights()


    def set_shot_lights(self):
        for x in range(0, 10):
            state = self.player.char_zero_shotlist[x]["state"]
            if state != 'off':
                self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="char_Zero", action="add")


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
        if self.player.char_zero_state == 1:
            state = self.player.char_zero_shotlist[shot]["state"]
            if state == "orange":
                #first time for this shot            
                self.set_zero_shot()
                self.machine.events.post('say_here_you_go')
            elif state == "red":
                self.player.char_zero_shot_index = shot
                self.machine.events.post('zero_bark')
                if self.player.char_zero_shots_made < 6:
                    score = self.player.char_zero_shot_points[self.player.char_zero_shots_made]
                else:
                    score = self.player.char_zero_shot_points[6]
                score *= self.player.multiplier_shot_value_list[shot] # 1X, 2X or 3X
                self.player.char_zero_score = score
                self.player.score += score
                self.player.char_zero_shots_made  += 1
                if self.player.char_zero_shots_made >= self.player.char_zero_shots_needed:
                    self.player.char_zero_completed = 1
                self.log.info('char_zero - score pts - ' + str(score))
            else:
                #this shot is unlit, reset the shot
                self.player.char_zero_shot_index = shot
                self.set_zero_shot()
                self.machine.events.post('say_here_you_go')                
                self.player.char_zero_shots_made = 0
            next_shot = self.player.char_zero_shots_made
            if next_shot > 6:
                next_shot = 6
            self.player.char_zero_next = self.player.char_zero_shot_points[next_shot] * self.player.multiplier_shot_value_list[shot]


    def ball_at_zero(self, **kwargs):
        #todo - more time with zero shot?
        if self.player.char_zero_state == 1:        
            self.ticks += 16
            self.ticks_msg += 16
            if self.ticks > 90:
                self.ticks = 90
                self.machine.events.post("zero_mode_time_extended_max")
            else:
                self.machine.events.post("zero_mode_time_extended")
            

    def clear_shots(self):
        for x in range(0, 10):
            state = self.player.char_zero_shotlist[x]["state"]
            if state != 'off':
                self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="char_Zero", action="remove")                        
                self.player.char_zero_shotlist[x]["state"] = "off"


    def mode_stop(self, **kwargs):
        self.log.info('char_zero mode_stop')
        self.char_zero_stop()
        self.clear_shots()


