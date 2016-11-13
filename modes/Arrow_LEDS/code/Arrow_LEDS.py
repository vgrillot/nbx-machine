from mpf.core.mode import Mode
from mpf.core.delays import DelayManager


# Arrow_LEDS   


class Arrow_LEDS(Mode):

    def mode_init(self):
        self.log.info('Arrow_LEDS mode_init')

    def mode_start(self, **kwargs):
        self.log.info('Arrow_LEDS mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)

        self.arrows_ledlist = [
            "rgb_mayor_arrow",
            "rgb_lorbit_arrow",
            "rgb_lramp_arrow",
            "rgb_leftloop_arrow",
            "rgb_oogie_cw_arrow",
            "rgb_oogie_ccw_arrow",
            "rgb_grave_arrow",
            "rgb_rramp_arrow",
            "rgb_rorbit_arrow",
            "rgb_soup_arrow"
            ]
        self.player.arrows_show_handles = [0] * 10
        self.player.arrows_change = [0] * 10
        self.player.arrows_scripts_lists = [[] for i in range(10)]
        self.add_mode_event_handler('arrow_change', self.arrow_change)
        self.delay.add(name='update_arrows', ms=50, callback=self.update)


    def arrow_change(self, **kwargs):
        #led_num, script_name, mode_name, priority, action (add/remove)
        if 'led_num' in kwargs:
            x = kwargs['led_num']
            if x >= 0 and x < 10:
                if 'mode_name' in kwargs:
                    mode_name = kwargs['mode_name']
                else:
                    self.log.info("mode missing in arrow_change")
                if 'script_name' in kwargs:
                    script_name = kwargs['script_name']
                if 'action' in kwargs:
                    action = kwargs['action']
                if action == 'add':
                    #add to front of the list 
                    script_list = self.player.arrows_scripts_lists[x]
                    entry = script_name+':'+mode_name
                    if entry not in script_list: script_list.insert(0,entry)
                    #self.log.info('Add ' + str(x) + " " + entry )
                if action == 'remove':
                    script_list = self.player.arrows_scripts_lists[x]
                    entry = script_name+':'+mode_name
                    if entry in script_list: script_list.remove(entry)
                    #self.log.info('Remove ' + str(x) + " " + entry )                    	
                self.player.arrows_change[x] = 1
        else:
            self.log.info("led_num missing in arrow_change")
 

    def update(self, **kwargs):
        #compare current and old values and send differences
        for x in range(0, 10):
            if self.player.arrows_change[x] == 1:
                self.player.arrows_change[x] = 0
                led = self.arrows_ledlist[x]
                sc_list = self.player.arrows_scripts_lists[x]
                scp_name = "flash" + str(len(sc_list))             
                if len(sc_list) > 0:
                    for index, item in enumerate(sc_list):
                        color_name, mode_name = item.split(':')
                        if index == 0:
                            color_dic = {'color1': color_name} 
                        else:
                            color_dic['color'+ str(index+1)] = color_name
                    color_dic['leds'] = led
                    #stop currently playing show
                    if self.player.arrows_show_handles[x] != 0:
                        self.player.arrows_show_handles[x].stop()
                        self.player.arrows_show_handles[x] = 0
                    self.player.arrows_show_handles[x] = self.machine.shows[scp_name].play(show_tokens=color_dic, speed=6.0, loops=-1)
                else:
                    #remove show, if any 
                    if self.player.arrows_show_handles[x] != 0:
                        self.player.arrows_show_handles[x].stop()
                        self.player.arrows_show_handles[x] = 0
                    #self.player.arrows_show_handles[x] = self.machine.shows[scp_name].play(show_tokens=dict(leds=led), speed=4.0)							                
        self.delay.add(name='update_arrows', ms=50, callback=self.update)


    def mode_stop(self, **kwargs):
        self.log.info('Arrow_LEDS mode_stop')
        for x in range(0, 10):
            if self.player.arrows_show_handles[x] != 0:
                self.player.arrows_show_handles[x].stop()
                self.player.arrows_show_handles[x] = 0
