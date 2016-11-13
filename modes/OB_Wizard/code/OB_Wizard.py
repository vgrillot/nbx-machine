from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# Oogie Boogie Wizard Mode - "Mega Oogie Showdown"                                                                                                                Page 37
# 
# Brief Description
# 5-ball multiball where Jack and Mega Oogie both have health bars. 
# You must make combos to deplete Mega Oogie's health before he has enough time to pummel
# Jack into the ground!
# 
# Scenario
# Through an unknown power, Oogie Boogie has managed to revive himself, growing to many times 
# his normal size as he prepares to smash Halloween Town to rubble! 
# Jack must do battle with Mega Oogie and only one of them will come out standing!
# 
# Details
# This wizard mode has some similarities to the wizard mode on Tales of the Arabian Nights. 
# When the mode begins two health bars will show up on the display. 
# One for Mega Oogie, the other for Jack. Every 4 to 12 seconds, randomly selected for each attack, 
# Mega Oogie will attack Jack and damage his health. 
# While this mode is running, all five balls will be in play and if one drains the player immediately gets it back. 
# The idea of this mode is to score combos. 
# Combos are normally disabled during multiballs because of how high they could get during multiballs. 
# To that end, normal combo awards are not awarded during this wizard mode. 
# The greater the combo you make, the more damage you do. A 10-hit combo, which is the maximum possible, 
# will hurt Mega Oogie for almost 1/2 of his health, while a 2-hit combo will hardly scratch him. 
# Jack can survive for approximately 1 1/2 minutes, but random luck could alter this a little. 
# Jack and Mega Oogie both have 120 HP. Each time Jack is hit he takes 10 HP damage. 
# A single major shot, starting a combo, damages Mega Oogie for 1 HP. When you obtain a 2x combo you do an additional 2HP
# damage. Getting up to 3x does an additional 3 HP damage. Thus if you manage to max out at a 10x combo, 
# you will have done a total of 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10 HP of damage, which is 55 HP in total. 
# Every point of damage you do scores a large number of points and winning the battle scores an additional
# 100,000,000. The gate also stays closed during this mode and each hit to a standup target on the gate counts as 1 HP 
# of damage to Mega Oogie.
# 
# Scoring
# Every 1 HP Damage to Mega Oogie                        1,000,000
# Win the Battle                                         100,000,000
# 
# Lighting
# Combo lighting works as expected, except all major shots flash when no combo is ready to indicate 
# that you can start a combo. The lights in front of the gate flash green and rapidly flash white when hit.
# 
# Difficulty Adjustments
# Very Easy          Jack has 140 HP, Mega Oogie has 100 HP
# Easy               Jack has 130 HP, Mega Oogie has 110 HP
# Normal             Jack has 120 HP, Mega Oogie has 120 HP
# Hard               Jack has 110 HP, Mega Oogie has 130 HP
# Very Hard          Jack has 100 HP, Mega Oogie has 140 HP


class OB_Wizard(Mode):

    def mode_init(self):
        self.log.info('OB_Wizard mode_init')

    def mode_start(self, **kwargs):
        self.log.info('OB_Wizard mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.OB_mode_6_started == 0:
            #once per game only
            self.player.OB_mode_6_started = 1
            self.player.OB_mode_6_running = 0
        self.ticks = 20  #TODO
        self.add_mode_event_handler('sw_oogietarget2', self.bug2)
        self.targets_list = [
            {"led":"rgb_bug_2", "state":"unlit"}
            ]
#        self.blueflash = []
#        self.blueflash.append({'color': '000033', 'time': 200, 'tocks': 10})
#        self.blueflash.append({'color': '000099', 'time': 200, 'tocks': 10})
#        self.blueflash.append({'color': '0000ff', 'time': 200, 'tocks': 10})
#        self.blueflash.append({'color': '000099', 'time': 200, 'tocks': 10})
        self.start_battle()
        
    def bug2(self, **kwargs):
        self.log.info("bug 2 called in OB_Wizard")
        if self.player:
            if (self.player.OB_mode_6_running == 1):
                self.hit_target(0)
        else:
            self.log.info("call to a mode without a player object?")


    def hit_target(self, x):
        nb = random.randint(1,6)
        self.machine.events.post('bug_splat_'+str(nb))
        self.player["score"] += (22220)
        self.turn_off_bug_light(x)
        self.set_bug_light(x)


    def end_battle(self):
        if (self.player.OB_mode_6_running == 1):
            self.player.OB_mode_6_running = 2
            self.machine.events.post('OB_Unravel_music_stop')
            self.log.info("OB mode 6 over")
            self.turn_off_bug_light(0)
            self.delay.remove('OB_mode_6_ticker')  
            self.machine.events.post('ob_mode_stopped', ob_state="complete", ob_mode="7")

    def start_battle(self):
        self.log.info("In The Oogie hole - start the battle?")
        if (self.player.OB_mode_6_running == 0):
            self.set_bug_light_state(0, 'blue')
            self.set_bug_light(0)
            self.player.OB_mode_6_running = 1
            self.machine.events.post('OB_Unravel_music_start')
            self.delay.add(name='OB_mode_6_ticker', ms=500, callback=self.ticker)
            self.log.info("60 seconds to hide Santa")

    def ticker(self):
        self.log.info("500ms ticks "+str(self.ticks))
        self.machine.events.post('unravel_OB_countdown', value=int(self.ticks))
        self.ticks -= 0.5;
        if self.ticks <= 0:
            self.end_battle()
        else:
            self.delay.add(name='OB_mode_6_ticker', ms=500, callback=self.ticker)


    def set_bug_light_state(self, x, state):
        self.targets_list[x]["state"] = state

    def set_bug_light(self, x):
        led = self.targets_list[x]["led"]
        state = self.targets_list[x]["state"]
        if state == 'blue':
            #self.machine.light_controller.run_script(leds=led,script=self.blueflash ,priority=50, tocks_per_sec=80, key=led+"_"+state, blend=True)
            self.machine.shows["sc_blue_flash"].play(show_tokens=dict(leds=led), speed=8.0, loops=-1)			

    def turn_off_bug_light(self, x):
       self.log.info("turn off bug light")
       led = self.targets_list[x]["led"]
       state = self.targets_list[x]["state"]
       #self.machine.light_controller.stop_script(led+"_"+state)
       #self.machine.leds[led].color([10 ,10 ,10 ], 0, 0, 0, 1, 1) 
       self.machine.shows["sc_off"].play(show_tokens=dict(leds=led), speed=8.0, loops=1)			


    def mode_stop(self, **kwargs):
        self.log.info('OB_Wizard mode_stop')
        self.end_battle()

