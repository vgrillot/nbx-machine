from mpf.core.mode import Mode
from mpf.core.delays import DelayManager



# char_Qualify
# keep track of which char is qualified and start the modes when appropriate
#
# For Character Modes, each needs to first be qualified, then started. 
# Each character mode has its own qualifying and starting methods. 
# When a character mode is qualified, any shot which will start the mode will flash orange. 
# Only one character's modes can be qualified at a time, thus if you qualify one character's 
# mode then qualify another's, the one you qualified first will be disqualified and will 
# have to be requalified before you can start it. The exception to this is Lock, Shock and 
# Barrel as they have a special bank of targets and bathtub for locking balls, so they don't 
# override the other characters. (However, you can only have one Character Mode running at 
# a time, so if you start say, "What's This?" Frenzy, the LSB multiball cannot be started 
# until the frenzy ends. You CAN however combine "What's This?" Frenzy with a 
# multiball from the Hinterlands or Oogie Boogie.)
#
#   Character Mode               Qualifying Method                                 Starting Method
# "Where's Jack?"             Spell JACK (Some Character Modes not Complete)    Graveyard, Soup or Mayor
# "The Scientific Method"     Spell JACK (All other Character Modes Complete)   Graveyard, Soup or Mayor
# "Sally's Stitches"          Get 100 spins on the spinner                      Graveyard, Soup or Mayor
# "A Marked Improvement"      Shoot Doctor Finklestein                          Graveyard, Soup or Mayor
# "I Can't Make Decisions!"   Shoot the Mayor                                   Mayor (Yes, you shoot once to qualify, again to start)
# "Go Fetch!"                 Zero or hinterlands spot                          Zero Kickback
#
# Special modes:  repeatable before the wizard mode
# "Kidnap the Sandi-Claws"    Lock, Shock and Barrel Targets                    Bathtub Lock
# "What's This?" Frenzy       Spell JACK                                        Hinterlands (Overrides starting a Door Mode)
#
# 5 Characters on the display  M, Z, J, S, D
# Each character shows up as a small head above the scores. 
# Jack gets two different heads - one for Where/Science and one for What's This
# Once a mode is complete it cannot be qualified again until you've completed all the other 
# Character modes and play the "Deliver the Presents" Wizard Mode.
#
# "Kidnap the Sandi-Claws" is an exception to this as it simply gets more difficult 
# to qualify and lock balls with each completion and is meant to be a multiball you can
# reliably go for without understanding the rest of the rules. The first time, you only 
# have to complete the LSB standup targets once to enable all three bathtub locks.
# The second time and onwards you have to complete the LSB standups three times, once 
# for each ball you wish to lock.
#
# Jack-What will be repeatable as well (after Where's Jack has been completed, but not all characters completed)

class Char_Qualify(Mode):

    def mode_init(self):
        self.log.info('char_Qualify mode_init')

    def mode_start(self, **kwargs):
        self.vuk_fired = 0
        self.log.info('char_Qualify mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.char_Qualify_mode_started == 0:
            self.player.modes_played = 0
            self.player.graves = 0
            #once per game only
            self.player.char_Qualify_mode_started = 1
            # char state 
            # 0 = nothing, 
            # 1 = char qualified, 
            # 2 = char running, 
            # 3 = all completed (wizard ready)
            # 4 - wizard running
            # 5 - wizard completed
            self.player.char_What_state = 0
            self.player.char_Where_state = 0
            self.player.char_Science_state = 0
            self.player.char_Sally_state = 0
            self.player.char_Doctor_state = 0
            self.player.char_Mayor_state = 0
            self.player.char_Zero_state = 0
            self.player.char_LSB_state = 0
            self.player.char_Wizard_state = 0
            self.player_mayor_spin = 1
            self.player.char_Wizard_played = 0
            self.player.char_tub_state = 0
        self.player.char_state = 0              
        self.player.char_timer_ispaused = 0            
        self.player.char_qualified = "none"  #char mode currently qualified
        self.player.char_played = "none"  #char mode just played
        self.balls_in_subway = 0
        self.add_mode_event_handler("jack_spelled", self.jack_qualified)
        self.add_mode_event_handler("sally_spin_qualify", self.sally_qualified)
        self.add_mode_event_handler("sw_doctor", self.doctor_qualified)
        self.add_mode_event_handler("major_0_singlestep_unlit_hit", self.mayor)
        #self.add_mode_event_handler("major_6_singlestep_unlit_hit", self.zero_qualified)
        self.add_mode_event_handler("LSB_bathtub_ready", self.LSB_qualified)
        self.add_mode_event_handler("major_2_singlestep_unlit_hit", self.hinterlands)
        self.add_mode_event_handler("sw_saucer", self.saucer)
        self.add_mode_event_handler("mystery_done_with_ball", self.saucer)        
        self.add_mode_event_handler("taste_the_soup_singlestep_unlit_hit", self.soup)
        self.add_mode_event_handler("sw_zero", self.zero)
        self.add_mode_event_handler("tub_ball_locked", self.LSB)
        self.add_mode_event_handler("sw_subwayoogie", self.subway_add_ball)
        self.add_mode_event_handler("sw_subwaytrees", self.subway_add_ball)  
        self.add_mode_event_handler("char_mode_stopped", self.char_mode_stopped) 
        self.add_mode_event_handler("char_show_chars", self.setup_display) 
        self.add_mode_event_handler("char_is_qualified", self.set_lights)  
        self.add_mode_event_handler("balldevice_soupvuk_ball_eject_attempt", self.soup_ejected)  
        self.add_mode_event_handler("char_pause_and_hide", self.pause_and_hide)  
        self.add_mode_event_handler("char_resume_and_show", self.resume_and_show)  
        self.player.char_Qualify_show_handles = [0] * 7
        self.player.char_led_list = [
             {"char":"jack", "led":"rgb_jack_circle", "state":"off"}
            ,{"char":"sally", "led":"rgb_sally_circle", "state":"off"}
            ,{"char":"doctor", "led":"rgb_doctor_circle", "state":"off"}
            ,{"char":"mayor", "led":"rgb_mayor_c_circle", "state":"off"}
            ,{"char":"zero", "led":"rgb_zero_circle", "state":"off"}
            ,{"char":"lsb", "led":"rgb_bathtub_rect", "state":"off"}
            ,{"char":"wizard", "led":"rgb_charwiz_rect", "state":"off"}
            ]
        self.reset_states()
        self.machine.events.post("char_LSB_start")    #always running
        self.check_wiz()
        self.setup_display()    

        
    def pause_and_hide(self, **kwargs):        
        self.machine.events.post("char_remove_all")   
        self.machine.events.post("char_hide_timer")            
        self.player.char_timer_ispaused = 1

        
    def resume_and_show(self, **kwargs):        
        self.setup_display()    
        self.player.char_timer_ispaused = 0

        
    def reset_lights(self):
        for x in range(0, 7):
            led = self.player.char_led_list[x]["led"]
            self.machine.shows["sc_off"].play(show_tokens=dict(leds=led), speed=8.0, loops=1)
            if self.player.char_Qualify_show_handles[x] != 0:
                self.player.char_Qualify_show_handles[x].stop()
                self.player.char_Qualify_show_handles[x] = 0


    def set_lights(self, value, **kwargs):
        for x in range(0, 7):
            if self.player.char_Qualify_show_handles[x] != 0:
                self.player.char_Qualify_show_handles[x].stop()
                self.player.char_Qualify_show_handles[x] = 0
            self.player.char_led_list[x]["state"] = "off"

        if value == "Jack":
                self.player.char_led_list[0]["state"] = "Science"

        #one of these Jack modes qualified or complete?
        if self.player.char_Where_state > 1:
            self.player.char_led_list[0]["state"] = "Where_solid"
        else:
            if value == "Where":            
                self.player.char_led_list[0]["state"] = "Where"            

        if self.player.char_Science_state > 1:
            self.player.char_led_list[0]["state"] = "Science_solid"
        else:
            if value == "Science":
                self.player.char_led_list[0]["state"] = "Science" 

        if self.player.char_Sally_state > 1:
            self.player.char_led_list[1]["state"] = "Sally_solid"
        else:
            if value == "Sally":
                self.player.char_led_list[1]["state"] = "Sally"
    
        if self.player.char_Doctor_state > 1:
            self.player.char_led_list[2]["state"] = "Doctor_solid"
        else:
            if value == "Doctor":        
                self.player.char_led_list[2]["state"] = "Doctor"            

        if self.player.char_Mayor_state > 1:
            self.player.char_led_list[3]["state"] = "Mayor_solid"
        else:
            if value == "Mayor":
                self.player.char_led_list[3]["state"] = "Mayor"
    
        #if zero complete, show that
        if self.player.char_Zero_state > 1:
            self.player.char_led_list[4]["state"] = "Zero_solid"
            #if WHAT complete show both
            if self.player.char_What_state > 1:
                self.player.char_led_list[4]["state"] = "Zero_Solid_What_solid"
            else:
                # if JACK qualified and WHAT hasnt been completed
                if value == "Jack":  
                    if self.player.char_What_state < 2:
                        self.player.char_led_list[4]["state"] = "Zero_Solid_What_Flash"            
        elif self.player.char_What_state > 1:
            self.player.char_led_list[4]["state"] = "What_solid"
            #if Zero is qualified
            if value == "Zero":
                if self.player.char_Zero_state < 2:            
                    self.player.char_led_list[4]["state"] = "What_Solid_Zero_Flash"
        else:
            #nothing complete
            #show if either What or Zero is qualified            
            if value == "Zero":
                if self.player.char_Zero_state < 2:            
                    self.player.char_led_list[4]["state"] = "Zero"
            elif value == "Jack":  
                # if JACK qualified and WHAT hasnt been completed
                if self.player.char_What_state < 2:
                    self.player.char_led_list[4]["state"] = "What"            

        if self.player.char_LSB_state > 1:
            self.player.char_led_list[5]["state"] = "LSB_solid"
        else:
            if value == "LSB":
                self.player.char_led_list[5]["state"] = "LSB"
    
        if self.player.char_Wizard_played > 0:
            #we played the wizard mode - keep it solid
            #todo, another toggle needed once ultimate has been played
            self.player.char_led_list[6]["state"] = "Wizard_solid"
            
        if value == "Wizard":
            self.player.char_led_list[6]["state"] = "Wizard"
                
        for x in range(0, 7):
            state = self.player.char_led_list[x]["state"]
            led = self.player.char_led_list[x]["led"]
            script_name = "sc_char_"+state
            self.player.char_Qualify_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)			
        
        
    def reset_states(self, force=False):
        #reset any char that were in the middle of running
        if self.player.char_What_state == 1:
            self.player.char_What_state = 0            
        if self.player.char_Where_state == 1:
            self.player.char_Where_state = 0
        if self.player.char_Science_state == 1:
            self.player.char_Science_state = 0            
        if self.player.char_Sally_state == 1:
            self.player.char_Sally_state = 0
        if self.player.char_Doctor_state == 1:
            self.player.char_Doctor_state = 0
        if self.player.char_Mayor_state == 1:
            self.player.char_Mayor_state = 0
        if self.player.char_Zero_state == 1:
            self.player.char_Zero_state = 0
        if self.player.char_LSB_state == 1:
            self.player.char_LSB_state = 0
            self.player.char_tub_state = 0
        if self.player.char_Wizard_state == 1:
            self.player.char_Wizard_state = 0
        if force:
            #reset all back to 0
            self.player.char_What_state = 0            
            self.player.char_Where_state = 0
            self.player.char_Science_state = 0            
            self.player.char_Sally_state = 0
            self.player.char_Doctor_state = 0
            self.player.char_Mayor_state = 0
            self.player.char_Zero_state = 0
            self.player.char_LSB_state = 0
            self.player.char_Wizard_state = 0
            self.player.char_tub_state = 0
            

    def show_status(self):
        self.log.info('char_Qualify - status')                  
        self.log.info('char_Qualify - Char state: '+str(self.player.char_state)) 
        self.log.info('char_Qualify - Char Qualified: '+str(self.player.char_qualified)) 
        self.log.info('char_Qualify - What state: '+str(self.player.char_What_state))        
        self.log.info('char_Qualify - Where state: '+str(self.player.char_Where_state))        
        self.log.info('char_Qualify - Sally state: '+str(self.player.char_Sally_state))        
        self.log.info('char_Qualify - Science state: '+str(self.player.char_Science_state))        
        self.log.info('char_Qualify - LSB state: '+str(self.player.char_LSB_state))        
        self.log.info('char_Qualify - Zero state: '+str(self.player.char_Zero_state))        
        self.log.info('char_Qualify - Mayor state: '+str(self.player.char_Mayor_state))        
        self.log.info('char_Qualify - Doctor state: '+str(self.player.char_Doctor_state))        
        self.log.info('char_Qualify - Wizard state: '+str(self.player.char_Wizard_state))   
        self.log.info("BIP="+str(self.machine.game.balls_in_play))
        self.log.info("BOP="+str(self.machine.playfield._balls))   
        #self.log.info(self.player.vars.keys())
        

    def char_mode_stopped(self, char_mode=None, char_state=None, **kwargs):
        self.log.info('char_Qualify - a mode stopped - complete? '+str(char_state))
        self.player.char_state = 0
        self.player.char_played = char_mode
        self.player.modes_played += 1
        #state can be "complete" or "incomplete"
        if char_state == "complete":
            state = 2 #completed
            self.machine.events.post("char_is_completed", value=char_mode)
        else:
            state = 0 #back to ready
            self.machine.events.post("char_is_ended", value=char_mode)            
        if char_mode == "What":
            self.player.char_What_state = state
            self.machine.events.post("char_what_stop")            
        if char_mode == "Where":
            self.player.char_Where_state = state
            self.machine.events.post("char_where_stop")
        if char_mode == "Science":
            self.player.char_Science_state = state
            self.machine.events.post("char_science_stop")            
        if char_mode == "Sally":
            self.player.char_Sally_state = state
            self.machine.events.post("char_sally_stop")
        if char_mode == "Doctor":
            self.player.char_Doctor_state = state
            self.machine.events.post("char_doctor_stop")            
        if char_mode == "Mayor":
            self.player.char_Mayor_state = state
            self.machine.events.post("char_mayor_stop")            
        if char_mode == "Zero":
            self.player.char_Zero_state = state
            self.machine.events.post("char_zero_stop")            
        if char_mode == "LSB":
            self.player.char_LSB_state = state
            self.player.char_tub_state = 3
            if state == 2:
                self.player.char_tub_state = 9
            self.machine.events.post("char_LSB_soft_stop")            
        if char_mode == "Wizard":
            self.player.char_Wizard_state = 2  #always completes
            self.player.char_state = 5
            self.machine.events.post("char_wizard_stop")  
            self.player.char_Wizard_played += 1
            self.delay.add(name="delayed_chars_reset", ms=5000, callback=self.reset_callback)
        self.setup_display()
        self.check_wiz()
        self.set_lights(value=None)        


    def reset_callback(self, **kwargs ):
        self.log.info('char_Qualify - resetting')
        self.player.char_state = 0
        self.reset_states(True)        
        self.setup_display()
        self.set_lights(value=None)        

        
    def check_wiz(self):
        allcomplete = 0
        if self.player.char_Where_state == 2 or self.player.char_Science_state == 2:
            if self.player.char_Sally_state == 2:
                if self.player.char_Doctor_state == 2:
                    if self.player.char_Mayor_state == 2:
                        if self.player.char_Zero_state == 2:
                            if self.player.char_LSB_state == 2:
                                allcomplete = 1
        if allcomplete == 1:
            self.log.info('char_Qualify - All modes complete')
            if self.player.char_state < 3:  #wizard mode not already ready
                if self.player.char_Wizard_state < 2: 
                    self.player.char_state = 3
                    self.Wizard_qualified()
            else:
                #all modes and wizard complete - now what? TODO - make Char Wiz LED solid
                self.log.info('char_Qualify - All modes and Wizard complete - wait for reset')


        
        
    def setup_display(self, **kwargs):
        self.log.info('char_Qualify - setup display')
        #add/remove characters to the display 
        if self.player.char_state == 0:        
            self.log.info('char_Qualify - setup display - nothing running, show C, B, Qs')
            #nothing should be running
            self.machine.events.post("stop_all_character_messages")  # and timer
            #remove any running icons
            self.machine.events.post("char_jack_r_remove")
            self.machine.events.post("char_jack2_r_remove")        
            self.machine.events.post("char_sally_r_remove")        
            self.machine.events.post("char_doctor_r_remove")
            self.machine.events.post("char_mayor_r_remove")
            self.machine.events.post("char_zero_r_remove")        
            self.machine.events.post("char_lsb_r_remove")                    
            
            if self.player.char_qualified == "Jack":
                if self.player.char_Where_state == 2 or self.player.char_Science_state == 2:
                    self.machine.events.post("char_jack2_q_add")
                    self.machine.events.post("char_jack_c_remove")
                    self.machine.events.post("char_jack_b_remove")
                else:
                    self.machine.events.post("char_jack_q_add")
                    self.machine.events.post("char_jack_c_remove")
                    self.machine.events.post("char_jack_b_remove")
            elif self.player.char_Where_state == 2 or self.player.char_Science_state == 2:
                self.machine.events.post("char_jack_c_add")
                self.machine.events.post("char_jack_q_remove")
                self.machine.events.post("char_jack_b_remove")                
            else:
                self.machine.events.post("char_jack_q_remove")
                self.machine.events.post("char_jack_c_remove")
                self.machine.events.post("char_jack_b_add")
            
            if self.player.char_Sally_state == 2:
                self.machine.events.post("char_sally_c_add")
                self.machine.events.post("char_sally_b_remove")
                self.machine.events.post("char_sally_q_remove")
            elif self.player.char_qualified == "Sally":
                self.machine.events.post("char_sally_c_remove")
                self.machine.events.post("char_sally_b_remove")
                self.machine.events.post("char_sally_q_add")                
            else:
                self.machine.events.post("char_sally_c_remove")
                self.machine.events.post("char_sally_b_add")
                self.machine.events.post("char_sally_q_remove")
                
            if self.player.char_Doctor_state == 2:
                self.machine.events.post("char_doctor_c_add")
                self.machine.events.post("char_doctor_b_remove")
                self.machine.events.post("char_doctor_q_remove")
            elif self.player.char_qualified == "Doctor":
                self.machine.events.post("char_doctor_c_remove")
                self.machine.events.post("char_doctor_b_remove")
                self.machine.events.post("char_doctor_q_add")
            else:
                self.machine.events.post("char_doctor_q_remove")
                self.machine.events.post("char_doctor_c_remove")
                self.machine.events.post("char_doctor_b_add")
                
            if self.player.char_Mayor_state == 2:
                self.machine.events.post("char_mayor_c_add")
                self.machine.events.post("char_mayor_b_remove")
                self.machine.events.post("char_mayor_q_remove")            
            elif self.player.char_qualified == "Mayor":
                self.machine.events.post("char_mayor_c_remove")
                self.machine.events.post("char_mayor_b_remove")            
                self.machine.events.post("char_mayor_q_add")
            else:
                self.machine.events.post("char_mayor_c_remove")
                self.machine.events.post("char_mayor_b_add")            
                self.machine.events.post("char_mayor_b_remmove")
                
            if self.player.char_Zero_state == 2:
                self.machine.events.post("char_zero_c_add")
                self.machine.events.post("char_zero_b_remove")
                self.machine.events.post("char_zero_q_remove")
            elif self.player.char_qualified == "Zero":
                self.machine.events.post("char_zero_c_remove")
                self.machine.events.post("char_zero_b_remove")
                self.machine.events.post("char_zero_q_add")                
            else:
                self.machine.events.post("char_zero_c_remove")
                self.machine.events.post("char_zero_b_add")
                self.machine.events.post("char_zero_q_remove")

            self.update_lsb_display()

        else:
            self.log.info('char_Qualify - setup display - char mode is running, show R')
            #some char mode is running - show it.
            if (self.player.char_Science_state == 1 or self.player.char_Where_state == 1):             
                self.machine.events.post("char_jack_r_add")
            if self.player.char_What_state == 1:                 
                self.machine.events.post("char_jack2_r_add")
                self.machine.events.post("char_show_timer")
            if self.player.char_Sally_state == 1:                 
                self.machine.events.post("char_sally_r_add")
                self.machine.events.post("char_show_timer")
            if self.player.char_Doctor_state == 1:                 
                self.machine.events.post("char_doctor_r_add")
                self.machine.events.post("char_show_timer")
            if self.player.char_Mayor_state == 1:                 
                self.machine.events.post("char_mayor_r_add")
                self.machine.events.post("char_show_timer")
            if self.player.char_Zero_state == 1: 
                self.machine.events.post("char_zero_r_add")
                self.machine.events.post("char_show_timer")
            if self.player.char_LSB_state == 1: 
                self.machine.events.post("char_lsb_r_add")
                #self.machine.events.post("char_show_timer")

                
    def update_lsb_display(self):
        #b-tub dim
        #b-tub dim + L
        #b-tub dim + LS
        #b-tub dim + LSB            
        #q-tub bright + green
        #q-tub bright + L + green                         
        #q-tub bright + LS + green
        #q-tub bright + LSB + green            
        #r-tub bright + LSB + blue
        #c-tub bright + LSB + yellow
        
        if self.player.char_tub_state == 0:
            #empty tub
            self.machine.events.post("char_lsb_c_remove")
            self.machine.events.post("char_lsb_b_add")            
            self.machine.events.post("char_lsb_q_remove")
            self.machine.events.post("char_lock_q_remove")
            self.machine.events.post("char_shock_q_remove")
            self.machine.events.post("char_barrel_q_remove")
            self.machine.events.post("char_lock_b_remove")
            self.machine.events.post("char_shock_b_remove")
            self.machine.events.post("char_barrel_b_remove")
        elif self.player.char_tub_state == 1:            
            #tub + L
            self.machine.events.post("char_lsb_c_remove")
            self.machine.events.post("char_lsb_b_add")            
            self.machine.events.post("char_lsb_q_remove")
            self.machine.events.post("char_lock_q_remove")
            self.machine.events.post("char_shock_q_remove")
            self.machine.events.post("char_barrel_q_remove")
            self.machine.events.post("char_lock_b_add")
            self.machine.events.post("char_shock_b_remove")
            self.machine.events.post("char_barrel_b_remove")
        elif self.player.char_tub_state == 2:            
            #tub + LS
            self.machine.events.post("char_lsb_c_remove")
            self.machine.events.post("char_lsb_b_add")            
            self.machine.events.post("char_lsb_q_remove")
            self.machine.events.post("char_lock_q_remove")
            self.machine.events.post("char_shock_q_remove")
            self.machine.events.post("char_barrel_q_remove")
            self.machine.events.post("char_lock_b_add")
            self.machine.events.post("char_shock_b_add")
            self.machine.events.post("char_barrel_b_remove")
        elif self.player.char_tub_state == 3:            
            #tub + LSB
            self.machine.events.post("char_lsb_c_remove")
            self.machine.events.post("char_lsb_b_add")            
            self.machine.events.post("char_lsb_q_remove")
            self.machine.events.post("char_lock_q_remove")
            self.machine.events.post("char_shock_q_remove")
            self.machine.events.post("char_barrel_q_remove")
            self.machine.events.post("char_lock_b_add")
            self.machine.events.post("char_shock_b_add")
            self.machine.events.post("char_barrel_b_add")
        elif self.player.char_tub_state == 4:
            #qualified, tub 
            self.machine.events.post("char_lsb_c_remove")
            self.machine.events.post("char_lsb_b_remove")            
            self.machine.events.post("char_lsb_q_add")
            self.machine.events.post("char_lock_q_remove")
            self.machine.events.post("char_shock_q_remove")
            self.machine.events.post("char_barrel_q_remove")
            self.machine.events.post("char_lock_b_remove")
            self.machine.events.post("char_shock_b_remove")
            self.machine.events.post("char_barrel_b_remove")
        elif self.player.char_tub_state == 5:
            #qualified, tub + L
            self.machine.events.post("char_lsb_c_remove")
            self.machine.events.post("char_lsb_b_remove")            
            self.machine.events.post("char_lsb_q_add")
            self.machine.events.post("char_lock_q_add")
            self.machine.events.post("char_shock_q_remove")
            self.machine.events.post("char_barrel_q_remove")
            self.machine.events.post("char_lock_b_remove")
            self.machine.events.post("char_shock_b_remove")
            self.machine.events.post("char_barrel_b_remove")                
        elif self.player.char_tub_state == 6:
            #qualified, tub + LS
            self.machine.events.post("char_lsb_c_remove")
            self.machine.events.post("char_lsb_b_remove")            
            self.machine.events.post("char_lsb_q_add")
            self.machine.events.post("char_lock_q_add")
            self.machine.events.post("char_shock_q_add")
            self.machine.events.post("char_barrel_q_remove")
            self.machine.events.post("char_lock_b_remove")
            self.machine.events.post("char_shock_b_remove")
            self.machine.events.post("char_barrel_b_remove")
        elif self.player.char_tub_state == 7:
            #qualified, tub + LSB
            self.machine.events.post("char_lsb_c_remove")
            self.machine.events.post("char_lsb_b_remove")            
            self.machine.events.post("char_lsb_q_add")
            self.machine.events.post("char_lock_q_add")
            self.machine.events.post("char_shock_q_add")
            self.machine.events.post("char_barrel_q_add")
            self.machine.events.post("char_lock_b_remove")
            self.machine.events.post("char_shock_b_remove")
            self.machine.events.post("char_barrel_b_remove")
        elif self.player.char_tub_state == 8:
            #running, tub + LSB
            self.machine.events.post("char_lsb_r_add")            
            self.machine.events.post("char_lsb_c_remove")
            self.machine.events.post("char_lsb_b_remove")            
            self.machine.events.post("char_lsb_q_remove")
            self.machine.events.post("char_lock_q_remove")
            self.machine.events.post("char_shock_q_remove")
            self.machine.events.post("char_barrel_q_remove")
            self.machine.events.post("char_lock_b_remove")
            self.machine.events.post("char_shock_b_remove")
            self.machine.events.post("char_barrel_b_remove")
        elif self.player.char_tub_state == 9:
            #completed
            self.machine.events.post("char_lsb_c_add")
            self.machine.events.post("char_lsb_b_remove")
            self.machine.events.post("char_lsb_q_remove")            
            self.machine.events.post("char_lock_q_add")
            self.machine.events.post("char_shock_q_add")
            self.machine.events.post("char_barrel_q_add")
            self.machine.events.post("char_lock_b_remove")
            self.machine.events.post("char_shock_b_remove")
            self.machine.events.post("char_barrel_b_remove")
                
    
    def subway_add_ball(self, **kwargs):
        self.log.info('char_Qualify - ball in subway from Oogie or tree')
        self.balls_in_subway += 1

    def jack_qualified(self, **kwargs):
        if self.player.char_state < 2:
            if (self.player.char_What_state == 0 or
              ( self.player.char_Where_state == 0 and self.player.char_Science_state == 0) ):
                self.machine.events.post("set_gi_col_pulse", red=150, green=20, blue=150)        
                if self.player.char_qualified != "Jack":                        
                    self.log.info('char_Qualify Jack Qualified')
                    self.machine.events.post("char_"+self.player.char_qualified+"_q_remove")
                    self.machine.events.post("char_"+self.player.char_qualified+"_b_add")                
                    self.player.char_qualified = "Jack"
                    self.qualify_change()
                    #leads to one of these: "What", "Where" or "Science"
                    self.machine.events.post("char_jack_qualified")
                    self.machine.events.post("char_"+self.player.char_qualified+"_b_remove")
                    self.machine.events.post("char_"+self.player.char_qualified+"_q_add")                

    def sally_qualified(self, **kwargs):
        if self.player.char_state < 2:
            if self.player.char_Sally_state == 0:        
                self.machine.events.post("set_gi_col_pulse", red=150, green=40, blue=40)
                self.log.info('char_Qualify Sally Qualified')
                self.machine.events.post("char_"+self.player.char_qualified+"_q_remove")
                self.machine.events.post("char_"+self.player.char_qualified+"_b_add")            
                self.player.char_qualified = "Sally"
                self.machine.events.post("char_sally_qualified")
                self.machine.events.post("char_"+self.player.char_qualified+"_b_remove")
                self.machine.events.post("char_"+self.player.char_qualified+"_q_add")
                self.qualify_change()            

    def doctor_qualified(self, **kwargs):
        if self.player.char_state < 2:
            if self.player.char_Doctor_state == 0:
                self.machine.events.post("set_gi_col_pulse", red=30, green=30, blue=180)
                if self.player.char_qualified != "Doctor":
                    self.log.info('char_Qualify Doctor Qualified')
                    self.machine.events.post("char_"+self.player.char_qualified+"_q_remove")
                    self.machine.events.post("char_"+self.player.char_qualified+"_b_add")                    
                    self.player.char_qualified = "Doctor"
                    self.machine.events.post("char_doctor_qualified")
                    self.machine.events.post("char_"+self.player.char_qualified+"_b_remove")
                    self.machine.events.post("char_"+self.player.char_qualified+"_q_add")
                    self.qualify_change()

                    

    #qualified by Zero (when unlit) or by Hinterland ramp (unlit)
    def zero_qualified(self, **kwargs):
        if self.player.char_state < 2:
            if self.player.char_Zero_state == 0:
                self.machine.events.post("set_gi_col_pulse", red=180, green=100, blue=10)
                if self.player.char_qualified != "Zero":
                    self.log.info('char_Qualify Zero Qualified')
                    self.machine.events.post("char_"+self.player.char_qualified+"_q_remove")
                    self.machine.events.post("char_"+self.player.char_qualified+"_b_add")
                    self.player.char_qualified = "Zero"
                    self.machine.events.post("char_zero_qualified")
                    self.machine.events.post("char_"+self.player.char_qualified+"_b_remove")
                    self.machine.events.post("char_"+self.player.char_qualified+"_q_add")
                    self.qualify_change()
            else:
                self.machine.events.post("zero_not_now")            

                
    def qualify_change(self):
        self.log.info('char_Qualified changed')
        self.machine.events.post("char_is_qualified", value=self.player.char_qualified)            
        if self.player.char_qualified == "Zero" or self.player.char_qualified == "Jack":
            self.enable_zero_diverter()
        else:
            self.disable_zero_diverter()
       
    def enable_zero_diverter(self):
        self.machine.events.post('zero_enable_diverter')
        self.machine.events.post('mayor_disable_diverter')

    def disable_zero_diverter(self):
        self.machine.events.post('zero_disable_diverter')
        self.machine.events.post('mayor_enable_diverter')
                    

    def LSB(self, **kwargs):
        self.log.info('LSB - tub ball count change!' + str(self.player.lsb_balls_locked))        
        if 'lock' in kwargs:
            lock_number = kwargs['lock']
        if lock_number == 1:
            self.player.char_tub_state = 5
        if lock_number == 2:
            self.player.char_tub_state = 6
        if lock_number == 3:        
            self.player.char_tub_state = 7        
            if self.player.char_state < 2:
                if self.player.char_LSB_state < 2: #not already running
                    self.player.char_LSB_state = 1
                    self.player.char_state = 2
                    self.machine.events.post("char_LSB_start_mb")
                    self.player.char_tub_state = 8
            else:
                self.log.info('3rd ball locked in tub, but already running another char mode!')
        #self.update_lsb_display()

            
    def LSB_qualified(self, **kwargs):
        self.player.char_tub_state = 4
        #self.update_lsb_display()
        if self.player.char_state < 2:
            self.log.info('char_Qualify LSB Qualified')
            self.machine.events.post("set_gi_col_pulse", red=180, green=180, blue=10)
            
            
    def Wizard_qualified(self, **kwargs):
        if self.player.char_state == 3:
            self.log.info('char_Qualify Wizard Qualified')
            self.player.char_qualified = "Wizard"
            self.qualify_change()


    def mayor(self, **kwargs):
        self.log.info('char_Qualify - Mayor hit')    
        if self.balls_in_subway == 0:
            if self.player_mayor_spin == 1:
                self.machine.events.post("mayor_spin_1")
                self.player_mayor_spin = 2
#               todo - servo - show happy face
            else:
                self.machine.events.post("mayor_spin_2")
                self.player_mayor_spin = 1
#               todo - servo - show scared face
            if self.player.char_state < 2:
                # if nothing is running, try mayor, or the others
                if self.player.char_qualified == "Mayor":
                    self.log.info('char_Qualify - start mayor mode?')                    
                    self.mayor_try_start()
                else:
                    #see if any of Jack, Sally, or Doctor are qualified, then start them
                    self.try_start()
                #if no char mode was started
                if self.player.char_state < 2:
                    # qualify the mayor, if not already run
                    if self.player.char_Mayor_state == 0:
                        self.log.info('char_Qualify - Mayor Qualified')
                        self.machine.events.post("char_"+self.player.char_qualified+"_q_remove")
                        self.machine.events.post("char_"+self.player.char_qualified+"_b_add")
                        self.player.char_qualified = "Mayor"
                        self.machine.events.post("char_mayor_qualified")
                        self.machine.events.post("char_"+self.player.char_qualified+"_b_remove")
                        self.machine.events.post("char_"+self.player.char_qualified+"_q_add")
                        self.qualify_change()                  
        else:
            #ball came from oogie or trees, decrement subway count, eject it
            self.balls_in_subway -= 1
            self.log.info('char_Qualify - ball in mayor, came from oogie BIS '+str(self.balls_in_subway))


    def mayor_try_start(self):
        #Mayor is qualified
        if self.player.char_qualified == "Mayor":
            if self.player.char_Mayor_state < 2:
                self.player.char_Mayor_state = 1
                self.player.char_state = 2
                self.machine.events.post("char_mayor_start")
                self.remove_all_display()
                self.machine.events.post("char_mayor_r_add")


    def saucer(self, **kwargs):
        # if ball is in saucer collecting mystery
        # wait for event callback when mystery is done
        if self.player.mystery_ball_in_saucer == 0:
            self.try_start()
            self.delay.add(name="delayed_saucer_eject", ms=3000, callback=self.eject_saucer_ball)
        else:
            self.log.info( 'ball is busy with mystery, waiting for callback' )

    def eject_saucer_ball(self):
        self.machine.coils['jackkickout'].pulse()                
        

    def soup(self, **kwargs):
        self.try_start()
        self.log.info('char_Qualify - in the soup')
        #set a 2s timer, if we haven't ejected from VUK, then pulse it.
        self.vuk_fired = 0            
        self.delay.add(name="ball_stuck_in_VUK", ms=2000, callback=self.soup_eject)

    def soup_eject(self, **kwargs):
        if self.vuk_fired == 0:
            self.log.info('char_Qualify - stuck in the soup, eject')
            self.machine.coils['soupVUK'].pulse()

    def soup_ejected(self, **kwargs):
        self.vuk_fired = 1


    def try_start(self):
        # if nothing is running
        if self.player.char_state < 2:
            #if jack is qualified
            if self.player.char_qualified == "Jack":
                #if all other chars have been played, then play Scientific Method
                #else play Where's Jack
                if (self.player.char_Sally_state > 0
                  and self.player.char_Doctor_state > 0
                  and self.player.char_Mayor_state > 0
                  and self.player.char_Zero_state > 0
                  and self.player.char_LSB_state > 0):
                    if self.player.char_Science_state == 0:
                        self.player.char_qualified = "Science"
                        self.player.char_Science_state = 1
                        self.player.char_state = 2
                        self.machine.events.post("char_science_start")
                        self.remove_all_display()
                        self.machine.events.post("char_jack_r_add")
                else: 
                    #if Where's Jack hasn't been played, start it
                    if self.player.char_Where_state < 2:
                        self.player.char_qualified = "Where"
                        self.player.char_Where_state = 1
                        self.player.char_state = 2
                        self.machine.events.post("char_where_start")
                        self.remove_all_display()
                        self.machine.events.post("char_jack_r_add")
            #if Sally is qualified
            elif self.player.char_qualified == "Sally":
                if self.player.char_Sally_state < 2:
                    self.player.char_Sally_state = 1
                    self.player.char_state = 2
                    self.machine.events.post("char_sally_start")
                    self.remove_all_display()
                    self.machine.events.post("char_"+self.player.char_qualified+"_r_add")
            #if Doctor is qualified
            elif self.player.char_qualified == "Doctor":
                if self.player.char_Doctor_state < 2:
                    self.player.char_Doctor_state = 1
                    self.player.char_state = 2
                    self.machine.events.post("char_doctor_start")
                    self.remove_all_display()
                    self.machine.events.post("char_"+self.player.char_qualified+"_r_add")
        elif self.player.char_state == 3:
            self.player.char_Wizard_state = 1
            self.player.char_state = 4
            self.machine.events.post("char_wizard_start")
       

    def hinterlands(self, **kwargs):
        self.log.info('Hinterlands ' + str(self.player.Doors_state))        
        if self.player.Doors_state == 1:
            # in the trees, during a running holiday mode        
            if (self.player.doors_currentdoor == 5 or self.player.doors_currentdoor == 6):
                # if thanksgiving or hallowen running, spot a zero qualify
                self.log.info('Hinterlands - H or T door mode was running, spot a zero qualify')        
                self.zero_qualified()


    def zero(self, **kwargs):
        self.show_status()   #debugging info
        # if no char mode is already running
        if self.player.char_state < 2:
            #if Zero is qualified
            if self.player.char_qualified == "Zero":
                #if Zero Fetch hasn't been completed, start it
                if self.player.char_Zero_state < 2:
                    self.player.char_qualified = "Zero"
                    self.player.char_Zero_state = 1
                    self.player.char_state = 2
                    self.machine.events.post("char_zero_start")
                    self.remove_all_display()
                    self.machine.events.post("char_"+self.player.char_qualified+"_r_add")
                    self.disable_zero_diverter()
            elif self.player.char_qualified == "Jack":
                if ( self.player.char_What_state == 0 or
                    (self.player.char_What_state != 1 
                    and (self.player.char_Where_state == 2 or self.player.char_Science_state == 2))):
                    #if we've havent run What yet, or if we have but Where or Science have run
                    self.player.char_qualified = "What"
                    self.player.char_What_state = 1
                    self.player.char_state = 2
                    self.machine.events.post("char_what_start")
                    self.remove_all_display()
                    self.machine.events.post("char_jack2_r_add")
                    self.log.info('Char - What - start posted')
                    self.disable_zero_diverter()
                else:
                    self.zero_qualified()
            else:
                self.zero_qualified()
                    
    def remove_all_display(self):
        self.machine.events.post("char_remove_all")        

        
    def mode_stop(self, **kwargs):
        #if a mode was running, stop it
        self.log.info('stop_all_character_messages')
        self.log.info('char_Qualify mode_stop')
        self.reset_lights()
