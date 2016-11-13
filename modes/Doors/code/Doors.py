from mpf.core.mode import Mode
from mpf.core.delays import DelayManager

import random

class Doors(Mode):

    def mode_init(self):
        self.log.info('Doors mode_init')

    def mode_start(self, **kwargs):
        self.log.info('Doors mode_start')
        self.delay = DelayManager(self.machine.delayRegistry)
        if self.player.Doors_started == 0:
            #once per game only
            self.player.Doors_started = 1
            self.player.Doors_state = 0
            self.player.doors_currentdoor = 0
            self.player.doors_list = [
                {"led":"rgb_holiday_christmas", "state":1}
                ,{"led":"rgb_holiday_valentine", "state":0}
                ,{"led":"rgb_holiday_stpat", "state":0}
                ,{"led":"rgb_holiday_easter", "state":0}
                ,{"led":"rgb_holiday_independence", "state":0}
                ,{"led":"rgb_holiday_halloween", "state":0}
                ,{"led":"rgb_holiday_thanksgiving", "state":0}
                ,{"led":"rgb_holiday_door", "state":0}
                ]
        self.player.doors_show_handles = [0] * 10
        self.add_mode_event_handler('sw_slingl', self.rotate_doors)
        self.add_mode_event_handler('sw_slingr', self.rotate_doors)
        self.add_mode_event_handler('LSB_advance_door', self.rotate_doors)        
        self.add_mode_event_handler('major_2_singlestep_unlit_hit', self.trees_hit)
        self.add_mode_event_handler('holiday_mode_stopped', self.holiday_stopped)
        self.add_mode_event_handler("doors_pause_and_hide", self.pause_and_hide)  
        self.add_mode_event_handler("doors_resume_and_show", self.resume_and_show)  
        self.setup_scripts()
        self.set_door_lights()

        
    def pause_and_hide(self, **kwargs):     
        self.log.info('pause_and_hide - pause timer')
        self.player.door_timer_ispaused = 1

        
    def resume_and_show(self, **kwargs):        
        self.log.info('resume_and_show - unpause timer')    
        self.player.door_timer_ispaused = 0

        
    def set_door_lights(self):
        self.log.info('Setting door lights')
        for x in range(0, 8):
            if self.player.doors_show_handles[x] != 0:
                self.player.doors_show_handles[x].stop()
                self.player.doors_show_handles[x] = 0
        for x in range(0, 8):
            state = self.player.doors_list[x]["state"]
            led = self.player.doors_list[x]["led"]
            self.log.info("Setting " + led + " to " + str(state) + " " + self.script[x][state])
            self.player.doors_show_handles[x] = self.machine.shows[self.script[x][state]].play(show_tokens=dict(leds=led), speed=4, loops=-1)			



    def holiday_stopped(self, state=None, **kwargs):
        self.log.info( 'Doors - holiday_stopped - state %s',state )
        #state can be "complete" or "incomplete"
        self.player.Doors_state = 0  
        cd = self.player.doors_currentdoor 
        if state == "complete":
            self.player.doors_list[cd]["state"] = 3 #completed
        else:
            self.player.doors_list[cd]["state"] = 1 #back to ready
        self.machine.events.post('door_mode_'+str(cd)+'_stop')
        self.CycleDoors()
        self.set_door_lights()


    def rotate_doors(self, **kwargs):
        cd = self.player.doors_currentdoor 
        state = self.player.doors_list[cd]["state"]
        #only move the 'ready' door
        #cant move unlit, playing or solid doors
        if state == 1:
            self.log.info( 'Doors - rotate')  
            self.CycleDoors()
            self.set_door_lights()
        else:
            self.log.info("Doors - can't rotate, door state: " + str(state))  
            
            
    def trees_hit(self, **kwargs):
        self.log.info( 'Doors - tree gate')
        if self.player.Doors_state == 0:
            #only if LSB MB and dice mode are not running
            if (self.player.LSB_MB_running != 1 and self.player.OB_mode_4_running != 1):
                #no other door mode is running 
                cd = self.player.doors_currentdoor 
                state = self.player.doors_list[cd]["state"]
                #only start a 'ready' door
                if state == 1:  
                    self.StartHoliday()
                    self.set_door_lights()
            else:
                self.log.info("Can't Start Holiday during LSB MB or Dice")      
        else:
            self.log.info("Can't Start with another Holiday running")      


    def StartHoliday(self):
        self.log.info('Start Holiday')      
        cd = self.player.doors_currentdoor 
        self.player.doors_list[cd]["state"] = 2 #playing
        self.machine.events.post('door_mode_'+str(cd)+'_start')
        self.player.Doors_state = 1  #playing a holiday 


    def mode_stop(self, **kwargs):
        self.log.info('Doors mode_stop')
        cd = self.player.doors_currentdoor 
        state = self.player.doors_list[cd]["state"]
        if state == 2:
            self.player.doors_list[cd]["state"] = 1
#        self.set_door_lights()
        for x in range(0, 8):
            if self.player.doors_show_handles[x] != 0:
                self.player.doors_show_handles[x].stop()
                self.player.doors_show_handles[x] = 0
        self.player.Doors_state = 0  



    def CycleDoors(self):
        dcount = 0 
        done = 0
        t = 0
        CurrentDoor = self.player.doors_currentdoor
        NewDoor = self.player.doors_currentdoor

        while (dcount < 6) and (done == 0):
            NewDoor = NewDoor + 1
            if NewDoor > 6:
                NewDoor = 0
            ds = self.player.doors_list[NewDoor]["state"]
            if ( ds == 0 ):
                #found next door, done
                self.player.doors_list[NewDoor]["state"] = 1
                if self.player.doors_list[CurrentDoor]["state"] == 1:
                    self.player.doors_list[CurrentDoor]["state"] = 0
                done = 1
            dcount = dcount + 1
        if done == 0:
            self.log.info("At least 6 doors completed of 7")
            # no next door?
            dcount = 0
            for t in range(0,7):
                if self.player.doors_list[t]["state"] == 3: 
                    dcount = dcount + 1
            if dcount == 7:
                if self.player.doors_list[7]["state"] == 3:
                    #if wizard mode was completed, reset 
                    #shut off lights
                    for t in range(0,7):
                        self.player.doors_list[t]["state"] = 0
                    #select a random door
                    NewDoor = random.randint(0,6)
                    self.player.doors_list[NewDoor]["state"] = 1
                    self.log.info("Wizard mode completed, reset doors")
                else:               
                    #all at state 3 - then set to door 7, Wizard mode                
                    self.player.doors_list[7]["state"] = 1
                    NewDoor = 7
                    self.log.info("Wizard door mode available")
            else:
                NewDoor = self.player.doors_currentdoor
        self.player.doors_currentdoor = NewDoor


# 0 - off 1
# 1 - ready 1 (blink)
# 2 - MB 1
# 3 - completed 1
    def setup_scripts(self): 
        self.script = [[0 for x in range(8)] for x in range(8)] 
        self.script[0][0] = "sc_off"
        self.script[0][1] = "sc_christmas_ready"
        self.script[0][2] = "sc_christmas_playing"
        self.script[0][3] = "sc_christmas_done"

        self.script[1][0] = "sc_off"
        self.script[1][1] = "sc_valentines_ready"
        self.script[1][2] = "sc_valentines_playing"
        self.script[1][3] = "sc_valentines_done"

        self.script[2][0] = "sc_off"
        self.script[2][1] = "sc_stpats_ready"
        self.script[2][2] = "sc_stpats_playing"
        self.script[2][3] = "sc_stpats_done"

        self.script[3][0] = "sc_off"
        self.script[3][1] = "sc_easter_ready"
        self.script[3][2] = "sc_easter_playing"
        self.script[3][3] = "sc_easter_done"

        self.script[4][0] = "sc_off"
        self.script[4][1] = "sc_independence_ready"
        self.script[4][2] = "sc_independence_playing"
        self.script[4][3] = "sc_independence_done"

        self.script[5][0] = "sc_off"
        self.script[5][1] = "sc_halloween_ready"
        self.script[5][2] = "sc_halloween_playing"
        self.script[5][3] = "sc_halloween_done"

        self.script[6][0] = "sc_off"
        self.script[6][1] = "sc_thanksgiving_ready"
        self.script[6][2] = "sc_thanksgiving_playing"
        self.script[6][3] = "sc_thanksgiving_done"

        self.script[7][0] = "sc_off"
        self.script[7][1] = "sc_door_ready"
        self.script[7][2] = "sc_door_playing"
        self.script[7][3] = "sc_door_done"

