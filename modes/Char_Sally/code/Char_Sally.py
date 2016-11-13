from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Character Mode - "Sally's Stitches"                                                                                                                                   Page 17
# 
# Brief Description
# Shoot the spinner to get lots of points and to complete the mode before time runs out. 
# Upper right flipper is disabled for the duration.
# 
# Scenario
# Sally's arm has come off! She must stitch it back on before anyone comes looking for her.
# 
# Details
# When the mode begins and for the duration of the mode, the upper right flipper is 
# NO-HOLD and the popup post will be on standby to raise when the ball
# enters the loops. You must get 100 spinner spins to complete the mode and have 30 seconds to 
# do so within, which seems very tricky, but you can upgrade the
# spinner during this mode by getting the ball into the pop bumpers. pop hits will give  
# spinner upgrades so that each spin is now worth double. more pop hits
# afterwards will triple the spinner. Repeat up to 5X.  
# The shot multiplier will also factor in, thus a tripler 
# on the spinner shot combined with a 5X upgrade will award 15 spins at a time!
#
# 
# Scoring
# Spinner Spin               25,000 (multiplied by upgrades)
# inner loop - scores 10 spins.  (20, 30 with multipliers)  *25,000 points
# 
# Lighting
# The pops will all flash orange to indicate that hitting them can get you an upgrade. 
# Once all upgrades are acquired, the pop bumpers stop flashing. The spinner
# shot will have a flashing yellow triangle.
# 
# Difficulty Adjustments
# Very Easy         40 Seconds, 60 Spins Needed,   1,3,6,10   Pops for Upgrades
# Easy              30 Seconds, 80 Spins Needed,   2,5,10,17  Pops for Upgrades
# Normal            30 Seconds, 100 Spins Needed,  3,8,15,24  Pops for Upgrades
# Hard              30 Seconds, 120 Spins Needed,  4,10,18,28 Pops for Upgrades
# Very Hard         25 Seconds, 150 Spins Needed,  5,12,21,32 Pops for Upgrades
#
# orbits will pop up the post until all pops are at max

class Char_Sally(Mode):

    def mode_init(self):
        self.log.info('char_Sally mode_init')

    def mode_start(self, **kwargs):
        self.log.info( 'char_Sally mode_start' )
        self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.char_sally_initialized == 0:
            self.player.char_sally_initialized = 1
            self.player.char_sally_state = 0            
            self.player.char_sally_times_attempted = 0            
            self.player.char_sally_times_completed = 0
            
            #these should come from settings
            self.player.char_sally_base_ticks = 60 #30 seconds
            self.player.char_sally_pop_upgrade_1 = 3
            self.player.char_sally_pop_upgrade_2 = 8
            self.player.char_sally_pop_upgrade_3 = 15
            self.player.char_sally_pop_upgrade_4 = 24                        
            self.player.char_sally_spins_needed = 100
            
        self.player.char_sally_pops = 0        
        self.player.char_sally_spin_value = 1

        self.player.char_shared_timeleft = int(self.player.char_sally_base_ticks/2)
        self.player.char_sally_shotlist = [
            {"led":"rgb_rorbit_arrow", "state":"off"}
            ,{"led":"rgb_lorbit_arrow", "state":"off"}
            ,{"led":"rgb_leftloop_arrow", "state":"off"}
            ]
        self.player.sally_show_handles = [0] * 3
        self.add_mode_event_handler('sw_sally', self.spin)        
        self.add_mode_event_handler('sw_bumpertop', self.pophit)
        self.add_mode_event_handler('sw_bumperleft', self.pophit)
        self.add_mode_event_handler('sw_bumperright', self.pophit)
        self.add_mode_event_handler("major_3_singlestep_unlit_hit", self.major_3)        
        self.add_mode_event_handler("extend_char_time", self.extend_time) 
        self.add_mode_event_handler('door_switch_to_narrow', self.hide_slide)    
        self.add_mode_event_handler('oogie_switch_to_narrow', self.hide_slide)
        self.add_mode_event_handler("char_resume_and_show", self.resume_and_show)
        self.add_mode_event_handler("char_pause_and_hide", self.remove_all_widgets)          
        self.char_sally_start()
        self.msg = 1        
        self.ticks_msg = self.ticks                    
        

    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_sally_messages")  
        self.machine.events.post('char_sally_hide_slide')


    def char_sally_start(self):
        self.log.info( "char_sally start")
        if (self.player.char_sally_state == 0):
            self.player.char_sally_state = 1
            self.player.char_sally_times_attempted = 0            
            self.ticks = self.player.char_sally_base_ticks
            self.player.char_sally_spins_needed = 100
            self.player.char_sally_pops = 0
            self.player.char_sally_spin_value = 1
            self.player.char_sally_spin_worth = self.player.char_sally_spin_value*self.player.multiplier_shot_value_list[1]
            self.ticks_msg = self.ticks                        
            self.set_lights()
            self.disable_flipper()
            self.machine.events.post("char_sally_music_start")
            self.machine.events.post('show_sally_msg_1')
            self.machine.events.post('popuppost_enable_up')
            self.machine.events.post("set_gi_col", red=150, green=40, blue=40)   
            self.machine.events.post("char_show_timer")
            self.machine.events.post("ob_pause_and_hide")
            self.machine.events.post("doors_pause_and_hide")
            self.delay.add(name="char_sally_ticker", ms=500, callback=self.ticker)            
            self.delay.add(name="char_sally_slide_delay", ms=5000, callback=self.hide_slide)           
        elif (self.player.char_sally_state == 5):
            #restarting
            self.player.char_sally_state = 6
            self.player.char_sally_times_attempted += 1 
            self.ticks = self.player.char_sally_base_ticks
            self.player.char_sally_pops = 0
            self.player.char_sally_spin_value = 1
            self.player.char_sally_spin_worth = self.player.char_sally_spin_value*self.player.multiplier_shot_value_list[1]
            self.ticks_msg = self.ticks                        
            self.set_lights()
            self.disable_flipper()
            self.machine.events.post("char_sally_music_start")
            self.machine.events.post('show_sally_msg_1')
            self.machine.events.post('popuppost_enable_up')
            self.machine.events.post("set_gi_col", red=150, green=40, blue=40)   
            self.machine.events.post("char_show_timer")
            self.machine.events.post("ob_pause_and_hide")
            self.machine.events.post("doors_pause_and_hide")
            self.delay.add(name="char_sally_ticker", ms=500, callback=self.ticker)            
            self.delay.add(name="char_sally_slide_delay", ms=5000, callback=self.hide_slide)           
            
            
            
    def resume_and_show(self, **kwargs):   
        if (self.player.Doors_state == 0 and self.player.OB_Gate_current_mode_state == 0):
            if self.player.sally_zero_state > 0:
                self.machine.events.post("char_sally_show_slide")            

           
    def hide_slide(self, **kwargs):   
        if (self.player.Doors_state != 0 or self.player.OB_Gate_current_mode_state != 0):
            self.remove_all_widgets()
        self.log.info("char_sally - hide slide")                        
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         

            
    def extend_time(self, time, **kwargs):
        self.log.info("char_sally - time extended " +str(time))
        self.ticks += time*2;
        self.ticks_msg += time*2;        
        self.player.char_shared_timeleft = int(self.ticks/2)

        
    def ticker(self):
        self.log.info( "char_Sally - 500ms ticks " + str(self.ticks))
        self.player.char_shared_timeleft = int(self.ticks/2)
        self.delay.add(name="char_sally_ticker", ms=500, callback=self.ticker)
        if self.player.char_sally_state == 1 or self.player.char_sally_state == 6:
            self.player.char_sally_state = 10
        if self.player.char_timer_ispaused == 0:
            self.ticks -= 1;
            if self.ticks < 20:
                self.machine.events.post("set_gi_col_pulse", red=190, green=70, blue=70)
            if self.ticks <= 0:
                #out of time
                if self.player.char_sally_state != 25:
                    self.player.char_sally_state = 15            
                self.char_sally_stop()
            else:
                self.player.char_sally_spin_worth = self.player.char_sally_spin_value*self.player.multiplier_shot_value_list[1]
                if  self.ticks_msg-self.ticks > 3:
                    self.msg += 1
                    self.ticks_msg = self.ticks
                    if self.msg > 3: 
                        self.msg = 1                   
                    self.machine.events.post('show_sally_msg_'+str(self.msg))


    def char_sally_stop(self):
        if self.player.char_sally_state >= 10:
            self.machine.events.post('char_sally_music_stop')
            self.machine.events.post('char_sally_hide_slide')
            self.machine.events.post("char_hide_timer")
            self.log.info( "char_sally over")
            self.machine.events.post("stop_all_character_messages")         
            self.delay.remove("char_sally_ticker")            
            if self.player.char_sally_spins_needed > 0:            
                #todo play failed music?
                self.machine.events.post('char_mode_stopped', char_state="incomplete", char_mode="Sally")
                self.player.char_sally_state = 5   #ready to start again
                self.machine.events.post("say_sally_TODO") 
                self.machine.events.post('char_sally_failed')   
            elif self.player.char_sally_state == 25:  #completed
                self.machine.events.post('char_mode_stopped', char_state="complete", char_mode="Sally")
                self.player.char_sally_times_completed += 1
                self.player.char_sally_state = 0   #ready to start            
                self.machine.events.post('char_sally_completed')
            self.reset_lights()
            self.enable_flipper()
            self.machine.events.post('popuppost_disable_up')
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         

        
    def set_lights(self):
        for x in range(0, 3):
            if self.player.sally_show_handles[x] != 0:
                self.player.sally_show_handles[x].stop()
                self.player.sally_show_handles[x] = 0
            self.player.char_sally_shotlist[x]["state"] = "pink_flash"
            state = self.player.char_sally_shotlist[x]["state"]
            led = self.player.char_sally_shotlist[x]["led"]
            script_name = "sc_"+state
            self.player.sally_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=16.0, loops=-1)			
        self.machine.events.post('toy_pops_override', script_name='sc_pop_purple')            		

        
    def reset_lights(self):
        for x in range(0, 3):
            if self.player.sally_show_handles[x] != 0:
                self.player.sally_show_handles[x].stop()
                self.player.sally_show_handles[x] = 0
            self.player.char_sally_shotlist[x]["state"] = "off"
            state = self.player.char_sally_shotlist[x]["state"]
            led = self.player.char_sally_shotlist[x]["led"]
            script_name = "sc_off"
            self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=1)
        self.machine.events.post('toy_pops_restore')


        
    def major_3(self, **kwargs):
        if self.player.char_sally_state > 0:    	
            self.log.info( 'char_Sally inner loop - 10 (20?, 30?) spins')
            self.spval  = 10 
            self.machine.events.post('sally_10_spins')            
            self.spval *= self.player.multiplier_shot_value_list[3] # 1X, 2X or 3X 
            self.player.char_sally_spins_needed -= self.spval 
            self.score = 25000*self.spval
            if self.player.char_sally_spins_needed <= 0:
                self.player.char_sally_spins_needed = 0
                self.enable_flipper()                
                self.player.char_sally_state = 25  #complete
            self.player.score += self.score 
            self.log.info('char_sally - spins -' + str(self.player.char_sally_spins_needed))            
    
    
    def pophit(self, **kwargs):
        if self.player.char_sally_state > 0:    	
            #pop bumper hit, increase spinner value?
            self.player.char_sally_pops += 1
            self.log.info("char_sally  - " + str(self.player.char_sally_pops ))            
            if self.player.char_sally_pops >= self.player.char_sally_pop_upgrade_4:
                self.player.char_sally_spin_value = 5
                self.machine.events.post('popuppost_disable_up')                
            elif self.player.char_sally_pops >= self.player.char_sally_pop_upgrade_3:            
                self.player.char_sally_spin_value = 4            
            elif self.player.char_sally_pops >= self.player.char_sally_pop_upgrade_2:            
                self.player.char_sally_spin_value = 3            
            elif self.player.char_sally_pops >= self.player.char_sally_pop_upgrade_1:            
                self.player.char_sally_spin_value = 2            
            else:
                self.player.char_sally_spin_value = 1


    def enable_flipper(self):
        self.machine.autofires.noholdflipper.disable()        
        self.machine.flippers['flipperUpR'].enable()

        
    def disable_flipper(self):
        self.machine.flippers['flipperUpR'].disable()
        self.machine.autofires.noholdflipper.enable()

        
    def spin(self, **kwargs):
        if self.player.char_sally_state > 0:
            self.log.info( 'char_Sally spin')
            self.spval  = self.player.char_sally_spin_value 
            self.spval *= self.player.multiplier_shot_value_list[1] # 1X, 2X or 3X 
            self.player.char_sally_spins_needed -= self.spval 
            self.score = 25000*self.spval
            if self.player.char_sally_spins_needed <= 0:
                self.player.char_sally_spins_needed = 0
                self.enable_flipper()
                self.player.char_sally_state = 25  #complete
            self.player.score += self.score 
            self.log.info('char_sally - spins -' + str(self.player.char_sally_spins_needed))            

                
    def mode_stop(self, **kwargs):
        self.log.info( 'char_Sally mode_stop')
        self.char_sally_stop()
        self.enable_flipper()
        self.reset_lights()
        self.machine.events.post('popuppost_disable_up')


