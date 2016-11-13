from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Oogie Boogie Mode #1 - "Bug Bash" Multiball                                                                                                                        Page 31
#
# Brief Description
# All of the standups light for huge points, but the point value of each decreases each time it's hit.
#
# Scenario
# Oogie Boogie's first line of defence is the army of bugs he has as his command! 
# Squash as many as you can!
#
# Details
# This is a 2-ball multiball. When the mode begins, the gate rises and stays 
# up for the duration of the multiball. The JACK targets, the LSB targets, the Doctor
# Finklestein target, and the Gate targets (11 in total) all light up to indicate bugs 
# to squash. Each target you hit is worth an amount of points, but the amount of points
# you get decreases per target each time it's hit. To get the most points possible 
# before draining out of this multiball you must hit as many different standups as you
# can. As with most multiballs in this game, this mode is completed simply by starting it.
#
# Scoring
# First Hit of a Standup            200,000 (Blue)
# Second Hit                        100,000 (Green)
# Third Hit                         50,000 (Yellow)
# Fourth Hit                        25,000 (Orange)
# All Hits Following                10,000 (Red)
#
# Lighting
# Standups flash in the colours indicated in the scoring section.
#
# Difficulty Adjustments
# None

class OB_Bug_Bash(Mode):

    def mode_init(self):
        self.log.info('OB Bug Bash Multiball mode_init')
        self.delay = DelayManager(self.machine.delayRegistry)
        
    def mode_start(self, **kwargs):
        self.log.info( 'OB Bug Bash Multiball mode_start')
        if self.player.OB_mode_1_mb_started == 0:
            #once per game only
            self.player.OB_mode_1_mb_started = 1
            self.player.OB_multiball_running = 0
        self.player.bug_score = 0
        self.add_mode_event_handler('sw_bugbashtarget1', self.bug_hit1)
        self.add_mode_event_handler('sw_bugbashtarget2', self.bug_hit2)
        self.add_mode_event_handler('sw_bugbashtarget3', self.bug_hit3)
        self.add_mode_event_handler('sw_bugbashtarget4', self.bug_hit4)
        self.add_mode_event_handler('sw_bugbashtarget5', self.bug_hit5)
        self.add_mode_event_handler('sw_bugbashtarget6', self.bug_hit6)
        self.add_mode_event_handler('sw_bugbashtarget7', self.bug_hit7)
        self.add_mode_event_handler('sw_bugbashtarget8', self.bug_hit8)
#        self.add_mode_event_handler('sw_bugbashtarget9', self.bug_hit9)
        self.add_mode_event_handler('sw_bugbashtarget10', self.bug_hit10)
        self.add_mode_event_handler('sw_bugbashtarget11', self.bug_hit11)
        self.add_mode_event_handler('sw_bugbashtarget12', self.bug_hit12)
        self.add_mode_event_handler('balldevice_trough_ball_enter', self.ball_drained)
        self.add_mode_event_handler('oogie_switch_to_narrow', self.switch_to_narrow)        
        self.add_mode_event_handler('oogie_switch_to_wide', self.switch_to_wide)   
        self.add_mode_event_handler("ob_resume_and_show", self.reshow_screen)    
        self.add_mode_event_handler("ob_pause_and_hide", self.remove_all_widgets)
        self.player.bug_targets_list = [
            {"led":"rgb_lramp_ldiamond", "state":"unlit"}
            ,{"led":"rgb_lramp_rdiamond", "state":"unlit"}
            ,{"led":"rgb_lock_rect", "state":"unlit"}
            ,{"led":"rgb_shock_rect", "state":"unlit"}
            ,{"led":"rgb_barrel_rect", "state":"unlit"}
            ,{"led":"rgb_bug_1", "state":"unlit"}
            ,{"led":"rgb_bug_2", "state":"unlit"}
            ,{"led":"rgb_bug_3", "state":"unlit"}
#            ,{"led":"rgb_mystery_rect", "state":"unlit"}
            ,{"led":"rgb_rramp_ldiamond", "state":"unlit"}
            ,{"led":"rgb_rramp_rdiamond", "state":"unlit"}
            ,{"led":"rgb_doctor_rect", "state":"unlit"}
            ]
        self.ticks = 0    
        self.msg = 1
        self.ticks_msg = self.ticks
        self.start_multiball()
 
 
    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_bug_bash_messages")  
        self.machine.events.post('remove_bug_bash_slide_wide')
        self.machine.events.post('remove_bug_bash_slide_narrow')
        self.machine.events.post('remove_bug_bash_slide_intro')
        
        
    def reshow_screen(self, **kwargs):   
        self.log.info('reshow_screen')
        if self.player.Doors_state == 1:  #door mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        
        
        
    def switch_to_narrow(self, **kwargs):   
        self.remove_all_widgets()
        self.machine.events.post('show_bug_bash_slide_narrow')


    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()
        self.machine.events.post('show_bug_bash_slide_wide')


    def ball_drained(self, **kwargs):
        if (self.player.OB_Gate_mode_number == 1 and self.player.OB_Gate_current_mode_state == 1):
            self.log.info('OB Bug Bash multiball - ball drained BIP='+str(self.machine.game.balls_in_play))
            if self.machine.game.balls_in_play <= 2:
                if self.player.ball_save_active == 0:
                    #there is only 1 ball on playfield, end multiball
                    self.log.info( "Bug Bash multiball over" )                    
                    self.player.OB_multiball_running = 2
                    self.machine.events.post('bug_bash_music_stop')
                    self.machine.events.post('ob_mode_stopped', ob_state="complete", ob_mode="1")                
                    self.machine.events.post('enable_combos')
                    self.machine.events.post('add_a_ball_stop')
                    self.machine.events.post("char_resume_and_show")                    
                    self.machine.events.post('door_switch_to_wide')                 
                    self.remove_all_widgets()        
                else:
                    self.log.info( "OB Bug Bash multiball - ball drained - but ball save is running" )
            else:
                self.log.info( "OB Bug Bash multiball - ball drained - still are at least 2 BIP" )            


    def start_multiball(self):
        if (self.player.OB_multiball_running == 0):
            self.log.info( "In The Oogie hole - start the Bug Bash Multiball mode" )
            for x in range(0, 11):
                self.set_bug_light_state(x, 'blue')
            bip = self.machine.game.balls_in_play             
            if bip < 6:
                self.log.info( "OB - BB - add a bip")
                self.machine.game.balls_in_play = bip+1
                self.machine.playfield.add_ball(1, player_controlled=False)
            self.player.OB_multiball_running = 1
            self.machine.events.post('bug_bash_music_start')
            self.machine.events.post('disable_combos')
            self.machine.events.post('add_a_ball_start')
            self.machine.events.post('enable_the_mb_ball_save')   
            self.machine.events.post('show_bug_bash_slide_intro') 
            self.machine.events.post('char_pause_and_hide')
            self.machine.events.post("doors_pause_and_hide")
            self.player.ob_timer_ispaused = 0
            self.delay.add(name="show_full_bug_bash_intro_remover", ms=5000, callback=self.show_screen)

            
    def show_screen(self, **kwargs):
        self.log.info( "5 seconds passed, show narrow or wide" )
        self.delay.add(name='OB_mode_1_ticker', ms=500, callback=self.ticker)
        if self.player.ob_timer_ispaused == 0:
            self.reshow_screen()
            self.machine.events.post("char_resume_and_show")
            self.machine.events.post("doors_resume_and_show")
        

    def ticker(self):
        self.log.info("500ms ticks " + str(self.ticks))
        self.delay.add(name='OB_mode_1_ticker', ms=500, callback=self.ticker)                    
        if self.player.ob_timer_ispaused == 0:        
            self.ticks += 1;
            if self.ticks_msg-self.ticks > 3:
                self.msg += 1
                self.ticks_msg = self.ticks
                if self.msg > 3: 
                    self.msg = 1  
                if self.ticks > 2:                                
                    if self.player.Doors_state == 1:  #door mode running            	
                        self.machine.events.post('show_OB_bug_bash__msg_'+str(self.msg)+'_n')            
                    else:
                        self.machine.events.post('show_OB_bug_bash__msg_'+str(self.msg))            


    def bug_hit1(self, **kwargs):
        self.hit_target(0)
    def bug_hit2(self, **kwargs):
        self.hit_target(1)
    def bug_hit3(self, **kwargs):
        self.hit_target(2)
    def bug_hit4(self, **kwargs):
        self.hit_target(3)
    def bug_hit5(self, **kwargs):
        self.hit_target(4)
    def bug_hit6(self, **kwargs):
        self.hit_target(5)
    def bug_hit7(self, **kwargs):
        self.hit_target(6)
    def bug_hit8(self, **kwargs):
        self.hit_target(7)
    def bug_hit10(self, **kwargs):
        self.hit_target(8)
    def bug_hit11(self, **kwargs):
        self.hit_target(9)
    def bug_hit12(self, **kwargs):
        self.hit_target(10)


    def hit_target(self, x):
        self.log.info("Oogie Bug Bash - target hit - " + str(x))    
        if self.player.OB_multiball_running == 1:
            nb = random.randint(1,6)
            self.machine.events.post('bug_splat_'+str(nb))
            if self.player.Doors_state == 1:  #door mode running            
                self.machine.events.post('show_bug_bash_bash_narrow')            
            else:
                self.machine.events.post('show_bug_bash_bash_wide')                        
            state = self.player.bug_targets_list[x]["state"]
            if state == 'blue':
                self.player.bug_score = 200000
                self.player.bug_targets_list[x]["state"] = 'green'
            elif state == 'green':
                self.player.bug_score = 100000
                self.player.bug_targets_list[x]["state"] = 'yellow'
            elif state == 'yellow':
                self.player.bug_score = 50000
                self.player.bug_targets_list[x]["state"] = 'orange'
            elif state == 'orange':
                self.player.bug_score = 25000
                self.player.bug_targets_list[x]["state"] = 'red'
            elif state == 'red':
                self.player.bug_score = 10000

            self.player["score"] += self.player.bug_score
            if state == 'red':
                #check if all red?, then reset to blue?
                total = 0
                for xx in range(0, 11):
                    if self.player.bug_targets_list[xx]["state"] == 'red':
                        total += 1
                if total == 11:
                    for xx in range(0, 11):
                        self.set_bug_light_state(xx, 'blue')


    def set_bug_light_state(self, x, state):
        self.player.bug_targets_list[x]["state"] = state


    def mode_stop(self, **kwargs):
        self.log.info( 'OB Bug Bash mode_stop' )


