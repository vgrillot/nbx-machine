from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Character Mode - "Kidnap the Sandi-Claws" Multiball
# 
# Brief Description
# Similar multiball to CFTBL. Three random major shots are lit, but only one has 
# Santa Claus in it. Once found, you have to get him back to Jack in the Graveyard 
# for a jackpot, or you can make the jackpot super by hitting all of the LSB targets 
# after finding Santa but before delivering him! This mode also overrides the normal
# functioning of the Hinterlands to give an alternative way of capturing Santa Claus.
# 
# Scenario
# Lock, Shock and Barrel are out to kidnap Santa Claus!
# 
# Details
# When this multiball starts, three major shots will be lit at random except for the Graveyard 
# and the left ramp, as these have special usage in this multiball. One of the major shots will 
# have Santa Claus, the other two will be bogus. Once you've got Santa Claus, the shot at the 
# graveyard lights and you must get past the gravestone and get to Jack to score the jackpot. 
# (You'll also get an add-a-ball if it's been qualified by the mystery target.) This process doesn't 
# change throughout the multiball, although there's a couple interesting points of note. Firstly, 
# it's possible to upgrade the jackpot into a super jackpot. To do this, you must hit all three of the LSB
# standups after kidnapping Santa Claus but before you deliver him to Jack. Secondly, the normal 
# functioning of the Hinterlands is overridden while this mode is active. Normally, starting a multiball 
# disables the Hinterlands Doors, but this mode keeps them going. If you shoot into the Hinterlands 
# with the wrong door selected, you get a small bonus and are treated to Jack saying you kidnapped the 
# wrong one. The slingshots will change the selected door as usual. When Christmas Town is selected, 
# the left ramp triangle will light up to indicate that shooting the Hinterlands will immediately 
# capture Santa Claus, guaranteed, but if you cycle the Hinterlands off of Christmas Town again, 
# the light will go out. Needless to say, this shot doesn't do anything while Santa Claus is captured. 
# As with all mutliballs, this mode is completed simply by starting it.
# 
# Scoring
# Wrong Major Shot                  100,000
# Wrong Hinterlands Door            100,000
# Santa Claus Kidnapped             250,000
# Jackpot                           5,000,000
# Jackpot Increase                  1,000,000
# Super Jackpot                     12,500,000
# Super Jackpot Increase            2,500,000
# 
# Lighting
# Major shots to aim for will flash with orange triangles. 
# The one with Santa Claus will actually be VERY slightly more yellow. 
# The Graveyard shot will flash a yellow triangle once ready for jackpot. 
# The LSB targets will flash red when hit before capturing Santa Claus and will begin 
# flashing white once Santa Claus is captured.
# Hitting them at this point makes them go solid white and once a super jackpot is ready, 
# the Graveyard shot will flash both the triangle and circle white. If the correct
# Hinterlands Door is selected to kidnap Santa Claus in this alternate manner, 
# the left ramp triangle will flash blue.
# 
# Difficulty Adjustments
# Very Easy        2 Major Shots Lit for Santa Claus
# Easy              2 Major Shots Lit for Santa Claus the First Time, 3 Each Subsequent Time
# Normal            3 Major Shots Lit for Santa Claus
# Hard              3 Major Shots Lit for Santa Claus the First Time, 4 Each Subsequent Time
# Very Hard         4 Major Shots Lit for Santa Claus
# 
# char_LSB - LSB Multiball
# - completed LSB lights, enable locks
# - left ramp gate - opens bathtub diverter for 5 seconds
# - tub optos - count ball locks
# - 3 locks - start MB & drain sequence
# - diverter disabled when MB running
# - MB ends when complete or balls in play == 1

class Char_LSB(Mode):

    def mode_init(self):
        self.log.info( 'char_LSB - LSB Multiball mode_init')

    def mode_start(self, **kwargs):
        self.log.info( 'LSB Multiball mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.lsb_multiball_mode_started == 0:
            #once per game only
            self.player.lsb_multiball_mode_started = 1
            self.player.lsb_mb_times_started = 0
            self.player.lsb_physical_balls_locked = 0
            self.player.lsb_balls_locked = 0
            self.index_list= [0,1,3,4,5,7,8,9]
        self.player.LSB_MB_running = 0
        self.player.LSB_MB_completed = 0        
        self.player.tub_lock_ready = 0
        self.santa_collected = 0
        self.santa_shot = 6
        self.not_santa_shot_1 = 6
        self.not_santa_shot_2 = 6
        self.super_jackpot_enabled = 0
        self.player.char_lsb_santa_value = 250000
        self.player.char_lsb_not_santa_value = 100000
        self.player.char_jackpot_value = 5000000
        self.player.char_jackpot_inc = 1000000
        self.player.char_super_jackpot_value = 12500000
        self.player.char_super_jackpot_inc = 2500000        
        
        self.player.char_lsb_shotlist = [
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
        #trees
        self.add_mode_event_handler("sw_hrampgate", self.into_the_trees)
        self.add_mode_event_handler("major_3_singlestep_unlit_hit", self.major_3)
        self.add_mode_event_handler("major_4_singlestep_unlit_hit", self.major_4)
        self.add_mode_event_handler("major_5_singlestep_unlit_hit", self.major_5)
        self.add_mode_event_handler("major_5a_singlestep_unlit_hit", self.major_5)
        #grave
        self.add_mode_event_handler("major_6_hit", self.grave_stone)
        self.add_mode_event_handler("major_6a_hit", self.jack_saucer)
        
        self.add_mode_event_handler("major_7_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_7a_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_8_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("major_8a_singlestep_unlit_hit", self.major_8)
        self.add_mode_event_handler("major_9_singlestep_unlit_hit", self.major_9)
        
        self.add_mode_event_handler('ball_starting', self.count_balls_in_bathtub)
        self.add_mode_event_handler('sw_lrampgate', self.open_bathtub_diverter)
        self.add_mode_event_handler("lsb_standups_lsbp_lit_complete", self.lsb_complete)        
        self.add_mode_event_handler('sw_enter_tub', self.close_bathtub_diverter) #opto 3 triggered
        self.add_mode_event_handler('sw_enter_tub', self.settle_time)
        self.add_mode_event_handler('balldevice_trough_ball_enter', self.ball_drained)
        self.add_mode_event_handler('door_switch_to_narrow', self.hide_slide)    
        self.add_mode_event_handler('oogie_switch_to_narrow', self.hide_slide) 
        self.add_mode_event_handler("char_resume_and_show", self.resume_and_show)
        
        


    def settle_time(self, **kwargs):
        self.log.info("LSB - delay 1 second for settling")
        self.delay.add(name='ball_entered', ms=1000, callback=self.ball_entered)


    def count_balls_in_bathtub(self, **kwargs):
        self.log.info('LSB - count balls in tub')
        self.player.lsb_physical_balls_locked = 0
        if self.machine.switch_controller.is_active('tublock1_opt'):
            self.player.lsb_physical_balls_locked += 1
        if self.machine.switch_controller.is_active('tublock2_opt'):
            self.player.lsb_physical_balls_locked += 1
        if self.machine.switch_controller.is_active('tublock3_opt'):
            self.player.lsb_physical_balls_locked += 1
        self.log.info('LSB - balls in tub = ' + str(self.player.lsb_physical_balls_locked))


    def open_bathtub_diverter(self, **kwargs):
        if (self.player.tub_lock_ready == 1 and self.player.LSB_MB_running == 0):
            if self.player.char_state == 2:
                self.log.info("LSB - another char mode is running, don't open for lock?")
            else:
                self.log.info("LSB - Bathtub Diverter open for 5 seconds")
                self.machine.coils['bathtubdiverter'].enable()
                self.delay.add(name='close_bathtub_diverter', ms=5000, callback=self.close_bathtub_diverter)


    def close_bathtub_diverter(self, **kwargs):
        self.log.info( "LSB - Bathtub Diverter closed")
        self.machine.coils['bathtubdiverter'].disable()


    def ball_drained(self, **kwargs):
        if self.player.LSB_MB_running == 1:
            self.log.info( "LSB - MB - ball drained" )
            self.log.info( "LSB - balls in play = " + str(self.machine.game.balls_in_play) )
            if self.machine.game.balls_in_play <= 2:
                if self.player.ball_save_active == 0:
                    #there is only 1 ball on playfield, end multiball
                    self.player.tub_lock_ready = 0
                    self.machine.events.post('tub_mb_music_stop')                    
                    self.log.info( "LSB - MB over")
                    if self.player.LSB_MB_completed > 0:
                        self.machine.events.post('char_mode_stopped', char_state="complete", char_mode="LSB")
                        self.player.LSB_MB_running = 2 #completed
                    else:
                        self.machine.events.post('char_mode_stopped', char_state="incomplete", char_mode="LSB")
                        self.player.LSB_MB_running = 0 #ready to start again
                    self.clear_shots()
                    self.machine.events.post('add_a_ball_stop')
                    self.machine.events.post('enable_combos')
                else:
                    self.log.info( "LSB - MB - ball drained - but ball save is running" )
            else:
                self.log.info( "LSB - MB - ball drained - more than 2 BIP" )            
                
                
    def lsb_complete(self, **kwargs):
        self.log.info( "LSB - lights completed")        	
        if self.player.LSB_MB_running == 0:
            if self.player.tub_lock_ready == 0:
                self.log.info( "LSB - lights complete - enable tub lock")
                self.player.tub_lock_ready = 1
                self.flash_lock_ready()
                if self.player.lsb_balls_locked == 0:
                    self.machine.events.post('LSB_bathtub_ready')
                elif self.player.lsb_balls_locked == 1:
                    self.machine.events.post('LSB_bathtub_ready1')
                else:
                    self.machine.events.post('LSB_bathtub_ready2')                    
                self.machine.events.post('char_remove_all')
                self.delay.add(name="restore_chars_screen_timer", ms=3000, callback=self.restore_chars_icons)
        else:
            self.log.info("LSB - lights complete during MB - super jackpot if santa collected")
            if self.santa_collected == 1:
                self.super_jackpot_enabled = 1
                self.clear_shots()
                self.player.char_lsb_shotlist[6]["state"] = 'purple'
                self.set_shot_lights()


    def restore_chars_icons(self, **kwargs):
        self.machine.events.post("char_resume_and_show")


    def flash_lock_ready(self):
        self.log.info("LSB - Flash the bathtub lock light" )
        led = "rgb_lramp_arrow"
        self.machine.events.post("arrow_change", led_num=2, script_name="green", mode_name="LSB_LOCK", action="add")


    def turn_off_lock_light(self):
        self.log.info('LSB - turn off lock light')
        led = "rgb_lramp_arrow"
        self.machine.events.post('arrow_change', led_num=2, script_name="green", mode_name="LSB_LOCK", action="remove")        


    def ball_entered(self):
        self.log.info('LSB - ball entered tub')
        oldcount = self.player.lsb_physical_balls_locked
        self.count_balls_in_bathtub()
        if self.player.LSB_MB_running == 0:
            if self.player.tub_lock_ready == 1:
                if self.player.char_state == 2:
                    #we are running another character mode, drain out a ball and continue
                    self.drain_tub()                
                else:
                    self.player.lsb_balls_locked += 1
                    self.machine.events.post('tub_ball_locked', lock=self.player.lsb_balls_locked)
                    self.machine.events.post('tub_ball_'+str(self.player.lsb_balls_locked)+'_locked', lock=self.player.lsb_balls_locked)            
                    self.machine.events.post('char_remove_all')
                    self.log.info('LSB - ball '+str(self.player.lsb_balls_locked)+' locked in tub')
                    if self.player.lsb_balls_locked < 3:                    
                        self.delay.add(name="restore_chars_screen_timer", ms=3000, callback=self.restore_chars_icons)
                    #reset the lockready if on harder level.  re-enable by LSB complete
                    if self.player.lsb_mb_times_started > 0:
                        self.player.tub_lock_ready = 0
                        self.turn_off_lock_light()
                    #more balls in tub, if not ours, drain instead of launching new one
                    if self.player.lsb_physical_balls_locked > self.player.lsb_balls_locked:
                        self.log.info('LSB - release excess ball')
                        self.drain_tub()
                    else:
                        if self.player.lsb_balls_locked >= 3:
                            #this is the 3rd ball, start MB
                            self.machine.events.post('LSB_ball_3_locked')                    
                            self.startMB()
                        else:
                            self.log.info('LSB - launch another ball')
                            self.delay.add(name='drain_bathtub', ms=2000, callback=self.add_another_ball)
            else:
                #we are in NOT MB and lock is NOT ready, why is there a ball entering the tub?  
                #the tub diverter should be closed too!
                self.drain_tub()
        else:
            #we are in MB, why is there a ball in tub?  
            #the tub diverter should be closed too!
            self.drain_tub()

            
    def add_another_ball(self):
        #if not already in a MB mode, then player can plunge and skillshot available
        if self.machine.game.balls_in_play < 2:
            self.machine.playfield.add_ball(balls=1, player_controlled=True)
            self.machine.events.post('start_skillshot_mode')
        else:
            self.machine.playfield.add_ball(balls=1, player_controlled=False)            
    
    
    def startMB(self):
        #start multiball
        self.log.info('LSB - start MB')
        self.player.LSB_MB_running = 1
        self.santa_collected = 0
        self.player.lsb_balls_locked = 0
        self.player.lsb_mb_times_started += 1
        if self.player.lsb_physical_balls_locked == 3:
            self.delay.add(name='drain_bathtub', ms=1000, callback=self.slowrelease)
        if self.player.lsb_physical_balls_locked == 2:
            self.delay.add(name='drain_bathtub', ms=1000, callback=self.slowrelease)
            self.log.info('LSB - 1 ball needed from trough')
            self.machine.playfield.add_ball(balls=1, player_controlled=False)
        if self.player.lsb_physical_balls_locked == 1:
            self.delay.add(name='drain_bathtub', ms=1000, callback=self.slowrelease)
            self.log.info('LSB - 2 balls needed from trough')
            self.machine.playfield.add_ball(balls=2, player_controlled=False)
        for x in range(0, 2):
            bip = self.machine.game.balls_in_play             
            if bip < 6:
                self.machine.game.balls_in_play = bip+1
        self.set_up_santa_shot()
        self.machine.events.post("mode_base_stop_music")                            
        self.machine.events.post('add_a_ball_start') 
        self.machine.events.post('enable_the_mb_ball_save')           
        self.machine.events.post('disable_combos')
        self.machine.events.post('char_remove_all')               
        self.turn_off_lock_light()
        self.machine.events.post("char_lsb_show_tub_full")           
        self.delay.add(name="char_lsb_slide_delay", ms=2000, callback=self.hide_slide1)
        self.machine.events.post("ob_pause_and_hide")
        self.machine.events.post("doors_pause_and_hide")

    def major_0(self, **kwargs):
        self.handle_shot(0)
    def major_1(self, **kwargs):
        self.handle_shot(1)
#    def major_2(self, **kwargs):
#        self.handle_shot(2)
    def major_3(self, **kwargs):
        self.handle_shot(3)
    def major_4(self, **kwargs):
        self.handle_shot(4)
    def major_5(self, **kwargs):
        self.handle_shot(5)
#    def major_6(self, **kwargs):
#        self.handle_shot(6)
    def major_7(self, **kwargs):
        self.handle_shot(7)
    def major_8(self, **kwargs):
        self.handle_shot(8)
    def major_9(self, **kwargs):
        self.handle_shot(9)


    def handle_shot(self, shot):
        if self.player.LSB_MB_running == 1:
            if self.santa_collected == 0:
                self.log.info("char_lsb MB - shot "+str(shot))
                state = self.player.char_lsb_shotlist[shot]["state"]
                self.log.info("char_lsb MB - shot "+str(shot) + " hit, state = "+state)        	                
                self.score = 0
                #not lit, skip it
                if state != "off":
                    #is this santa?
                    if state == 'santa':
                        self.log.info('char_LSB MB - got the santa')                	                	
                        self.score = self.player.char_lsb_santa_value  #250000
                        self.machine.events.post("say_sandy_claws")    
                        self.machine.events.post("show_santa_captured")   
                        self.santa_collected = 1
                        self.clear_shots()
                        self.player.char_lsb_shotlist[self.not_santa_shot1]["state"] = 'off'
                        self.player.char_lsb_shotlist[self.not_santa_shot2]["state"] = 'off'
                        self.player.char_lsb_shotlist[self.santa_shot]["state"] = 'off'                        
                        self.player.char_lsb_shotlist[6]["state"] = 'white'
                        self.set_shot_lights()
                    else:
                        # "notsanta"
                        self.log.info('char_LSB MB - not santa')                	                	
                        self.score = self.player.char_lsb_not_santa_value  #100000
                        self.machine.events.post("say_thats_not_santa") 
                        self.machine.events.post("show_not_santa")                    
                        self.clear_shots()
                        self.player.char_lsb_shotlist[shot]["state"] = 'off'
                        self.set_shot_lights()
                    self.score *= self.player.multiplier_shot_value_list[shot] # 1X, 2X or 3X 
                    self.player.score += self.score
                else:
                    self.log.info('char_lsb MB - shot, not lit')
    
                    
    def into_the_trees(self, **kwargs):
        if self.player.LSB_MB_running == 1:    
            if self.player.doors_currentdoor == 0:
                self.log.info('char_lsb MB - trees')     
                #if christmas
                if self.santa_collected == 0:            
                    self.log.info('char_lsb MB - trees, xmas, grab santa')                 
                    self.machine.events.post("say_we_got_him") 
                    self.machine.events.post("show_santa_captured")
                    self.score = self.player.char_lsb_santa_value
                    self.score *= self.player.multiplier_shot_value_list[6]
                    self.player.score += self.score
                    self.santa_collected = 1            
                    self.clear_shots()
                    self.player.char_lsb_shotlist[self.not_santa_shot1]["state"] = 'off'
                    self.player.char_lsb_shotlist[self.not_santa_shot2]["state"] = 'off'
                    self.player.char_lsb_shotlist[self.santa_shot]["state"] = 'off'                        
                    self.player.char_lsb_shotlist[6]["state"] = 'white'
                    self.set_shot_lights()
                else:
                    self.log.info('char_lsb MB - trees, xmas, already have santa')                             
                    #already have him, back for what?
            else:
                #not christmas
                self.log.info('char_lsb MB - trees, not xmas')                 
                if self.santa_collected == 0:                
                    self.machine.events.post("show_not_santa")
                    if self.player.doors_currentdoor == 3:  #easter
                        self.machine.events.post("say_bunny")                
                    else:
                        self.machine.events.post("say_who_is_it")
                    self.score = self.player.char_lsb_not_santa_value
                    self.score *= self.player.multiplier_shot_value_list[6]
                    self.player.score += self.score
                else:
                    self.log.info('char_lsb MB - trees, not xmas, already have santa')                             
                    #already have him, back for what?
            self.machine.events.post("LSB_advance_door")                

            
    def grave_stone(self, **kwargs):
        if self.player.LSB_MB_running == 1:        
            self.log.info('char_lsb MB - grave_stone')         
            if self.santa_collected == 1:            
                self.machine.events.post("say_its_oogies_boys")
            else:
                self.machine.events.post("say_what_are_you_doing")
            self.score = self.player.char_lsb_not_santa_value  #100000
            self.score *= self.player.multiplier_shot_value_list[6]
            self.player.score += self.score
            

    def jack_saucer(self, **kwargs):     
        if self.player.LSB_MB_running == 1:        
            self.log.info('char_lsb MB - jack_saucer')             
            if self.santa_collected == 1:
                if self.super_jackpot_enabled == 1:
                    self.log.info('char_lsb MB - jack_saucer, SUPER santa')
                    self.machine.events.post("say_you_dont_have_claws")
                    self.machine.events.post("show_santa_at_jacks_super")
                    self.score = self.player.char_super_jackpot_value
                    self.score *= self.player.multiplier_shot_value_list[6]
                    self.player.score += self.score
                else:
                    self.log.info('char_lsb MB - jack_saucer, santa')                  
                    self.machine.events.post("say_what_a_pleasure")
                    self.machine.events.post("show_santa_at_jacks")
                    self.score = self.player.char_jackpot_value
                    self.score *= self.player.multiplier_shot_value_list[6]
                    self.player.score += self.score
                #reset the santa shots
                self.player.LSB_MB_completed += 1
                self.clear_shots()
                self.set_up_santa_shot()
            else:
                self.log.info('char_lsb MB - jack_saucer, no santa')                         
                self.machine.events.post("say_bring_me_santclause")
                self.machine.events.post("show_angry_jack")
            
        
    def set_up_santa_shot(self, **kwargs):   
        self.log.info('char_lsb MB - set up santa shot')
        self.santa_collected = 0
        self.super_jackpot_enabled = 0
        # pick 3 random shots, 1 santa, 2 impostors
        for x in range(0, 10):
            self.player.char_lsb_shotlist[x]["state"] = "off"
        self.santa_shot = random.randint(0,7)            
        self.not_santa_shot1 = random.randint(0,7)
        while (self.not_santa_shot1 == self.santa_shot):
            self.not_santa_shot1 = random.randint(0,7)
        self.not_santa_shot2 = random.randint(0,7)
        while (self.not_santa_shot2 == self.santa_shot or self.not_santa_shot2 == self.not_santa_shot1):
            self.not_santa_shot2 = random.randint(0,7)
        self.santa_shot = self.index_list[self.santa_shot]
        self.not_santa_shot1 = self.index_list[self.not_santa_shot1]
        self.not_santa_shot2 = self.index_list[self.not_santa_shot2]
        self.player.char_lsb_shotlist[self.santa_shot]["state"] = "santa"
        self.player.char_lsb_shotlist[self.not_santa_shot1]["state"] = "notsanta"
        self.player.char_lsb_shotlist[self.not_santa_shot2]["state"] = "notsanta"        
        self.set_shot_lights()
        
   
    def set_shot_lights(self):
        for x in range(0, 10):
            state = self.player.char_lsb_shotlist [x]["state"]
            if state != 'off':
                led = self.player.char_lsb_shotlist [x]["led"]
                col = state
                if state == 'santa':
                    col = "ffff00"
                if state == 'notsanta':
                    col = "cfcf00"
                self.machine.events.post('arrow_change', led_num=x, script_name=col, mode_name="LSB_MB", action="add")

                
    def clear_shots(self):
        for x in range(0, 10):
            state = self.player.char_lsb_shotlist [x]["state"]
            if state != 'off':
                col = state
                if state == 'santa':
                    col = "ffff00"
                if state == 'notsanta':
                    col = "cfcf00"
                led = self.player.char_lsb_shotlist [x]["led"]
                self.machine.events.post('arrow_change', led_num=x, script_name=col, mode_name="LSB_MB", action="remove")                        

                
    def hide_slide1(self, **kwargs):   
        self.delay.add(name="char_lsb_slide_delay", ms=5000, callback=self.hide_slide)           
        self.machine.events.post("char_lsb_hide_tub")   
        self.machine.events.post('tub_mb_music_start')

        
    def hide_slide(self, **kwargs):   
        if (self.player.Doors_state != 0 or self.player.OB_Gate_current_mode_state != 0):
            self.machine.events.post("char_lsb_hide_slide")   
        self.machine.events.post("ob_resume_and_show") 
        self.machine.events.post("doors_resume_and_show")         


    def resume_and_show(self, **kwargs):   
        if (self.player.Doors_state == 0 and self.player.OB_Gate_current_mode_state == 0):
            if self.player.LSB_MB_running == 1:
                self.machine.events.post("char_lsb_show_slide")            


    def slowrelease(self):
        self.log.info('LSB - slow release')
        if self.player.lsb_physical_balls_locked > 0:
            self.drain_tub()
            self.delay.add(name='drain_bathtub', ms=2000, callback=self.slowrelease)
        else: 
            self.log.info('LSB - tub is empty')        	


    def drain_tub(self):
        self.log.info('LSB - drain a ball from tub')
        self.machine.coils['bathtubdrain'].pulse(milliseconds=40)
        self.count_balls_in_bathtub()


    def mode_stop(self, **kwargs):
        self.log.info( 'LSB - mode_stop')
        self.delay.remove('close_bathtub_diverter')
        self.close_bathtub_diverter()
        self.clear_shots()
        self.turn_off_lock_light()
