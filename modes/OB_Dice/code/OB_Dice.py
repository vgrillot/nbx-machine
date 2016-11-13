from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Oogie Boogie Mode #4 - "Luck o' the Dice"                                                                                                                            Page 34
# 
# Brief Description
# You must get the ball into the pops to change the values of Oogie Boogie's dice rolls. 
# If the cumulative value of all of his dice rolls exceeds 32, the mode ends.
# 
# Scenario
# Santa and Sally are perilously tied up on an insidious platform Oogie Boogie has. 
# If Oogie Boogie presses the lever of his machine enough times, Santa and Sally
# are doomed! Thankfully, he's decided to leave the number of his presses up to random chance...
# 
# Details
# When this mode begins, a random roll of the dice is shown on-screen (total value of 9 or higher) 
# and after 10 seconds elapse, or you shoot the right ramp, this will be
# what Oogie Boogie actually rolls. If you're not satisfied with the value currently shown, you 
# need to get the ball up into the pops. To that end, the popup post will
# activate during the course of this mode. Each pop bumper hit will change the highest die to a 
# new random value from 1 to 6 and will delay the timer for a moment
# until the pops aren't being hit anymore. Chances are good that you will at least get one die 
# down to 1 with enough pop bumper hits, at which point the highest roll
# possible becomes 7. This is good because to complete this mode, you must survive four dice 
# rolls without reaching or exceeding a cumulative value of 32. Once
# Oogie Boogie rolls the dice, the new value to come up will always be at least 9. 
# The gate to Oogie Boogie's lair remains down for the duration of this mode and
# shooting the lair immediately awards 1,000,000 points, but also re-randomizes both dice 
# without resetting the timer. If you make it past four dice rolls, Jack breaks in
# and distracts Oogie Boogie, though you only see Oogie Boogie's reaction on the display so 
# as to instill a sense of wonder as to the next mode. If you fail to survive
# four rolls, Santa and Sally fall in and Oogie Boogie proclaims, "Better luck next time!"
# 
# Scoring
# Survive 1st Dice Roll        500,000
# Survive 2nd Dice Roll      1,000,000
# Survive 3rd Dice Roll      1,500,000
# Survive 4th Dice Roll      2,000,000
# Survive 5th Dice Roll      2,500,000
# Early Roll             Extra 500,000 if you survive
# Lair Shot                  1,000,000
# 
# Lighting
# The right ramp will show a solid red triangle with any dice roll value higher than 7. 
# A value of 7 will flash a yellow triangle on the right ramp. A value less than 7 will
# flash a green triangle on the right ramp. The pops will also be flashing in a particular 
# lighting pattern to get the player's attention to shoot for them. The bug lights in
# front of the lair flash red.
# 
# Difficulty Adjustments
# Very Easy           Need to survive 3 rolls
# Easy                Need to survive 3 rolls
# Normal              Need to survive 4 rolls
# Hard                Need to survive 4 rolls
# Very Hard           Need to survive 5 rolls

class OB_Dice(Mode):

    def mode_init(self):
        self.log.info('OB_Dice mode_init')


    def mode_start(self, **kwargs):
        self.log.info('OB_Dice mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.OB_mode_4_started == 0:
            #once per game only
            self.player.OB_mode_4_started = 1
            self.player.OB_mode_4_running = 0
            self.player.OB_Dice_times_attempted = 0            
            self.player.OB_Dice_times_completed = 0
            self.player.OB_Dice_points_scored = 0
            self.player.OB_Dice_shots_made = 0
            self.player.OB_Dice_shots_needed = 4            
            self.player.OB_Dice_die_1 = 3
            self.player.OB_Dice_die_2 = 3
            self.player.OB_Dice_total_rolled = 0
            self.player.OB_Dice_state = 0
            self.player.OB_Dice_base_ticks = 40              
            self.player.OB_Dice_timeleft = int(self.player.OB_Dice_base_ticks/2)
            self.player.OB_Dice_base_score = 500000
            self.player.OB_Dice_oogie_score = 1000000
            self.player.OB_Dice_shotlist = [
                 {"led":"rgb_lramp_arrow", "state":"off", "mult":2}
                ]
        #handlers for shots 
        self.add_mode_event_handler('sw_bumpertop', self.pophit)
        self.add_mode_event_handler('sw_bumperleft', self.pophit)
        self.add_mode_event_handler('sw_bumperright', self.pophit)
        self.add_mode_event_handler('sw_subwayoogie', self.subway_oogie_hit)
        self.add_mode_event_handler('sw_oogiebanktrap', self.oogie_hit)        
        self.add_mode_event_handler("major_2_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_2a_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("extend_OB_time", self.extend_time)                        
        self.add_mode_event_handler('oogie_switch_to_narrow', self.switch_to_narrow)        
        self.add_mode_event_handler('oogie_switch_to_wide', self.switch_to_wide)
        self.add_mode_event_handler("ob_resume_and_show", self.reshow_screen) 
        self.add_mode_event_handler("ob_pause_and_hide", self.remove_all_widgets)
        self.ticks = self.player.OB_Dice_base_ticks        
        self.msg = 1
        self.ticks_msg = self.ticks
        self.start_battle()


    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_OB_Dice_messages")  
        self.machine.events.post('remove_OB_Dice_all_dice')                                
        self.machine.events.post('remove_OB_Dice_slide_wide')
        self.machine.events.post('remove_OB_Dice_slide_narrow')
        self.machine.events.post('remove_OB_Dice_slide_intro')
 
 
    def reshow_screen(self, **kwargs):   
        if self.player.Doors_state == 1:  #door mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        
        
        
    def start_battle(self):
        self.log.info("OB_Dice_start")
        if (self.player.OB_mode_4_running == 0):
            self.player.OB_mode_4_running = 1
            #starting mode/level for first time
            self.player.OB_Dice_state = 1
            self.ticks = self.player.OB_Dice_base_ticks
            self.player.OB_Dice_die_1 = 3
            self.player.OB_Dice_die_2 = 3
            self.player.OB_Dice_total_rolled = 0
            self.player.OB_Dice_shots_made = 0
            self.player.ob_timer_ispaused = 1                        
            self.set_dice(reset_time=True, makerandom=False)
            self.machine.events.post("set_gi_col", red=160, green=10, blue=10)
            self.machine.events.post("mode_base_stop_music")            
            self.machine.events.post("OB_Dice_music_start")
            self.ticks_msg = self.ticks
            self.machine.events.post('popuppost_enable_up')            
            self.machine.events.post('show_OB_Dice_slide_intro') 
            self.machine.events.post('char_pause_and_hide')   
            self.machine.events.post("doors_pause_and_hide")
            self.player.ob_timer_ispaused = 0            
            self.delay.add(name="show_full_OB_Dice_intro_remover", ms=7000, callback=self.show_screen)
            self.machine.events.post('toy_pops_override', script_name='sc_pop_yellow')                


    def show_screen(self, **kwargs):
        self.log.info( "7 seconds passed, show narrow or wide" )
        self.delay.add(name='OB_mode_4_ticker', ms=500, callback=self.ticker)
        if self.player.ob_timer_ispaused == 0:
            self.machine.events.post("char_resume_and_show")   
            self.machine.events.post("doors_resume_and_show")             
            self.reshow_screen()        
            if self.player.Doors_state == 1:  #door mode running
                self.machine.events.post('show_OB_Dice_msg_1_n')            
                self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_1)+'_left_n')        
                self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_2)+'_right_n')                
            else:
                self.machine.events.post('show_OB_Dice_msg_1')            
                self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_1)+'_left_w')        
                self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_2)+'_right_w')                


    def switch_to_narrow(self, **kwargs):   
        self.remove_all_widgets()            
        self.machine.events.post('show_OB_Dice_slide_narrow')
        self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_1)+'_left_n')        
        self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_2)+'_right_n')                


    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()
        self.machine.events.post('show_OB_Dice_slide_wide')
        self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_1)+'_left_w')        
        self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_2)+'_right_w')                


    def ticker(self):
        self.log.info("500ms ticks " + str(self.ticks))
        self.machine.events.post("OB_Dice_countdown")
        self.player.OB_Dice_timeleft = int(self.ticks/2)
        self.delay.add(name="OB_Dice_ticker", ms=500, callback=self.ticker)        
        if self.player.ob_timer_ispaused == 0:
            self.ticks -= 1;
            if self.ticks <= 0:
                #out of time
                self.accept_roll()
            else:
                if self.ticks_msg - self.ticks > 3:
                    self.ticks_msg = self.ticks
                    self.msg += 1
                    if self.msg > 3: 
                        self.msg = 1
                    if self.ticks > 2:
                        if self.player.Doors_state == 1:  #door mode running            	
                            self.machine.events.post('show_OB_Dice_msg_'+str(self.msg)+'_n')            
                        else:
                            self.machine.events.post('show_OB_Dice_msg_'+str(self.msg))            

            
    def extend_time(self, time, **kwargs):
        self.log.info("OB_Dice - time extended " +str(time))
        self.ticks += time*2;
        self.ticks_msg += time*2;        
        self.player.OB_Dice_timeleft = int(self.ticks/2)
        

    def end_battle(self):
        self.log.info("OB_Dice_stop")    
        if (self.player.OB_mode_4_running == 1):
            self.player.OB_mode_4_running = 2
            self.machine.events.post('OB_Dice_music_stop')
            self.log.info("OB mode 4 over")
            self.delay.remove("OB_Dice_ticker")            
            self.machine.events.post('advance_to_next_mode')
            self.machine.events.post("ob_hide_timer") 
            self.player.OB_Dice_state = 2    
            if self.player.OB_Dice_shots_made < self.player.OB_Dice_shots_needed:  
                #incomplete
                #todo play failed music?
                self.machine.events.post('ob_mode_stopped', ob_state="incomplete", ob_mode="4")
                self.machine.events.post('OB_Dice_failed')                            
            else:
                #completed
                self.machine.events.post('ob_mode_stopped', ob_state="complete", ob_mode="4")
                self.machine.events.post('OB_Dice_completed')                                        
            self.reset_lights()
        self.machine.events.post('toy_pops_restore') 
        self.machine.events.post('popuppost_disable_up')
        self.machine.events.post("char_resume_and_show")                    
        self.machine.events.post('door_switch_to_wide')                 
        self.remove_all_widgets()        


    def set_shot_col(self, col):
        self.reset_lights()
        self.player.OB_Dice_shotlist[0]["state"] = col
        self.set_lights()


    def set_lights(self):
        state = self.player.OB_Dice_shotlist[0]["state"]
        if state != 'off':
            led = self.player.OB_Dice_shotlist[0]["led"]
            self.machine.events.post('arrow_change', led_num=2, script_name=state, mode_name="OB_Dice", action="add")


    def pophit(self, **kwargs):
        if self.player.OB_Dice_state == 1:    	
            self.log.info("OB_Dice pop hit, decrease the highest die number")        
            self.machine.events.post('remove_OB_Dice_all_dice')        
            #pop bumper hit, decrease die value
            if self.player.OB_Dice_die_1 > self.player.OB_Dice_die_2:
                self.player.OB_Dice_die_1 = random.randint(1,6)
            else:
                self.player.OB_Dice_die_2 = random.randint(1,6)
            self.log.info('OB_Dice - die 1 ' + str(self.player.OB_Dice_die_1))
            self.log.info('OB_Dice - die 2 ' + str(self.player.OB_Dice_die_2))
            if self.player.ob_timer_ispaused == 0:
                if self.player.Doors_state == 1:  #door mode running
                    self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_1)+'_left_n')        
                    self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_2)+'_right_n')                
                else:
                    self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_1)+'_left_w')        
                    self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_2)+'_right_w')
            if self.player.OB_Dice_die_1 == 1 and self.player.OB_Dice_die_2 == 1:
                self.machine.events.post('OB_Dice_snake_eyes')                    
                self.player.OB_Dice_state = 3
                self.delay.add(name="OB_Dice_settle", ms=2000, callback=self.unsettle)
            self.set_arrow_color()

            
    def unsettle(self, **kwargs):
        self.player.OB_Dice_state = 1
        self.accept_roll()
        

    def oogie_hit(self, **kwargs):
        if self.player.OB_Dice_state == 1:
            #oogie hit - randomize dice
            self.log.info("OB_Dice oogie hit randomize dice")            
            self.player.OB_Dice_points_scored += self.score
            self.set_dice(reset_time=False, makerandom=True)
            self.machine.events.post('OB_Dice_dice_roll')        


    def subway_oogie_hit(self, **kwargs):
        if self.player.OB_Dice_state == 1:
            self.log.info("OB_Dice subway - points")
            #oogie hit, 1000000 points
            self.machine.events.post('OB_Dice_oogie_hit')                    
            self.score = self.player.OB_Dice_oogie_score
            self.player.score += self.score
            

    def set_dice(self, reset_time, makerandom):
        self.log.info('OB_Dice - set dice values')
        self.machine.events.post('remove_OB_Dice_all_dice')        
        if reset_time:
            if self.ticks <= 0:
                self.delay.add(name="OB_Dice_ticker", ms=500, callback=self.ticker)
            self.ticks = self.player.OB_Dice_base_ticks
            self.ticks_msg = self.ticks            
            self.player.OB_Dice_timeleft = int(self.ticks/2)
        if makerandom:
            self.player.OB_Dice_die_1 = random.randint(1,6)
            self.player.OB_Dice_die_2 = random.randint(1,6)
        else:
        	  # at least 9, start with 6
            self.player.OB_Dice_die_1 = 3
            self.player.OB_Dice_die_2 = 3
            while ((self.player.OB_Dice_die_1 + self.player.OB_Dice_die_1) < 9):
                self.player.OB_Dice_die_1 = random.randint(4,6)
                self.player.OB_Dice_die_2 = random.randint(4,6)
        self.set_arrow_color()
        self.log.info('OB_Dice - die 1 ' + str(self.player.OB_Dice_die_1))
        self.log.info('OB_Dice - die 2 ' + str(self.player.OB_Dice_die_2))
        if self.player.ob_timer_ispaused == 0:
            if self.player.Doors_state == 1:  #door mode running
                self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_1)+'_left_n')        
                self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_2)+'_right_n')                
            else:
                self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_1)+'_left_w')        
                self.machine.events.post('show_OB_Dice_die_'+str(self.player.OB_Dice_die_2)+'_right_w')                
        

    def set_arrow_color(self):
        self.dietotal = self.player.OB_Dice_die_1 + self.player.OB_Dice_die_2
        col = 'yellow'
        if self.dietotal > 7:
            col = 'red'
        if self.dietotal < 7:
            col = 'green'
        self.set_shot_col(col)


    def major_2(self, **kwargs):
        if self.player.OB_Dice_shots_made < (self.player.OB_Dice_shots_needed-1):    
            self.machine.events.post('OB_Dice_one_more_roll')
        else:
            self.machine.events.post('OB_Dice_bye_bye')        
        self.player.OB_Dice_state = 3
        self.delay.add(name="OB_Dice_settle", ms=2000, callback=self.unsettle)
        
        
    def accept_roll(self):
        self.log.info('OB_Dice - roll accepted '+ str(self.player.OB_Dice_shots_made+1))
        if self.player.OB_Dice_state == 1:  #running
            self.score = 0
            self.player.OB_Dice_shots_made += 1
            self.score = self.player.OB_Dice_jackpot_score * self.player.OB_Dice_shots_made
            mult_index = self.player.OB_Dice_shotlist[0]["mult"]
            self.score *= self.player.multiplier_shot_value_list[mult_index] # 1X, 2X or 3X 
            self.player.score += self.score
            self.player.OB_Dice_points_scored += self.score
            self.player.OB_Dice_total_rolled += self.player.OB_Dice_die_1
            self.player.OB_Dice_total_rolled += self.player.OB_Dice_die_2            
            if self.player.OB_Dice_total_rolled < 32:
                #still in the game, are we done yet?
                if self.player.OB_Dice_shots_made == self.player.OB_Dice_shots_needed:
                    self.end_battle()
                else:
                    self.set_dice(reset_time=True, makerandom=False)
                    self.machine.events.post('OB_Dice_dice_roll')        
            else:
                #rolled over 32
                self.end_battle()               


    def reset_lights(self):
        state = self.player.OB_Dice_shotlist[0]["state"]
        if state != 'off':
            led = self.player.OB_Dice_shotlist[0]["led"]
            self.machine.events.post('arrow_change', led_num=2, script_name=state, mode_name="OB_Dice", action="remove")                        
            self.player.OB_Dice_shotlist[0]["state"] = "off"


    def mode_stop(self, **kwargs):
        self.log.info('OB_Dice_mode_stop')
        self.end_battle()
