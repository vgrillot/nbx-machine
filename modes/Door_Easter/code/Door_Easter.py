from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Hinterlands Door Mode - "Easter Egg Hunt"                                                                                                                           Page 25
# 
# Brief Description
# All the major shots are lit for various values, but the values are assigned at random 
# from a pool of values. Once you know the value of a shot you can continue to
# shoot it to score those points over and over. You must uncover at least three 
# different values to complete the mode.
# 
# Scenario
# The Easter Bunny has hidden a whole bunch of eggs all over Halloween Town. Find them!
# 
# Details
# All ten major shots will flash solid white when this mode begins. 
# Each major shot will also have a value hidden within it. There are ten values to assign thus they are
# shuffled and distributed between all shots. There are 4x "50,000" values, 
# 2x "100,000" values, 2x "250,000" values, 1x "500,000" and 1x "1,000,000". 
# When you make a shot it will change colour to indicate how good of a shot it is. 
# You can then go for that shot as much as you want within the 30 second time limit. 
# Once you've unveiled three different shots, the mode is complete and all other unveiled shots will go out, 
# but until the mode timer expires you can continue to shoot the shots
# you've uncovered to score more points from them.
# 
# Scoring
# Shot Values                50,000 / 100,000 / 250,000 / 500,000 / 1,000,000
# 
# Lighting
# Major shot triangles will all flash white at first. Once a shot value is unveiled it will be 
# red for 50,000, 
# orange for 100,000, 
# yellow for 250,000, 
# green for 500,000 and
# blue for 1,000,000.
# 
# Difficulty Adjustments
# Very Easy        40 Second Time Limit
# Easy             35 Second Time Limit
# Normal           30 Second Time Limit
# Hard             25 Second Time Limit
# Very Hard        20 Second Time Limit

class Door_Easter(Mode):

    def mode_init(self):
        self.log.info('Door_Easter mode_init')

    def mode_start(self, **kwargs):
        self.log.info('Door_Easter mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.door_easter_started == 0:
            self.player.door_easter_started = 1
            self.player.door_easter_running = 0
        self.ticks = 0
        self.player.door_easter_base_ticks = 90  #90 = 45 seconds
        self.player.door_easter_timeleft = int(self.player.door_easter_base_ticks/2)        
        self.player.door_easter_shots_needed = 3
        self.player.door_easter_score = 0
        self.player.door_easter_shots_revealed = 0
        self.player.door_easter_shot_pool = [1000000,500000,250000,250000, 
                100000,100000,50000,50000,50000,50000]
        self.player.door_easter_shot_value = [0,0,0,0,0,0,0,0,0,0]        
        self.player.door_easter_shotlist = [
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
        self.add_mode_event_handler("extend_door_time", self.extend_time)  
        self.add_mode_event_handler('door_switch_to_narrow', self.switch_to_narrow)        
        self.add_mode_event_handler('door_switch_to_wide', self.switch_to_wide)                
        self.add_mode_event_handler("doors_resume_and_show", self.reshow_screen)        
        self.add_mode_event_handler("doors_pause_and_hide", self.remove_all_widgets) 
        self.door_easter_start()
        self.msg = 1
        self.ticks_msg = self.ticks
        

    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_easter_messages")  
        self.machine.events.post('remove_easter_slide_narrow')
        self.machine.events.post('remove_easter_slide_wide')
        self.machine.events.post('remove_easter_slide_full')
        

    def reshow_screen(self, **kwargs):   
        if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        


    def door_easter_start(self):
        self.log.info("door_easter_start")
        if (self.player.door_easter_running == 0):
            self.ticks = self.player.door_easter_base_ticks
            self.player.door_easter_timeleft = int(self.player.door_easter_base_ticks/2)
            self.player.door_easter_shots_needed = 3
            self.player.door_easter_score = 0
            self.player.door_easter_shots_revealed = 0
            self.set_shots()
            self.player.door_easter_running = 1
            self.machine.events.post("holiday_easter_music_start")
            self.machine.events.post('show_easter_slide_full')   
            self.machine.events.post('char_pause_and_hide')
            self.machine.events.post("ob_pause_and_hide")
            self.player.door_timer_ispaused = 0            
            self.delay.add(name="show_full_easter_intro_remover", ms=5000, callback=self.show_screen)


    def show_screen(self, **kwargs):
        self.log.info( "5 seconds passed, show narrow or wide" )
        self.ticks_msg = self.ticks
        self.delay.add(name="door_easter_ticker", ms=500, callback=self.ticker) 
        if self.player.door_timer_ispaused == 0:        
            self.machine.events.post("char_resume_and_show")
            self.machine.events.post("ob_resume_and_show")         
            self.reshow_screen()        
            if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                self.machine.events.post('show_easter_msg_1_n')                
            else:
                self.machine.events.post('show_easter_msg_1')

            
    def ticker(self):
        self.log.info("door_easter - 500ms ticks " +str(self.ticks))
        self.player.door_easter_timeleft = int(self.ticks/2)
        if self.player.door_easter_running == 1:         
            self.delay.add(name="door_easter_ticker", ms=500, callback=self.ticker)        
        if self.player.door_timer_ispaused == 0:        
            self.ticks -= 1
            if self.ticks <= 0:
                self.door_easter_stop()
            else:
                if  self.ticks_msg-self.ticks > 3:
                    self.msg += 1
                    self.ticks_msg = self.ticks
                    if self.msg > 3: 
                        self.msg = 1                  
                    if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                        self.machine.events.post('show_easter_msg_'+str(self.msg)+'_n')            
                    else:
                        self.machine.events.post('show_easter_msg_'+str(self.msg))            

                
    def switch_to_narrow(self, **kwargs):   
        self.remove_all_widgets()
        self.machine.events.post('show_easter_slide_narrow')

        
    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()
        self.machine.events.post('show_easter_slide_wide')


    def extend_time(self, time, **kwargs):
        self.log.info("door_easter - time extended " +str(time))
        self.ticks += time*2;
        self.ticks_msg += time*2;        
        self.player.door_easter_timeleft = int(self.ticks/2)
                        

    def door_easter_stop(self):
        if self.player.door_easter_running == 1:
            self.machine.events.post('holiday_easter_music_stop')
            self.log.info("door_easter over")
            if self.player.door_easter_shots_revealed >= self.player.door_easter_shots_needed:
                self.machine.events.post('holiday_mode_stopped', state="complete")
                self.player.door_easter_running = 2 #completed
            else:
                self.machine.events.post('holiday_mode_stopped', state="incomplete")
                self.player.door_easter_running = 0 #ready to start again
            self.clear_shots()
        self.machine.events.post('remove_easter_messages')
        self.machine.events.post('oogie_switch_to_wide')
        self.machine.events.post('remove_easter_narrow')
        self.machine.events.post('remove_easter_wide')
        self.machine.events.post("char_resume_and_show")


    def set_shots(self):
        x = 0
        while x < 10:
            p = random.randint(0,9)
            if self.player.door_easter_shot_value[p] == 0:
                self.player.door_easter_shot_value[p] = self.player.door_easter_shot_pool[x]
                x += 1
        self.log.info('door_easter - shots - ' + str(self.player.door_easter_shot_value)) 
        self.clear_shots()
        for x in range(0, 10):
            self.player.door_easter_shotlist[x]["state"] = "violet"
        self.set_shot_lights()


    def set_shot_lights(self):
        for x in range(0, 10):
            state = self.player.door_easter_shotlist[x]["state"]
            if state != 'off':
                self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="Door_Easter", action="add")


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
        

    def reveal_state(self, shot):
        old_state = self.player.door_easter_shotlist[shot]["state"]    	
        self.machine.events.post('arrow_change', led_num=shot, script_name=old_state, mode_name="Door_Easter", action="remove")
        val = self.player.door_easter_shot_value[shot]
        new_state = "off"
        if val == 1000000:
            new_state = "blue"
        if val == 500000:
            new_state = "green"
        if val == 250000:
            new_state = "yellow"
        if val == 100000:
            new_state = "orange"
        if val == 50000:
            new_state = "red"
        self.player.door_easter_shotlist[shot]["state"] = new_state
        self.machine.events.post('arrow_change', led_num=shot, script_name=new_state, mode_name="Door_Easter", action="add")
    

    def handle_shot(self, shot):
        if self.player.door_easter_running == 1:
            self.log.info('door_easter - shot hit - ' + str(shot))         
            if self.player.door_easter_shotlist[shot]["state"] == "violet":
                self.log.info('door_easter - reveal ')
                self.machine.events.post('easter_value_revealed')
                self.reveal_state(shot)
                self.player.door_easter_shots_revealed += 1
                if self.player.door_easter_shots_revealed == 3:
                    self.log.info('door_easter - 3 shots revealed')
                    #shut off the remaining white ones         
                    for x in range(0, 10):
                        state = self.player.door_easter_shotlist[x]["state"]
                        if state == "violet":
                            self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="Door_Easter", action="remove")                        
                            self.player.door_easter_shotlist[x]["state"] = "off"
            if self.player.door_easter_shotlist[shot]["state"] != "off":
                self.log.info('door_easter - shot hit - ' + str(self.player.door_easter_shot_value[shot]))         
                self.machine.events.post('easter_value_collected')
                #score
                self.score = self.player.door_easter_shot_value[shot]
                self.score *= self.player.multiplier_shot_value_list[shot] # 1X, 2X or 3X 
                self.player.door_easter_score = self.score
                self.player.score += self.score
    
    
    def clear_shots(self):
        for x in range(0, 10):
            state = self.player.door_easter_shotlist[x]["state"]
            if state != 'off':
                self.machine.events.post('arrow_change', led_num=x, script_name=state, mode_name="Door_Easter", action="remove")                        
                self.player.door_easter_shotlist[x]["state"] = "off"
    

    def mode_stop(self, **kwargs):
        self.log.info('Door_Easter mode_stop')
        self.door_easter_stop()
        self.clear_shots()

