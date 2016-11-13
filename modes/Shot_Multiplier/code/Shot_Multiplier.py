from mpf.core.mode import Mode
from mpf.core.delays import DelayManager


# Shot Multiplier     
# 
# Whenever you make the Soup Shot under the upper flipper, the diverter beside it opens up for 10 seconds. If you manage to quickly get the ball into the Soup Shot
# again, the ball will be diverted to the shooter lane and the circle lights on all the major shots will start flashing blue. The next major shot you make will then have a
# 2x multiplier applied to it for the rest of the ball, indicated by a solid blue circle. This not only affects raw points awarded from making the shot, but affects ALL things
# awarded by that shot, including stitches, toys, jackpots, mystery awards, combos, time awards, multiplier advances, etc. The only things you can't double are extra
# balls and specials. This is referred to by the display as the Soup Doubler.
# 
# However, it's also possible to get a tripler, but this process is trickier. You not only have to get the diverter open, but you have to get the ball into the Zero kickback,
# then let the kickback fire the ball all the way to the diverter without hitting more than one unintended switch along the way. This is referred to on the display as the
# "Zero Tripler" and the circle lights will flash purple instead of blue, plus the tripled shot will stay solid purple instead of solid blue.
# 
# There are some tricks to this. First of all, if you apply a doubler or tripler to a shot which has already been affected, it's wasted. Furthermore, overwriting a doubled
# shot with a tripled shot is all well and good, but you can also accidentally overwrite a tripled shot with a doubled shot. There's no time limit on setting your
# doubled/tripled shot. Once the ball ends all doublers and triplers are lost.

class Shot_Multiplier(Mode):

    def mode_init(self):
        self.log.info('Shot_Multiplier mode_init')

    def mode_start(self, **kwargs):
        self.log.info( 'Shot_Multiplier mode_start' )
        self.delay = DelayManager(self.machine.delayRegistry)
        self.player.multiplier_shot_value_list = [1,1,1,1,1,1,1,1,1,1]
        self.player.multiplier_shot_x = 0
        self.player.awarded_multiplier = 1
        self.player.boost_time = 0        
        self.doc_hits = 0
        self.sally_boost = 0
        #states:  unlit, 2xFlash, 2xSolid, 3xFlash, 3xSolid
        self.player.multiplier_shotlist = [
            {"led":"rgb_mayor_circle", "state":"unlit"}
            ,{"led":"rgb_lorbit_circle", "state":"unlit"}
            ,{"led":"rgb_lramp_circle", "state":"unlit"}
            ,{"led":"rgb_leftloop_circle", "state":"unlit"}
            ,{"led":"rgb_oogie_cw_circle", "state":"unlit"}
            ,{"led":"rgb_oogie_ccw_circle", "state":"unlit"}
            ,{"led":"rgb_grave_circle", "state":"unlit"}
            ,{"led":"rgb_rramp_circle", "state":"unlit"}
            ,{"led":"rgb_rorbit_circle", "state":"unlit"}
            ,{"led":"rgb_soup_circle", "state":"unlit"}
            ]
        self.player.multiplier_show_handles = [0] * 11            
        self.add_mode_event_handler('taste_the_soup_singlestep_unlit_hit', self.open_soup_gate)
        self.add_mode_event_handler('returned_to_plunger2x_singlestep_unlit_hit', self.setup_multiplier_2xshots)        
        self.add_mode_event_handler('returned_to_plunger3x_singlestep_unlit_hit', self.setup_multiplier_3xshots)   
        self.add_mode_event_handler("sw_doctor", self.doctor_hit)
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
        self.add_mode_event_handler('ball_ending', self.reset_multipliers)
        self.add_mode_event_handler("plunged_singlestep_unlit_hit", self.disable_post_timer)
        self.add_mode_event_handler("multiplier_temp_boost", self.temp_boost)


        
    def doctor_hit(self, **kwargs):
        #count hits, every 3 hits, award a timed sally powerup
        self.doc_hits += 1
        if self.doc_hits == 3:
            self.log.info( "doc hit 3 times, power up sally" )
            self.machine.events.post('super_sally_multiplier')            
            self.doc_hits = 0
            self.sally_boost += 1
            self.player.multiplier_shot_value_list[1] += 1  
            self.delay.remove('multiplier_sally_timeout')            
            self.delay.add(name='multiplier_sally_timeout', ms=7000, callback=self.power_down_sally)   
            self.set_lights()

            
    def power_down_sally(self, **kwargs):
        self.log.info( "7 seconds up, power down sally" )            
        self.sally_boost -= 1
        self.player.multiplier_shot_value_list[1] -= 1
        if self.player.multiplier_shot_value_list[1] < 1:
            self.player.multiplier_shot_value_list[1] = 1
        self.set_lights() 
        if self.sally_boost > 0:
            self.delay.add(name='multiplier_sally_timeout', ms=7000, callback=self.power_down_sally)           

        
    def open_soup_gate(self, **kwargs):
        self.log.info( "10 seconds to get back to plunger for multiplier shot" )
       #open the gate for 10 seconds
        self.machine.coils['soupdiverter'].enable()
        self.machine.events.post('soup_gate_open')
        self.delay.remove('multiplier_gate_timeout')       
        self.delay.add(name='multiplier_gate_timeout', ms=10000, callback=self.close_soup_gate)
        self.player.multiplier_shot_x = 1
        self.machine.events.post('set_gi_x_ready')


    def close_soup_gate(self):
        self.log.info( "close the soup gate" )
        #times up, close the gate
        self.machine.coils['soupdiverter'].disable()   

        
    def flash_light_for_multiplier(self):
        self.log.info("Shot Multiplier - flash for multiplier")                        
        for x in range(0, 10):
            if self.player.multiplier_show_handles[x] != 0:
                self.player.multiplier_show_handles[x].stop()
                self.player.multiplier_show_handles[x] = 0
            shot_state = self.player.multiplier_shot_value_list[x]
            led = self.player.multiplier_shotlist[x]["led"]
            if shot_state == 1:
                #not set yet, flash the LED
                if self.player.multiplier_shot_x == 2:
                    #2x is blue
                    script_name = "sc_blue_flash"
                    self.player.multiplier_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)		
                elif self.player.multiplier_shot_x == 3:
                    #3X is purple
                    script_name = "sc_purple_flash"
                    self.player.multiplier_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)		
            elif shot_state == 2:
                script_name = "sc_blue_solid"
                self.player.multiplier_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)
            elif shot_state == 3:
                script_name = "sc_purple_solid"
                self.player.multiplier_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)

                    
    def reset_multipliers(self, **kwargs):
        for x in range(0, 10):
            #turn off the LED
            led = self.player.multiplier_shotlist[x]["led"]
            if self.player.multiplier_show_handles[x] != 0:
                self.player.multiplier_show_handles[x].stop()
                self.player.multiplier_show_handles[x] = 0
#            script_name = "sc_off"
#            self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0)					
            #reset to off (unlit) state
            self.player.multiplier_shotlist[x]["state"] = 'unlit'
            #reset to 1X
            self.player.multiplier_shot_value_list[x] = 1
        self.player.multiplier_shot_x = 0 	


    def set_lights(self):
        for x in range(0, 10):
            led = self.player.multiplier_shotlist[x]["led"]
            if self.player.multiplier_show_handles[x] != 0:
                self.player.multiplier_show_handles[x].stop()
                self.player.multiplier_show_handles[x] = 0
            if self.player.multiplier_shot_value_list[x] == 1:
                self.log.info("Shot Multiplier - set led off - "+str(x))
                script_name = "sc_off"
                self.player.multiplier_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)
            elif self.player.multiplier_shot_value_list[x] == 2:
                self.log.info("Shot Multiplier - set led blue - "+str(x))            
                script_name = "sc_blue_solid"
                self.player.multiplier_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)
            elif self.player.multiplier_shot_value_list[x] == 3:
                self.log.info("Shot Multiplier - set led purple - "+str(x))                        
                script_name = "sc_purple_solid"
                self.player.multiplier_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)
            elif self.player.multiplier_shot_value_list[x] > 3:
                self.log.info("Shot Multiplier - set led white - "+str(self.player.multiplier_shot_value_list[x]))                        
                script_name = "sc_white_solid"
                self.player.multiplier_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)

                
    def temp_boost(self, **kwargs):
        time = kwargs['boost_time']
        self.player.boost_time = time
        self.delay.remove('temp_boost_timeout')       
        self.delay.add(name='temp_boost_timeout', ms=1000, callback=self.temp_boost_countdown)

           
    def temp_boost_countdown(self):
        self.player.boost_time -= 1
        if self.player.boost_time > 0:
            self.delay.remove('temp_boost_timeout')       
            self.delay.add(name='temp_boost_timeout', ms=1000, callback=self.temp_boost_countdown)
            #check what the LED is doing, and boost it by 1  - colour for 4X?
            #self.player.multiplier_shot_value_list[1] = 2
            #self.player.multiplier_shotlist[1]["state"] = '2xSolid'
    

    def setup_multiplier_2xshots(self, **kwargs):
        #TODO - if char sally is running, ie no hold flipper, then give a 5X
        #self.setup_multiplier_5xshots()
        self.log.info( 'Setup for 2x' )
        if self.player.multiplier_shot_x == 1:
            self.log.info("Shot Multiplier - set up 2x")                        
            self.player.multiplier_shot_x = 2
            self.flash_light_for_multiplier()
            self.close_soup_gate()
            self.machine.events.post('set_gi_2x')
            self.machine.events.post('popuppost_enable_up')
            self.machine.events.post('returned_to_plunger')            

        
    def setup_multiplier_3xshots(self, **kwargs):
        #TODO - if char sally is running, ie no hold flipper, then give a 5X
        #self.setup_multiplier_5xshots()
        self.log.info( 'Setup for 3x' )
        if self.player.multiplier_shot_x == 1 or self.player.multiplier_shot_x == 2:
            self.log.info("Shot Multiplier - set up 3x")                                
            self.player.multiplier_shot_x = 3        
            self.flash_light_for_multiplier()
            self.close_soup_gate()
            self.machine.events.post('set_gi_3x')
            self.machine.events.post('popuppost_enable_up')
            self.machine.events.post('returned_to_plunger')            


    def disable_post_timer(self, **kwargs):   
        self.log.info('Ball plunged - start post down timer')    
        if self.player.multiplier_shot_x > 0:
            self.delay.add(name="multiplier_post_down", ms=5000, callback=self.disable_post)
        
    def disable_post(self):
        self.log.info('Disable the popup post')
        self.machine.events.post('popuppost_disable_up')


    def major_0(self, **kwargs):
#        print 'Shot Multiplier - major shot 0'
        self.handle_shot(0)
    def major_1(self, **kwargs):
#        print 'Shot Multiplier - major shot 1'
        self.handle_shot(1)
    def major_2(self, **kwargs):
#        print 'Shot Multiplier - major shot 2'
        self.handle_shot(2)
    def major_3(self, **kwargs):
#        print 'Shot Multiplier - major shot 3'
        self.handle_shot(3)
    def major_4(self, **kwargs):
#        print 'Shot Multiplier - major shot 4'
        self.handle_shot(4)
    def major_5(self, **kwargs):
#        print 'Shot Multiplier - major shot 5'
        self.handle_shot(5)
    def major_6(self, **kwargs):
#        print 'Shot Multiplier - major shot 6'
        self.handle_shot(6)
    def major_7(self, **kwargs):
#        print 'Shot Multiplier - major shot 7'
        self.handle_shot(7)
    def major_8(self, **kwargs):
#        print 'Shot Multiplier - major shot 8'
        self.handle_shot(8)
    def major_9(self, **kwargs):
#        print 'Shot Multiplier - major shot 9'
        self.handle_shot(9)


    def handle_shot(self, shot):
        #set the multiplier for this shot to the new X value
        if self.player.multiplier_shot_x == 2:
            #2x is blue
            self.log.info("Shot Multiplier - 2x shot "+str(shot))
            self.player.multiplier_shot_value_list[shot] = 2
            self.player.multiplier_shotlist[shot]["state"] = '2xSolid'
            self.player.awarded_multiplier = self.player.multiplier_shot_value_list[shot]
            self.machine.events.post('multiplier_2x_set')                     
            #end the   shoot for 2x/3x state
            self.player.multiplier_shot_x = 0
            self.set_lights()
            self.machine.events.post('popuppost_disable_up')
            
        elif self.player.multiplier_shot_x == 3:
            #3X is purple
            self.log.info("Shot Multiplier - 3x shot "+str(shot))        
            self.player.multiplier_shot_value_list[shot] = 3        	  
            self.player.multiplier_shotlist[shot]["state"] = '3xSolid'
            self.player.awarded_multiplier = self.player.multiplier_shot_value_list[shot]
            self.machine.events.post('multiplier_3x_set')
            #end the   shoot for 2x/3x state
            self.player.multiplier_shot_x = 0
            self.set_lights()
            self.machine.events.post('popuppost_disable_up')


    def mode_stop(self, **kwargs):
        self.log.info('Shot_Multiplier mode_stop')
        self.delay.remove('multiplier_gate_timeout')
        self.delay.remove('temp_boost_timeout')        
        self.close_soup_gate()
        self.reset_multipliers()
        

