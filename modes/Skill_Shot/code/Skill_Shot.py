from mpf.core.mode import Mode

# TODO - add Super and Secret skill shots
# Skill Shots
# 
# Skill Shot #1
# If you soft-plunge into the Bathtub Hole, you get a 1,000,000 skill shot, multiplied by the current ball number.
# 
# Skill Shot #2
# If you soft-plunge to the upper-right flipper and make the left toy-orbit shot, 
# you will get a Skill Shot worth a fixed 2,500,000 points. 
# This is the best one to go for on Ball 1 and 2, however, for Ball 3 (and 4/5 if playing a 5-ball game) 
# you're better off going with Skill Shot #1.
# 
# Super Skill Shot
# Normally, if you attempt to full-plunge, the popup post will cause the ball to fall into the toy pops. 
# If you hold the left flipper up while plunging, the popup post will go down (and stay down) the instant 
# the ball leaves the shooter lane, allowing the ball to go all the way around the orbit. 
# Simply make any major shot after this without qualifying the playfield to score 4,000,000 points and 25 toys. 
# All major shot triangles will flash cyan to indicate that you're ready to go for a Super Skill Shot.
# 
# Secret Skill Shot
# If you want to get really crazy, soft-plunge the ball and get it down to the main flippers without 
# hitting any switches or slingshots, then shoot the right ramp. 
# This will always send the ball into the Zero lane and will award a "Secret Skill Shot" worth 1,000,000 points, 
# multiplied by the current ball number, 25 toys, lowers the Oogie Boogie gate if it's up, 
# increases the bonus multiplier by 1x, and opens the shooter lane diverter on the Soup Shot for 10 
# seconds as though you had just made the Soup Shot, making it possible to immediately go for a shot tripler. 
# The game will actually flash the right ramp triangle cyan after about seven seconds if it thinks
# you're in the process of doing this, detected by confirming that the ball is not in the shooter lane, 
# that you didn't qualify a Super Skill Shot, that no switches have
# been hit, and that one of the flippers has been up for seven seconds straight.

class Skill_Shot(Mode):

# runs on MPF boot when the mode is read in and set up.
    def mode_init(self):
        self.log.info('Skill_Shot mode_init')

    def mode_start(self, **kwargs):
        self.log.info('Skill_Shot mode_start')
        if self.player.skill_shot_started == 0:
            self.player.skill_shot_started = 1 
            self.player.sally_spins = 0
            self.player.skill_shot_1_collected = 0
            self.player.skill_shot_2_collected = 0
            self.player.skill_shot_3_collected = 0
            self.player.skill_shot_4_collected = 0
        self.ticks = 0
        self.running = 0
        self.arrows_on = 0
        self.skillshot_collected = 0
        self.player.skill_shot_timeleft = 0
        self.player.skill_shot_value = 0
        self.add_mode_event_handler('sneakin_hit', self.skill_1)
        self.add_mode_event_handler('major_3_singlestep_unlit_hit', self.skill_2)
        #self.add_mode_event_handler('major_3_singlestep_unlit_hit', self.skill_2)
#        self.add_mode_event_handler('sneakinloop_opt_active', self.sneak_in_assist)
        self.add_mode_event_handler('balldevice_playfield_ball_enter', self.start_timer)        
        self.skillshot_start()
        self.msg = 1
        self.ticks_msg = self.ticks
        

    def skillshot_start(self):
        self.log.info("skillshot_start")
        self.ticks = 10
        self.machine.events.post("skillshot_start_display")        
        self.delay.add(name="skillshot_ticker", ms=500, callback=self.ticker)
        self.running = 0
        self.arrows_on = 0
        self.player.skill_shot_timeleft = 5
        
        
    def start_timer(self, **kwargs):
        self.log.info("skillshot start timer")    	
        self.running = 1  
        self.ticks_msg = self.ticks
        self.machine.events.post('show_skillshot_msg_1')
        self.machine.events.post("skillshot_start_timer")                
        

    def ticker(self):
        self.log.info("skillshot - 500ms ticks " +str(self.ticks))
        self.player.skill_shot_timeleft = int(self.ticks/2)
        self.machine.events.post("skillshot_countdown")
        if self.arrows_on == 0:        
            self.set_shot_lights()            
            self.arrows_on = 1
        if self.running == 1:
            self.ticks -= 1
            if self.ticks <= 0:
                self.skillshot_complete()
            else:
               self.delay.add(name="skillshot_ticker", ms=500, callback=self.ticker)
        else:
           self.delay.add(name="skillshot_ticker", ms=500, callback=self.ticker)  
        if  self.ticks_msg-self.ticks > 3:
            self.msg += 1
            self.ticks_msg = self.ticks
            if self.msg > 3: 
                self.msg = 1
            self.machine.events.post('show_skillshot_msg_'+str(self.msg))


    def skillshot_stop(self):
        self.log.info("skillshot over")    
        self.machine.events.post('skillshot_music_stop')
        self.clear_shot_lights()
        self.stop()


    def set_shot_lights(self):
        self.machine.events.post('arrow_change', led_num=3, script_name='violet', mode_name="skillshot", action="add")
        self.machine.events.post('arrow_change', led_num=5, script_name='violet', mode_name="skillshot", action="add")
        self.machine.events.post('arrow_change', led_num=7, script_name='violet', mode_name="skillshot", action="add")


    def clear_shot_lights(self):
        self.machine.events.post('arrow_change', led_num=3, script_name='violet', mode_name="skillshot", action="remove")
        self.machine.events.post('arrow_change', led_num=5, script_name='violet', mode_name="skillshot", action="remove")
        self.machine.events.post('arrow_change', led_num=7, script_name='violet', mode_name="skillshot", action="remove")


#    def sneak_in_assist(self, **kwargs):
#        self.log.info('skill shot - sneak_in_assist')
#        self.machine.events.post("sneak_in_assist")

        
    def skill_1(self, **kwargs):
        if self.skillshot_collected == 0:
            self.log.info('Skill_Shot 1 - sneakin') 
            self.player.skill_shot_1_collected += 1
            self.score = 1000000 * self.player.ball 
            self.player["score"] += self.score
            self.player.skill_shot_value = self.score
            self.machine.events.post("skill_shot_completed",value=self.score)
            self.skillshot_collected = 1
            self.skillshot_complete()


    def skill_2(self, **kwargs):
        if self.skillshot_collected == 0:    	
            self.log.info('Skill_Shot 2 - left inner loop') 
            self.player.skill_shot_2_collected += 1
            self.score = 2500000 
            self.player["score"] += self.score
            self.player.skill_shot_value = self.score            
            self.machine.events.post('skill_shot_completed',value=self.score)
            self.skillshot_collected = 1            
            self.skillshot_complete()

            
    def skillshot_complete(self, **kwargs):
        self.delay.remove("skillshot_ticker")
        self.machine.events.post('skill_shot_ended')        
        self.delay.add(name="skillshot_stopper", ms=2000, callback=self.skillshot_stop)


    def mode_stop(self, **kwargs):
        self.machine.events.post('skill_shot_ended')            	
        self.log.info('Skill_Shot mode_stop')


