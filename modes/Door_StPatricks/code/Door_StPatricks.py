from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Door_StPatricks    
# Hinterlands Door Mode - "Pot o' Gold"
# 
# Brief Description
# Shoot to the Hinterlands to collect the Pot o' Gold value 
# and complete the mode, but the value should be built up by the pop bumpers first.
# 
# Scenario
# A leprechaun has snuck into Halloween Town. More specifically, into a 
# cash vault in Oogie Boogie's Lair. He must collect as much gold for his pot as he can and get
# back home before he gets caught!
# 
# Details
# All you have to do to complete this timed mode is shoot the ball up the ramps, 
# which will collect the score for this mode. However, when the mode starts,
# this shot is only worth 100,000. Each pop bumper hit adds another 100,000 to this value 
# with no cap, thus the idea is to collect as many pop bumper hits as you feel
# safe to, then shoot for the Hinterlands. The pop-up post to divert to the pops will fire 
# on orbit shots for the duration of this mode.
# 
# Scoring
# Base Ramp Value                   100,000
# Left Ramp Increase per Pop        100,000
# Base Alternate Ramp Increase      250,000
# 
# Lighting
# The pop bumpers will be flashing yellow during this mode while the 
# Hinterlands shot will flash both its triangle and circle yellow.
# 
# Difficulty Adjustments
# Very Easy         40 Second Time Limit
# Easy              35 Second Time Limit
# Normal            30 Second Time Limit
# Hard              25 Second Time Limit
# Very Hard         20 Second Time Limit

class Door_StPatricks(Mode):

    def mode_init(self):
        self.log.info('Door_StPatricks mode_init')

    def mode_start(self, **kwargs):
        self.log.info('Door_StPatricks mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.ticks = 90  #90 = 45 seconds
        self.player.door_stpatricks_running = 0
        self.player.door_stpatricks_ramp_score = 0
        self.player.door_stpatricks_base_ticks = 90  #90 = 45 seconds
        self.player.door_stpatricks_timeleft = int(self.player.door_stpatricks_base_ticks/2)        
        self.player.door_stpatricks_ramp_value = 100000
        self.add_mode_event_handler("major_2_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_2a_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler('sw_bumpertop', self.pophit)
        self.add_mode_event_handler('sw_bumperleft', self.pophit)
        self.add_mode_event_handler('sw_bumperright', self.pophit)
        self.add_mode_event_handler("extend_door_time", self.extend_time) 
        self.add_mode_event_handler('door_switch_to_narrow', self.switch_to_narrow)        
        self.add_mode_event_handler('door_switch_to_wide', self.switch_to_wide) 
        self.add_mode_event_handler("doors_resume_and_show", self.reshow_screen)
        self.add_mode_event_handler("doors_pause_and_hide", self.remove_all_widgets)         
        self.stpatricks_start()
        self.msg = 1
        self.ticks_msg = self.ticks
        self.last_ramp = -1
        

    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_stpatricks_messages")  
        self.machine.events.post('remove_stpatricks_slide_narrow')
        self.machine.events.post('remove_stpatricks_slide_wide')
        self.machine.events.post('remove_stpatricks_slide_full')
        
        
    def reshow_screen(self, **kwargs):   
        self.log.info("reshow_screen")          
        if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        

            
    def stpatricks_start(self):
        self.log.info("holiday stpatricks start")
        if (self.player.door_stpatricks_running == 0):
            self.ticks = self.player.door_stpatricks_base_ticks
            self.player.door_stpatricks_timeleft = int(self.player.door_stpatricks_base_ticks/2)                        
            self.player.door_stpatricks_ramp_value = 100000
            self.player.door_stpatricks_ramp_score = 0
            self.player.door_stpatricks_running = 1
            self.machine.events.post("holiday_stpatricks_music_start")
            self.set_lights()
            self.machine.events.post('popuppost_enable_up')
            self.machine.events.post('show_stpatricks_slide_full')  
            self.machine.events.post('char_pause_and_hide')
            self.machine.events.post("ob_pause_and_hide")
            self.player.door_timer_ispaused = 0                    
            self.delay.add(name="show_full_stpatricks_intro_remover", ms=5000, callback=self.show_screen)

            
    def show_screen(self, **kwargs):
        self.log.info( "5 seconds passed, show narrow or wide" )
        self.ticks_msg = self.ticks
        self.delay.add(name="holiday_stpatricks_ticker", ms=500, callback=self.ticker)          
        if self.player.door_timer_ispaused == 0:   
            self.machine.events.post("char_resume_and_show")
            self.machine.events.post("ob_resume_and_show")         
            self.reshow_screen()        
            if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                self.machine.events.post('show_stpatricks_msg_1_n')                
            else:
                self.machine.events.post('show_stpatricks_msg_1')                                  


    def ticker(self):
        self.log.info("Door_stpatricks - 500ms ticks " + str(self.ticks))
        self.player.door_stpatricks_timeleft = int(self.ticks/2)        
        self.delay.add(name="holiday_stpatricks_ticker", ms=500, callback=self.ticker)        
        self.machine.events.post("holiday_stpatricks_countdown")
        if self.player.door_timer_ispaused == 0:
            self.ticks -= 1;
            if self.ticks <= 0:
                self.stpatricks_stop()
            else:
                if  self.ticks_msg-self.ticks > 3:
                    self.msg += 1
                    self.ticks_msg = self.ticks
                    if self.msg > 3: 
                        self.msg = 1                 
                    if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                        self.machine.events.post('show_stpatricks_msg_'+str(self.msg)+'_n')            
                    else:
                        self.machine.events.post('show_stpatricks_msg_'+str(self.msg)) 

                
    def switch_to_narrow(self, **kwargs):   
        self.remove_all_widgets()        
        self.machine.events.post('show_stpatricks_slide_narrow')

        
    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()
        self.machine.events.post('show_stpatricks_slide_wide')

        
    def extend_time(self, time, **kwargs):
        self.log.info("door_stpatricks - time extended " +str(time))
        self.ticks += time*2;
        self.ticks_msg += time*2;        
        self.player.door_stpatricks_timeleft = int(self.ticks/2)
            
            
    def stpatricks_stop(self):
        if self.player.door_stpatricks_running == 1:
            self.machine.events.post('holiday_stpatricks_music_stop')
            self.log.info("holiday stpatricks over")
            if self.player.door_stpatricks_ramp_score >= 0:
                self.machine.events.post('holiday_mode_stopped', state="complete")
                self.player.door_stpatricks_running = 2 #completed
            else:
                self.machine.events.post('holiday_mode_stopped', state="incomplete")
                self.player.door_stpatricks_running = 0 #ready to start again
            self.reset_lights()
            self.machine.events.post('popuppost_disable_up')
        self.machine.events.post('remove_stpatricks_messages')
        self.machine.events.post('remove_stpatricks_narrow')
        self.machine.events.post('remove_stpatricks_wide')
        self.machine.events.post('oogie_switch_to_wide')
        self.machine.events.post("char_resume_and_show")

        
    def major_2(self,**kwargs):
        if self.player.door_stpatricks_running == 1:
            self.log.info("Door_stpatricks - ramp")
            self.score = self.player.door_stpatricks_ramp_value
            self.score *= self.player.multiplier_shot_value_list[2] # 1X, 2X or 3X 
            self.player.door_stpatricks_ramp_score += self.score
            self.player.score += self.score
            self.machine.events.post('stpatricks_ramp_scored_left')
            self.stpatricks_stop()
    
        
    def pophit(self,**kwargs):
        self.log.info("Door_stpatricks - pop hit")
        if self.player.door_stpatricks_running == 1:
            self.player.door_stpatricks_ramp_value += 100000
            self.machine.events.post('stpatricks_ramp_value_increased', value=self.player.door_stpatricks_ramp_value )
            self.msg = 3
            
    
    def set_lights(self):
        #rgb_lramp_arrow
        script_name = "lime"
        self.machine.events.post('arrow_change', led_num=2, script_name=script_name, mode_name="Door_St", action="add")        
        #rgb_lorbit_arrow
        script_name = "lime"
        self.machine.events.post('arrow_change', led_num=1, script_name=script_name, mode_name="Door_St", action="add")        
        #rgb_rorbit_arrow
        script_name = "lime"
        self.machine.events.post('arrow_change', led_num=8, script_name=script_name, mode_name="Door_St", action="add")        
        self.machine.events.post('toy_pops_override', script_name='sc_pop_yellow')

        
    def reset_lights(self):
        #rgb_lramp_arrow
        script_name = "lime"
        self.machine.events.post('arrow_change', led_num=2, script_name=script_name, mode_name="Door_St", action="remove")        
        #rgb_lorbit_arrow
        script_name = "lime"
        self.machine.events.post('arrow_change', led_num=1, script_name=script_name, mode_name="Door_St", action="remove")        
        #rgb_rorbit_arrow
        script_name = "lime"
        self.machine.events.post('arrow_change', led_num=8, script_name=script_name, mode_name="Door_St", action="remove")        
        self.machine.events.post('toy_pops_restore')
    
    
    def mode_stop(self, **kwargs):
        self.log.info('Door_StPatricks mode_stop')
        self.stpatricks_stop()
        
        