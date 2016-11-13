from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Mystery Awards
# 
# Right next to the Graveyard/Jack shot is the mystery target. 
# Hitting this just once the first time (twice the second time, thrice the third, etc. up to a max of 5) lights
# the Graveyard as a mystery award, indicated by flashing the triangle light purple. 
# The visuals for this sequence shows Santa pulling up in his sleigh and reaching into his giant bag of toys, 
# which then zooms into the screen, fades away, then four different-looking presents drop onto the display. 
# Three of those four presents then drop away and the one remaining opens, revealing an award.
# 
# This sequence is important because there's a secret with this: If both flipper buttons are detected 
# as being held when the presents finish lining up on the display, a message will appear (along with 
# a seven second countdown) saying to choose a present! The initial present selected is the same one which 
# was going to be chosen automatically. You can then use the flipper buttons to change your selection and 
# press both at the same time again, or the start button, to select a gift.
# Furthermore, the award given is actually determined by the look of the gift, thus clever players can 
# learn what awards come from each and every gift. This trick can only be done once per game and is also 
# the only way to access Gate Keeper Multiball. It's also a good way to earn rare awards once you 
# know to recognize them.
# 
# Despite the name though, the awards are not entirely random. 
# Firstly, several of the awards are marked as (Default), meaning that if no awards are qualified, one of
# the defaults is selected entirely at random with equal odds. That said, each award has random odds 
# attached, but this only determines how likely the gift is to be selected to appear along with the four
# gifts which show up prior to opening one. This way, certain awards like Extra Ball and Special remain 
# difficult to acquire, even when you know how to perform the selection trick. You'll never see two of 
# the same gift on the display at the same time, as each gift selected in sequence is prevented from being 
# selected again for the spread of four gifts being shown. If multiple gifts are qualified, the one selected
# to appear will be randomly chosen while the others will be ignored and the other three gifts showing 
# up on the display will be selected as usual.
# 
# Add-a-Ball is slightly different. When in any multiball, the mystery target will be solid green. 
# Hit it once to make it start flashing, then again to clear it and light the
# graveyard shot with a green triangle. Hitting the graveyard now will start to display the mystery 
# award sequence, but a giant pinball will fall on the bag of toys,
# pushing the sleigh and Santa out of the display area and showing "Add-a-Ball" text. Afterwards, 
# the mystery shot no longer functions for the duration of the multiball.
# Also, if you start a multiball with the mystery award lit, the graveyard 
# shot immediately lights for an add-a-ball.
# 
# The potential mystery awards are as follows:
# 
# Odds              Award                     Qualifying Method
# 40 in 1,000       1,000,000                 [Default] Cannot be Qualified; Can only be selected with secret selection feature, or by random chance as a default award
# 125 in 1,000      Add Bonus Multiplier      [Default] (Adds 1x to bonus multiplier) Get at least 100 toys in a single ball.
# 125 in 1,000      +1 Toy Upgrade            [Default] Exit out of a multiball with add-a-ball lit but without collecting it. (Mystery award will stay lit but will flash purple.)
# 125 in 1,000      +25 Toys                  [Default] Go for a full minute of ball time without hitting a single pop bumper.
# 50 in 1,000       COllect Bonus             [Default] Raise the bonus multiplier at least 4 times on the current ball.
# 125 in 1,000      5,000,000                 Trigger the ball saver five times, either by starting balls, multiballs, even from the mystery award.
# 30 in 1,000       10,000,000                Play any wizard mode.
# 100 in 1,000      30 Second Ball Saver      Score less than 1,000,000 on the previous ball.
# 100 in 1,000      Complete SANTA            Have four of the five SANTA lights lit. Will relight the mystery shot again if possible. (See details on SANTA lights.)
# 50 in 1,000       Pops at Max               Have collected no toys at all for the current ball.
# 50 in 1,000       Clear Bugs                Make the mystery award shot within 5 seconds of hitting the gate.
# 10 in 1,000       Spot Mode                 Have only one mode completion left for Characters, Hinterlands or Oogie Boogie. Will spot the appropriate mode.
# 5 in 1,000        Extra Ball                Go for 5 minutes of ball time without getting a mystery award.
# 1 in 1,000        Special                   Reach ball 3 in under 1 minute of ball time.
# 50 in 1,000       Gate Keeper Multiball     Cannot be Qualified; Can only be selected with the secret mystery award selection feature.
# 4 in 1,000        Video Mode                ALWAYS awarded as the third mystery award, then every fifth mystery award following.

# N/A               Add 10 Seconds            ALWAYS awarded if a mode timer is running.
# N/A               Add-a-Ball                ALWAYS awarded as the first (and only award possible) in multiball.
# N/A               10 Points                 Somehow manage to get the ball into the Graveyard while mystery is lit and the Gravestone drop target is still up.
class Mystery(Mode):

    def mode_init(self):
        self.log.info('Mystery mode_init')

    def mode_start(self, **kwargs):
        self.log.info( 'Mystery mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.ticks = 0
        # states
        # 0 - accepting hits
        # 1 - reward ready
        # 2 - await 2 flipper input
        # 3 - award selection 
        # 4 - countdown
        self.player.mystery_state = 0 
        self.player.mystery_rewards_lit = 0
        self.player.mystery_target_hits = 0 
        self.player.mystery_target_hits_needed = 1   #1, 2, 3, 4, then hold at 5
        self.player.mystery_choices = [0,0,0,0]
        self.player.mystery_current_selection = 0
        self.player.mystery_selectable = 0
        self.player.mystery_base_ticks = 14 #14 X 500ms = 7 seconds to select
        self.player.mystery_ball_in_saucer = 0

        self.player.mystery_awards = [
            {"ind":0,  "name":"1m_points",        "q_method":"always",                   "q":1, "odds":40,  "times_awarded":0}
           ,{"ind":1,  "name":"bonus_multiplier", "q_method":"toys_100_collected_1_ball","q":0, "odds":125, "times_awarded":0}
           ,{"ind":2,  "name":"toy_upgrade",      "q_method":"unclaimed_add_a_ball",     "q":0, "odds":125, "times_awarded":0}
           ,{"ind":3,  "name":"toy_25",           "q_method":"toys_none_1min",           "q":1, "odds":125, "times_awarded":0}
           ,{"ind":4,  "name":"collect_bonus",    "q_method":"raise_multiplier_4x",      "q":0, "odds":50,  "times_awarded":0}
           ,{"ind":5,  "name":"5m_points",        "q_method":"ball_save_5x",             "q":0, "odds":125, "times_awarded":0}
           ,{"ind":6,  "name":"10m_points",       "q_method":"wizard_mode_played",       "q":0, "odds":30,  "times_awarded":0}
           ,{"ind":7,  "name":"30s_ball_save",    "q_method":"scored_under_1m",          "q":1, "odds":100, "times_awarded":0}
           ,{"ind":8,  "name":"spots_santa",      "q_method":"santas_4_of_5",            "q":0, "odds":100, "times_awarded":0}
           ,{"ind":9,  "name":"toys_at_max",      "q_method":"toys_none_previous_ball",  "q":1, "odds":50,  "times_awarded":0}
           ,{"ind":10, "name":"clear_bugs",       "q_method":"gate_hit_5s",              "q":0, "odds":50,  "times_awarded":0}
           ,{"ind":11, "name":"spot_mode",        "q_method":"one_mode_remaining",       "q":0, "odds":10,  "times_awarded":0}
           ,{"ind":12, "name":"extra_ball",       "q_method":"mystery_none_5min",        "q":0, "odds":5,   "times_awarded":0}
           ,{"ind":13, "name":"special",          "q_method":"ball_3_1min",              "q":0, "odds":1,   "times_awarded":0}
           ,{"ind":14, "name":"gate_keeper",      "q_method":"only_once",                "q":1, "odds":50,  "times_awarded":0}
           ,{"ind":15, "name":"video_mode",       "q_method":"third_5ths_mystery",       "q":0, "odds":4,   "times_awarded":0}

           ,{"ind":16, "name":"10_points",        "q_method":"graveyard_sneakin",        "q":0, "odds":10,  "times_awarded":0}
           ,{"ind":17, "name":"extend_10s",       "q_method":"timer_running",            "q":0, "odds":0,   "times_awarded":0}
           ,{"ind":18, "name":"add_a_ball",       "q_method":"mb_running",               "q":0, "odds":0,   "times_awarded":0}
        ]
        self.add_mode_event_handler('light_mystery_shot', self.mystery_ready)
        self.add_mode_event_handler('sw_mystery', self.mystery_hit)
        self.add_mode_event_handler('sw_grave', self.gravestone_hit)        
        self.add_mode_event_handler('sw_saucer', self.jack_saucer_hit)
        self.add_mode_event_handler('both_flippers_held', self.flippers_held)        
        self.add_mode_event_handler('sw_lower_left_flipper', self.flipper_left)
        self.add_mode_event_handler('sw_lower_right_flipper', self.flipper_right)
                
        #qualifiers
        self.qualify_always()
        self.add_mode_event_handler('toys_100_collected_1_ball', self.qualify_toys_100_collected_1_ball)
        self.add_mode_event_handler('unclaimed_add_a_ball', self.qualify_unclaimed_add_a_ball)        
        self.add_mode_event_handler('toys_none_1min', self.qualify_toys_none_1min)
        self.add_mode_event_handler('raise_multiplier_4x', self.qualify_raise_multiplier_4x)        
        self.add_mode_event_handler('ball_saved_5x', self.qualify_ball_saved_x5)
        self.add_mode_event_handler('wizard_mode_played', self.qualify_wizard_mode_played)
        self.add_mode_event_handler('scored_under_1m', self.qualify_scored_under_1m)
        self.add_mode_event_handler('santas_4_of_5', self.qualify_santas_4_of_5)
        self.add_mode_event_handler('toys_none_previous_ball', self.qualify_toys_none_previous_ball)
        self.add_mode_event_handler('gate_hit_5s', self.qualify_gate_hit_5s)
        self.add_mode_event_handler('one_mode_remaining', self.qualify_one_mode_remaining)        
        self.add_mode_event_handler('mystery_none_5min', self.qualify_mystery_none_5min)                
        self.add_mode_event_handler('ball_3_1min', self.qualify_ball_3_1min)   
        self.qualify_only_once()             
        self.add_mode_event_handler('third_5ths_mystery', self.qualify_third_5ths_mystery)
        self.add_mode_event_handler('graveyard_sneakin', self.qualify_graveyard_sneakin)
        self.add_mode_event_handler('timer_running', self.qualify_add_time)
        self.add_mode_event_handler('mb_running', self.qualify_add_a_ball)

        self.player.mystery_show_handles = [0] * 7
        
        #ball save flag for all the ball_drained in MB modes
        self.player.ball_save_active = 0
        self.add_mode_event_handler('ball_save_default_enabled', self.bs_enabled)
        self.add_mode_event_handler('ball_save_default_disabled', self.bs_disabled)
        self.add_mode_event_handler('ball_save_multiball_enabled', self.bs_enabled)
        self.add_mode_event_handler('ball_save_multiball_disabled', self.bs_disabled)


    def bs_enabled(self, **kwargs):
        self.log.info("Ball Save is active")    
        self.player.ball_save_active = 1
    
    def bs_disabled(self, **kwargs):
        self.log.info("Ball Save is over")        
        self.player.ball_save_active = 0        
                      
 
    def qualify_always(self, **kwargs):
        self.log.info("Mystery - qualify_always")
        self.player.mystery_awards[0]["q"] = 1
        #{"ind":0,  "name":"1m_points",        "q_method":"always",                   "q":1, "odds":40,  "times_awarded":0}

    def qualify_toys_100_collected_1_ball(self, **kwargs):
        self.log.info("Mystery - qualify_toys_100_collected_1_ball")
        self.player.mystery_awards[1]["q"] = 1
        # {"ind":1,  "name":"bonus_multiplier", "q_method":"toys_100_collected_1_ball","q":0, "odds":125, "times_awarded":0}

    def qualify_unclaimed_add_a_ball(self, **kwargs):
        self.log.info("Mystery - qualify_unclaimed_add_a_ball")
        self.player.mystery_awards[2]["q"] = 1
        #{"ind":2,  "name":"toy_upgrade",      "q_method":"unclaimed_add_a_ball",     "q":0, "odds":125, "times_awarded":0}

    def qualify_toys_none_1min(self, **kwargs):
        self.log.info("Mystery - qualify_toys_none_1min")
        self.player.mystery_awards[3]["q"] = 1
        #{"ind":3,  "name":"toy_25",           "q_method":"toys_none_1min",           "q":1, "odds":125, "times_awarded":0}
        
    def qualify_raise_multiplier_4x(self, **kwargs):
        self.log.info("Mystery - qualify_raise_multiplier_4x")
        self.player.mystery_awards[4]["q"] = 1
        #{"ind":4,  "name":"collect_bonus",      "q_method":"raise_multiplier_4x",      "q":0, "odds":50,  "times_awarded":0}

    def qualify_ball_saved_x5(self, **kwargs):
        self.log.info("Mystery - qualify_ball_saved_x5")
        self.player.mystery_awards[5]["q"] = 1
        #{"ind":5,  "name":"5m_points",        "q_method":"ball_save_5x",             "q":0, "odds":125, "times_awarded":0}
               
    def qualify_wizard_mode_played(self, **kwargs):
        self.log.info("Mystery - qualify_wizard_mode_played")
        self.player.mystery_awards[6]["q"] = 1
        #{"ind":6,  "name":"10m_points",       "q_method":"played_wiz",               "q":0, "odds":30,  "times_awarded":0}
        
    def qualify_scored_under_1m(self, **kwargs):
        self.log.info("Mystery - qualify_scored_under_1m")
        self.player.mystery_awards[7]["q"] = 1
        #{"ind":7,  "name":"30s_ball_save",    "q_method":"scored_under_1m",             "q":1, "odds":100, "times_awarded":0}
    
    def qualify_santas_4_of_5(self, **kwargs):
        self.log.info("Mystery - qualify_santas_4_of_5")
        self.player.mystery_awards[8]["q"] = 1
        #{"ind":8,  "name":"spots_santa",      "q_method":"4_of_5_santas",            "q":0, "odds":100, "times_awarded":0}
    
    def qualify_toys_none_previous_ball(self, **kwargs):
        self.log.info("Mystery - qualify_toys_none_previous_ball")
        self.player.mystery_awards[9]["q"] = 1
        # {"ind":9,  "name":"toys_at_max",      "q_method":"toys_none_previous_ball",             "q":1, "odds":50,  "times_awarded":0}
    
    def qualify_gate_hit_5s(self, **kwargs):
        self.log.info("Mystery - qualify_gate_hit_5s")
        self.player.mystery_awards[10]["q"] = 1
        #{"ind":10, "name":"clear_bugs",       "q_method":"gate_hit_within_5s",       "q":0, "odds":50,  "times_awarded":0}
    
    def qualify_one_mode_remaining(self, **kwargs):
        self.log.info("Mystery - qualify_one_mode_remaining")        
        self.player.mystery_awards[11]["q"] = 1
        #{"ind":11, "name":"spot_mode",        "q_method":"1_mode_left",              "q":0, "odds":10,  "times_awarded":0}

    def qualify_mystery_none_5min(self, **kwargs):                
        self.log.info("Mystery - qualify_mystery_none_5min")
        self.player.mystery_awards[12]["q"] = 1
        #{"ind":12, "name":"extra_ball",       "q_method":"5_minutes_no_mystery",     "q":0, "odds":5,   "times_awarded":0}

    def qualify_ball_3_1min(self, **kwargs):
        self.log.info("Mystery - qualify_ball_3_1min")
        self.player.mystery_awards[13]["q"] = 1
        #{"ind":13, "name":"special",          "q_method":"ball_3_1minute",           "q":0, "odds":1,   "times_awarded":0}

    def qualify_only_once(self, **kwargs):
        if self.player.mystery_awards[14]["times_awarded"] == 0:
            self.log.info("Mystery - only_once")
            self.player.mystery_awards[14]["q"] = 1
            #14 {"name":"gate_keeper",      "q_method":"only_once",               "q":1, "odds":50,  "times_awarded":0}

    def qualify_third_5ths_mystery(self, **kwargs):
        self.log.info("Mystery - third_5ths_mystery")
        self.player.mystery_awards[15]["q"] = 1
        #15 {"name":"video_mode",       "q_method":"third_5ths_mystery",      "q":0, "odds":4,   "times_awarded":0}

    def qualify_graveyard_sneakin(self, **kwargs):
        self.log.info("Mystery - graveyard_sneakin")
        self.player.mystery_awards[16]["q"] = 1        
        #16 {"name":"10_points",        "q_method":"graveyard_sneakin",       "q":0, "odds":10,  "times_awarded":0}
                
    def qualify_add_time(self, **kwargs):
        self.log.info("Mystery - qualify_add_time")
        self.player.mystery_awards[17]["q"] = 1
        #{"ind":17, "name":"extend_10s",       "q_method":"timer_running",            "q":0, "odds":0,   "times_awarded":0}

    def qualify_add_a_ball(self, **kwargs):
        self.log.info("Mystery - qualify_add_a_ball")    
        self.player.mystery_awards[18]["q"] = 1
        #{"ind":18, "name":"add_a_ball",       "q_method":"mb_running",               "q":0, "odds":0,   "times_awarded":0}
        


    def setup_rewards(self):
        self.log.info( 'Mystery - setup rewards')
        self.player.mystery_state = 3
        self.player.mystery_selectable = 0
        # TODO set the 4 choices based on stats
        self.player.mystery_choices[0] = 4  #  random.randint(0,15)
        self.player.mystery_choices[1] = 14 #  random.randint(0,15)
        self.player.mystery_choices[2] = random.randint(0,15)
        self.player.mystery_choices[3] = random.randint(0,15)
        self.player.mystery_current_selection = random.randint(0,3)
        self.start_ticker()
        self.machine.events.post('char_pause_and_hide')
        self.machine.events.post('doors_pause_and_hide')
        self.machine.events.post('OB_pause_and_hide')
        self.machine.events.post('show_mystery_award_background')
        self.machine.events.post('show_box'+str(self.player.mystery_choices[self.player.mystery_current_selection]+1))


    def start_ticker(self):
        if self.player.mystery_state == 3:
            self.player.mystery_selectable = 1
            self.log.info( "Mystery - Award selection countdown started")
            self.player.mystery_state = 4
            self.ticks = self.player.mystery_base_ticks
            self.player.choose_gift_timeleft = int(self.ticks/2)            
            self.delay.add(name="mystery_award_selection_ticker", ms=500, callback=self.ticker)


    def ticker(self):
        self.log.info( "Mystery - Award selection countdown - 500ms ticks " +str(self.ticks))
        self.player.choose_gift_timeleft = int(self.ticks/2)
        self.ticks -= 1
        if self.ticks <= 0:
            self.accept_selection()
        else:
            self.delay.add(name="mystery_award_selection_ticker", ms=500, callback=self.ticker)


    def flippers_held(self):
        if self.ticks > 1:
            self.log.info( 'Mystery - both flippers held')
            self.player.mystery_selectable = 1
            self.ticks = 1


    def flipper_left(self, **kwargs):
        if self.player.mystery_state == 4:    
            if self.player.mystery_selectable == 1:
                #both flippers, select it
                if self.machine.switches['flipperlwr_sw'].state == 1:
                    self.flippers_held()
                else:
                    self.log.info( 'Mystery - rotate left')
                    self.player.mystery_previous_selection = self.player.mystery_current_selection
                    self.player.mystery_current_selection -= 1
                    if self.player.mystery_current_selection < 0:
                        self.player.mystery_current_selection = 3
                    self.machine.events.post('remove_box'+str(self.player.mystery_choices[self.player.mystery_previous_selection]+1))
                    self.machine.events.post('show_box'+str(self.player.mystery_choices[self.player.mystery_current_selection]+1))
                    self.machine.events.post('mystery_swap_sfx')
            elif self.player.mystery_state == 4:
                self.log.info( 'Mystery - left')


    def flipper_right(self, **kwargs):
        if self.player.mystery_state == 4:        
            if self.player.mystery_selectable == 1:
                #both flippers, select it                
                if self.machine.switches['flipperlwl_sw'].state == 1:
                    self.flippers_held()
                else:            	
                    self.log.info( 'Mystery - rotate right')
                    self.player.mystery_previous_selection = self.player.mystery_current_selection            
                    self.player.mystery_current_selection += 1
                    if self.player.mystery_current_selection > 3:
                        self.player.mystery_current_selection = 0
                    self.machine.events.post('remove_box'+str(self.player.mystery_choices[self.player.mystery_previous_selection]+1))
                    self.machine.events.post('show_box'+str(self.player.mystery_choices[self.player.mystery_current_selection]+1))
                    self.machine.events.post('mystery_swap_sfx')            
            elif self.player.mystery_state == 4:
                self.log.info( 'Mystery - right')


    def accept_selection(self):
        self.log.info( "Mystery - Award selection made")
        indx = self.player.mystery_choices[self.player.mystery_current_selection]        
        self.delay.remove("mystery_award_selection_ticker")
        self.log.info( "Mystery - Selected "+ str(self.player.mystery_current_selection))
        self.log.info( "Mystery - Award is "+ self.player.mystery_awards[indx]["name"])
        self.mystery_award_selected(value=self.player.mystery_awards[indx]["name"])
        self.machine.events.post("mystery_award_selected")
        self.boxtoshow = 'show_box'+str(indx+1)+'_selected'
        self.log.info(self.boxtoshow)
        self.machine.events.post('remove_box'+str(indx+1))                
        self.machine.events.post(self.boxtoshow)        
        self.machine.events.post('remove_mystery_award_background')                        
        self.player.mystery_state = 0
        self.player.mystery_ball_in_saucer = 0
        self.delay.add(name="restore_screen_timer", ms=4000, callback=self.show_screens)



    def mystery_award_selected(self, value="", **kwargs):
        if value == "1m_points":
            descrip ="1,000,000"
            self.player.score += 1000000

        if value == "bonus_multiplier":
            descrip = "Bonus Multiplier"
            if self.player.bonus_multiplier < 12:
                self.player.bonus_multiplier = self.player.bonus_multiplier +1
                self.machine.events.post('bonus_multiplier_increased',value=self.player.bonus_multiplier )
            elif self.player.bonus_multiplier == 12:
                self.player["score"] += (1000000)
                self.machine.events.post('jack_spelled_12')

        if value == "toy_upgrade":
            self.machine.events.post("toy_pops_upgrade", value="1")                                    
            descrip = "TOYS UPGRADE"
            
        if value == "toy_25":
            self.player.toys_collected += 25
            descrip = "+ 25 TOYS"
            
        if value == "collect_bonus":
            descrip = "COLLECT BONUS"
            self.player.collecting_bonus = 1
            self.machine.events.post("collect_bonus")                                        

        if value == "5m_points":
            self.player["score"] += (5000000)
            descrip = "5,000,000"                            

        if value == "10m_points":
            self.player["score"] += (10000000)
            descrip = "10,000,000"

        if value == "10_points":
            self.player["score"] += (10)
            descrip = "10"

        if value == "toys_at_max":
            descrip = "TOYS AT MAX"
            self.machine.events.post("toy_pops_max")                            
            
        if value == "spots_santa":
            descrip = "SANTA COMPLETE"
            self.machine.events.post("spot_a_santa")
            
        if value == "30s_ball_save":
            descrip = "30s Ball Save"
            self.machine.events.post("start_ball_save_30s")
                        
        if value == "clear_bugs":
            descrip = "Clear Bugs"
            self.machine.events.post("clear_bugs")

        if value == "special":
            descrip = "special"
            self.machine.events.post("award_special")            

        if value == "spot_mode":
            descrip = "MODE SPOTTED"

        if value == "extra_ball":
            descrip = "Extra Ball"
            self.machine.events.post("award_EB_start")            

        if value == "gate_keeper":
            descrip = "Gate Keeper"
            self.machine.events.post("gate_keeper_MB_start")

        if value == "video_mode":
            descrip = "Video Mode"

        if value == "extend_10s":
            descrip = "10s Extension"
            #TODO: char, door, OR oogie?
            self.machine.events.post("extend_char_time", time=10)
            self.machine.events.post("extend_oogie_time", time=10)
            self.machine.events.post("extend_door_time", time=10)

        if value == "add_a_ball":
            descrip = "Add-a-Ball"

        self.player.mystery_award_description = descrip
        


    def mystery_ready(self, **kwargs):
        self.log.info( 'Mystery - reward ready')
        self.player.mystery_state = 1
        self.light_grave()
        self.machine.coils['DropDown'].pulse()
        self.machine.events.post('mystery_award_ready')
        self.player.mystery_rewards_lit += 1
        if self.player.mystery_rewards_lit == 3 or (self.player.mystery_rewards_lit-3)%5 == 0:
            self.log.info('Mystery - video mode qualified')
            self.machine.events.post('third_5ths_mystery')
        self.delay.add(name="restore_screen_timer", ms=4000, callback=self.show_screens)
        self.machine.events.post('char_pause_and_hide') 
        self.machine.events.post("doors_pause_and_hide")
        self.machine.events.post('OB_pause_and_hide')         


    def show_screens(self, **kwargs):
        if self.player.mystery_state < 2:
            self.log.info( "4 seconds passed, show " )
            self.machine.events.post("char_resume_and_show")
            self.machine.events.post("doors_resume_and_show")
            self.machine.events.post("OB_resume_and_show")
            self.machine.events.post("mystery_done_with_ball")        


    def mystery_hit(self, **kwargs):
        if self.player.add_a_ball_state == 0:
            if self.player.mystery_state == 0:
                self.machine.events.post('mystery_sfx')                    
                #mystery_light
                if self.player.mystery_show_handles[0] != 0:
                    self.player.mystery_show_handles[0].stop()
                    self.player.mystery_show_handles[0] = 0
                self.player.mystery_target_hits += 1
                self.log.info( "Mystery - Mystery hit, " + str(self.player.mystery_target_hits) + " / " + str(self.player.mystery_target_hits_needed) + " hits needed")
                if self.player.mystery_target_hits == self.player.mystery_target_hits_needed:
                    self.player.mystery_target_hits = 0
                    self.player.mystery_target_hits_needed += 1
                    if self.player.mystery_target_hits_needed > 5:
                        self.player.mystery_target_hits_needed = 5
                    self.mystery_ready()
                else:
                    led = "rgb_mystery_rect"
                    script_name = "sc_green_flash"
                    speed = 8.0 + self.player.mystery_target_hits * 4.0
                    self.player.mystery_show_handles[0] = self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=speed, loops=-1)
            else:
                self.log.info( "Mystery - Mystery hit, reward is ready - TODO pts?")
                self.machine.events.post('mystery_ready_sfx')                                    
        else:
            self.log.info( "Mystery - Mystery hit during add a ball")
            

    def light_grave(self):          
        #light the grave target
        self.machine.events.post('arrow_change', led_num=6, script_name="green", mode_name="mystery_reward", action="add")
        self.player.mystery_ball_in_saucer = 1


    def gravestone_hit(self, **kwargs):
        self.log.info( 'Mystery - grave hit - do nothing, - maybe say - ring the bell!')


    def jack_saucer_hit(self, **kwargs):
        if self.player.add_a_ball_state == 0:
            if self.player.mystery_state == 1:
                self.log.info( 'Mystery - jack saucer hit')
                self.machine.events.post("mystery_award_choose")
                self.player.mystery_state = 2
                self.machine.events.post('arrow_change', led_num=6, script_name="green", mode_name="mystery_reward", action="remove")
                led = "rgb_grave_arrow"
                script_name = "sc_white_flash"
                self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=8.0, loops=3)			
                self.setup_rewards()
       

    def mode_stop(self, **kwargs):
        self.log.info( 'Mystery mode_stop')
        if self.player.mystery_show_handles[0] != 0:
            self.player.mystery_show_handles[0].stop()
            self.player.mystery_show_handles[0] = 0
        led = "rgb_mystery_rect"
        script_name = "sc_off"		
        self.machine.shows[script_name].play(show_tokens=dict(leds=led), speed=6.0, loops=1)		
        self.machine.events.post('arrow_change', led_num=6, script_name="green", mode_name="mystery_reward", action="remove")
