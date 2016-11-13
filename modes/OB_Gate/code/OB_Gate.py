from mpf.core.mode import Mode
from mpf.core.delays import DelayManager


# For Oogie Boogie, there's a gate in front of his lair which bars access. Getting through the gate is a different process for each Oogie Boogie mode you have yet to
# play and involves different colours of bugs. Once the gate is down though, all you have to do is shoot the ball into his lair to start the next Oogie Boogie mode. If you
# manage to get a ball back there with the gate up, you can start the next mode without having to knock the gate down. Unlike Character and Door modes, Oogie
# Boogie modes MUST be completed in order.
# 
# To open the gate for each Oogie Boogie mode (including the wizard mode), first it's important to understand the bug colours:
# 
# Bug Colour       How it Works
# Yellow          Simply hit it and it clears away
# Green           When hit, it turns red and counts as cleared
# Red             If you hit a red bug before you finish clearing the rest, ALL bugs reset to how they started!
# Purple          When hit the first time, starts flashing. You then have 10 seconds to hit it again to clear it away, otherwise it stops flashing
# 
# Oogie Boogie Mode                 Defending Bugs
# 1 - Bug Bash                      All Yellow Bugs
# 2 - Santa Vs. Oogie Boogie        Middle Green Bug, Outer Yellow Bugs
# 3 - Sally Vs. Oogie Boogie        Middle Yellow Bug, Outer Green Bugs
# 4 - Luck o' the Dice              All Green Bugs
# 5 - Jack Vs. Oogie Boogie         Middle Purple Bug, Outer Yellow Bugs
# 6 - Oogie Boogie's Unravelling    All Purple Bugs
# W - Mega Oogie Showdown           Middle Green Bug, Outer Purple Bugs

class OB_Gate(Mode):

    def mode_init(self):
        self.log.info('OB Gate mode_init')

    def mode_start(self, **kwargs):
        self.log.info('OB Gate mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.OB_Gate_started == 0:
            #once per game only
            self.player.OB_Gate_started = 1
            self.player.OB_Gate_mode_number = 1
            self.player.OB_Gate_current_mode_state = 0
            self.player.OB_Gate_bug_state = [0,0,0] 
            self.player.OB_Gate_state = "unknown"
        self.player.gate_show_handles = [0] * 3
        self.add_mode_event_handler('sw_targetbankdown', self.stop_moving_down)
        self.add_mode_event_handler('sw_targetbankup', self.stop_moving_up)
        self.add_mode_event_handler('sw_oogietarget1', self.t1_hit)
        self.add_mode_event_handler('sw_oogietarget2', self.t2_hit)
        self.add_mode_event_handler('sw_oogietarget3', self.t3_hit)
        self.add_mode_event_handler('sw_subwayoogie', self.oogie_hit)
        self.add_mode_event_handler('GK_starting', self.GK_starting)  
        self.add_mode_event_handler('GK_ending', self.GK_ending)          
        
        self.add_mode_event_handler('GK_close_the_gate', self.close_the_gate)
        self.add_mode_event_handler('GK_open_the_gate', self.open_the_gate)                    
        self.add_mode_event_handler('ob_mode_stopped', self.ob_mode_stopped)
        self.add_mode_event_handler("ob_pause_and_hide", self.pause_and_hide)  
        self.add_mode_event_handler("ob_resume_and_show", self.resume_and_show)  
        self.machine.events.post('ob_mode_stop_leds')
        if self.player.OB_Gate_current_mode_state == 1:
            #previous ball ended during a mode, skip to next one
            self.ob_mode_stopped()
        #make sure gate starts in up position
        self.player.OB_Gate_wanted_state = "up"
        if self.player.OB_Gate_state != 'up':
            self.start_moving()
        #set bug states
        self.set_bugs()
        
        
    def GK_starting(self, **kwargs):
        self.player.OB_Gate_current_mode_state = 1
        self.clear_all_lights()
                
                
    def GK_ending(self, **kwargs):
        self.player.OB_Gate_current_mode_state = 0    
        self.reset_all_lights()
        self.machine.events.post('gate_keeper_MB_stop')
        
        
    def pause_and_hide(self, **kwargs):      
        self.log.info("pause_and_hide, post ob_remove_all")
        self.player.ob_timer_ispaused = 1

        
    def resume_and_show(self, **kwargs):        
        self.player.ob_timer_ispaused = 0


    def ob_mode_stopped(self, ob_mode=None, ob_state=None, **kwargs):
        self.machine.events.post('ob_mode_'+str(ob_mode)+'_stop')
        self.log.info("Advancing Oogie Mode")
        self.player.OB_Gate_current_mode_state = 0
        self.player.OB_Gate_mode_number += 1 
        self.set_bugs()
        if self.player.OB_Gate_state != 'up':
            self.start_moving()


    def set_bugs(self):
        self.log.info(("Setting bugs to mode "+str(self.player.OB_Gate_mode_number )))
        if self.player.OB_Gate_mode_number == 1:
            self.player.OB_Gate_bug_state[0] = 1
            self.player.OB_Gate_bug_state[1] = 1
            self.player.OB_Gate_bug_state[2] = 1
            self.machine.events.post('ob_mode_1_next')
        elif self.player.OB_Gate_mode_number == 2:
            self.player.OB_Gate_bug_state[0] = 1
            self.player.OB_Gate_bug_state[1] = 2
            self.player.OB_Gate_bug_state[2] = 1
            self.machine.events.post('ob_mode_2_next')
        elif self.player.OB_Gate_mode_number == 3:
            self.player.OB_Gate_bug_state[0] = 2
            self.player.OB_Gate_bug_state[1] = 1
            self.player.OB_Gate_bug_state[2] = 2
            self.machine.events.post('ob_mode_3_next')
        elif self.player.OB_Gate_mode_number == 4:
            self.player.OB_Gate_bug_state[0] = 2
            self.player.OB_Gate_bug_state[1] = 2
            self.player.OB_Gate_bug_state[2] = 2
            self.machine.events.post('ob_mode_4_next')
        elif self.player.OB_Gate_mode_number == 5:
            self.player.OB_Gate_bug_state[0] = 1
            self.player.OB_Gate_bug_state[1] = 4
            self.player.OB_Gate_bug_state[2] = 1
            self.player.OB_Gate_wanted_state = 'up'
            self.machine.events.post('ob_mode_5_next')
        elif self.player.OB_Gate_mode_number == 6:
            self.player.OB_Gate_bug_state[0] = 4
            self.player.OB_Gate_bug_state[1] = 4
            self.player.OB_Gate_bug_state[2] = 4
            self.machine.events.post('ob_mode_6_next')
        elif self.player.OB_Gate_mode_number == 7:
            self.player.OB_Gate_bug_state[0] = 4
            self.player.OB_Gate_bug_state[1] = 2
            self.player.OB_Gate_bug_state[2] = 4
            self.machine.events.post('ob_mode_7_next')
        self.set_light(0)
        self.set_light(1)
        self.set_light(2)


    def reset_all_lights(self, **kwargs):
        self.set_light(0)
        self.set_light(1)
        self.set_light(2)
        
        
    def clear_lights(self, x):
        if self.player.gate_show_handles[x] != 0:
            self.player.gate_show_handles[x].stop()
            self.player.gate_show_handles[x] = 0

    def set_light(self, x):
        led = "rgb_bug_"+str(x+1)
        self.clear_lights(x)
        self.log.info(("Setting rgb "+led + " to " +str(self.player.OB_Gate_bug_state[x] )))
        #self.machine.light_controller.stop_script("OB_Gate_"+str(x))
        if self.player.OB_Gate_bug_state[x] == 0:
            script_name = "sc_off"
            #self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=1)						
        if self.player.OB_Gate_bug_state[x] == 1:
            script_name = "sc_yellow_flash"
            self.player.gate_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)									
        if self.player.OB_Gate_bug_state[x]== 2:
            script_name = "sc_green_flash"
            self.player.gate_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)									
        if self.player.OB_Gate_bug_state[x]== 3:
            script_name = "sc_red_flash"
            self.player.gate_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)									
        if self.player.OB_Gate_bug_state[x]== 4:
            script_name = "sc_purple_flash"
            self.player.gate_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)									
        if self.player.OB_Gate_bug_state[x]== 5:
            script_name = "sc_blue_flash"
            self.player.gate_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)						



    def close_the_gate(self, **kwargs):
        self.player.OB_Gate_wanted_state = "up"
        self.start_moving()


    def open_the_gate(self, **kwargs):
        self.player.OB_Gate_wanted_state = "down"
        self.start_moving()
    	

    def stop_moving_up(self, **kwargs):
        self.machine.coils['targetbankmotor'].disable()
        self.player.OB_Gate_state = "up"
        if self.player.OB_Gate_wanted_state == "down":
            self.start_moving()


    def stop_moving_down(self, **kwargs):
        self.machine.coils['targetbankmotor'].disable()
        self.player.OB_Gate_state = "down"
        if self.player.OB_Gate_wanted_state == "up":
            self.start_moving()

    def start_moving(self):
        self.log.info(("Move the target bank "+ self.player.OB_Gate_wanted_state))
        self.machine.coils['targetbankmotor'].enable()

    def t1_hit(self, **kwargs):
        if self.player.gate_keeper_multiball_running != 1:
            self.hit(0)
    def t2_hit(self, **kwargs):
        if self.player.gate_keeper_multiball_running != 1:    	
            self.hit(1)
    def t3_hit(self, **kwargs):
        if self.player.gate_keeper_multiball_running != 1:    	
            self.hit(2)

    def hit(self, x):
        if self.player.OB_Gate_current_mode_state == 0:
            self.log.info(('Bug hit - '+str(x)))
            self.machine.events.post('bug_hit_'+str(x))
            if self.player.OB_Gate_bug_state[x] == 0:   # off
                #do nothing
                self.player.OB_Gate_bug_state[x] = 0
                self.machine.events.post('bug_splat_1')
                self.player["score"] += (1000)
            elif self.player.OB_Gate_bug_state[x] == 1:   #yellow -> off
                self.player.OB_Gate_bug_state[x] = 0
                self.machine.events.post('bug_splat_2')
                self.player["score"] += (2000)
            elif self.player.OB_Gate_bug_state[x] == 2:   #green -> red
                self.player.OB_Gate_bug_state[x] = 3
                self.machine.events.post('bug_splat_3')
                self.player["score"] += (3000)
            elif self.player.OB_Gate_bug_state[x] == 3:   #red -> reset all
                self.set_bugs()
                self.machine.events.post('bug_splat_nooo')
                self.player["score"] += (5000)
            elif self.player.OB_Gate_bug_state[x] == 4:   #purple -> blue
                self.player.OB_Gate_bug_state[x] = 5
                self.machine.events.post('bug_splat_5')
                self.player["score"] += (2000)
                #start timer, 10 seconds, if expires, reset to state 4
                if x == 0: 
                    self.delay.add(name='target_purple_revert_0', ms=10000, callback=self.purple_revert_0)
                elif x == 1: 
                    self.delay.add(name='target_purple_revert_1', ms=10000, callback=self.purple_revert_1)
                elif x == 2: 
                    self.delay.add(name='target_purple_revert_2', ms=10000, callback=self.purple_revert_2)
            elif self.player.OB_Gate_bug_state[x] == 5:   #blue -> off, if timeout ->purple
                #stop the timer
                self.delay.remove('target_purple_revert_'+str(x))
                self.player.OB_Gate_bug_state[x] = 0
                self.machine.events.post('bug_splat_6')
                self.player["score"] += (10000)
            else:
                self.log.info("Unknown bug state!")
            self.set_light(x)
            #check states?  are we all 0 or 3s?
            if (self.player.OB_Gate_bug_state[0] == 0 or self.player.OB_Gate_bug_state[0] == 3):
                if (self.player.OB_Gate_bug_state[1] == 0 or self.player.OB_Gate_bug_state[1] == 3):
                    if (self.player.OB_Gate_bug_state[2] == 0 or self.player.OB_Gate_bug_state[2] == 3):
                        self.player.OB_Gate_wanted_state = "down"
                        self.start_moving()
                        self.machine.events.post('ob_mode_'+str(self.player.OB_Gate_mode_number)+'_ready')
                        self.machine.events.post('gate_goes_down')
                        self.player.OB_Gate_bug_state[0] = 0
                        self.player.OB_Gate_bug_state[1] = 0
                        self.player.OB_Gate_bug_state[2] = 0
                        self.set_light(0)
                        self.set_light(1)
                        self.set_light(2)


    def purple_revert_0(self):
       self.player.OB_Gate_bug_state[0] = 4
       self.set_light(0)
    def purple_revert_1(self):
       self.player.OB_Gate_bug_state[1] = 4
       self.set_light(1)
    def purple_revert_2(self):
       self.player.OB_Gate_bug_state[2] = 4
       self.set_light(2)

       
    def clear_all_lights(self, **kwargs):
        self.log.info('OB Gate - clear lights')
        self.clear_lights(0)
        self.clear_lights(1)
        self.clear_lights(2)                


    def oogie_hit(self, **kwargs):
        if (self.player.OB_Gate_current_mode_state == 0 and self.player.gate_keeper_multiball_running != 1):
            self.log.info(("Oogie hit - mode "+str(self.player.OB_Gate_mode_number)))
            if self.player.OB_Gate_mode_number == 1:
                self.player.OB_Gate_wanted_state = "up"
                self.start_moving()
            elif self.player.OB_Gate_mode_number == 2:
                self.player.OB_Gate_wanted_state = "up"
                self.start_moving()
            elif self.player.OB_Gate_mode_number == 3:
                self.player.OB_Gate_wanted_state = "up"
                self.start_moving()
            elif self.player.OB_Gate_mode_number == 4:
                self.player.OB_Gate_wanted_state = "down"
            elif self.player.OB_Gate_mode_number == 5:
                self.player.OB_Gate_wanted_state = "up"
                self.start_moving()
            elif self.player.OB_Gate_mode_number == 6:
                self.player.OB_Gate_wanted_state = "up"
                self.start_moving()
            elif self.player.OB_Gate_mode_number == 7:
                self.player.OB_Gate_wanted_state = "up"
                self.start_moving()
            self.machine.events.post('ob_mode_'+str(self.player.OB_Gate_mode_number)+'_start')
            #self.machine.events.post('ob_mode_4_start')            
            self.player.OB_Gate_current_mode_state = 1 #mode running


    def mode_stop(self, **kwargs):
        self.log.info('OB Gate mode_stop')
        self.clear_all_lights()

