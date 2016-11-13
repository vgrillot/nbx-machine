from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Door_Wizard
# Hinterlands Wizard Mode - "Holiday Rescue"                                                                                                                            Page 30
# 
# Brief Description
# Most major shots are lit to rescue holiday figures once shot enough times. 
# When a holiday figure is rescued you have to bring them back to the Hinterlands.
# 
# Scenario
# So it turns out that opening the doors in the Hinterlands may not've been such a good idea... 
# various holiday figures have ended up lost in various different worlds.
# Jack sends everyone out to help traverse the doors, find these important individuals, 
# and bring them back to the Hinterlands in order to return them to their realm.
# 
# Details
# This is a 4-ball multiball and you must keep all 4 balls going to get the best scores possible. 
# The ball saver is a generous 30 seconds when you start and can be manually triggered and reset 
# to 30 seconds a total of 3 times over the course of the multiball, each time simply by getting 
# a ball into the Graveyard. When this mode begins, 7 of the major shots are lit to rescue holiday figures. 
# The colour of the shot corresponds to the colour of the Hinterlands Door, so you know who you're
# rescuing. Of the 10 major shots, the ones not lit for rescues are Soup, Left Ramp and Graveyard. 
# As for all the other shots, to make a rescue, you simply need to hit the same shot three times. 
# When you do this, ALL other rescue shots go dark while the Left Ramp and Soup will both start flashing. 
# At this point, you can upgrade the jackpot shot into a super jackpot by getting a ball into soup, 
# then shooting the Hinterlands, but this upgrade only lasts 7 seconds, so you need to be quick. Once
# you get a ball into the Hinterlands, the holiday figure is rescued, you score a jackpot, and the 
# remaining rescues relight and reset to requiring 3 shots each. This means it's far more efficient to 
# go for the same shot three times in a row rather than to scatter shots all across the playfield, 
# since any progress you made on other rescues is lost once you're ready to rescue someone else. 
# If you get down to a single ball, any remaining ball saver triggers are lost and a 30 second timer 
# will show up. If you drain the last ball or the timer expires, the flippers die and the wizard mode ends, 
# returning the player to regular play following.
# 
# Scoring
# Rescue Jackpot                      2,500,000 (Multiplied by number of balls in play)
# Rescue Jackpot Increase             1,250,000
# Super Jackpot                       3x Jackpot Value
# 
# Lighting
# Holiday figures to rescue will flash the triangle of their shots with the appropriate Hinterlands door colour. 
# When that holiday figure is rescued, the Hinterlands shot will flash its triangle the appropriate colour. 
# The Graveyard shot alternates its triangle between orange and white to indicate that it will trigger the ball saver. 
# The soup shot alternates its triangle between white and the appropriate colour to indicate when it will upgrade 
# the jackpot to a super jackpot. Super jackpots on the Hinterlands shot will flash both the triangle and circle.
# 
# Difficulty Adjustments
# Very Easy  5 Balls, Each Shot Needs to be Hit 2 Times for Rescue, Ball Saver Time is 40 Seconds, Can Re-Trigger Ball Saver 4 Times
# Easy       4 Balls, Each Shot Needs to be Hit 3 Times for Rescue, Ball Saver Time is 30 Seconds, Can Re-Trigger Ball Saver 4 Times
# Normal     4 Balls, Each Shot Needs to be Hit 3 Times for Rescue, Ball Saver Time is 30 Seconds, Can Re-Trigger Ball Saver 3 Times
# Hard       4 Balls, Each Shot Needs to be Hit 4 Times for Rescue, Ball Saver Time is 30 Seconds, Can Re-Trigger Ball Saver 3 Times
# Very Hard  3 Balls, Each Shot Needs to be Hit 4 Times for Rescue, Ball Saver Time is 25 Seconds, Can Re-Trigger Ball Saver 2 Times

class Door_Wizard(Mode):

    def mode_init(self):
        self.log.info('Door_Wizard mode_init')

    def mode_start(self, **kwargs):
        self.log.info('Door_Wizard mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.shot_value = 20000
        self.jackpot_value = 2000000
        self.super_jackpot_value = 10000000
        self.ticks = 0
        if self.player.door_wizard_started == 0:
            #once per game only
            self.player.door_wizard_started = 1
            self.player.door_wizard_running = 0
            self.player.door_wizard_score = 0
        self.player.door_wizard_shot_index = 0
        self.player.door_wizard_shot_direction = 1
        self.player.door_wizard_shotlist = [
            {"led":"rgb_mayor_arrow", "mindex":0, "state":"off"}
            ,{"led":"rgb_lramp_arrow", "mindex":2, "state":"off"}
            ,{"led":"rgb_rramp_arrow", "mindex":7, "state":"off"}
            ,{"led":"rgb_soup_arrow", "mindex":9, "state":"off"}
            ]
        self.add_mode_event_handler("major_0_singlestep_unlit_hit", self.major_0)
        self.add_mode_event_handler("major_2_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_2a_singlestep_unlit_hit", self.major_2)
        self.add_mode_event_handler("major_7_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_7a_singlestep_unlit_hit", self.major_7)
        self.add_mode_event_handler("major_9_singlestep_unlit_hit", self.major_9)
        self.add_mode_event_handler('balldevice_trough_ball_enter', self.ball_drained)
        self.door_wizard_start()
        self.msg = 1
        self.ticks_msg = self.ticks
        self.roaming_on = 0


    def door_wizard_start(self):
        self.log.info("door_wizard_start")
        if (self.player.door_wizard_running == 0):
            self.player.door_wizard_running = 1
            self.player.door_wizard_shots_made = 0
            self.set_shots()
            self.machine.events.post("holiday_wizard_music_start")
            self.ticks_msg = self.ticks            
            self.machine.events.post('show_wizard_msg_1')
            self.machine.events.post('disable_combos')
            for x in range(0, 3):
                bip = self.machine.game.balls_in_play             
                if bip < 6:
                    self.machine.game.balls_in_play = bip+1
                    self.machine.playfield.add_ball(1, player_controlled=False)
            self.machine.events.post('add_a_ball_start')
            self.machine.events.post('enable_the_mb_ball_save')   
            self.roaming_on = 0
            self.cycle_shots()
            self.ticks = 0            

    def door_wizard_stop(self):
        if self.player.door_wizard_running == 1:
            self.delay.remove('door_wizard_shot_cycler')
            self.machine.events.post('holiday_wizard_music_stop')
            self.log.info("door_wizard over")
            if self.player.door_wizard_shots_made > 0:
                self.machine.events.post('holiday_mode_stopped', state="complete")
                self.player.door_wizard_running = 2 #completed
            else:
                self.machine.events.post('holiday_mode_stopped', state="incomplete")
                self.player.door_wizard_running = 0 #ready to start again
            self.clear_shots()
            self.machine.events.post('enable_combos')
            self.machine.events.post('add_a_ball_stop')


    def ball_drained(self, **kwargs):
        if self.player.door_wizard_running == 1:
            self.log.info("door_wizard - ball drained")
            self.log.info("door_wizard - balls in play "+str(self.machine.game.balls_in_play))
            if self.machine.game.balls_in_play <= 2:
                if self.player.ball_save_active == 0:
                    #there is only 1 ball on playfield, end multiball
                    self.log.info("door_wizard - Fireworks MB over")
                    self.door_wizard_stop()
                else:
                    self.log.info( "door_wizard multiball - ball drained - but ball save is running" )
            else:
                self.log.info( "door_wizard multiball - ball drained - more than 2 BIP" )            
                

    def set_shots(self):
        self.player.door_wizard_shots_qualified = 0
        for x in range(0, 4):
            self.player.door_wizard_shotlist[x]["state"] = "white"
        self.set_shot_lights()


    def set_shot_lights(self):
        for x in range(0, 4):
            state = self.player.door_wizard_shotlist[x]["state"]
            mindex = self.player.door_wizard_shotlist[x]["mindex"] 
            self.machine.events.post('arrow_change', led_num=mindex, script_name=state, mode_name="Door_wizard", action="add")



    def major_0(self, **kwargs):
        self.handle_shot(0)
    def major_2(self, **kwargs):
        self.handle_shot(1)
    def major_7(self, **kwargs):
        self.handle_shot(2)
    def major_9(self, **kwargs):
        self.handle_shot(3)

 
    def handle_shot(self, shot):
        self.log.info('door_wizard - handle_shot')
        if self.player.door_wizard_running == 1:
            self.score = 0
            state = self.player.door_wizard_shotlist[shot]["state"]
            mindex = self.player.door_wizard_shotlist[shot]["mindex"]
            if state != "off":
                if state == "white":
                    #qualifier
                    self.log.info('door_wizard - jackpot')                                    
                    #stop the flash LED
                    self.machine.events.post('arrow_change', led_num=mindex, script_name=state, mode_name="Door_wizard", action="remove")
                    self.player.door_wizard_shotlist[shot]["state"] = "off"
                    self.score = self.jackpot_value * self.player.multiplier_shot_value_list[mindex] 
                    self.player.door_wizard_shots_qualified += 1
                    self.machine.events.post('holiday_wizard_jackpot', value=self.score)                                            
                    self.player.door_wizard_shots_made += 1
                    if self.player.door_wizard_shots_qualified == 4:
                        self.log.info('door_wizard - start the super jackpot!')
                        self.roaming_on = 1
                elif state == "red":
                    #super jackpot
                    self.log.info('door_wizard - super jackpot')
                    #stop the flash LED
                    self.machine.events.post('arrow_change', led_num=mindex, script_name=state, mode_name="Door_wizard", action="remove")
                    self.player.door_wizard_shotlist[shot]["state"] = "off"
                    self.roaming_on = 0
                    self.score = self.super_jackpot_value * self.player.multiplier_shot_value_list[mindex] 
                    self.machine.events.post('door_wizard_sjackpot_hit', value=self.score)
                    self.set_shots()                    
                else:
                    # "off" - already collected
                    self.log.info('door_wizard - points')                    
                    self.score = self.shot_value * self.player.multiplier_shot_value_list[mindex] 
                    self.machine.events.post('door_wizard_points_hit', value=self.score)
                self.player.score += self.score
                self.player.door_wizard_score += self.score

        

    def cycle_shots(self):
        self.log.info('door_wizard - cycle_shots')
        if self.player.door_wizard_running == 1:
            if self.roaming_on == 1:
                self.clear_shots()
                self.player.door_wizard_shot_index += self.player.door_wizard_shot_direction
                if self.player.door_wizard_shot_index > 3:
                    self.player.door_wizard_shot_index = 2
                    self.player.door_wizard_shot_direction = -1
                if self.player.door_wizard_shot_index < 0:
                    self.player.door_wizard_shot_index = 1
                    self.player.door_wizard_shot_direction = 1
                self.player.door_wizard_shotlist[self.player.door_wizard_shot_index]["state"] = "red"
                self.set_shot_lights()
                self.machine.events.post('holiday_wizard_cycling') 
                self.msg = 3                
            self.delay.add(name="door_wizard_shot_cycler", ms=500, callback=self.cycle_shots)  
            self.ticks += 1
            if self.ticks_msg-self.ticks < -3:
                self.msg += 1
                self.ticks_msg = self.ticks
                if self.msg > 2: 
                    self.msg = 1    
                if self.roaming_on == 1:
                    self.msg = 3 #show the roaming msg
                self.machine.events.post('show_wizard_msg_'+str(self.msg))            

                
    def clear_shots(self):
        for x in range(0, 4):
            state = self.player.door_wizard_shotlist[x]["state"]
            if state != 'off':
                mindex = self.player.door_wizard_shotlist[x]["mindex"]
                self.machine.events.post('arrow_change', led_num=mindex, script_name=state, mode_name="Door_wizard", action="remove")                        
                self.player.door_wizard_shotlist[x]["state"] = "off"


    def mode_stop(self, **kwargs):
        self.log.info('Door_Wizard mode_stop')
        self.door_wizard_stop()
        self.clear_shots()

