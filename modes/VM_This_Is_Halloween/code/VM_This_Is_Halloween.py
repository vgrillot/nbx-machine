from mpf.core.mode import Mode
# This is Halloween - Video Mode
#
# This video mode plays a lot like DDR or Guitar Hero. 
# The screen will show two rows of scrolling flipper buttons on the sides with 
# animation from the movie in the middle while playing a clip from "This is Halloween". 
# There are several clips which can be selected at random. 
# Each clip has timings in place for the buttons, but the buttons are different every time you play, 
# thus just because you had to hit three left flippers, one right, then two more lefts one time you see a clip, 
# the next time you see it you may need to hit two right, then two left, then one right and then both together. 
# Each clip should be around 16 seconds long (covers approximately 40 flipper hits based on how the song goes) 
# and you are awarded points based on your accuracy:
# 
# Display Effect   Margin of Error          Award
# Perfect!          0~39 ms                100,000 Points
# Excellent        40~59 ms                 75,000 Points
# Great            60~79 ms                 50,000 Points
# Good             80~99 ms                 25,000 Points
# OK             100~119 ms                 10,000 Points
# Poor           120~139 ms                  5,000 Points
# Bad            140~159 ms                  1,000 Points
# Miss              160+ ms                      0 Points
# 
# 
# There's also a 2,500,000 point award for making it through the song without failing. 
# You fail the song and end up ejected from the mode prematurely if you miss
# three times. You don't actually have to push a button for a miss as it will happen automatically. 
# Once a miss occurs you can't actually get another miss until the next
# note comes into the hit range as the flippers will be ignored beforehand.
# 
# One potential hurdle for making this video mode is there might be a delay between the audio, 
# video, and feedback from the flippers. This delay will have to be measured extremely accurately 
# and compensated for to ensure this video mode plays as best as it can.

# 16 seconds * 50 = 800 note 'slots' - 'window' will be several slots long
# 20 ms callback - generate events to scroll the images, increment the note list, turn off/on the left/right note 'windows'


class VM_This_Is_Halloween(Mode):

    def mode_init(self):
        self.log.info('VM_This_Is_Halloween mode_init')

    def mode_start(self, **kwargs):
        self.log.info('VM_This_Is_Halloween mode_start')

    def mode_stop(self, **kwargs):
        self.log.info('VM_This_Is_Halloween mode_stop')
