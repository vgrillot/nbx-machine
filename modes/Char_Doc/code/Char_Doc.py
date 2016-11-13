from mpf.core.mode import Mode
from mpf.core.delays import DelayManager
import random

# Character Mode - Doctor - "A Decided Improvement"
#
# Brief Description:
# 5 major shots are lit. 
# Specifically: Left Ramp, Right Ramp, Left Orbit, Right Orbit, and Left Pops Orbit. 
# You must make all 5 shots within the time limit to complete the mode.
# 
# Scenario:
# Doctor Finklestein is trying to come up with a design for a new assistant, 
# but he needs to find all of his build plans.
# 
# Details:
# When the mode begins, 5 major shots are lit: 
# Left Ramp, Right Ramp, Left Orbit, Right Orbit, and Left Pops Orbit. 
# Each one is worth an increasing number of points.
# Clearing all 5 completes the mode. 
#
# There's a time limit (20-40s) to complete the mode.
# Less time alotted at higher levels.
# 
# Scoring:
# Base score:  200,000
# Each Shot awards  Base * (shot number) eg 200,000  400,000  600,000  etc.
# Shots to the Doctor increase the base by 50,000
# 
# Lighting:
# The shots you need to make will have flashing blue arrows.
# 
# Difficulty Adjustments:
# Very Easy        40 Second Time Limit
# Easy             35 Second Time Limit
# Normal           30 Second Time Limit
# Hard             25 Second Time Limit
# Very Hard        20 Second Time Limit
# 


class Char_Doc(Mode):

    def mode_init(self):
        self.log.info('char_doc mode_init')
        self.delay = DelayManager(self.machine.delayRegistry)
        

    def mode_start(self, **kwargs):
        self.log.info('char_doc mode_start')
        #once per game only        
        if self.player.char_doctor_initialized == 0:
            self.player.char_doctor_initialized = 1
            self.player.char_doctor_times_attempted = 0            
            self.player.char_doctor_times_completed = 0
            self.player.char_doctor_part_collected = [0,0,0,0,0]
            self.player.char_doctor_points_scored = 0
            self.player.char_doctor_shots_made = 0
            self.player.char_doctor_state = 0
            self.player.char_shared_timeleft = 45    #displayed value in seconds        
            self.player.char_doctor_base_ticks = 90  # 90 for 45 seconds
            self.player.char_doctor_base_score = 200000
            # state:  
            # 0 - ready to start.  
            # 1 - intro display (level). 
            # 5 - ready to restart. 
            # 6 - restart display (level, attempts).
            # 10 - running.
            # 15 - failed (time out).
            # 25 - completed
            self.player.char_doctor_shotlist = [
                 {"led":"rgb_lorbit_arrow", "state":"off", "mult":1}
                ,{"led":"rgb_lramp_arrow", "state":"off", "mult":2}
                ,{"led":"rgb_leftloop_arrow", "state":"off", "mult":3}
                ,{"led":"rgb_rramp_arrow", "state":"off", "mult":7}
                ,{"led":"rgb_rorbit_arrow", "state":"off", "mult":8}
                ]
        #handlers for shots 
        self.add_mode_event_handler('sw_doctor', self.doctor_hit)
        self.add_mode_event_handler("major_1_singlestep_unlit_hit", self.major_1)
        self.add_mode_event_handler("major_2_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_2a_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_3_singlestep_unlit_hit", self.major_3)
        self.add_mode_event_handler("major_7_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_7a_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_8_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("major_8a_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("extend_char_time", self.extend_time)  
        self.add_mode_event_handler('door_switch_to_narrow', self.hide_slide)    
        self.add_mode_event_handler('oogie_switch_to_narrow', self.hide_slide)
        self.add_mode_event_handler("char_resume_and_show", self.resume_and_show)
        self.add_mode_event_handler("char_pause_and_hide", self.remove_all_widgets)        
        self.char_doctor_start()
        self.msg = 1
        self.ticks_msg = self.ticks

        
    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_doctor_messages")  
        self.machine.events.post('char_doctor_hide_slide')
        

    def char_doctor_start(self):
        self.log.info("char_doctor_start")
        if (self.player.char_doctor_state == 0):
            #starting mode/level for first time
            self.player.char_doctor_state = 1
            #number of times attempted at this level
            self.player.char_doctor_times_attempted = 1
            #set up timer - TODO - adjust time based on level
            self.ticks = self.player.char_doctor_base_ticks
            self.player.char_doctor_shots_made = 0
            #set parts to not collected
            for x in range(0, 5):
                self.player.char_doctor_part_collected[x] = 0
            self.set_shots()
            self.delay.add(name="char_doctor_ticker", ms=500, callback=self.ticker)
            self.machine.events.post("set_gi_col", red=0, green=80, blue=160)
            #first time, TODO vary based on level?
            self.machine.events.post("mode_base_stop_music")            
            self.machine.events.post("char_doctor_music_start")
            self.machine.events.post("char_show_timer")
            self.machine.events.post("say_improvement")
            self.machine.events.post('show_doctor_msg_1')
            self.ticks_msg = self.ticks
            self.player.char_doctor_jackpot_score = self.player.char_doctor_base_score 
            self.player.char_doctor_next_jackpot_score = self.player.char_doctor_jackpot_score
            self.player.char_timer_ispaused = 0
            self.delay.add(name="char_doctor_slide_delay", ms=5000, callback=self.hide_slide)            
            self.machine.events.post("ob_pause_and_hide")
            self.machine.events.post("doors_pause_and_hide")
        elif (self.player.char_doctor_state == 5):
            #continuing from previous attempt
            self.player.char_doctor_state = 6
            #number of times attempted at this level
            self.player.char_doctor_times_attempted += 1
            #set up timer - TODO - adjust time based on number of attempts and level 
            self.ticks = self.player.char_doctor_base_ticks
            #continue from previous attempt - self.player.char_doctor_part_collected[x]
            self.set_shots()
            self.delay.add(name="char_doctor_ticker", ms=500, callback=self.ticker)
            self.machine.events.post("set_gi_col", red=0, green=80, blue=160)
            #todo, vary these based on number of attempts and level
            self.machine.events.post("char_doctor_music_start")
            self.machine.events.post("char_show_timer")                        
            self.machine.events.post("say_improvement")
            self.machine.events.post('show_doctor_msg_1')
            self.ticks_msg = self.ticks            
            self.player.char_doctor_jackpot_score = self.player.char_doctor_base_score 
            self.player.char_doctor_next_jackpot_score = self.player.char_doctor_jackpot_score * self.player.char_doctor_shots_made
            self.player.char_timer_ispaused = 0
            self.delay.add(name="char_doctor_slide_delay", ms=5000, callback=self.hide_slide)
            self.machine.events.post("ob_pause_and_hide")
            self.machine.events.post("doors_pause_and_hide")


    def resume_and_show(self, **kwargs):   
        if (self.player.Doors_state == 0 and self.player.OB_Gate_current_mode_state == 0):
            if self.player.char_doctor_state > 0:
                self.machine.events.post("char_doctor_show_slide")            
           
           
    def hide_slide(self, **kwargs):   
        if (self.player.Doors_state != 0 or self.player.OB_Gate_current_mode_state != 0):
            self.remove_all_widgets()            
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         

            
    def extend_time(self, time, **kwargs):
        self.log.info("char_doc - time extended " +str(time))
        self.ticks += time*2;
        self.ticks_msg += time*2;        
        self.player.char_shared_timeleft = int(self.ticks/2)
        
            
    def ticker(self):
        self.log.info("char_doc - 500ms ticks " + str(self.ticks))
        if self.player.char_doctor_state == 1 or self.player.char_doctor_state == 6:
            self.player.char_doctor_state = 10
        self.player.char_shared_timeleft = int(self.ticks/2)
        self.delay.add(name="char_doctor_ticker", ms=500, callback=self.ticker)
        if self.player.char_timer_ispaused == 0:
            self.ticks -= 1;
            if self.ticks < 20:
                if self.ticks%2 == 0:
                    self.machine.events.post("set_gi_col_pulse", red=30, green=30, blue=190)
            if self.ticks <= 0:
                #out of time
                self.player.char_doctor_state = 15
                self.char_doctor_stop()
            else:
                if self.ticks_msg - self.ticks > 3:
                    self.ticks_msg = self.ticks
                    self.msg += 1
                    if self.msg > 3: 
                        self.msg = 1
                    if self.ticks > 3:
                        self.machine.events.post('show_doctor_msg_'+str(self.msg))            
       

    def char_doctor_stop(self):
        self.log.info("char_doctor_stop")
        if self.player.char_doctor_state >= 10:
            self.machine.events.post('char_doctor_music_stop')
            self.machine.events.post("char_doctor_hide_slide")
            self.machine.events.post("char_hide_timer") 
            self.machine.events.post("stop_all_character_messages")         
            if self.player.char_doctor_state == 15:  #out of time, incomplete
                self.delay.remove("char_doctor_ticker")
                #todo play failed music?
                self.machine.events.post('char_mode_stopped', char_state="incomplete", char_mode="Doctor")
                self.player.char_doctor_state = 5   #ready to start again
                self.machine.events.post("say_doc_line3") 
                self.machine.events.post('char_doctor_failed')                            
            elif self.player.char_doctor_state == 25:  #completed
                self.machine.events.post('char_mode_stopped', char_state="complete", char_mode="Doctor")
                self.player.char_doctor_times_completed += 1
                self.player.char_doctor_state = 0   #ready to start            
                self.machine.events.post('char_doctor_completed')                                        
            self.clear_shots()
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         


    def set_shots(self):
        for x in range(0, 5):
            #if not collected, flash the LED
            if self.player.char_doctor_part_collected[x] == 0:
                self.player.char_doctor_shotlist[x]["state"] = "blue"
            else:
                self.player.char_doctor_shotlist[x]["state"] = "off"            
        self.set_shot_lights()


    def set_shot_lights(self):
        for x in range(0, 5):
            state = self.player.char_doctor_shotlist[x]["state"]
            if state != 'off':
                led = self.player.char_doctor_shotlist[x]["led"]
                arrow_index = self.player.char_doctor_shotlist[x]["mult"] #1,2,3,7,8
                self.machine.events.post('arrow_change', led_num=arrow_index, script_name=state, mode_name="char_doc", action="add")


    def major_1(self, **kwargs):
        self.handle_shot(0)
    def major_2(self, **kwargs):
        self.handle_shot(1)
    def major_3(self, **kwargs):
        self.handle_shot(2)
    def major_7(self, **kwargs):
        self.handle_shot(3)
    def major_8(self, **kwargs):
        self.handle_shot(4)


    def handle_shot(self, shot):
        self.log.info('char_doc shot ' +str(shot))
        if self.player.char_doctor_state == 10:  #running
            self.score = 0
            state = self.player.char_doctor_shotlist[shot]["state"]
            #not lit, skip it
            if state != "off":
                self.player.char_doctor_shots_made += 1
                self.score = self.player.char_doctor_jackpot_score * self.player.char_doctor_shots_made
                mult_index = self.player.char_doctor_shotlist[shot]["mult"] #1,2,3,7,8
                self.player.char_doctor_part_collected[shot] = 1
                self.score *= self.player.multiplier_shot_value_list[mult_index] # 1X, 2X or 3X 
                self.player.score += self.score
                self.player.char_doctor_points_scored += self.score
                #stop the flash LED
                led = self.player.char_doctor_shotlist[shot]["led"]
                self.machine.events.post('arrow_change', led_num=mult_index, script_name=state, mode_name="char_doc", action="remove")
                self.machine.shows["sc_doc_out"].play(show_tokens=dict(leds=led), speed=8.0, loops=3)			
                self.player.char_doctor_shotlist[shot]["state"] = "off"
                self.player.char_doctor_next_jackpot_score = self.player.char_doctor_jackpot_score * (self.player.char_doctor_shots_made+1)
                if self.player.char_doctor_shots_made == 5:
                    self.machine.events.post('say_doc_line2')                
                    self.player.char_doctor_state = 25
                    self.char_doctor_stop()
                else:
                    self.machine.events.post('say_doc_line')


    def doctor_hit(self, **kwargs):
        if self.player.char_doctor_state == 10:
            self.log.info('char_doc hit')
            self.player.char_doctor_jackpot_score += 50000
            self.player.char_doctor_next_jackpot_score = self.player.char_doctor_jackpot_score * (self.player.char_doctor_shots_made+1)

            
    def clear_shots(self):
        for x in range(0, 5):
            state = self.player.char_doctor_shotlist[x]["state"]
            if state != 'off':
                led = self.player.char_doctor_shotlist[x]["led"]
                mult_index = self.player.char_doctor_shotlist[x]["mult"] #1,2,3,7,8
                self.machine.events.post('arrow_change', led_num=mult_index, script_name="blue", mode_name="char_doc", action="remove")                        
                self.player.char_doctor_shotlist[x]["state"] = "off"


    def mode_stop(self, **kwargs):
        self.log.info('char_doctor_mode_stop')
        self.char_doctor_stop()

