from mpf.core.mode import Mode
from mpf.core.delays import DelayManager


# Character Wizard Mode - "Deliver the Presents"                                                                                                                         Page 22
# 
# Brief Description
# You have a health gauge in this mode. Certain shots will be lit to score points, 
# other shots will be lit to decrease health. The more good shots you make, the more
# bad shots will light up. You have unlimited balls in this mode, although you lose 
# toys every time a ball drains. The mode ends if you run out of toys or health, draining
# all balls, then resuming normal gameplay for the current player.
# 
# Scenario
# Jack is ready to deliver his toys for Christmas! He has to be careful though because 
# it turns out his ghoulish toys may not be a welcome sight...
# 
# Details
# This multiball mode always keeps four balls in play at all times. 
# You also get a health gauge which doesn't show any numbers but has five (adjustable) points on it
# Your toys count will always be shown. 
# At the start of this mode, three major shots will be lit green. 
# Shooting a green shot does multiple things: 
# - scores the wizard value of 4,000,000
# - unlights the shot 
# - lights a different shot green
# - decreases your toys count by 1
# Draining a ball - You lose 10% or 10 toys (whichever is greater)
# Every time you make three green shots one of the shots still unlit will light red. 
# Shooting a red shot will damage the sleigh and decrease your health. 
# If the sleigh runs out of energy, or if you run out of toys, the flippers will die, 
# the balls will drain, and the wizard mode will end. 
# Each red shot presently on the field also increases a multiplier for the wizard value up to a potential 
# maximum of 8x. 
# If a red shot is selected to become green after making a green shot, the green shot you just made 
# will become red in its place. Every 12 major shots, regardless of if they're red or green 
# (just so long as they're lit), will randomly light one of the major shots as a flashing white super shot, 
# regardless of if that shot is already lit red or green, and it will stay this way for 10 seconds. 
# Hitting a flashing white super shot will score double the wizard value on top of the wizard multiplier, 
# doesn't decrease your toys count, and also restores one point of health,
# returning the shot to its previous state, either unlit, green, or red, which it will 
# also return to if the 10 second counter expires. If you make another 12 lit shots while a
# flashing white shot is going, it simply adds 10 seconds to the timer for the flashing white shot 
# already going. Ultimately, if you keep the mode going long enough,
# three major shots will be green and the remaining seven will be red. If you get to 
# this state the animation on the display will also change to show things getting more
# desperate and a fifth ball will be added to the mix. It's important to note that all 
# methods for increasing your toy count (such as the pop bumpers) will not do so while
# this mode is running.
# 
# Start mode:  all character complete, down to single ball, flash pops and zero, get the ball to Zero to start
#
#
# Scoring
# Base Wizard Value                  4,000,000
# Maximum Wizard Value               64,000,000 (8x W izard Multiplier + Super Shot)
# Red Major Shots                    500,000 (ALSO affected by the Wizard Multiplier!)
# 
# Lighting
# Major shots will show flashing green triangles if they'll score the wizard value 
# and will be solid red (not flashing) if they'll damage the sleigh. The super shot will flash
# a white triangle and circle.
# 
# Difficulty Adjustments
# Very Easy   Sleigh has 7 Health Points,  8 Major Shots Lights Super Shot for 15 Seconds, 3 Balls in Play by Default
# Easy        Sleigh has 6 Health Points, 10 Major Shots Lights Super Shot for 12 Seconds, 3 Balls in Play by Default
# Normal      Sleigh has 5 Health Points, 12 Major Shots Lights Super Shot for 10 Seconds, 4 Balls in Play by Default
# Hard        Sleigh has 5 Health Points, 14 Major Shots Lights Super Shot for 10 Seconds, 4 Balls in Play by Default
# Very Hard   Sleigh has 4 Health Points, 16 Major Shots Lights Super Shot for 8 Seconds, 5 Balls in Play by Default

class Char_Wizard(Mode):

    def mode_init(self):
        self.log.info('char_Wizard mode_init')

    def mode_start(self, **kwargs):
        self.log.info('char_Wizard mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.ticks = 90  #90 = 45 seconds
        if self.player.char_wizard_started == 0:
            #once per game only
            self.player.char_wizard_started = 1
            self.player.char_wizard_running = 0
        self.add_mode_event_handler('sw_mystery', self.wizard_stop)
        self.wizard_start()
        
    def wizard_start(self):
        self.log.info("char_Wizard start")
        if (self.player.char_wizard_running == 0):
            self.player.char_wizard_running = 1
            self.machine.events.post("char_wizard_music_start")

    def wizard_stop(self, **kwargs):
        if self.player.char_wizard_running == 1:
            self.player.char_wizard_running = 2
            self.machine.events.post('char_wizard_music_stop')
            self.log.info("char_wizard over")
            self.machine.events.post('char_mode_stopped', char_state="complete", char_mode="Wizard")            
            self.machine.events.post('enable_combos')

    def mode_stop(self, **kwargs):
        self.log.info('char_wizard mode_stop')        
