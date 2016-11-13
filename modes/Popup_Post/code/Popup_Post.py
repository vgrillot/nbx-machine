from mpf.core.mode import Mode

from mpf.core.delays import DelayManager

#pop up post

class Popup_Post(Mode):

    def mode_init(self):
        self.log.info('Pop up post mode_init')

        
    def mode_start(self, **kwargs):
        self.log.info('Pop up post mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        self.player.popuppost_state = 'not allowed'
        self.add_mode_event_handler('popuppost_enable_up', self.enable_up)        
        self.add_mode_event_handler('popuppost_disable_up', self.disable_up)        
        self.add_mode_event_handler('popuppost_up_3s', self.up_3s)
        self.add_mode_event_handler('popuppost_up', self.up)        
        self.add_mode_event_handler('popuppost_down', self.down)
        self.add_mode_event_handler('sw_leftorbitlower', self.left_orbit)
        self.add_mode_event_handler('sw_leftloop', self.left_loop)        
        self.add_mode_event_handler('sw_rorbitupper', self.right_orbit)


    def enable_up(self, **kwargs):
        self.player.popuppost_state = 'allowed'

        
    def disable_up(self, **kwargs):
        self.player.popuppost_state = 'not allowed'

        
    def left_orbit(self, **kwargs):
        if self.player.popuppost_state == 'allowed':
            self.up_3s()

            
    def left_loop(self, **kwargs):
        if self.player.popuppost_state == 'allowed':
            self.up_3s()
            
            
    def right_orbit(self, **kwargs):
        if self.player.popuppost_state == 'allowed':
            self.up_3s()

            
    def up_3s(self, **kwargs):
        self.log.info("Post up for 3s")
        self.up()
        self.delay.remove('popuppost_timeout')       
        self.delay.add(name='popuppost_timeout', ms=3000, callback=self.down)

        
    def up(self, **kwargs):
        self.log.info("post up")
        self.machine.coils['dissappearingpost'].enable()

        
    def down(self, **kwargs):
        self.log.info("post down")
        self.machine.coils['dissappearingpost'].disable()

        
    def mode_stop(self, **kwargs):
        self.log.info('Popuppost mode_stop')
        self.delay.remove('popuppost_timeout')
        self.down()
