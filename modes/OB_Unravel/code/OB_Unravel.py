from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Oogie Boogie Mode #6 - "Oogie Boogie's Unravelling" Multiball                                                                                                       Page 36
# 
# Brief Description
# This is a very unusual 3-ball multiball frenzy where all targets are worth points, 
# but you don't actually get any of the points until you're down to one ball, at which point
# you have 15 seconds to get the ball into Oogie Boogie's lair, or the mode is failed 
# and you don't get anything.
# 
# Scenario
# Jack is ready to unravel Oogie Boogie, but he has to be careful in case 
# Oogie Boogie happens to have an ace up his non-existent sleeves!
# 
# Details
# This is a 3-ball multiball, but not in a traditional sense. 
# When this mode begins, the whole playfield lights up and every switch is worth 50,000 points, the value of
# which can be raised by hitting the gate, which stays up for most of the multiball. However, none of the 
# frenzy points scored while this mode is active will actually be given to the player, and instead are getting 
# "Banked" according to the display. (Non-frenzy scoring will still be awarded as normal so as to be compatible 
# with any other modes which happen to be running.) Once two balls have drained and only one ball remains, 
# the gate finally goes down and you have 15 seconds to get the ball into Oogie Boogie's lair to finish the mode 
# and score your banked points. Failing to do this will end the mode without awarding any of your banked points. 
# (But at least you'll be able to play the mode again.)
# 
# Start with 10,000,000 points in bank, gate up.
# Every switch hit (except gate) reduces bank by 1,000,000 
# If it drops to 0, mode over.  If ball ends, mode over.
# CW horseshoe loop opens oogie diverter for 10 seconds.
# Make the CCW horseshoe to add 1,000,000 to bank.
# Complete gate targets, gate drops.  Collect bank at Oogie hole.
# 
# Scoring
# Every Switch                        50,000 (Banked)
# Frenzy Value Increments             2,500 (5,000 if two targets hit on gate simultaneously, 7,500 if all three)
# 
# Lighting
# All the lights go crazy during this mode, though the gate lights will rapidly flash white. 
# Once you're down to one ball, ALL of the playfield lights go out, except for the
# gate lights which will pulse yellow to alert the player to shoot for the lair ASAP!
# 
# Difficulty Adjustments
# Very Easy         4-Ball Multiball, 25 Seconds to Make Final Shot
# Easy              3-Ball Multiball, 20 Seconds to Make Final Shot
# Normal            3-Ball Multiball, 15 Seconds to Make Final Shot
# Hard              3-Ball Multiball, 12 Seconds to Make Final Shot
# Very Hard         2-Ball Multiball, 10 Seconds to Make Final Shot

class OB_Unravel(Mode):

    def mode_init(self):
        self.log.info('OB_Unravel mode_init')

    def mode_start(self, **kwargs):
        self.log.info('OB_Unravel mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.OB_mode_6_started == 0:
            #once per game only
            self.player.OB_mode_6_started = 1
            self.player.OB_mode_6_running = 0
        self.ticks = 20  #TODO
        self.player.OB_Unravel_timeleft = int(self.ticks/2)
        self.add_mode_event_handler('oogie_switch_to_narrow', self.switch_to_narrow)        
        self.add_mode_event_handler('oogie_switch_to_wide', self.switch_to_wide)
        self.add_mode_event_handler("ob_resume_and_show", self.reshow_screen)   
        self.add_mode_event_handler("ob_pause_and_hide", self.remove_all_widgets)        
        self.msg = 1
        self.ticks_msg = self.ticks
        self.start_battle()

        
    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_OB_Unravel_messages")  
        self.machine.events.post('remove_OB_Unravel_slide_wide')
        self.machine.events.post('remove_OB_Unravel_slide_narrow')
        self.machine.events.post('remove_OB_Unravel_slide_intro')
        

    def reshow_screen(self, **kwargs):   
        if self.player.Doors_state == 1:  #door mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        
        

    def hit_target(self, x):
        nb = random.randint(1,6)
        self.machine.events.post('bug_splat_'+str(nb))
        self.player["score"] += (22220)


    def end_battle(self):
        if (self.player.OB_mode_6_running == 1):
            self.player.OB_mode_6_running = 2
            self.machine.events.post('OB_Unravel_music_stop')
            self.log.info("OB mode 6 over")
            self.delay.remove('OB_mode_6_ticker')  
            self.machine.events.post('ob_mode_stopped', ob_state="complete", ob_mode="6")      
        self.remove_all_widgets()
        self.machine.events.post("char_resume_and_show")
        self.machine.events.post("doors_resume_and_show")        


    def start_battle(self):
        self.log.info("In The Oogie hole - start the battle?")
        if (self.player.OB_mode_6_running == 0):
            self.player.OB_mode_6_running = 1
            self.machine.events.post('OB_Unravel_music_start')
            self.ticks = 40
            self.player.OB_Unravel_timeleft = int(self.ticks/2)
            self.machine.events.post('show_OB_Unravel_slide_intro') 
            self.machine.events.post('char_pause_and_hide')  
            self.machine.events.post("doors_pause_and_hide")
            self.player.ob_timer_ispaused = 0                    
            self.delay.add(name="show_full_OB_Unravel_intro_remover", ms=5000, callback=self.show_screen)


    def show_screen(self, **kwargs):
        self.log.info( "5 seconds passed, show narrow or wide" )
        self.delay.add(name='OB_mode_6_ticker', ms=500, callback=self.ticker)
        if self.player.ob_timer_ispaused == 0:
            self.machine.events.post("char_resume_and_show")
            self.machine.events.post("doors_resume_and_show")                
            self.reshow_screen()        


    def ticker(self):
        self.log.info("500ms ticks " + str(self.ticks))
        self.machine.events.post('Unravel_OB_countdown')
        self.player.OB_Unravel_timeleft = int(self.ticks/2)
        self.delay.add(name='OB_mode_6_ticker', ms=500, callback=self.ticker)        
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
                            self.machine.events.post('show_OB_Unravel_msg_'+str(self.msg)+'_n')            
                        else:
                            self.machine.events.post('show_OB_Unravel_msg_'+str(self.msg))            

                
    def switch_to_narrow(self, **kwargs):   
        self.remove_all_widgets()    
        self.machine.events.post('show_OB_Unravel_slide_narrow')


    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()    
        self.machine.events.post('show_OB_Unravel_slide_wide')


    def mode_stop(self, **kwargs):
        self.log.info('OB_Unravel mode_stop')
        self.end_battle()

