from mpf.core.mode import Mode

# Ultimate Wizard Mode - "Christmas Time in Halloween Town" Multiball Frenzy                                                                                           Page 38
# 
# Brief Description
# 5-ball multiball frenzy where every switch is worth the same number of points, except each time you hit a switch you haven't yet hit since starting the mode, the point
# value goes up.
# 
# Scenario
# Well, you've come to the end of a long journey. As such, it's time to celebrate with Christmas with everyone in Halloween Town!
# 
# Details
# This is a 5-ball multiball frenzy mode. The base value for all switches starts at 100,000, but increases by 25,000 each time you hit a switch you haven't yet hit during
# the mode. This includes switches you normally wouldn't want to hit such as the drain, outlanes, etc. A 2x multiplier is applied to all frenzy scores once you've hit at
# least 50% of all switches, a 3x multiplier once you've hit 85% of all switches, a 4x multiplier once you've hit all but two switches, a 5x multiplier for all but one switch,
# and a 10x multiplier for managing to hit every switch in the game at least once!
# 
# Scoring
# Base Frenzy Value                                    100,000
# Frenzy Increment for each Unique Switch Hit          25,000
# 
# Frenzy Multipliers
# Less than 50% of All Switches = 1x
# 50% of All Switches = 2x
# 85% of All Switches = 3x
# All But 2 Switches = 4x
# All But 1 Switch = 5x
# All Switches Hit at least Once = 10x
# 
# Lighting
# The lighting goes nuts in this mode for obvious reasons: It doesn't really matter what you hit! However, the display will actually tell you what percentage of the
# switches you've hit at least once until there's only 5 left. At which point, it will count them down individually. The display never actually tells you which switches you
# still have left, since part of the challenge of this mode is keeping a mental record of what tricky switches you've gotten, since there's little else to do other than shoot
# everything!
# 
# Difficulty Adjustments
# Very Easy          6-Ball Multiball, 40 Seconds of Ball Saver at Start
# Easy               5-Ball Multiball, 35 Seconds of Ball Saver at Start
# Normal             5-Ball Multiball, 30 Seconds of Ball Saver at Start
# Hard               5-Ball Multiball, 25 Seconds of Ball Saver at Start
# Very Hard          4-Ball Multiball, 20 Seconds of Ball Saver at Start

class Ultimate_Wizard(Mode):

    def mode_init(self):
        self.log.info('Ultimate_Wizard mode_init')

    def mode_start(self, **kwargs):
        self.log.info('Ultimate_Wizard mode_start')

    def mode_stop(self, **kwargs):
        self.log.info('Ultimate_Wizard mode_stop')

