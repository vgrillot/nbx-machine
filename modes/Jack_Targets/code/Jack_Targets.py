from mpf.core.mode import Mode

# JACK Targets
# 
# When you light all four JACK lights by hitting the standups for them at the sides of the two major ramps, you raise the bonus multiplier by 1x up to a maximum of
# 12x. Completing the JACK lights with no character mode or multiball running also qualifies the frenzy mode "W hat's This?" by getting the ball into the Hinterlands
# (normally, shooting the Hinterlands starts a Door Mode) and also qualifies "Where's Jack?" or "The Scientific Method" (if all other character modes are completed)
# by shooting any of the other holes. (Graveyard, Mayor, Soup.) Since both are qualified at the same time, if you qualify a different character mode, all JACK-related
# modes are disqualified. If one's already been completed it won't be qualified. If both have been completed neither will.
# 
# 
# Completing the JACK lights when the bonus multiplier is already up to a maximum of 12x awards 1,000,000 points.

class Jack_Targets(Mode):

# runs on MPF boot when the mode is read in and set up.
    def mode_init(self):
        self.log.info('Jack_Targets mode_init')

    def mode_start(self, **kwargs):
        self.player.jacks_collected = 0
        #self.player.jacks_lights = 
        self.player.bonus_multiplier = 1
        self.j_lit = 0
        self.a_lit = 0
        self.c_lit = 0
        self.k_lit = 0
        self.log.info('Jack_target mode_start')
        self.add_mode_event_handler('jack_standups_jack_lights_lit_complete', self.handle_jack_complete)
        self.add_mode_event_handler('lrampstandup_left_jack_lights_unlit_hit', self.handle_j_lit)
        self.add_mode_event_handler('lrampstandup_right_jack_lights_unlit_hit', self.handle_a_lit)
        self.add_mode_event_handler('rrampstandup_left_jack_lights_unlit_hit', self.handle_c_lit)
        self.add_mode_event_handler('rrampstandup_right_jack_lights_unlit_hit', self.handle_k_lit)


    def handle_jack_complete(self, **kwargs):
        self.log.info('handle_jack_complete')
        self.j_lit = 0
        self.a_lit = 0
        self.c_lit = 0
        self.k_lit = 0
        self.machine.events.post('jack_spelled')                    
        self.player.jacks_collected = self.player.jacks_collected + 1
        if self.player.bonus_multiplier == 12:
            self.player["score"] += (1000000)
            self.machine.events.post('jack_spelled_12')
        if self.player.bonus_multiplier < 12:
            self.player.bonus_multiplier = self.player.bonus_multiplier +1
            self.machine.events.post('bonus_multiplier_increased',value=self.player.bonus_multiplier )


    def post_jack_event(self):
        self.machine.events.post('show_jack_letters')    
        letterscompleted = 0
        if self.j_lit == 1:
            self.machine.events.post('show_jack_letter_j')    
            letterscompleted += 1
        if self.a_lit == 1:
            self.machine.events.post('show_jack_letter_a')    
            letterscompleted += 1            
        if self.c_lit == 1:
            self.machine.events.post('show_jack_letter_c')    
            letterscompleted += 1            
        if self.k_lit == 1:
            self.machine.events.post('show_jack_letter_k')    
            letterscompleted += 1
        if letterscompleted < 4:
            self.machine.events.post('say_jack_letter_hit')


    def handle_j_lit(self, **kwargs):
        self.log.info('handle_j_lit')
        self.post_jack_event()        
        self.j_lit = 1
        self.machine.events.post('show_jack_letter_blink_j')    


    def handle_a_lit(self, **kwargs):
        self.log.info('handle_a_lit')
        self.post_jack_event()
        self.a_lit = 1        
        self.machine.events.post('show_jack_letter_blink_a')            


    def handle_c_lit(self, **kwargs):
        self.log.info('handle_c_lit')
        self.post_jack_event()        
        self.c_lit = 1
        self.machine.events.post('show_jack_letter_blink_c')


    def handle_k_lit(self, **kwargs):
        self.log.info('handle_k_lit')
        self.post_jack_event()        
        self.k_lit = 1
        self.machine.events.post('show_jack_letter_blink_k')


    def mode_stop(self, **kwargs):
        self.log.info('Jack_target mode_stop')
