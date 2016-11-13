from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Gate Keeper Multiball
# 
# This is a super-secret multiball mode which can only be accessed by knowing how 
# to select your gift from the mystery award process. This 2-ball multiball basically
# boils down to hitting the gate in front of Oogie Boogie's lair for 250,000 points each hit. 
# The 9th hit lowers the gate and if you get the ball back into Oogie Boogie's lair
# you'll get an extra ball, after which the gate comes up and stays up and simply continues to 
# award 250,000 points. The trick is there's no ball save on this multiball,
# although you do get one for 15 seconds when the multiball ends, thus you can't double-drain out of it. 
# If multiple targets are hit at once, it still only counts as a single
# gate hit, as there's an extremely short delay after any target on the gate is hit where the 
# targets won't register a second time.

class Gate_Keeper(Mode):
        
    def mode_init(self):
        self.log.info('OB Gate Keeper Multiball mode_init')
        self.delay = DelayManager(self.machine.delayRegistry)
        
    def mode_start(self, **kwargs):
        self.log.info( 'Gate Keeper Multiball mode_start')
        if self.player.gate_keeper_mb_started == 0:
            self.player.gate_keeper_mb_started = 1
            self.player.gate_keeper_multiball_running = 0
        self.player.gates_hit = 0
        self.player.GK_extra_ball_awarded = 0
        self.player.GK_hits_needed = 9
        self.player.GK_jackpot_value = 250000
        self.player.gatekeeper_total_score = 0
        
        self.add_mode_event_handler('sw_oogietarget1', self.hit_target)
        self.add_mode_event_handler('sw_oogietarget2', self.hit_target)
        self.add_mode_event_handler('sw_oogietarget3', self.hit_target)
        
        self.add_mode_event_handler('sw_subwayoogie', self.oogie_hit)        

        self.add_mode_event_handler('balldevice_trough_ball_enter', self.ball_drained)
        
        self.add_mode_event_handler('oogie_switch_to_narrow', self.switch_to_narrow)        
        self.add_mode_event_handler('oogie_switch_to_wide', self.switch_to_wide)   
        self.add_mode_event_handler("ob_resume_and_show", self.reshow_screen)    
        self.add_mode_event_handler("ob_pause_and_hide", self.remove_all_widgets)
        self.player.gk_gate_show_handles = [0] * 3        
        self.ticks = 0    
        self.msg = 1
        self.ticks_msg = self.ticks
        self.start_multiball()
 
 
    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_gatekeeper_messages")  
        self.machine.events.post('remove_gatekeeper_slide_wide')
        self.machine.events.post('remove_gatekeeper_slide_narrow')
        self.machine.events.post('remove_gatekeeper_slide_intro')
        
        
    def reshow_screen(self, **kwargs):   
        self.log.info('reshow_screen')
        if self.player.Doors_state == 1:  #door mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        
        
        
    def switch_to_narrow(self, **kwargs):   
        self.remove_all_widgets()
        self.machine.events.post('show_gatekeeper_slide_narrow')


    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()
        self.machine.events.post('show_gatekeeper_slide_wide')


    def ball_drained(self, **kwargs):
        if self.player.gate_keeper_multiball_running == 1:
            self.log.info('OB Gate Keeper multiball - ball drained BIP='+str(self.machine.game.balls_in_play))
            if self.machine.game.balls_in_play <= 2:
                #there is only 1 ball on playfield, end multiball
                self.log.info( "Gate Keeper multiball over" )                    
                self.player.gate_keeper_multiball_running = 2
                self.machine.events.post('gate_keeper_music_stop')
                self.machine.events.post('GK_ending')                
                self.machine.events.post('enable_combos')
                self.machine.events.post('add_a_ball_stop')
                self.machine.events.post("char_resume_and_show")                    
                self.machine.events.post('door_switch_to_wide')                 
                self.remove_all_widgets()        
                if self.player.ball_save_active == 0:
                    #TODO - activate a 15 second ball save
                    self.log.info( "Gate Keeper multiball - ball drained - MB over, add a ball save" )
                    self.machine.events.post('enable_the_ball_save')                       
            else:
                self.log.info( "Gate Keeper multiball - ball drained - still are at least 2 BIP" )            


    def start_multiball(self):
        if (self.player.gate_keeper_multiball_running == 0):
            self.log.info( "Starting GK MB" )
            self.set_lights()
            bip = self.machine.game.balls_in_play             
            if bip < 6:
                self.log.info( "GK - add a bip")
                self.machine.game.balls_in_play = bip+1
                self.machine.playfield.add_ball(1, player_controlled=False)
            self.player.gate_keeper_multiball_running = 1
            self.machine.events.post('gate_keeper_music_start')
            self.machine.events.post("GK_close_the_gate")             
            self.machine.events.post('GK_starting')   
            self.player.OB_Gate_current_mode_state = 1            
            self.machine.events.post('disable_combos')
            self.machine.events.post('add_a_ball_start')
            self.machine.events.post('show_gatekeeper_slide_intro') 
            self.machine.events.post('char_pause_and_hide')
            self.machine.events.post("doors_pause_and_hide")
            self.ready_for_hit = 1            
            self.player.ob_timer_ispaused = 0            
            self.delay.add(name="show_full_gatekeeper_intro_remover", ms=6000, callback=self.show_screen)

            
    def show_screen(self, **kwargs):
        self.log.info( "5 seconds passed, show narrow or wide" )
        self.delay.add(name='GK_MB_ticker', ms=500, callback=self.ticker)
        if self.player.ob_timer_ispaused == 0:
            self.reshow_screen()
            self.machine.events.post("char_resume_and_show")
            self.machine.events.post("doors_resume_and_show")
        

    def ticker(self):
        self.log.info("500ms ticks " + str(self.ticks))
        self.delay.add(name='GK_MB_ticker', ms=500, callback=self.ticker)                    
        if self.player.ob_timer_ispaused == 0:        
            self.ticks += 1;
            if self.ticks_msg-self.ticks < -3:
                self.msg += 1
                self.ticks_msg = self.ticks
                if self.msg > 3: 
                    self.msg = 1  
                if self.ticks > 2:                                
                    if self.player.Doors_state == 1:  #door mode running            	
                        self.machine.events.post('show_gatekeeper_msg_'+str(self.msg)+'_n')            
                    else:
                        self.machine.events.post('show_gatekeeper_msg_'+str(self.msg))            


    def hit_target(self, **kwargs):
        self.log.info("Oogie Gate Keeper - target bank hit")    
        if self.player.gate_keeper_multiball_running == 1:
            if self.ready_for_hit == 1:
                self.ready_for_hit = 0
                nb = random.randint(1,6)
                self.machine.events.post('bug_splat_'+str(nb))
                self.player.bug_score = self.player.GK_jackpot_value
                self.player["score"] += self.player.bug_score
                self.player.gatekeeper_total_score += self.player.bug_score
                self.machine.events.post('gate_keeper_gate_jackpot')                
                self.clear_lights()
                self.player.gates_hit += 1
                if self.player.GK_hits_needed > 0:
                    self.player.GK_hits_needed -= 1
                if self.player.gates_hit == 9:
                    #lower the gate and wait for oogie subway shot
                    self.machine.events.post("GK_open_the_gate")                                
                else:
                    self.delay.add(name='GK_ready_pause', ms=50, callback=self.reset_ready)
                    
                    
    def oogie_hit(self, **kwargs):
        if self.player.gate_keeper_multiball_running == 1:
            if self.player.GK_extra_ball_awarded == 0:
                self.player.GK_extra_ball_awarded = 1
                self.log.info("Oogie hit - GK mode")
                self.player.bug_score = self.player.GK_jackpot_value
                self.player["score"] += self.player.bug_score
                self.player.gatekeeper_total_score += self.player.bug_score                
                #award extra ball
                self.machine.events.post("award_EB_start")            
                #close the gate
                self.machine.events.post("GK_close_the_gate") 
                self.reset_ready()


    def reset_ready(self, **kwargs):
        self.ready_for_hit = 1
        self.set_lights()


    def clear_lights(self):
        for x in range(0, 3):    	
            if self.player.gk_gate_show_handles[x] != 0:
                self.player.gk_gate_show_handles[x].stop()
                self.player.gk_gate_show_handles[x] = 0


    def set_lights(self):
        self.clear_lights()    	
        for x in range(0, 3):
            led = "rgb_bug_"+str(x+1)
            self.log.info("Setting rgb "+led + " to red")
            script_name = "sc_red_flash"
            self.player.gk_gate_show_handles[x] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)									


    def mode_stop(self, **kwargs):
        self.log.info( 'OB Gate Keeper mode_stop' )
        self.clear_lights()
        


