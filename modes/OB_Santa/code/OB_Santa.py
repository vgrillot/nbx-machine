from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Oogie Boogie Mode #2 - "Santa vs. Oogie Boogie"
# 
# Brief Description
# You must hide from Oogie Boogie by shooting for any shot which would get the ball off of the playfield. 
# In fact, the instructions on the display simply say, 
# "Get the ball off the playfield!"
# 
# Scenario
# Santa has no hope in combat against Oogie Boogie, so he hatches a plan to escape, 
# but Oogie Boogie is effortlessly tracking him in the dark! You must find Santa someplace to hide!
# 
# Details
# This mode has a 60 second time limit and NO ball saver. 
# The reason for having no ball saver is because one of the potential hiding places for getting the ball 
# off of the playfield... is the drain! Thus the first time you drain the ball in this mode actually 
# counts as hiding from Oogie Boogie, but because you can't use the same hiding
# space more than once, draining a second time will end the ball as normal. 
# This mode kills the playfield lighting, though things will still flash briefly when you shoot
# them so that the player knows the game isn't broken. Other places you can hide the ball include the 
# hinterlands, the graveyard, soup and the mayor. Hide the ball in three different places to complete the mode... 
# with Santa getting captured. Oh well, can't say he didn't TRY!
# 
# Scoring
# 1st Hiding Place     500,000
# 2nd Hiding Place   1,000,000
# 3rd Hiding Place   2,500,000
# 
# Lighting
# The entire playfield goes dark for this mode, but shots will flash briefly when you hit them so the 
# player doesn't think the game's broken.
# 
# Difficulty Adjustments
# Very Easy          90 Second Time Limit, Need to Hide 2 Times to Win
# Easy               90 Second Time Limit, Need to Hide 3 Times to Win
# Normal             60 Second Time Limit, Need to Hide 3 Times to Win
# Hard               60 Second Time Limit, Need to Hide 4 Times to Win
# Very Hard          40 Second Time Limit, Need to Hide 4 Times to Win

class OB_Santa(Mode):

    def mode_init(self):
        self.log.info('OB_Santa mode_init')

    def mode_start(self, **kwargs):
        self.log.info('OB_Santa mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.OB_mode_2_started == 0:
            #once per game only
            self.player.OB_mode_2_started = 1
            self.player.OB_mode_2_running = 0
        self.ticks = 40
        self.player.OB_Santa_timeleft = int(self.ticks/2)
        self.add_mode_event_handler('oogie_switch_to_narrow', self.switch_to_narrow)        
        self.add_mode_event_handler('oogie_switch_to_wide', self.switch_to_wide)
        self.add_mode_event_handler("ob_resume_and_show", self.reshow_screen)   
        self.add_mode_event_handler("ob_pause_and_hide", self.remove_all_widgets)        
        #todo - mayor, tub/hinterlands, grave, soup, drain
        self.msg = 1
        self.ticks_msg = self.ticks
        self.start_battle()
        
        
    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_OB_Santa_messages")  
        self.machine.events.post('remove_OB_Santa_slide_wide')
        self.machine.events.post('remove_OB_Santa_slide_narrow')
        self.machine.events.post('remove_OB_Santa_slide_intro')


    def reshow_screen(self, **kwargs):   
        self.log.info("reshow_screen")      
        if self.player.Doors_state == 1:  #door mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        
        
        
    def start_battle(self):
        self.log.info("In The Oogie hole - start the battle?")
        if (self.player.OB_mode_2_running == 0):
            self.ticks = 40
            self.player.OB_Santa_timeleft = int(self.ticks/2)
            self.player.OB_mode_2_running = 1
            self.machine.events.post('OB_Santa_music_start')
            self.machine.events.post('show_OB_Santa_slide_intro') 
            self.machine.events.post('char_pause_and_hide')
            self.machine.events.post("doors_pause_and_hide")
            self.player.ob_timer_ispaused = 0
            self.delay.add(name="show_full_OB_Santa_intro_remover", ms=5000, callback=self.show_screen)

            
    def show_screen(self, **kwargs):
        self.log.info( "5 seconds passed, show narrow or wide" )
        self.delay.add(name='OB_mode_2_ticker', ms=500, callback=self.ticker)
        if self.player.ob_timer_ispaused == 0:
            self.machine.events.post("char_resume_and_show") 
            self.machine.events.post("doors_resume_and_show")
            self.reshow_screen()


    def end_battle(self):
        if (self.player.OB_mode_2_running == 1):
            self.player.OB_mode_2_running = 2
            self.machine.events.post('OB_Santa_music_stop')
            self.log.info("OB mode 2 over")
            self.delay.remove('OB_mode_2_ticker')  
            self.machine.events.post('ob_mode_stopped', ob_state="complete", ob_mode="2")
        self.remove_all_widgets()
        self.machine.events.post("char_resume_and_show")
        self.machine.events.post("doors_resume_and_show")        


    def ticker(self):
        self.log.info("500ms ticks " + str(self.ticks))
        self.delay.add(name='OB_mode_2_ticker', ms=500, callback=self.ticker)
        self.player.OB_Santa_timeleft = int(self.ticks/2)  
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
                            self.machine.events.post('show_OB_Santa_msg_'+str(self.msg)+'_n')            
                        else:
                            self.machine.events.post('show_OB_Santa_msg_'+str(self.msg))            


    def switch_to_narrow(self, **kwargs):   
        self.remove_all_widgets()
        self.machine.events.post('show_OB_Santa_slide_narrow')


    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()
        self.machine.events.post('show_OB_Santa_slide_wide')


    def mode_stop(self, **kwargs):
        self.log.info('OB_Santa mode_stop')
        self.end_battle()

