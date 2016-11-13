from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Character Mode - Mayor - "I Can't Make Decisions!"
# 
# Brief Description:
# A travelling shot is scrolling across all the major shots really fast. 
# It's worth a ton of points to hit, but completely comes down to luck because 
# of how fast it moves.
# Instead, you can shoot the mayor to temporarily lock the shot in place so that 
# it's not worth quite as much, but can be made, so the mode can be completed.
# 
# Scenario:
# The mayor of Halloween Town needs help to plan the next Halloween, but 
# Jack's not around to help out and the mayor can't make decisions on his own!
# 
# Details:
# When the mode starts, the Mayor toy flips to show that he's unhappy and one 
# of the major shots will light up... but the shot travels to other major shots extremely
# quickly, changing about 10 times a second. This is nearly impossible to time, 
# but the shot CAN be made while it's still travelling and is worth a lot more points 
# if made this way. However, to complete the mode, you only have to make the travelling shot 
# once, thus the best thing to do is to shoot the mayor. This will flip the mayor
# around to his happy side and will stop the lit shot from travelling around. 
# It stays stopped for about 10 seconds and will begin to flash if it's getting ready 
# to start moving again. Making the shot ends the mode, plain and simple.
# 
# Scoring:
# Major Shot Cleared (Travelling)             10,000,000
# Major Shot Cleared (Halted)                 2,500,000
# 
# Lighting:
# When the major shot is travelling it lights both the arrow red. 
# When it's halted, it turns cyan. The Mayor shot shows a flashing blue triangle when
# the major shot is travelling and goes out once the major shot is halted.
# 
# 
# Difficulty Adjustments
# Very Easy        40 Second Time Limit
# Easy             35 Second Time Limit
# Normal           30 Second Time Limit
# Hard             25 Second Time Limit
# Very Hard        20 Second Time Limit

class Char_Mayor(Mode):

    def mode_init(self):
        self.log.info('char_Mayor mode_init')
        
    # NOTE: this mode restarts completely, no continuation
    def mode_start(self, **kwargs):
        self.log.info('char_Mayor mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.player.char_mayor_completed_roving = 0
        self.player.char_mayor_completed_static = 0            
        self.player.char_mayor_roving_score = 10000000
        self.player.char_mayor_static_score = 2500000  
        self.player.char_mayor_base_ticks = 90     #90        
        self.player.char_shared_timeleft = int(self.player.char_mayor_base_ticks/2)
        self.player.char_mayor_shot_state = 0
        self.player.char_mayor_shot_made = 0
        self.player.char_mayor_shot_number = 0
        self.player.char_mayor_points_scored = 0
        self.player.char_mayor_state = 0  
        # 0 - ready
        # 1 - starting
        # 2 - roaming
        # 3 - frozen
        # 4 - unfreezing
        # 5 - completed          

        self.player.char_mayor_shotlist = [
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
        self.add_mode_event_handler("major_0_singlestep_unlit_hit", self.mayor_hit)
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
        self.char_mayor_start()
        self.msg = 1
        self.ticks_msg = self.ticks        
        self.roaming_on = 0
    

    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_mayor_messages")  
        self.machine.events.post('char_mayor_hide_slide')

    
    def char_mayor_start(self):
        self.log.info("char_mayor_start")
        if (self.player.char_mayor_state == 0):
            self.player.char_mayor_state = 1
            self.ticks = self.player.char_mayor_base_ticks
            self.player.char_mayor_shot_made = 0
            self.set_shots()
            self.machine.events.post("char_mayor_music_start")
            self.machine.events.post("char_show_timer")
            self.machine.events.post('show_mayor_msg_1')
            self.ticks_msg = self.ticks
            self.machine.events.post("say_i_cant")
            self.delay.add(name="char_mayor_ticker", ms=500, callback=self.ticker)
            self.delay.add(name="char_mayor_start_shot_cycler", ms=200, callback=self.start_cycle_shots)
            self.player.char_timer_ispaused = 0            
            self.delay.add(name="char_mayor_slide_delay", ms=5000, callback=self.hide_slide)
            self.machine.events.post("ob_pause_and_hide")
            self.machine.events.post("doors_pause_and_hide")


    def resume_and_show(self, **kwargs):   
        if (self.player.Doors_state == 0 and self.player.OB_Gate_current_mode_state == 0):
            if self.player.char_mayor_state > 0:
                if self.player.char_mayor_state == 2:
                    self.machine.events.post("char_mayor_show_slide_happy")            
                else:
                    self.machine.events.post("char_mayor_show_slide_scared")            


    def hide_slide(self, **kwargs):   
        if (self.player.Doors_state != 0 or self.player.OB_Gate_current_mode_state != 0):
            self.remove_all_widgets() 
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         
            
            
    def extend_time(self, time, **kwargs):
        self.log.info("char_mayor - time extended " +str(time))
        self.ticks += time*2;
        self.ticks_msg += time*2;        
        self.player.char_shared_timeleft = int(self.ticks/2)
            
            
    def ticker(self):
        self.log.info("char_mayor - 500ms ticks " + str(self.ticks))
        self.player.char_shared_timeleft = int(self.ticks/2)
        self.delay.add(name="char_mayor_ticker", ms=500, callback=self.ticker)        
        if self.player.char_timer_ispaused == 0:
            self.ticks -= 1;
            if self.ticks > 30:
                self.machine.events.post("set_gi_col", red=80, green=0, blue=160)
            else:
                if self.ticks%2 == 0:        
                    self.machine.events.post("set_gi_col", red=80, green=0, blue=10+self.ticks*5)         
                else:
                    self.machine.events.post("set_gi_col", red=80, green=0, blue=160)
            if self.ticks <= 0:
                self.char_mayor_stop()
            else:
                if self.ticks_msg - self.ticks > 3:
                    self.ticks_msg = self.ticks
                    self.msg += 1
                    if self.msg > 3: 
                        self.msg = 1
                    if self.player.char_mayor_state == 3:
                        self.machine.events.post('show_mayor_msg_'+str(self.msg+3))
                    else:
                        self.machine.events.post('show_mayor_msg_'+str(self.msg))

            
    def char_mayor_stop(self):
        if self.player.char_mayor_state > 0: # and self.player.char_mayor_state < 3:
            self.log.info('char_mayor - stopping. remove delays') 
            self.delay.remove("char_mayor_shot_cycler")
            self.delay.remove("char_mayor_start_shot_cycler")
            self.delay.remove("char_mayor_ticker")
            self.delay.remove("char_mayor_shot_unfreeze")
            self.machine.events.post('char_mayor_music_stop')
            self.machine.events.post("char_mayor_hide_slide")
            self.machine.events.post("char_hide_timer")
            self.machine.events.post("stop_all_character_messages")
            if self.player.char_mayor_shot_made == 1:
                #completed
                self.machine.events.post('char_mode_stopped', char_state="complete", char_mode="Mayor")
                self.player.char_mayor_state = 0 #ready to start again
                self.machine.events.post('char_mayor_completed')
            else:
                self.machine.events.post('char_mode_stopped', char_state="incomplete", char_mode="Mayor")
                self.player.char_mayor_state = 0 #ready to start again
                self.machine.events.post('char_mayor_failed')                
            self.clear_shots()
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         

            
    def set_shots(self):
        for x in range(0, 10):
            self.player.char_mayor_shotlist[x]["state"] = "off"
        self.player.char_mayor_shotlist[0]["state"] = "blue"
        self.player.char_mayor_shot_number = random.randint(1,9)
        self.player.char_mayor_shotlist[self.player.char_mayor_shot_number]["state"] = "red"
        self.set_shot_lights()

        
    def start_cycle_shots(self):
        self.log.info("Start cycle shots")       	
        self.player.char_mayor_state = 2
        self.player.char_mayor_shot_value = self.player.char_mayor_roving_score        
        self.cycle_shots()
        self.machine.events.post("show_happy_face")        
        self.machine.events.post("mayor_shot_unfrozen")
        self.delay.add(name="char_mayor_slide_delay", ms=3000, callback=self.hide_slide)        

        
    def cycle_shots(self):
        self.log.info('char_mayor - cycle_shots')
        if self.player.char_mayor_state == 2:
            self.player.char_mayor_shot_number += 1
            if self.player.char_mayor_shot_number > 9:
                self.player.char_mayor_shot_number = 1
            self.clear_shots()
            self.player.char_mayor_shotlist[self.player.char_mayor_shot_number]["state"] = "red"
            self.player.char_mayor_shotlist[0]["state"] = "blue"
            self.set_shot_lights()            
            if self.ticks > 2:
                self.delay.add(name="char_mayor_shot_cycler", ms=500, callback=self.cycle_shots)
                self.log.info('char_mayor - cycle_shots 200ms delay added')
                

    def freeze_shot(self):
        self.log.info("Freeze shot")
        if self.player.char_mayor_state == 2:
            self.player.char_mayor_state = 3
            self.msg = 1
            self.delay.remove("char_mayor_shot_cycler")
            self.machine.events.post("mayor_shot_frozen")
            self.player.char_mayor_shot_value = self.player.char_mayor_static_score
            self.clear_shots()
            self.player.char_mayor_shotlist[self.player.char_mayor_shot_number]["state"] = "cyan"
            self.set_shot_lights()
            if self.ticks > 12:
                self.delay.add(name="char_mayor_shot_unfreeze", ms=6000, callback=self.unfreeze_shot)
            self.machine.events.post("show_scared_face")
            self.delay.add(name="char_mayor_slide_delay", ms=3000, callback=self.hide_slide)            

    def unfreeze_shot(self):
        self.log.info("Unfreeze shot")   
        if self.player.char_mayor_state == 3:
            self.player.char_mayor_state = 4
            self.msg = 1
            self.clear_shots()
            self.player.char_mayor_shotlist[self.player.char_mayor_shot_number]["state"] = "teal"
            self.set_shot_lights()            
            self.delay.add(name="char_mayor_start_shot_cycler", ms=3000, callback=self.start_cycle_shots)



    def set_shot_lights(self):
        for x in range(0, 10):
            state = self.player.char_mayor_shotlist[x]["state"]        	
            if state != 'off':
                led = self.player.char_mayor_shotlist[x]["led"]
                self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="char_Mayor", action="add")


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
        self.log.info("char_mayor - shot "+str(shot))
        if self.player.char_mayor_state > 0 and self.player.char_mayor_state < 5:
            state = self.player.char_mayor_shotlist[shot]["state"]
            self.log.info("char_mayor - shot "+str(shot) + " hit, state = "+state)        	                
            self.score = 0
            #not lit, skip it
            if state != "off":
                self.player.char_mayor_shot_made = 1
                self.player.char_mayor_state = 5
                if self.player.char_mayor_shot_roaming == 0:
                    self.log.info('char_mayor - got the static shot')                	                	
                    self.score = self.player.char_mayor_static_score
                    self.machine.events.post("say_jackpot") 
                else:
                    self.log.info('char_mayor - got the roving shot!')                	
                    self.score = self.player.char_mayor_roving_score
                    self.machine.events.post("say_super_jackpot") 
                self.score *= self.player.multiplier_shot_value_list[shot] # 1X, 2X or 3X 
                self.player.score += self.score
                self.char_mayor_stop()
            else:
                self.log.info('char_mayor - missed shot')


    def mayor_hit(self, **kwargs):
        self.log.info('char_mayor hit '+str(self.player.char_mayor_state))
        if self.player.char_mayor_state == 2:
            self.log.info('char_mayor hit')
            self.freeze_shot()
        else:
            self.machine.events.post("mayor_shot_refrozen") 


    def clear_shots(self):
        for x in range(0, 10):
            state = self.player.char_mayor_shotlist[x]["state"]
            if state != 'off':
                led = self.player.char_mayor_shotlist[x]["led"]
                self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="char_Mayor", action="remove")                        
                self.player.char_mayor_shotlist[x]["state"] = "off"


    def mode_stop(self, **kwargs):
        self.log.info('char_mayor_mode_stop')
        self.char_mayor_stop()

