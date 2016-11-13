from mpf.core.mode import Mode


# Combos                                                                                                                                                   Page 6

class Combos(Mode):

    def mode_init(self):
        self.log.info('Combos mode_init')

    def mode_start(self, **kwargs):
        self.log.info('Combos mode_start')
        #self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.combos_started == 0:
            #once per game only
            self.player.combos_started = 1 
            self.player.combos_Extra_Ball_collected = 0
            self.player.combos_Special_collected = 0
        #resets every ball
        self.player.combos_running = 1
        self.player.combos_number = 0
        self.player.combos_number_display = 1
        self.player.combos_Hold_Bonus_collected = 0
        self.player.combos_Light_Mystery_collected = 0
        #states:  unlit, lit, collected
        self.player.combos_shotlist = [
            {"led":"rgb_mayor_arrow", "state":"unlit"}
            ,{"led":"rgb_lorbit_arrow", "state":"unlit"}
            ,{"led":"rgb_lramp_arrow", "state":"unlit"}
            ,{"led":"rgb_leftloop_arrow", "state":"unlit"}
            ,{"led":"rgb_oogie_cw_arrow", "state":"unlit"}
            ,{"led":"rgb_oogie_ccw_arrow", "state":"unlit"}
            ,{"led":"rgb_grave_arrow", "state":"unlit"}
            ,{"led":"rgb_rramp_arrow", "state":"unlit"}
            ,{"led":"rgb_rorbit_arrow", "state":"unlit"}
            ,{"led":"rgb_soup_arrow", "state":"unlit"}
            ]
        self.add_mode_event_handler('major_0_singlestep_unlit_hit', self.major_0)
        self.add_mode_event_handler('major_1_singlestep_unlit_hit', self.major_1)
        self.add_mode_event_handler('major_2_singlestep_unlit_hit', self.major_2)
        self.add_mode_event_handler('major_2a_singlestep_unlit_hit', self.major_2)
        self.add_mode_event_handler('major_3_singlestep_unlit_hit', self.major_3)
        self.add_mode_event_handler('major_4_singlestep_unlit_hit', self.major_4)
        self.add_mode_event_handler('major_5_singlestep_unlit_hit', self.major_5)
        self.add_mode_event_handler('major_5a_singlestep_unlit_hit', self.major_5)
        self.add_mode_event_handler('major_6_singlestep_unlit_hit', self.major_6)
        self.add_mode_event_handler('major_6a_singlestep_unlit_hit', self.major_6)
        self.add_mode_event_handler('major_7_singlestep_unlit_hit', self.major_7)
        self.add_mode_event_handler('major_7a_singlestep_unlit_hit', self.major_7)
        self.add_mode_event_handler('major_8_singlestep_unlit_hit', self.major_8)
        self.add_mode_event_handler('major_8a_singlestep_unlit_hit', self.major_8)
        self.add_mode_event_handler('major_9_singlestep_unlit_hit', self.major_9)
        self.add_mode_event_handler('ball_ending', self.reset_combos)

        self.add_mode_event_handler('disable_combos', self.disable_combos)
        self.add_mode_event_handler('enable_combos', self.enable_combos)

    def enable_combos(self, **kwargs):
       self.log.info("Enable Combos")
       self.player.combos_running = 1

    def disable_combos(self, **kwargs):
       self.reset_combos()
       self.log.info("Combos - Disabled")
       self.player.combos_running = 0

    def light_for_combo(self, notthis):
        for x in range(0, 10):
            #skip notthis
            if x != notthis:
                self.player.combos_shotlist[x]["state"] = 'lit'
                led = self.player.combos_shotlist[x]["led"]
                self.machine.events.post('arrow_change', led_num=x, script_name="yellow", mode_name="Combos", action="add")


    def major_0(self, **kwargs):
        self.handle_shot(0)
    def major_1(self, **kwargs):
        self.handle_shot(1)
    def major_2(self, **kwargs):
        self.handle_shot(2)
    def major_3(self, **kwargs):
        self.handle_shot(3)
    def major_4(self, **kwargs):
        self.handle_shot(4)
    def major_5(self, **kwargs):
        self.handle_shot(5)
    def major_6(self, **kwargs):
        self.handle_shot(6)
    def major_7(self, **kwargs):
        self.handle_shot(7)
    def major_8(self, **kwargs):
        self.handle_shot(8)
    def major_9(self, **kwargs):
        self.handle_shot(9)


    def handle_combo_number(self, multiplier):
        if self.player.combos_running == 1: 
 #           print "Handle Combo " + str(self.player.combos_number)
            self.toys = 0
            self.score = 0
            if self.player.combos_number == 2:
                self.score = 50000 * multiplier
            if self.player.combos_number == 3:
                self.score = 75000 * multiplier
                self.toys = 5 * multiplier
            if self.player.combos_number == 4:
                self.score = 100000 * multiplier
                self.toys = 5 * multiplier
                if self.player.combos_Hold_Bonus_collected == 0:
                    self.player.combos_Hold_Bonus_collected = 1
                    self.machine.events.post("bonus_hold")                                        
            if self.player.combos_number == 5:
                self.score = 125000 * multiplier
                self.toys = 10 * multiplier
            if self.player.combos_number == 6:
                self.score = 150000 * multiplier
                self.toys = 10 * multiplier
                if self.player.combos_Light_Mystery_collected == 0:
                    self.player.combos_Light_Mystery_collected = 1
                    self.machine.events.post('light_mystery_shot')
            if self.player.combos_number == 7:
                self.score = 300000 * multiplier
                self.toys = 20 * multiplier
            if self.player.combos_number == 8:
                self.score = 500000 * multiplier
                self.toys = 30 * multiplier
                if self.player.combos_Extra_ball_collected == 0:
                    self.player.combos_Extra_ball_collected = 1
                    self.machine.events.post("award_EB_start")
            if self.player.combos_number == 9:
                self.score = 1000000 * multiplier
                self.toys = 50 * multiplier
            if self.player.combos_number == 10:
                self.score = 5000000 * multiplier
                self.toys = 100 * multiplier
                if self.player.combos_Special_collected == 0:
                    self.player.combos_Special_collected = 1
                    self.machine.events.post("award_special_start")                    
            self.player.combos_number_display = self.player.combos_number
            self.machine.events.post('combos_collected', value=self.player.combos_number)
            self.machine.events.post("combo_collected_"+str(self.player.combos_number)+"x")
            self.player.toys_collected += self.toys
            self.player.score += self.score


    def reset_combos(self, **kwargs):
        self.log.info("Combos timer expired")
        self.player.combos_number = 0
        for x in range(0, 10):
            self.player.combos_shotlist[x]["state"] = 'unlit'
            #stop the flashing LED show
            led = self.player.combos_shotlist[x]["led"]
            self.machine.events.post('arrow_change', led_num=x, script_name="yellow", mode_name="Combos", action="remove")            


    def handle_shot(self, shot):
        if self.player.combos_running == 1: 
            if self.player.combos_number == 0:
                self.player.combos_number = 1
                self.player.combos_shotlist[shot]["state"] = "collected"
                #first shot, start flashing the rest
                self.light_for_combo(shot)
                led = self.player.combos_shotlist[shot]["led"]
                self.machine.events.post('arrow_change', led_num=shot, script_name="yellow", mode_name="Combos", action="remove")
                self.machine.shows["sc_combo_out"].play(show_tokens=dict(leds=led), speed=8.0, loops=3)			
				
                #remove old timer, start a 7 second timer
                self.delay.remove('combo_timeout')
                self.delay.add(name='combo_timeout', ms=7000, callback=self.reset_combos)
            else:
                if self.player.combos_shotlist[shot]["state"] != "collected":
                    self.player.combos_number += 1
                    #not the first shot, mark it as collected
                    self.player.combos_shotlist[shot]["state"] = "collected"
                    multiplier = self.player.multiplier_shot_value_list[shot]
                    self.handle_combo_number(multiplier)
                    #stop the flash LED
                    led = self.player.combos_shotlist[shot]["led"]
                    self.machine.events.post('arrow_change', led_num=shot, script_name="yellow", mode_name="Combos", action="remove")
                    self.machine.shows["sc_combo_out"].play(show_tokens=dict(leds=led), speed=8.0, loops=3)			
					
                    #remove old timer, start a 7 second timer
                    self.delay.remove('combo_timeout')
                    self.delay.add(name='combo_timeout', ms=7000, callback=self.reset_combos)
#                else:
#                    #do nothing for now
#                   print 'Combos already claimed this one'
    

    def mode_stop(self, **kwargs):
        self.log.info('Combos mode_stop')
        self.delay.remove('combo_timeout')
        self.reset_combos()

