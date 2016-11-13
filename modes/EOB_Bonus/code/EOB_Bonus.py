from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

# EOB_Bonus Awards                                                                                                                                                         Page 10
# End of Ball Bonus
# 
# At the end of each ball you get bonus points based on the following cumulative values tracked throughout the game:
#
# Survival 
# switches - 10 pts
# 1 Mode Completed = 2,500 Bonus
# 1 Tombstone = 1,000 Bonus
# 1 Stitch (spinner spins) = 100 Bonus 
# 1 Toy = 250 Bonus

# Bonus Multiplier Held on Last Ball = 100,000 Bonus
# 
# There is also a bonus multiplier which is raised by spelling JACK. 
# It can be raised up to a maximum of 12x and can also be held between balls by making a 4x
# combo or from a potential mystery award. Because the bonus does not decrement at any point 
# in the game, if your bonus is held when you lose your last ball you
# simply get a special awarded factored into your multiplied bonus, as opposed to getting your 
# bonus twice as would be the case in some games.

class EOB_Bonus(Mode):

    def mode_start(self, **kwargs):
        if self.machine.game.tilted:
            self.bonus_score = 0        
            self.stop()
        else:
            self.bonus_score = 0
            self.bonus_start()

    def bonus_start(self):
        self.machine.events.post("doors_pause_and_hide")
        self.machine.events.post('char_pause_and_hide')
        self.machine.events.post("ob_pause_and_hide")
        self.machine.events.post("char_remove_all")           
        self.machine.events.post("char_hide_timer")
        if self.player.collecting_bonus == 1:
            self.machine.events.post('bonus_start_ingame')            
        else:
            self.machine.events.post('bonus_start')
        self.delay.add(name='bonus', ms=1000, callback=self.bonus_survival)

        
    def bonus_survival(self):
        self.bonus_score += self.player['graves'] * 1000
        self.bonus_score += self.player['modes_played'] * 2500
        self.bonus_score += self.player['switches_hit'] * 10
        self.player['base_bonus'] = self.bonus_score
        self.machine.events.post('bonus_survival')
        self.delay.add(name='bonus', ms=1000, callback=self.total_stitches)

        
    def total_stitches(self):
        self.machine.events.post('bonus_stitches')
        self.bonus_score += self.player['sally_spins'] * 100
        self.delay.add(name='bonus', ms=600, callback=self.total_toys)


    def total_toys(self):
        self.machine.events.post('bonus_toys')
        self.bonus_score += self.player['toys_collected'] * 250
        self.delay.add(name='bonus', ms=600, callback=self.do_multiplier)


    def do_multiplier(self):
        if self.player['bonus_multiplier'] > 1:
            self.machine.events.post('bonus_multiplier')
            self.delay.add(name='bonus', ms=600, callback=self.total_bonus)
        else:
            self.total_bonus()


    def total_bonus(self):
        self.log.info('EOB - total')
        self.bonus_score *= self.player['bonus_multiplier']
        self.player['score'] += self.bonus_score
        self.player['total_bonus_points'] = self.bonus_score
        self.machine.events.post('bonus_total')
        self.delay.add(name='bonus_clear', ms=2000, callback=self.clear_screen)
        self.delay.add(name='bonus', ms=2100, callback=self.end_bonus)


    def clear_screen(self):
        self.log.info('EOB - clear')    	
        self.machine.events.post('clear_bonus_screen')


    def end_bonus(self):
        self.log.info('EOB - stopping')    	    	
        if self.player.collecting_bonus == 0:
            self.player['bonus_multiplier'] = 0
        self.player.collecting_bonus = 0
        self.stop()
