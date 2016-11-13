from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random
#
# Door_Thanksgiving  
# Hinterlands Door Mode - "Collecting Food for a feast"
#
# Brief Description
# Loop mode 
# - around oogie
# - inner loop
# Soup - doubles the values
# 
# Scenario
# Sally has made a meal for Jack.  
# Jack must lift the basket up to his window by completing loops.
#
# soup ( butterfly animation)
# 
# Details
# Meal value starts at 250,000
# Every loop increases meal value by 250,000.
# Soup shot will score the meal value and doubles the loop increment value.
#
# Scoring
# Base Meal Value                 250,000
# Loop increments                 250,000
# Soup collects and doubles increment.
# 
# Lighting
# The soup and loops shots will flash white triangles.
# 
# Difficulty Adjustments
# Very Easy        60 Second Time Limit, 1,500,000 Points to Complete
# Easy             50 Second Time Limit, 2,000,000 Points to Complete
# Normal           45 Second Time Limit, 2,500,000 Points to Complete
# Hard             40 Second Time Limit, 3,000,000 Points to Complete
# Very Hard        35 Second Time Limit, 3,500,000 Points to Complete                                                                                                                      Page 31

class Door_Thanksgiving(Mode):

    def mode_init(self):
        self.log.info('Door_Thanksgiving mode_init')


    def mode_start(self, **kwargs):
        self.log.info('Door_thanksgiving mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)

        self.player.door_thanksgiving_running = 0
        
        self.player.door_thanksgiving_soup_score = 0
        self.player.door_thanksgiving_soup_value = 250000
        self.player.door_thanksgiving_soup_inc = 250000
        self.player.door_thanksgiving_loop_value = 50000        
        self.player.door_thanksgiving_score_needed = 2500000

        self.ticks = 0
        self.player.door_thanksgiving_base_ticks = 90  #90 = 45 seconds
        self.player.door_thanksgiving_timeleft = int(self.player.door_thanksgiving_base_ticks/2)
        
        self.add_mode_event_handler("major_3_singlestep_unlit_hit", self.major_3)
        self.add_mode_event_handler("major_4_singlestep_unlit_hit", self.major_4)
        self.add_mode_event_handler("major_5_singlestep_unlit_hit", self.major_5)
        self.add_mode_event_handler("major_5a_singlestep_unlit_hit", self.major_5)
        self.add_mode_event_handler("major_9_singlestep_unlit_hit", self.soup)
        
        self.add_mode_event_handler("extend_door_time", self.extend_time)
        self.add_mode_event_handler('door_switch_to_narrow', self.switch_to_narrow)        
        self.add_mode_event_handler('door_switch_to_wide', self.switch_to_wide)                
        self.add_mode_event_handler("doors_resume_and_show", self.reshow_screen)
        self.add_mode_event_handler("doors_pause_and_hide", self.remove_all_widgets) 
        self.thanksgiving_start()
        self.msg = 1
        self.ticks_msg = self.ticks
       

    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_thanks_messages")  
        self.machine.events.post('remove_thanks_slide_narrow')
        self.machine.events.post('remove_thanks_slide_wide')
        self.machine.events.post('remove_thanks_slide_full')
        
        
    def reshow_screen(self, **kwargs):   
        if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        
                 
                
    def thanksgiving_start(self):
        self.log.info("holiday thanksgiving start")
        if (self.player.door_thanksgiving_running == 0):
            self.ticks = self.player.door_thanksgiving_base_ticks
            self.player.door_thanksgiving_timeleft = int(self.player.door_thanksgiving_base_ticks/2)            
            self.player.door_thanksgiving_soup_value = 250000
            self.player.door_thanksgiving_score_needed = 2500000
            self.player.door_thanksgiving_soup_inc = 250000            
            self.player.door_thanksgiving_loop_value = 50000
            self.player.door_thanksgiving_soup_score = 0
            self.set_shot_lights()
            self.player.door_thanksgiving_running = 1
            self.machine.events.post("turn_on_oogie_loop_mode")            
            self.machine.events.post("holiday_thanksgiving_music_start")            
            self.machine.events.post('show_thanks_slide_full')
            self.machine.events.post('char_pause_and_hide')
            self.machine.events.post("ob_pause_and_hide")
            self.player.door_timer_ispaused = 0                    
            self.delay.add(name="show_full_thanks_intro_remover", ms=5000, callback=self.show_screen)

            
    def show_screen(self, **kwargs):
        self.log.info( "5 seconds passed, show narrow or wide" )
        self.ticks_msg = self.ticks 
        self.delay.add(name="holiday_thanksgiving_ticker", ms=500, callback=self.ticker)        
        if self.player.door_timer_ispaused == 0:        
            self.machine.events.post("char_resume_and_show")
            self.machine.events.post("ob_resume_and_show")         
            self.reshow_screen()        
            if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                self.machine.events.post('show_thanks_msg_1_n')                
            else:
                self.machine.events.post('show_thanks_msg_1')                                  
            
           
    def ticker(self):
        self.log.info("Door_thanksgiving - 500ms ticks "+ str(self.ticks))
        self.player.door_thanksgiving_timeleft = int(self.ticks/2)
        if self.player.door_thanksgiving_running == 1:         
            self.delay.add(name="holiday_thanksgiving_ticker", ms=500, callback=self.ticker)        
        if self.player.door_timer_ispaused == 0:
            self.ticks -= 1;
            if self.ticks <= 0:
                self.thanksgiving_stop()
            else:
                if  self.ticks_msg-self.ticks > 3:
                    self.msg += 1
                    self.ticks_msg = self.ticks
                    if self.msg > 3: 
                        self.msg = 1                  
                    if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                        self.machine.events.post('show_thanks_msg_'+str(self.msg)+'_n')            
                    else:
                        self.machine.events.post('show_thanks_msg_'+str(self.msg)) 

            
    def switch_to_narrow(self, **kwargs):   
        self.remove_all_widgets()   
        self.machine.events.post('show_thanks_slide_narrow')

        
    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()   
        self.machine.events.post('show_thanks_slide_wide')

        
    def extend_time(self, time, **kwargs):
        self.log.info("door_thanksgiving - time extended " +str(time))
        self.ticks += time*2;
        self.ticks_msg += time*2;        
        self.player.door_thanksgiving_timeleft = int(self.ticks/2)


    def thanksgiving_stop(self):
        if self.player.door_thanksgiving_running == 1:
            self.machine.events.post('holiday_thanksgiving_music_stop')
            self.log.info("holiday thanksgiving over")
            if self.player.door_thanksgiving_soup_score >= self.player.door_thanksgiving_score_needed:
                self.machine.events.post('holiday_mode_stopped', state="complete")
                self.player.door_thanksgiving_running = 2 #completed
            else:
                self.machine.events.post('holiday_mode_stopped', state="incomplete")
                self.player.door_thanksgiving_running = 0 #ready to start again
            self.reset_shots_lights()
        self.machine.events.post('remove_thanks_messages')
        self.machine.events.post('remove_thanks_narrow')
        self.machine.events.post('remove_thanks_wide')
        self.machine.events.post('oogie_switch_to_wide')
        self.machine.events.post("char_resume_and_show")
        self.machine.events.post("turn_off_oogie_loop_mode")                    
            

    def set_shot_lights(self):
        self.machine.events.post('arrow_change', led_num=3, script_name='white', mode_name="Door_Thanks", action="add")
        self.machine.events.post('arrow_change', led_num=4, script_name='white', mode_name="Door_Thanks", action="add")
        self.machine.events.post('arrow_change', led_num=5, script_name='white', mode_name="Door_Thanks", action="add")
        self.machine.events.post('arrow_change', led_num=9, script_name='white', mode_name="Door_Thanks", action="add")


    def major_3(self, **kwargs):
        self.handle_shot(3)
    def major_4(self, **kwargs):
        self.handle_shot(4)
    def major_5(self, **kwargs):
        self.handle_shot(5)

        
    def handle_shot(self, shot):
        if self.player.door_thanksgiving_running == 1:
            self.player.door_thanksgiving_soup_value += self.player.door_thanksgiving_soup_inc
            self.machine.events.post('thanksgiving_soup_value_increased')
            self.player.score += self.player.door_thanksgiving_loop_value            


    def soup(self, **kwargs):
        if self.player.door_thanksgiving_running == 1:
            self.score = self.player.door_thanksgiving_soup_value
            self.score *= self.player.multiplier_shot_value_list[9] # 1X, 2X or 3X 
            self.player.door_thanksgiving_soup_score += self.score
            self.player.score += self.score
            self.player.door_thanksgiving_soup_inc *= 2
            if self.player.door_thanksgiving_soup_inc > 2000000:
                self.player.door_thanksgiving_soup_inc = 2000000
            self.machine.events.post('thanksgiving_soup_score_increased', 
                    value=self.player.door_thanksgiving_soup_score )

                    
    def reset_shots_lights(self):
        self.machine.events.post('arrow_change', led_num=3, script_name='white', mode_name="Door_Thanks", action="remove")
        self.machine.events.post('arrow_change', led_num=4, script_name='white', mode_name="Door_Thanks", action="remove")
        self.machine.events.post('arrow_change', led_num=5, script_name='white', mode_name="Door_Thanks", action="remove")
        self.machine.events.post('arrow_change', led_num=9, script_name='white', mode_name="Door_Thanks", action="remove")



    def mode_stop(self, **kwargs):
        self.log.info('Door_thanksgiving mode_stop')
        self.thanksgiving_stop()
        

