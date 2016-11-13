from mpf.core.mode import Mode

# Toys & Pop Bumpers                                                                                                                                                   Page 6
# 
# The pop bumpers are only worth 1,200 points per hit. 
# However, each time you hit one you also get a "Toy" which is a cumulative value kept 
# throughout the game which factors into your end of ball bonus, but is also a factor 
# for jackpots, timed modes, and the "Deliver the Presents" wizard mode.
# 
# Jackpots         All "jackpots" are increased by 10,000 points per toy you have. If the shot is worth a lot but is NOT a jackpot, it is unaffected.
# Timed Modes      All modes with time limits will get a 1 second increase to its initial time limit per 100 toys you have. Does not affect combos and non-mode timers.
# Presents         When in "Deliver the Presents" each present delivered actually drops your toy count by 1. More details can be found in the section for this mode.
# 
# Toys are often awarded from other methods as well, plus you can upgrade a single pop bumper 
# by spelling SANTA or by collecting the appropriate Mystery award, or there's also a mystery award 
# "Pops at Max" which will upgrade all three pop bumpers to triple value. The lights of the pops 
# change from white, to green, to red to indicate 1x, 2x, and 3x value, which affects both 
# the points awarded and the toys collected.
# 
# Also, any time a shot you make which scores toys happens to have a shot multiplier attached, 
# the toys awarded are also affected. Thus if you make a combo which
# awards 10 toys on a tripled shot, you get 30 toys!

class Toys(Mode):

    def mode_init(self):
        self.log.info('Toys mode_init')

    def mode_start(self, **kwargs):
        self.log.info('Toys mode_start')
        if self.player.toys_started == 0:
            self.player.toys_started = 1 
            self.player.toys_collected = 0
        self.player.toy_left_value = 1
        self.player.toy_right_value = 1
        self.player.toy_top_value = 1
        self.player.toys_at_max = 0
        self.player.toys_show_handles = [0] * 3
        self.add_mode_event_handler('sw_bumpertop', self.top_hit)
        self.add_mode_event_handler('sw_bumperleft', self.left_hit)
        self.add_mode_event_handler('sw_bumperright', self.right_hit)
        self.add_mode_event_handler("toy_pops_upgrade", self.upgrade_toy_values)
        self.add_mode_event_handler("toy_pops_max", self.toys_at_max)        
        self.add_mode_event_handler("toy_pops_override", self.override_pop_lights)
        self.add_mode_event_handler("toy_pops_restore", self.set_pop_lights)
        self.set_pop_lights()

        
    def toys_at_max(self, **kwargs):
        self.player.toy_left_value = 3
        self.player.toy_right_value = 3
        self.player.toy_top_value = 3
        self.player.toys_at_max = 1
        self.score = 50000   
        self.player["score"] += self.score
        self.set_pop_lights()


    def upgrade_toy_values(self, **kwargs):
        if self.player.toy_left_value == 1:
            self.player.toy_left_value = 2
        elif self.player.toy_right_value == 1:
            self.player.toy_right_value = 2
        elif self.player.toy_top_value == 1:
            self.player.toy_top_value = 2
        elif self.player.toy_left_value == 2:
            self.player.toy_left_value = 3
        elif self.player.toy_right_value == 2:
            self.player.toy_right_value = 3
        elif self.player.toy_top_value == 2:
            self.player.toy_top_value = 3
            self.player.toys_at_max = 1
        if self.player.toys_at_max == 1:
            self.player.toys_collected += 10
            self.score = 50000   
            self.player["score"] += self.score
            #if no char mode running, show the toys collected
            if (self.player.char_state == 0 and self.player.Doors_state == 0):
                if self.player.OB_mode_4_running != 1:
                    self.machine.events.post('toys_collected_update',value=self.player.toys_collected)
        self.set_pop_lights()


    def override_pop_lights(self, script_name, **kwargs):
        self.log.info("Pops - override lights")    	
        for x in range(0, 3):
            if self.player.toys_show_handles[x] != 0:
                self.player.toys_show_handles[x].stop()
        led = "grb_gi_25"
        self.player.toys_show_handles[0] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)		
        led = "grb_gi_24"
        self.player.toys_show_handles[1] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)				
        led = "grb_gi_26"
        self.player.toys_show_handles[2] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)		


    def set_pop_lights(self, **kwargs):
        self.log.info("Pops - set lights")
        for x in range(0, 3):
            if self.player.toys_show_handles[x] != 0:
                self.player.toys_show_handles[x].stop()
        led = "grb_gi_25"
        script_name = "sc_pop_"+str(self.player.toy_top_value)
        self.player.toys_show_handles[0] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)		
        led = "grb_gi_24"
        script_name = "sc_pop_"+str(self.player.toy_left_value)
        self.player.toys_show_handles[1] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)		
        led = "grb_gi_26"
        script_name = "sc_pop_"+str(self.player.toy_right_value)
        self.player.toys_show_handles[2] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)		


        
    def right_hit(self, **kwargs):
        self.log.info('right bumper hit')
        self.player.toys_collected += self.player.toy_right_value 
        self.score = 1200   #TODO maybe factor in playfield multiplier here
        self.player["score"] += self.score
        if (self.player.char_state == 0 and self.player.Doors_state == 0):
            if self.player.OB_mode_4_running != 1:
                self.machine.events.post('toys_collected_update',value=self.player.toys_collected)
            

    def left_hit(self, **kwargs):
        self.log.info('left bumper hit')
        self.player.toys_collected += self.player.toy_left_value 
        self.score = 1200   #TODO maybe factor in playfield multiplier here
        self.player["score"] += self.score
        if (self.player.char_state == 0 and self.player.Doors_state == 0):
            if self.player.OB_mode_4_running != 1:
                self.machine.events.post('toys_collected_update',value=self.player.toys_collected)

                
    def top_hit(self, **kwargs):
        self.log.info('top bumper hit')
        self.player.toys_collected += self.player.toy_top_value 
        self.score = 1200   #TODO maybe factor in playfield multiplier here
        self.player["score"] += self.score
        if (self.player.char_state == 0 and self.player.Doors_state == 0):
            if self.player.OB_mode_4_running != 1:
                self.machine.events.post('toys_collected_update',value=self.player.toys_collected)

                
    def mode_stop(self, **kwargs):
        self.log.info('Toys mode_stop')
        for x in range(0, 3):
            if self.player.toys_show_handles[x] != 0:
                self.player.toys_show_handles[x].stop()
                self.player.toys_show_handles[x] = 0

