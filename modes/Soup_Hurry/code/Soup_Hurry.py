from mpf.core.mode import Mode
from mpf.core.delays import DelayManager
import random

# Soup Hurry-Up
# If you get 100 stitches in normal play (outside of all modes and so long as the hurry up is not running) 
# it starts the Soup Hurry-Up where you must get the ball to the
# Soup Shot under the upper flipper within 15 seconds. The base value of the hurry up starts at 2,000,000 
# and after 2 seconds starts dropping by 4% of its base
# value every quarter-second down to a minimum value of 10% of the base value. 
# Every stitch earned from the spinner while the hurry up is running increases the
# base value by 50,000 points for the rest of the game. 
# If the shooter lane diverter is open when you make the Soup Shot you still get the hurry up award.
 

class Soup_Hurry(Mode):

# runs on MPF boot when the mode is read in and set up.
    def mode_init(self):
        self.log.info('Soup Hurry-Up mode_init')

    def mode_start(self, **kwargs):
        self.log.info('Soup Hurry-Up mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)        
        self.soup_hurry_min_value = 2000000
        self.soup_hurry_ticker = 0
        self.soup_hurry_ticker_last_chance = 0
        
        if self.player.soup_hurry_base_value == 0:
            self.player.soup_hurry_base_value = 5000000        
            
        #when mode starts, start with the base value
        self.player.soup_hurry_current_value = self.player.soup_hurry_base_value

        self.add_mode_event_handler('sw_sally', self.spin)
        self.add_mode_event_handler('sw_soupentrance', self.tastesoup)
        self.delay.add(name='soup_hurry_ticker', ms=50, callback=self.ticker)
        self.soup_hurry_led_state = "white"
        self.player.soup_hurry_state = 1        
        self.set_shot_lights()
        self.machine.events.post('soup_hurry_up_started')  
        self.soup_dec_value = int(self.player.soup_hurry_base_value / 3000)*10
        #approx 16660 for 5,000,000  = 300 ticks @ 50ms = 15 seconds
        
        
    def set_shot_lights(self):
        state = self.soup_hurry_led_state
        if state != "off":
            self.machine.events.post('arrow_change', led_num=9, script_name=state, mode_name="Soup_hurry", action="add")
        

    def spin(self, **kwargs):
        #self.log.info('Soup Hurry-Up - spin')
        #increase the soup starting value for next time
        self.player.soup_hurry_base_value += 50000
        
        
    def tastesoup(self, **kwargs):
        #self.log.info('Soup Hurry-Up - collected') 
        if self.player.soup_hurry_state > 0:
            self.score = self.player.soup_hurry_current_value
            self.score = self.score * self.player.multiplier_shot_value_list[9] 
            self.player["score"] += (self.score)
            self.machine.events.post('taste_the_soup_completed')
            self.machine.events.post('soup_hurry_hide_slide')                                        
            self.delay.remove('soup_hurry_ticker')
            self.player.soup_hurry_state = 5
            self.delay.add(name='soup_hurry_ticker', ms=50, callback=self.ticker)
            self.soup_hurry_ticker_last_chance = self.soup_hurry_ticker            
            self.clear_shots()

            
    def ticker(self):
        #self.log.info('Soup Hurry-Up 50ms tick')
        self.soup_hurry_ticker += 1        
        
        if self.player.soup_hurry_state == 1:
        
            if self.soup_hurry_ticker == 10:
                self.log.info('Soup Hurry-Up ready yet?')            
                self.machine.events.post('say_ready_yet')
                
            if self.soup_hurry_ticker > 40:                
                self.player.soup_hurry_state = 2                        
                
        elif self.player.soup_hurry_state == 2:        
            #after 2 seconds, decrement the value

            self.player.soup_hurry_current_value -= self.soup_dec_value
            if self.player.soup_hurry_current_value < self.soup_hurry_min_value:
                self.player.soup_hurry_current_value = self.soup_hurry_min_value
                self.player.soup_hurry_state = 3
         #       self.log.info('Soup Hurry-Up - min, stay for 2 secs')
                self.soup_hurry_ticker_last_chance = self.soup_hurry_ticker

        elif self.player.soup_hurry_state == 3:        
            #after 2 seconds at min, shut off light, go to grace period for 1 second
            
            if self.soup_hurry_ticker - self.soup_hurry_ticker_last_chance > 50:
                self.player.soup_hurry_state = 4
                self.clear_shots()
                self.machine.events.post('soup_hurry_hide_slide')                
                self.machine.events.post('say_nothings_more')                
                
        elif self.player.soup_hurry_state == 4:        
            #grace period for 1 second
            if self.soup_hurry_ticker - self.soup_hurry_ticker_last_chance > 80:
                self.delay.remove('soup_hurry_ticker')
                self.player.soup_hurry_state = 0
                self.machine.events.post('soup_hurry_stop')

        elif self.player.soup_hurry_state == 5:        
            self.log.info('Soup Hurry-Up - min, extro for 2 secs')        
            #extro, 2 seconds
            if self.soup_hurry_ticker - self.soup_hurry_ticker_last_chance > 40:
                self.player.soup_hurry_state = 0
                self.machine.events.post('soup_hurry_stop')
#                self.log.info('Soup Hurry-Up - min, soup_hurry_stop state: ' +str(self.player.soup_hurry_state))        
                
        if self.player.soup_hurry_state != 0:
            self.delay.add(name='soup_hurry_ticker', ms=50, callback=self.ticker)

        if (self.player.soup_hurry_state > 0 and self.player.soup_hurry_state < 4):            
            if self.soup_hurry_ticker % 4 == 0:
                state = self.soup_hurry_led_state            
                self.machine.events.post('arrow_change', led_num=9, script_name=state, mode_name="Soup_hurry", action="remove")                    
                r = random.randint(0,20)*10
                g = random.randint(10,20)*10
                b = random.randint(0,20)*10        
                self.soup_hurry_led_state = "purple"  #TODO - replace purple with hex color string from r,g,b
                state = self.soup_hurry_led_state
                self.machine.events.post('arrow_change', led_num=9, script_name=state, mode_name="Soup_hurry", action="add")
            
        
    def clear_shots(self):
        state = self.soup_hurry_led_state
        if state != 'off':
            self.machine.events.post('arrow_change', led_num=9, script_name=state, mode_name="Soup_hurry", action="remove")
            self.soup_hurry_led_state = "off"

           
    def mode_stop(self, **kwargs):
        self.log.info('Soup Hurry-Up mode_stop')
        self.delay.remove('soup_hurry_ticker')
        self.player.soup_hurry_state = 0
        self.machine.events.post('soup_hurry_stop')        
        self.clear_shots()
        
