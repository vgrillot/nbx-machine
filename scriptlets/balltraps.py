# balltraps Scriptlet for Nightmare
#eject balls in soup and mayor if there for more than 1 sec
#only temp - should be rules based

from mpf.core.scriptlet import Scriptlet
#from mpf.core.timing import Timer

from mpf.core.delays import DelayManager


class Balltraps(Scriptlet):

    def on_load(self):
        self.delay = DelayManager(self.machine.delayRegistry)
        self.balls_locked = 0
        self.machine.switch_controller.add_switch_handler(
            'soupVUK_opt', self.spitout, ms=1000)
        self.machine.switch_controller.add_switch_handler(
            'mayor_sw', self.spitout2, ms=2000)
        self.machine.events.add_handler('collecting_balls', self.drain_the_tub)
        self.machine.events.add_handler('player_add_success', self.added_player)        
        self.machine.events.add_handler('ball_started', self.added_player)                


    def added_player(self, num=1, ball=0, player=0, **kwargs):
        if ball == 1 and player == 1:
            self.machine.events.post('player_added_1')
        else:
            if num > 1: 
                self.machine.events.post('player_added_'+str(num))

    def spitout(self):
         self.log.info("Ball in soup for more than 1 second - eject")
         self.machine.coils['soupVUK'].pulse()

    def spitout2(self):
        self.log.info("Ball in mayor for more than 2 seconds - eject")
        self.machine.coils['mayorkickout'].pulse(10)


    def drain_the_tub(self):
        self.count_balls_in_bathtub()
        if self.balls_locked > 0:
            self.drain_tub()
            self.delay.add(name='drain_bathtub', ms=2000, callback=self.drain_the_tub)
        else: 
            self.log.info('balltrap - tub is empty')        	

    def drain_tub(self):
        self.log.info('balltrap - drain tub')
        self.machine.coils['bathtubdrain'].pulse(milliseconds=50)

        
    def count_balls_in_bathtub(self, **kwargs):
        self.balls_locked = 0
        self.log.info('balltrap - count balls in tub')
        if self.machine.switch_controller.is_active('tublock1_opt'):
            self.balls_locked += 1
        if self.machine.switch_controller.is_active('tublock2_opt'):
            self.balls_locked += 1
        if self.machine.switch_controller.is_active('tublock3_opt'):
            self.balls_locked += 1
        self.log.info('LSB - balls in tub = ' + str(self.balls_locked))
