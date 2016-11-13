from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random
#
# left/right alternate  l orbit, l ramp,cw oogie  vs  ccw oogie, r ramp, r orbit
#
# 
# Oogie Boogie Mode #3 - "Sally vs. Oogie Boogie"
# 
# Brief Description
# Health-bar limited mode where you must make shots to keep the mode going as long as you can... 
# at least until you reach a target score.
# 
# Scenario
# Sally's trying to rescue Santa and decides to distract Oogie Boogie with one of her detached legs. 
# But, it's only a matter of time before Oogie Boogie figures it out, so
# you have to keep him going as long as you can!
# 
# Details
# The health bar for this mode is actually more like a timer and will last 15 seconds. 
# Three random, major shots will be lit for 250,000 points each and will reset the
# health bar to maximum as well. When you make one major shot, all three lit major shots will change. 
# The spinner however will be lit for 50,000 points per spin and will never be selected as a random major shot, 
# while Soup will award you all the points you've accumulated for the mode again, 
# thus if you've scored 312,510 points since starting the mode, 
# the soup shot will award this many points. To complete the mode you must accumulate 2,000,000 points 
# while it's running, which will effectively end the mode as well.
# 
# Scoring
# Lit Major Shot            250,000
# Spinner Spin              50,000
# Soup                      Equal to Number of Points Accumulated Since Starting the Mode
# 
# Lighting
# The spinner rapidly flashes an orange triangle, lit major shots flash yellow triangles, 
# soup flashes a white triangle and circle.
# 
# Difficulty Adjustments
# Very Easy         Health Bar Lasts 18 Seconds, 4 Major Shots Lit at a Time, Need 1,500,000 Points to Complete
# Easy              Health Bar Lasts 15 Seconds, 4 Major Shots Lit at a Time, Need 1,750,000 Points to Complete
# Normal            Health Bar Lasts 15 Seconds, 3 Major Shots Lit at a Time, Need 2,000,000 Points to Complete
# Hard              Health Bar Lasts 12 Seconds, 3 Major Shots Lit at a Time, Need 2,250,000 Points to Complete
# Very Hard         Health Bar Lasts 12 Seconds, 2 Major Shots Lit at a Time, Need 2,500,000 Points to Complete

class OB_Sally(Mode):

    def mode_init(self):
        self.log.info('OB_Sally mode_init')

    def mode_start(self, **kwargs):
        self.log.info('OB_Sally mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.OB_mode_3_started == 0:
            #once per game only
            self.player.OB_mode_3_started = 1
            self.player.OB_mode_3_running = 0
        self.ticks = 30
        self.player.OB_Sally_timeleft = int(self.ticks/2)
        self.player.OB_sally_spin_value = 50000
        self.player.OB_sally_jackpot_value = 250000   
        self.index_list= [0,2,3,4,5,6,7,8]
        self.sally_shot_1 = 1
        self.sally_shot_2 = 1
        self.sally_shot_3 = 1
        
        self.add_mode_event_handler('oogie_switch_to_narrow', self.switch_to_narrow)
        self.add_mode_event_handler('oogie_switch_to_wide', self.switch_to_wide) 
        self.add_mode_event_handler("ob_resume_and_show", self.reshow_screen)
        self.add_mode_event_handler("ob_pause_and_hide", self.remove_all_widgets)
        self.player.OB_Sally_shotlist = [
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
        #self.add_mode_event_handler("major_1_singlestep_unlit_hit", self.major_1)
        self.add_mode_event_handler('sw_sally', self.spin)        
        self.add_mode_event_handler("major_2_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_2a_singlestep_unlit_hit", self.major_2)        
        self.add_mode_event_handler("major_3_singlestep_unlit_hit", self.major_3)
        self.add_mode_event_handler("major_4_singlestep_unlit_hit", self.major_4)
        self.add_mode_event_handler("major_5_singlestep_unlit_hit", self.major_5)
        self.add_mode_event_handler("major_5a_singlestep_unlit_hit", self.major_5)
        self.add_mode_event_handler("major_6_hit", self.major_6)
        self.add_mode_event_handler("major_6a_hit", self.major_6)
        self.add_mode_event_handler("major_7_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_7a_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_8_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("major_8a_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("major_9_singlestep_unlit_hit", self.soup)
            
        self.msg = 1
        self.ticks_msg = self.ticks
        self.start_battle()

        
    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_OB_Sally_messages")  
        self.machine.events.post('remove_OB_Sally_slide_wide')
        self.machine.events.post('remove_OB_Sally_slide_narrow')
        self.machine.events.post('remove_OB_Sally_slide_intro')
        

    def reshow_screen(self, **kwargs):   
        if self.player.Doors_state == 1:  #door mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        


    def end_battle(self):
        if (self.player.OB_mode_3_running == 1):
            self.player.OB_mode_3_running = 2
            self.machine.events.post('OB_Sally_music_stop')
            self.log.info("OB mode 3 over")
            self.delay.remove('OB_mode_3_ticker')  
            self.machine.events.post('ob_mode_stopped', ob_state="complete", ob_mode="3")
            self.machine.events.post("char_resume_and_show")                    
            self.machine.events.post('door_switch_to_wide')                 
            self.remove_all_widgets()        
            

    def start_battle(self):
        self.log.info("In The Oogie hole - start the battle?")
        if (self.player.OB_mode_3_running == 0):
            self.player.OB_mode_3_running = 1
            self.machine.events.post('OB_Sally_music_start')
            self.ticks = 30
            self.player.OB_Sally_timeleft = int(self.ticks/2)
            self.machine.events.post('show_OB_Sally_slide_intro') 
            self.machine.events.post('char_pause_and_hide') 
            self.machine.events.post("doors_pause_and_hide")
            self.set_up_shots()
            self.set_shot_lights()
            self.player.ob_timer_ispaused = 0                    
            self.delay.add(name="show_full_OB_Sally_intro_remover", ms=5000, callback=self.show_screen)


    def show_screen(self, **kwargs):
        self.log.info( "5 seconds passed, show narrow or wide" )
        self.delay.add(name='OB_mode_3_ticker', ms=500, callback=self.ticker)
        if self.player.ob_timer_ispaused == 0:        
            self.machine.events.post("char_resume_and_show")
            self.machine.events.post("doors_resume_and_show")                
            self.reshow_screen()
        

    def ticker(self):
        self.log.info("500ms ticks " + str(self.ticks))
        self.player.OB_Sally_timeleft = int(self.ticks/2)
        self.delay.add(name='OB_mode_3_ticker', ms=500, callback=self.ticker)        
        if self.player.ob_timer_ispaused == 0:
            self.ticks -= 1;
            if self.ticks <= 0:
                self.end_battle()
            else:
                if self.ticks_msg-self.ticks > 3:
                    self.msg += 1
                    self.ticks_msg = self.ticks
                    if self.msg > 3: 
                        self.msg = 1          
                    if self.ticks > 2:                                            
                        if self.player.Doors_state == 1:  #door mode running            	
                            self.machine.events.post('show_OB_Sally_msg_'+str(self.msg)+'_n')            
                        else:
                            self.machine.events.post('show_OB_Sally_msg_'+str(self.msg))            

                
    def switch_to_narrow(self, **kwargs):   
        self.remove_all_widgets()
        self.machine.events.post('show_OB_Sally_slide_narrow')


    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()
        self.machine.events.post('show_OB_Sally_slide_wide')
        
        
    def major_0(self, **kwargs):
        self.handle_shot(0)
#    def major_1(self, **kwargs):
#        self.handle_shot(1)
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
#    def major_9(self, **kwargs):
#        self.handle_shot(9)


    def handle_shot(self, shot):
        if self.player.OB_mode_3_running == 1:
            self.log.info("OB Sally - shot "+str(shot))
            state = self.player.OB_Sally_shotlist[shot]["state"]
            self.log.info("OB Sally - shot "+str(shot) + " hit, state = "+state)        	                
            self.score = 0
            #not lit, skip it
            if state != "off":
                if state == 'yellow':
                    self.log.info('OB Sally - yellow shot')                	                	
                    self.score = self.player.OB_sally_jackpot_value  #250000
                    self.machine.events.post("say_sally_line1")    
                    self.machine.events.post("show_sally_distract")   
                    self.clear_shots()
                    self.player.OB_Sally_shotlist[self.sally_shot_1]["state"] = 'off'
                    self.player.OB_Sally_shotlist[self.sally_shot_2]["state"] = 'off'
                    self.player.OB_Sally_shotlist[self.sally_shot_3]["state"] = 'off'                        
                    self.player.OB_Sally_shotlist[9]["state"] = 'white'
                    self.set_up_shots()
                    self.set_shot_lights()
                    self.ticks = 30
                    self.msg = 1
                    self.ticks_msg = self.ticks
                    self.score *= self.player.multiplier_shot_value_list[shot] # 1X, 2X or 3X 
                    self.player.OB_Sally_accum_score += self.score
                    self.player.score += self.score
            else:
                self.log.info('OB Sally - shot, not lit')
    
        
    def spin(self, **kwargs):
        if self.player.char_sally_state > 0:
            self.log.info( 'OB Sally - spinner')
            self.score = self.player.OB_sally_spin_value * self.player.multiplier_shot_value_list[1] # 1X, 2X or 3X 
            self.player.score += self.score 
            self.player.OB_Sally_accum_score += self.score

            
    def soup(self, **kwargs):
        if self.player.char_sally_state > 0:
            self.log.info('OB Sally - soup')            
            self.machine.events.post("say_sally_line2")    
            self.machine.events.post("show_sally_distract2")   
            self.score = self.player.OB_Sally_accum_score * self.player.multiplier_shot_value_list[9] # 1X, 2X or 3X 
            self.player.score += self.score 
            
        
    def set_up_shots(self, **kwargs):   
        self.log.info('OB Sally - set up 3 shots')
        # pick 3 random shots (not soup or spinner)
        for x in range(0, 10):
            self.player.OB_Sally_shotlist[x]["state"] = "off"
        self.sally_shot_1 = random.randint(0,7)            
        self.sally_shot_2 = random.randint(0,7)
        while (self.sally_shot_1 == self.sally_shot_2):
            self.sally_shot_2 = random.randint(0,7)
        self.sally_shot_3 = random.randint(0,7)
        while (self.sally_shot_3 == self.sally_shot_2 or self.sally_shot_3 == self.sally_shot_1):
            self.sally_shot_3 = random.randint(0,7)
        self.sally_shot_1 = self.index_list[self.sally_shot_1]
        self.sally_shot_2 = self.index_list[self.sally_shot_2]
        self.sally_shot_3 = self.index_list[self.sally_shot_3]
        self.player.OB_Sally_shotlist[self.sally_shot_1]["state"] = "yellow"
        self.player.OB_Sally_shotlist[self.sally_shot_2]["state"] = "yellow"
        self.player.OB_Sally_shotlist[self.sally_shot_3]["state"] = "yellow"        
        self.set_shot_lights()
        
   
    def set_shot_lights(self):
        for x in range(0, 10):
            state = self.player.OB_Sally_shotlist [x]["state"]
            if state != 'off':
                led = self.player.OB_Sally_shotlist [x]["led"]
                col = state
                self.machine.events.post('arrow_change', led_num=x, script_name=col, mode_name="OB_SALLY", action="add")

                
    def clear_shots(self):
        for x in range(0, 10):
            state = self.player.OB_Sally_shotlist [x]["state"]
            if state != 'off':
                col = state
                led = self.player.OB_Sally_shotlist [x]["led"]
                self.machine.events.post('arrow_change', led_num=x, script_name=col, mode_name="OB_SALLY", action="remove")                        


    def mode_stop(self, **kwargs):
        self.log.info('OB_Sally mode_stop')
        self.end_battle()

