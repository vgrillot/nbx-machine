from mpf.core.mode import Mode
import random

# SANTA Lights
# 
# There are five lanes by the flippers: two outlanes and three return lanes. 
# The lights above them spell SANTA. If they're completed, you're given a SANTA award
# which consists of several things:
# 
# Awards a base value of 100,000 points, 
# increased by 50,000 for each subsequent completion over the course of the game (capped at 500,000), 
# plus an additional 200 multiplied by the end-of-ball bonus multiplier 
# and multiplied again by the number of toys collected. (125 toys at 4x bonus would be 100,000
# additional points.)
# Awards a Toy Pops upgrade.
# Lights the Mystery Shot once per ball. If the mystery shot is already lit, 
# this is NOT wasted and can still be obtained later in the ball.
# 
# One trick to this however is that it's possible to alley pass the first 'A' in Santa. To prevent abuse of this, if SANTA is completed twice in a row without hitting any
# other switches other than SANTA switches, the SANTA lights will flash red and the display will show "Santa is Exhausted" which is worth a random number of
# points from 10 to 19,990.

class Santa_Targets(Mode):

# runs on MPF boot when the mode is read in and set up.
    def mode_init(self):
        self.log.info('Santa_Targets mode_init')

    def mode_start(self, **kwargs):
        if self.player.santa_started == 0:
            self.player.santa_started = 1 
            self.player.santas_collected = 0
            self.player.santa_points = 0
        self.mystery_shot_count = 0
        self.log.info('Santa_Targets mode_start')
        self.add_mode_event_handler('rollover_lanes_santa_lights_lit_complete', self.handle_santa_complete)
        self.add_mode_event_handler('ball_starting', self.reset_mystery_shot_counter)
        self.add_mode_event_handler('left_out_lane_santa_lights_lit_hit', self.santa_sound2)
        self.add_mode_event_handler('left_return_lane_santa_lights_lit_hit', self.santa_sound2)
        self.add_mode_event_handler('right_return_lane_santa_lights_lit_hit', self.santa_sound2)
        self.add_mode_event_handler('right_out_lane_santa_lights_lit_hit', self.santa_sound2)
        self.add_mode_event_handler('pac_loop_santa_lights_lit_hit', self.santa_sound2)
        self.add_mode_event_handler('left_out_lane_santa_lights_unlit_hit', self.santa_sound)
        self.add_mode_event_handler('left_return_lane_santa_lights_unlit_hit', self.santa_sound)
        self.add_mode_event_handler('right_return_lane_santa_lights_unlit_hit', self.santa_sound)
        self.add_mode_event_handler('right_out_lane_santa_lights_unlit_hit', self.santa_sound)
        self.add_mode_event_handler('pac_loop_santa_lights_unlit_hit', self.santa_sound)
        self.add_mode_event_handler('spot_a_santa', self.handle_santa_complete2)


    def santa_sound(self, **kwargs):
        self.machine.events.post('say_santa_letter_unlit')

    def santa_sound2(self, **kwargs):
        self.machine.events.post('say_santa_letter_already_lit')
   

#reset at the start of each ball
    def reset_mystery_shot_counter(self, **kwags):
        self.mystery_shot_count = 0


# points:  50,000 + 50,000 * santas completed 
# capped at 500,000 ie 9 santas - 50,000 + 9 * 50,000
# + 200 * bonus_multiplier * toys
    def handle_santa_complete(self, **kwargs):
        self.log.info("handle_santa_complete")
        self.player.santas_collected += 1
        self.player.santa_points = 50000 + 50000 * self.player.santas_collected 
        if self.player.santa_points > 500000:
            self.player.santa_points = 500000
        self.toyscore = 200 * self.player.bonus_multiplier * self.player.toys_collected
        self.log.info( 'toyscore ' + str(self.toyscore) )
        self.player.santa_points += self.toyscore
        self.player["score"] += self.player.santa_points
        if self.mystery_shot_count == 0:
            self.mystery_shot_count = 1
            #signal the mysteryshot mode to lite it
            self.machine.events.post('light_mystery_shot')
        self.machine.events.post('toy_pops_upgrade')
        self.machine.events.post('santas_collected_update')

    #awarded from mystery
    def handle_santa_complete2(self, **kwargs):
        self.log.info("handle_santa_complete2")
        self.player.santas_collected += 1
        self.player.santa_points = 50000 + 50000 * self.player.santas_collected 
        if self.player.santa_points > 500000:
            self.player.santa_points = 500000
        self.toyscore = 200 * self.player.bonus_multiplier * self.player.toys_collected
        self.log.info( 'toyscore ' + str(self.toyscore) )
        self.player.santa_points += self.toyscore
        self.player["score"] += self.player.santa_points
        self.machine.events.post('toy_pops_upgrade')
        #TODO - does this need a slide?
        #self.machine.events.post('santas_collected_update2')
        

    def mode_stop(self, **kwargs):
        self.log.info("Santa_Targets mode_stop")

