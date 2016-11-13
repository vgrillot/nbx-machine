from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Oogie Boogie Mode #5 - "Jack vs. Oogie Boogie"                                                                                                                 Page 35
# 
# Brief Description
# Several major shots need to be cleared, but the time limit is too small to work within. 
# You must shoot the spinner to build up more time, then you can focus on the
# major shots.
# 
# Scenario
# Jack and Oogie Boogie are battling it out! 
# Actually, it's more precise to say Oogie Boogie is sending Jack through a gauntlet full of traps 
# and Jack's having to dodge everything.
# 
# Details
# This mode only gives you a 15 second time limit to shoot 8 of the major shots. 
# (The only two major shots not lit are the spinner and Graveyard.) 
# This is too small of a time limit, obviously, so you need to get more time by shooting the spinner. 
# Each spinner spin adds 2 seconds to the timer. Once a major shot is cleared it unlights.
# Hit all eight lit major shots and the mode is completed.
# 
# Scoring
# Lit Major Shot             1,000,000
# Last Major Shot            5,000,000
# Spinner Spin               20,000 and +2 Seconds
# 
# Lighting
# Major shots you still need to hit flash a yellow triangle. 
# The spinner rapidly flashes both a blue triangle and circle.
#            
# Difficulty Adjustments
# Very Easy          20 second initial time limit, 7 major shots to shoot.
# Easy               15 second initial time limit, 7 major shots to shoot.
# Normal             15 second initial time limit, 8 major shots to shoot.
# Hard               12 second initial time limit, 8 major shots to shoot.
# Very Hard          10 second initial time limit, 8 major shots to shoot.

class OB_Jack(Mode):

    def mode_init(self):
        self.log.info('OB_Jack mode_init')

    def mode_start(self, **kwargs):
        self.log.info('OB_Jack mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.OB_mode_5_started == 0:
            #once per game only
            self.player.OB_mode_5_started = 1
            self.player.OB_mode_5_running = 0
            self.player.OB_Jack_times_attempted = 0            
            self.player.OB_Jack_times_completed = 0
            self.player.OB_Jack_points_scored = 0
            self.player.OB_Jack_shots_made = 0
            self.player.OB_Jack_state = 0
            self.player.OB_Jack_base_ticks = 30              
            self.player.OB_Jack_timeleft = int(self.player.OB_Jack_base_ticks/2)
            self.player.OB_Jack_base_score = 1000000
            self.player.OB_Jack_shotlist = [
                 {"led":"rgb_mayor_arrow", "state":"off", "mult":0}
                ,{"led":"rgb_lorbit_arrow", "state":"off", "mult":1} #spinner                
                ,{"led":"rgb_lramp_arrow", "state":"off", "mult":2}
                ,{"led":"rgb_leftloop_arrow", "state":"off", "mult":3}
                ,{"led":"rgb_oogie_cw_arrow", "state":"off", "mult":4}                
                ,{"led":"rgb_oogie_ccw_arrow", "state":"off", "mult":5}                
                ,{"led":"rgb_rramp_arrow", "state":"off", "mult":7}
                ,{"led":"rgb_rorbit_arrow", "state":"off", "mult":8}
                ,{"led":"rgb_soup_arrow", "state":"off", "mult":9}                                
                ]
        #handlers for shots 
        self.add_mode_event_handler('sw_sally', self.spinner_hit)
        self.add_mode_event_handler("major_0_singlestep_unlit_hit", self.major_0)        
        self.add_mode_event_handler("major_2_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_2a_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_3_singlestep_unlit_hit", self.major_3)
        self.add_mode_event_handler("major_4_singlestep_unlit_hit", self.major_4)
        self.add_mode_event_handler("major_5_singlestep_unlit_hit", self.major_5)
        self.add_mode_event_handler("major_5a_singlestep_unlit_hit", self.major_5)
        self.add_mode_event_handler("major_7_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_7a_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_8_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("major_8a_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("major_9_singlestep_unlit_hit", self.major_9)        
        self.add_mode_event_handler("extend_OB_time", self.extend_time)   
        self.add_mode_event_handler('oogie_switch_to_narrow', self.switch_to_narrow)        
        self.add_mode_event_handler('oogie_switch_to_wide', self.switch_to_wide)
        self.add_mode_event_handler("ob_resume_and_show", self.reshow_screen) 
        self.add_mode_event_handler("ob_pause_and_hide", self.remove_all_widgets)
        self.ticks = self.player.OB_Jack_base_ticks        
        self.msg = 1
        self.ticks_msg = self.ticks
        self.start_battle()

        
    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_OB_Jack_messages")  
        self.machine.events.post('remove_OB_Jack_slide_wide')
        self.machine.events.post('remove_OB_Jack_slide_narrow')
        self.machine.events.post('remove_OB_Jack_slide_intro')
        

    def reshow_screen(self, **kwargs):   
        if self.player.Doors_state == 1:  #door mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        


    def start_battle(self):
        self.log.info("OB_Jack_start")
        if (self.player.OB_mode_5_running == 0):
            self.player.OB_mode_5_running = 1
            #starting mode/level for first time
            self.player.OB_Jack_state = 1
            self.ticks = self.player.OB_Jack_base_ticks
            self.player.OB_Jack_shots_made = 0
            self.set_shots()
            self.machine.events.post("set_gi_col", red=160, green=10, blue=10)
            self.machine.events.post("mode_base_stop_music")            
            self.machine.events.post("OB_Jack_music_start")
            self.ticks_msg = self.ticks
            self.machine.events.post('show_OB_Jack_slide_intro') 
            self.machine.events.post('char_pause_and_hide') 
            self.machine.events.post("doors_pause_and_hide")
            self.player.ob_timer_ispaused = 0                    
            self.delay.add(name="show_full_OB_Jack_intro_remover", ms=5000, callback=self.show_screen)


    def show_screen(self, **kwargs):
        self.log.info( "5 seconds passed, show narrow or wide" )
        self.delay.add(name='OB_mode_5_ticker', ms=500, callback=self.ticker)
        if self.player.ob_timer_ispaused == 0:        
            self.machine.events.post("char_resume_and_show")
            self.machine.events.post("doors_resume_and_show") 
            self.reshow_screen()        
            if self.player.Doors_state == 1:  #door mode running
                self.machine.events.post('show_OB_Jack_msg_1_n')            
            else:
                self.machine.events.post('show_OB_Jack_msg_1')            


    def ticker(self):
        self.log.info("500ms ticks " + str(self.ticks))
        self.player.OB_Jack_timeleft = int(self.ticks/2)
        self.delay.add(name="OB_Jack_ticker", ms=500, callback=self.ticker)        
        if self.player.ob_timer_ispaused == 0:
            self.ticks -= 1;
            if self.ticks <= 0:
                #out of time
                self.player.OB_Jack_state = 15
                self.end_battle()
            else:
                if self.ticks_msg - self.ticks > 3:
                    self.ticks_msg = self.ticks
                    self.msg += 1
                    if self.msg > 3: 
                        self.msg = 1
                    if self.ticks > 2:                                        
                        if self.player.Doors_state == 1:  #door mode running            	
                            self.machine.events.post('show_OB_Jack_msg_'+str(self.msg)+'_n')            
                        else:
                            self.machine.events.post('show_OB_Jack_msg_'+str(self.msg))            

            
    def extend_time(self, time, **kwargs):
        self.log.info("OB_Jack - time extended " +str(time))
        self.ticks += time*2;
        self.ticks_msg += time*2;        
        self.player.OB_Jack_timeleft = int(self.ticks/2)

        
    def switch_to_narrow(self, **kwargs):   
        self.remove_all_widgets()    
        self.machine.events.post('show_OB_Jack_slide_narrow')


    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()    
        self.machine.events.post('show_OB_Jack_slide_wide')

        
    def end_battle(self):
        self.log.info("OB_Jack_stop")    
        if (self.player.OB_mode_5_running == 1):
            self.player.OB_mode_5_running = 2
            self.machine.events.post('OB_Jack_music_stop')
            self.log.info("OB mode 5 over")
            self.delay.remove("OB_Jack_ticker")            
            self.machine.events.post('advance_to_next_mode')
            self.machine.events.post("ob_hide_timer") 
            if self.player.OB_Jack_shots_made < 8:  
                #out of time, incomplete
                #todo play failed music?
                self.machine.events.post('ob_mode_stopped', ob_state="incomplete", ob_mode="5")
                self.machine.events.post('OB_Jack_failed')                            
            else:
                #completed
                self.machine.events.post('ob_mode_stopped', ob_state="complete", ob_mode="5")
                self.machine.events.post('OB_Jack_completed')                                        
            self.clear_shots()
        self.machine.events.post("char_resume_and_show")                    
        self.machine.events.post('door_switch_to_wide')                 
        self.remove_all_widgets()        


    def set_shots(self):
        for x in range(0, 9):
            self.player.OB_Jack_shotlist[x]["state"] = "yellow"
            if x == 1:
                self.player.OB_Jack_shotlist[x]["state"] = "blue"            
        self.set_shot_lights()


    def set_shot_lights(self):
        for x in range(0, 9):
            state = self.player.OB_Jack_shotlist[x]["state"]
            if state != 'off':
                led = self.player.OB_Jack_shotlist[x]["led"]
                arrow_index = self.player.OB_Jack_shotlist[x]["mult"] 
                self.machine.events.post('arrow_change', led_num=arrow_index, script_name=state, mode_name="OB_Jack", action="add")


    def major_0(self, **kwargs):
        self.handle_shot(0)
        
    def major_2(self, **kwargs):
        self.handle_shot(1)
    def major_3(self, **kwargs):
        self.handle_shot(2)
    def major_4(self, **kwargs):
        self.handle_shot(3)
    def major_5(self, **kwargs):
        self.handle_shot(4)
        
    def major_7(self, **kwargs):
        self.handle_shot(5)
    def major_8(self, **kwargs):
        self.handle_shot(6)
    def major_9(self, **kwargs):
        self.handle_shot(7)


    def handle_shot(self, shot):
        self.log.info('OB_Jack shot ' +str(shot))
        if self.player.OB_Jack_state == 1:  #running
            self.score = 0
            state = self.player.OB_Jack_shotlist[shot]["state"]
            #not lit, skip it
            if state != "off":
                self.player.OB_Jack_shots_made += 1
                self.score = self.player.OB_Jack_jackpot_score
                mult_index = self.player.OB_Jack_shotlist[shot]["mult"] #1,2,3,7,8
                self.score *= self.player.multiplier_shot_value_list[mult_index] # 1X, 2X or 3X 
                self.player.score += self.score
                self.player.OB_Jack_points_scored += self.score
                #stop the flash LED
                led = self.player.OB_Jack_shotlist[shot]["led"]
                self.machine.events.post('arrow_change', led_num=mult_index, script_name=state, mode_name="OB_Jack", action="remove")
#                self.machine.shows["sc_doc_out"].play(show_tokens=dict(leds=led), speed=8.0, loops=3)			
                self.player.OB_Jack_shotlist[shot]["state"] = "off"
                if self.player.OB_Jack_shots_made == 8:
                    self.machine.events.post('say_jack_success_line')                
                    self.end_battle()
                else:
                    self.machine.events.post('say_jack_fail_line')


    def spinner_hit(self, **kwargs):
        if self.player.OB_Jack_state > 0:
            self.log.info('spinner hit - add 2 seconds')
            self.player.score += 20000
            self.extend_time(time=2)

            
    def clear_shots(self):
        for x in range(0, 8):
            state = self.player.OB_Jack_shotlist[x]["state"]
            if state != 'off':
                led = self.player.OB_Jack_shotlist[x]["led"]
                mult_index = self.player.OB_Jack_shotlist[x]["mult"] #1,2,3,7,8
                self.machine.events.post('arrow_change', led_num=mult_index, script_name="blue", mode_name="OB_Jack", action="remove")                        
                self.player.OB_Jack_shotlist[x]["state"] = "off"


    def mode_stop(self, **kwargs):
        self.log.info('OB_Jack_mode_stop')
        self.end_battle()

        
