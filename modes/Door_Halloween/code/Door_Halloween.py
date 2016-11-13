from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Hinterlands Door Mode - "Trick or Treat!"                                                                                                                       Page 27
# 
# Brief Description
# You must complete the LSB standup bank as many time as you can without hitting the Doctor Finklestein standup.
# 
# Scenario
# Lock, Shock and Barrel are out trick-or-treating. Everyone in Halloween Town is a good sport about it, 
# but Doctor Finklestein is in the middle of a critical experiment, so disturbing him would be a really bad idea...
# 
# Details
# Unlike all the other single-ball modes in this game, this one is not timed, however, 
# hitting Doctor Finklestein immediately ends the mode. The trick is to complete the LSB standups 
# as many times as you can without hitting Doctor Finklestein. You only have to complete the bank 
# twice to complete the mode, but can then continue for as many completions as you want as the value 
# increases with each completion.
# 
# Scoring
# Lock, Shock or Barrel Standup              20,000
# Base LSB Completion Value                  1,000,000
# Completion Value Increase                  500,000
# Completion Value Cap                       5,000,000
# Doctor Finklestein                         10
# 
# Lighting
# Doctor Finklestein is solid red for the duration of the mode while the LSB targets flash yellow 
# when ready to hit and go solid yellow once hit. The LSB targets rapidly
# flash white each time they're completed.
# 
# Difficulty Adjustments
# Very Easy        1 LSB Completion Completes Mode, Doctor Finklestein must be hit twice to end the mode
# Easy             1 LSB Completion Completes Mode
# Normal           2 LSB Completions Completes Mode
# Hard             2 LSB Completions Completes Mode
# Very Hard        3 LSB Completions Completes Mode

class Door_Halloween(Mode):

    def mode_init(self):
        self.log.info('Door_Halloween mode_init')

    def mode_start(self, **kwargs):
        self.log.info('Door_Halloween mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.lock_was_hit = 0
        self.shock_was_hit = 0
        self.barrel_was_hit = 0
        self.ticks = 0        
        self.player.door_halloween_running = 0
        self.player.door_halloween_LSB_value = 500000
        self.player.door_halloween_LSB_score = 0
        self.player.door_halloween_LSB_completed = 0
        self.player.door_halloween_LSB_completed_needed = 1
        self.player.door_halloween_Doctor = 0
        self.player.door_halloween_next_jackpot = 1000000
        self.player.door_halloween_current_jackpot = 0
        self.player.halloween_show_handles = [0] * 2                    
        self.add_mode_event_handler('sw_lock', self.lock_hit)
        self.add_mode_event_handler('sw_shock', self.shock_hit)
        self.add_mode_event_handler('sw_barrel', self.barrel_hit)
        self.add_mode_event_handler("lsb_standups_lsbp_halloween_lit_complete", self.lsb_complete)        
        self.add_mode_event_handler('sw_doctor', self.doctor_hit)
        self.add_mode_event_handler('door_switch_to_narrow', self.switch_to_narrow)
        self.add_mode_event_handler('door_switch_to_wide', self.switch_to_wide)
        self.add_mode_event_handler("doors_resume_and_show", self.reshow_screen)
        self.add_mode_event_handler("doors_pause_and_hide", self.remove_all_widgets)                  
        self.msg = 1
        self.halloween_start()
        self.add_mode_event_handler("loop_halloween_part1_played", self.music_track_1_played)
        self.add_mode_event_handler("loop_halloween_part2_played", self.music_track_2_played)
        self.add_mode_event_handler("loop_halloween_part3_played", self.music_track_3_played)
        self.add_mode_event_handler("loop_halloween_part4_played", self.music_track_4_played)
        self.add_mode_event_handler("loop_halloween_part5_played", self.music_track_5_played)
        self.add_mode_event_handler("loop_halloween_part6_played", self.music_track_6_played)

        
    def music_track_1_played(self, **kwargs):     
        next_track = random.randint(2,5)
        self.machine.events.post("holiday_halloween_music_loop_"+str(next_track))
        self.log.info('queue up next track '+str(next_track))
        
    def music_track_2_played(self, **kwargs):     
        next_track = random.randint(2,5)
        self.machine.events.post("holiday_halloween_music_loop_"+str(next_track))
        self.log.info('queue up next track '+str(next_track))

    def music_track_3_played(self, **kwargs):     
        next_track = random.randint(2,5)
        self.machine.events.post("holiday_halloween_music_loop_"+str(next_track))
        self.log.info('queue up next track '+str(next_track))

    def music_track_4_played(self, **kwargs):     
        next_track = random.randint(2,5)
        self.machine.events.post("holiday_halloween_music_loop_"+str(next_track))
        self.log.info('queue up next track '+str(next_track))

    def music_track_5_played(self, **kwargs):     
        next_track = random.randint(2,5)
        self.machine.events.post("holiday_halloween_music_loop_"+str(next_track))
        self.log.info('queue up next track '+str(next_track))

    def music_track_6_played(self, **kwargs):     
        self.log.info('last track  no queue')
        
    def remove_all_widgets(self, **kwargs):     
        self.log.info('pause_and_hide - remove all messages')
        self.machine.events.post("remove_halloween_messages")  
        self.machine.events.post('remove_halloween_slide_narrow')
        self.machine.events.post('remove_halloween_slide_wide')
        self.machine.events.post('remove_halloween_slide_full')


    def reshow_screen(self, **kwargs):   
        if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
            self.switch_to_narrow()
        else:
            self.switch_to_wide()        


    def ticker(self):
        self.log.info("door_halloween - 500ms ticks " +str(self.ticks))
        if self.player.door_halloween_running == 1:
            self.delay.add(name="door_halloween_ticker", ms=500, callback=self.ticker)        
        if self.player.door_timer_ispaused == 0:        
            self.ticks += 1
            if  self.ticks_msg-self.ticks < -3:
                self.msg += 1
                self.ticks_msg = self.ticks
                if self.msg > 3: 
                    self.msg = 1                  
                if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                    self.machine.events.post('show_halloween_msg_'+str(self.msg)+'_n')            
                else:
                    self.machine.events.post('show_halloween_msg_'+str(self.msg))                    

            
    def switch_to_narrow(self, **kwargs):   
        self.remove_all_widgets()
        self.machine.events.post('show_halloween_slide_narrow')

        
    def switch_to_wide(self, **kwargs):
        self.remove_all_widgets()
        self.machine.events.post('show_halloween_slide_wide')

            
    def halloween_start(self):
        self.log.info("holiday halloween start")
        if (self.player.door_halloween_running == 0):
            self.player.door_halloween_running = 1
            self.machine.events.post("holiday_halloween_music_start")
            self.player.door_halloween_LSB_score = 0
            self.player.door_halloween_LSB_completed = 0
            self.player.door_halloween_Doctor = 2 #2 hits and its over
            self.set_lights()
            self.machine.events.post('show_halloween_slide_full')
            self.machine.events.post('char_pause_and_hide')
            self.machine.events.post("ob_pause_and_hide")  
            self.player.door_timer_ispaused = 0            
            self.delay.add(name="show_full_halloween_intro_remover", ms=5000, callback=self.show_screen)

            
    def show_screen(self, **kwargs):
        self.log.info( "5 seconds passed, show narrow or wide" )
        self.ticks_msg = self.ticks
        self.delay.add(name="door_halloween_ticker", ms=500, callback=self.ticker) 
        if self.player.door_timer_ispaused == 0:                
            self.machine.events.post("char_resume_and_show")
            self.machine.events.post("ob_resume_and_show")   
            self.reshow_screen()                
            if self.player.OB_Gate_current_mode_state == 1:  #oogie mode running
                self.machine.events.post('show_halloween_msg_1_n')                
            else:
                self.machine.events.post('show_halloween_msg_1')                


    def halloween_stop(self, **kwargs):
        if self.player.door_halloween_running == 1:
            self.machine.events.post('holiday_halloween_music_stop_looping')            
            self.machine.events.post('holiday_halloween_music_extro')                        
            self.log.info("holiday halloween over")
            if self.player.door_halloween_LSB_completed >= self.player.door_halloween_LSB_completed_needed:
                self.log.info("holiday halloween over - and complete")
                self.player.door_halloween_running = 2
                self.machine.events.post('holiday_mode_stopped', state="complete")            
            else:
                self.player.door_halloween_running = 0 #ready to start again
                self.machine.events.post('holiday_mode_stopped', state="incomplete")
            self.reset_lights()
        self.machine.events.post('remove_halloween_messages')
        self.machine.events.post('remove_halloween_narrow')
        self.machine.events.post('remove_halloween_wide')
        self.machine.events.post('oogie_switch_to_wide')
        self.machine.events.post("char_resume_and_show")
            

            
    def set_lights(self):
        led = "rgb_doctor_rect"
        script_name = "sc_red_flash"
        self.player.halloween_show_handles[0] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)			

        
    def reset_lights(self):
        if self.player.halloween_show_handles[0] != 0:
            self.player.halloween_show_handles[0].stop()
            self.player.halloween_show_handles[0] = 0
        led = "rgb_doctor_rect"
        script_name = "sc_off"
        self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=1)			

		
    def lsb_complete(self,**kwargs):
        if self.player.door_halloween_running == 1:
            self.log.info("door_halloween - LSB complete")
            self.player.door_halloween_current_jackpot = self.player.door_halloween_LSB_value * (self.player.door_halloween_LSB_completed+2)            
            self.player.door_halloween_LSB_completed += 1
            if self.player.door_halloween_LSB_completed > 8:
                self.player.door_halloween_LSB_completed = 8
            self.player.door_halloween_LSB_score += self.player.door_halloween_current_jackpot
            self.player.door_halloween_next_jackpot = self.player.door_halloween_LSB_value * (self.player.door_halloween_LSB_completed+2)
            self.machine.events.post('door_halloween_LSB_completed')
            self.player.score += self.player.door_halloween_current_jackpot
            self.lock_was_hit = 0
            self.shock_was_hit = 0
            self.barrel_was_hit = 0

            
    def lock_hit(self, **kwargs):
        self.log.info("Door_Halloween - lock hit")
        if self.lock_was_hit == 0:
            self.player.score += 20000
        else:
            self.player.score += 200            
        self.lock_was_hit = 1
        if self.shock_was_hit == 1 and self.barrel_was_hit == 1:
            self.lsb_complete()
        

    def shock_hit(self, **kwargs):
        self.log.info("Door_Halloween - shock hit")
        if self.shock_was_hit == 0:
            self.player.score += 20000
        else:
            self.player.score += 200            
        self.shock_was_hit = 1
        if self.lock_was_hit == 1 and self.barrel_was_hit == 1:
            self.lsb_complete()
        
    def barrel_hit(self, **kwargs):
        self.log.info("Door_Halloween - barrel hit")
        if self.barrel_was_hit == 0:
            self.player.score += 20000
        else:
            self.player.score += 200            
        if self.shock_was_hit == 1 and self.lock_was_hit == 1:
            self.lsb_complete()

        

    def doctor_hit(self, **kwargs):
        self.log.info("Door_Halloween - doctor hit")
        if self.player.door_halloween_running == 1:        
            self.player.score += 10                    
            self.player.door_halloween_Doctor -= 1
            if self.player.door_halloween_Doctor <= 0:
                #mode is over!
                self.halloween_stop()
                self.machine.events.post('door_halloween_doctor_hit_done')
            else:
                self.machine.events.post('door_halloween_doctor_hit')

                
    def mode_stop(self, **kwargs):
        self.log.info('Door_Halloween mode_stop')
        if self.player.door_halloween_running == 1:        
            self.halloween_stop()

            