from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# door_independence                                                                                                                     Page 31
# Hinterlands Door Mode - "Fireworks Festival" Multiball                                                                                                             Page 26
#
# Brief Description
# Four major shots are lit for jackpots. Once scored, a travelling super jackpot can be obtained.
# 
# Scenario
# Uncle Sam's made it to Halloween Town and scared out of his wits... 
# so he comes up with a great idea to avoid being scared: Celebrate with Fireworks!
# 
# Details
# This is a 3-ball multiball which starts with four shots lit for jackpots: 
# Left Ramp, Right Ramp, Mayor and Soup. Once all jackpots are collected a travelling super
# jackpot appears. Once collected, the original four jackpot shots relight.
# 
# Scoring
# Jackpot                    2,000,000
# Super Jackpot              10,000,000
# 
# Lighting
# Jackpot shots flash their triangles red, then white, then blue, then white. It's VERY important not 
# to flash straight from red to blue or from blue to red as this may
# cause epileptic reactions in some people. The roaming super jackpot flashes both a white triangle and circle.
# 
# Difficulty Adjustments
# Very Easy        Super Jackpot Travels Slowest
# Easy             Super Jackpot Travels Slower
# Normal           Super Jackpot Travels Normal Speed
# Hard             Super Jackpot Travels Faster
# Very Hard        Super Jackpot Travels Fastest

class Door_Independence(Mode):

    def mode_init(self):
        self.log.info('door_independence mode_init')

    def mode_start(self, **kwargs):
        self.log.info('door_independence mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.shot_value = 20000
        self.jackpot_value = 2000000
        self.super_jackpot_value = 10000000
        self.ticks = 0
        self.player.door_independence_running = 0
        self.player.door_independence_score = 0
        self.player.door_independence_shot_index = 0
        self.player.door_independence_shot_direction = 1
        self.player.door_independence_shotlist = [
            {"led":"rgb_mayor_arrow", "mindex":0, "state":"off"}
            ,{"led":"rgb_lramp_arrow", "mindex":2, "state":"off"}
            ,{"led":"rgb_rramp_arrow", "mindex":7, "state":"off"}
            ,{"led":"rgb_soup_arrow", "mindex":9, "state":"off"}
            ]
        self.add_mode_event_handler("major_0_singlestep_unlit_hit", self.major_0)
        self.add_mode_event_handler("major_2_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_2a_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_7_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_7a_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_9_singlestep_unlit_hit", self.major_9)
        self.add_mode_event_handler('balldevice_trough_ball_enter', self.ball_drained)
        self.add_mode_event_handler('door_switch_to_narrow', self.switch_to_narrow)        
        self.add_mode_event_handler('door_switch_to_wide', self.switch_to_wide)
        self.add_mode_event_handler("doors_resume_and_show", self.reshow_screen)
        self.add_mode_event_handler("doors_pause_and_hide", self.remove_all_widgets)                  
        self.door_independence_start()
        self.msg = 1
        self.roaming_on = 0


    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all slides and messages')
        self.machine.events.post("remove_independence_messages")  
        self.machine.events.post('remove_independence_slide_narrow')
        self.machine.events.post('remove_independence_slide_wide')
        self.machine.events.post('remove_independence_slide_full')
        
        
    def reshow_screen(self, **kwargs):   
        self.log.info('pause_and_hide - resume show')    
        if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        


    def door_independence_start(self):
        self.log.info("door_independence_start")
        if (self.player.door_independence_running == 0):
            self.player.door_independence_running = 1
            self.player.door_independence_shots_made = 0
            self.set_shots()
            self.set_shot_lights()            
            self.machine.events.post("holiday_independence_music_start")
            self.machine.events.post('disable_combos')
            for x in range(0, 3):
                bip = self.machine.game.balls_in_play             
                if bip < 6:
                    self.machine.game.balls_in_play = bip+1
                    self.machine.playfield.add_ball(1, player_controlled=False)
            self.machine.events.post('add_a_ball_start')
            self.machine.events.post('enable_the_mb_ball_save')
            self.roaming_on = 0
            self.machine.events.post('show_independence_slide_full')
            self.machine.events.post('char_pause_and_hide')
            self.machine.events.post("ob_pause_and_hide")  
            self.player.door_timer_ispaused = 0
            self.delay.add(name="show_full_independence_intro_remover", ms=5000, callback=self.show_screen)

            
    def show_screen(self, **kwargs):
        self.log.info( "5 seconds passed, show narrow or wide" )
        #self.ticks_msg = self.ticks   
        self.delay.add(name="holiday_independence_ticker", ms=500, callback=self.ticker)        
        if self.player.door_timer_ispaused == 0:                
            self.machine.events.post("char_resume_and_show")
            self.machine.events.post("ob_resume_and_show")         
            self.reshow_screen()
            if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                self.machine.events.post('show_independence_msg_1_n')
            else:
                self.machine.events.post('show_independence_msg_1')            


    def cycle_shots(self):
        self.log.info('door_independence - cycle_shots ' +str(self.player.door_independence_shot_index))
        self.clear_shots()
        self.player.door_independence_shot_index += self.player.door_independence_shot_direction
        if self.player.door_independence_shot_index > 3:
            self.player.door_independence_shot_index = 2
            self.player.door_independence_shot_direction = -1
        if self.player.door_independence_shot_index < 0:
            self.player.door_independence_shot_index = 1
            self.player.door_independence_shot_direction = 1
        self.player.door_independence_shotlist[self.player.door_independence_shot_index]["state"] = "red"
        self.set_shot_lights()
        self.machine.events.post('holiday_independence_cycling') 

           
    def ticker(self):
        self.log.info("door_independence - 500ms ticks "+str(self.ticks))
        if self.player.door_independence_running == 1:
            self.delay.add(name="door_independence_ticker", ms=500, callback=self.ticker)  
        if self.roaming_on == 1:
            self.cycle_shots()
        if self.player.door_timer_ispaused == 0:            
            self.ticks += 1
            if self.ticks % 4 == 0:
                self.msg += 1
                if self.msg > 2: 
                    self.msg = 1    
                if self.roaming_on == 1:
                    self.msg = 3 #show the roaming msg
                if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                    self.machine.events.post('show_independence_msg_'+str(self.msg)+'_n')            
                else:
                    self.machine.events.post('show_independence_msg_'+str(self.msg))            


    def switch_to_narrow(self, **kwargs):   
        self.remove_all_widgets()    
        self.machine.events.post('show_independence_slide_narrow')

        
    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()    
        self.machine.events.post('show_independence_slide_wide')


    def door_independence_stop(self):
        if self.player.door_independence_running == 1:
            self.delay.remove('door_independence_shot_cycler')
            self.machine.events.post('holiday_independence_music_stop')
            self.log.info("door_independence over")
            if self.player.door_independence_shots_made > 0:
                self.machine.events.post('holiday_mode_stopped', state="complete")
                self.player.door_independence_running = 2 #completed
            else:
                self.machine.events.post('holiday_mode_stopped', state="incomplete")
                self.player.door_independence_running = 0 #ready to start again
            self.clear_shots()
            self.machine.events.post('enable_combos')
            self.machine.events.post('add_a_ball_stop')
        self.machine.events.post('remove_independence_messages')
        self.machine.events.post('remove_independence_narrow')
        self.machine.events.post('remove_independence_wide')
        self.machine.events.post('oogie_switch_to_wide')
        self.machine.events.post("char_resume_and_show")


    def ball_drained(self, **kwargs):
        if self.player.door_independence_running == 1:
            self.log.info("door_independence - ball drained")
            self.log.info("door_independence - balls in play "+str(self.machine.game.balls_in_play))
            if self.machine.game.balls_in_play <= 2:
                if self.player.ball_save_active == 0:
                    #there is only 1 ball on playfield, end multiball
                    self.log.info("door_independence - Fireworks MB over")
                    self.door_independence_stop()
                else:
                    self.log.info( "door_independence multiball - ball drained - but ball save is running" )
            else:
                self.log.info( "door_independence multiball - ball drained - more than 2 BIP" )            


    def set_shots(self):
        self.player.door_independence_shots_qualified = 0
        for x in range(0, 4):
            self.player.door_independence_shotlist[x]["state"] = "white"
        self.set_shot_lights()


    def set_shot_lights(self):
        for x in range(0, 4):
            state = self.player.door_independence_shotlist[x]["state"]
            mindex = self.player.door_independence_shotlist[x]["mindex"] 
            self.machine.events.post('arrow_change', led_num=mindex, script_name=state, mode_name="Door_Independence", action="add")


    def major_0(self, **kwargs):
        self.handle_shot(0)
    def major_2(self, **kwargs):
        self.handle_shot(1)
    def major_7(self, **kwargs):
        self.handle_shot(2)
    def major_9(self, **kwargs):
        self.handle_shot(3)

 
    def handle_shot(self, shot):
        self.log.info('door_independence - handle_shot')
        if self.player.door_independence_running == 1:
            self.score = 0
            state = self.player.door_independence_shotlist[shot]["state"]
            mindex = self.player.door_independence_shotlist[shot]["mindex"]
            self.log.info('door_independence - shot state ' +str(state))
            if state != "off":
                if state == "white":
                    #qualifier
                    self.log.info('door_independence - jackpot')                                    
                    #stop the flash LED
                    self.machine.events.post('arrow_change', led_num=mindex, script_name=state, mode_name="Door_Independence", action="remove")
                    self.player.door_independence_shotlist[shot]["state"] = "off"
                    self.score = self.jackpot_value * self.player.multiplier_shot_value_list[mindex] 
                    self.player.door_independence_shots_qualified += 1
                    self.player.door_independence_jackpot_score = self.score
                    self.machine.events.post('show_independence_fireworks')                                            
                    self.machine.events.post('remove_independence_messages')
                    self.ticks = 0
                    self.machine.events.post('show_independence_jackpot_collected')
                    self.player.door_independence_shots_made += 1
                    if self.player.door_independence_shots_qualified == 4:
                        self.log.info('door_independence - start the super jackpot!')
                        self.roaming_on = 1
                        self.player.door_independence_shot_index = (shot + 2) % 4

                elif state == "red":
                    #super jackpot
                    self.log.info('door_independence - super jackpot')
                    #stop the flash LED
                    self.machine.events.post('arrow_change', led_num=mindex, script_name=state, mode_name="Door_Independence", action="remove")
                    self.player.door_independence_shotlist[shot]["state"] = "off"
                    self.roaming_on = 0
                    self.score = self.super_jackpot_value * self.player.multiplier_shot_value_list[mindex] 
                    self.player.door_independence_sjackpot_score = self.score
                    self.machine.events.post('show_independence_fireworks_super')
                    self.machine.events.post('remove_independence_messages')
                    self.ticks = 0
                    self.machine.events.post('show_independence_sjackpot_collected')
                    self.set_shots()                    
                else:
                    # "off" - already collected
                    self.log.info('door_independence - points')                    
                    self.score = self.shot_value * self.player.multiplier_shot_value_list[mindex] 
                    self.player.door_independence_points_score = self.score                    
                    self.machine.events.post('remove_independence_messages')
                    self.ticks = 0
                    if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                        self.machine.events.post('show_independence_points_collected_n')                    
                    else:
                        self.machine.events.post('show_independence_points_collected')
                self.player.score += self.score
                self.player.door_independence_score += self.score

                
    def clear_shots(self):
        for x in range(0, 4):
            state = self.player.door_independence_shotlist[x]["state"]
            if state != 'off':
                mindex = self.player.door_independence_shotlist[x]["mindex"]
                self.machine.events.post('arrow_change', led_num=mindex, script_name=state, mode_name="Door_Independence", action="remove")                        
                self.player.door_independence_shotlist[x]["state"] = "off"


    def mode_stop(self, **kwargs):
        self.log.info('door_independence_mode_stop')
        self.door_independence_stop()
        self.clear_shots()

