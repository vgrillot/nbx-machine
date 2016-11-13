from mpf.core.mode import Mode

# Base Mode 
# copy player vars to machine vars for display

class Base(Mode):

    def mode_start(self, **kwargs):
        self.log.info('mode starting')
        self.add_mode_event_handler("player_added_2", self.player_2_added)
        self.add_mode_event_handler("player_added_3", self.player_3_added)
        self.add_mode_event_handler("player_added_4", self.player_4_added)                
        if self.machine.is_machine_var('player_slot_2'):    
            if self.machine.game.num_players > 1:
                if self.machine.game.num_players == 2:
                    self.log.info('2 players')
                    if self.machine.game.player.number == 1:
                        self.log.info('show player 2 score on right')                    	
                        self.machine.set_machine_var('player_slot_2',2)
                        self.machine.set_machine_var('score_slot_2',self.machine.game.player_list[1]['score'])        
                    else:
                        self.log.info('show player 1 score on right')                    	
                        self.machine.set_machine_var('player_slot_2',1)
                        self.machine.set_machine_var('score_slot_2',self.machine.game.player_list[0]['score'])        
                elif self.machine.game.num_players == 3:                    
                    if self.machine.game.player.number == 1:
                        self.machine.set_machine_var('player_slot_2',2)
                        self.machine.set_machine_var('score_slot_2',self.machine.game.player_list[1]['score'])        
                        self.machine.set_machine_var('player_slot_3',3)
                        self.machine.set_machine_var('score_slot_3',self.machine.game.player_list[2]['score'])        
                    elif self.machine.game.player.number == 2:
                        self.machine.set_machine_var('player_slot_2',3)
                        self.machine.set_machine_var('score_slot_2',self.machine.game.player_list[2]['score'])        
                        self.machine.set_machine_var('player_slot_3',1)
                        self.machine.set_machine_var('score_slot_3',self.machine.game.player_list[0]['score'])
                    else:  #player 3 is up
                        self.machine.set_machine_var('player_slot_2',1)
                        self.machine.set_machine_var('score_slot_2',self.machine.game.player_list[0]['score'])        
                        self.machine.set_machine_var('player_slot_3',2)
                        self.machine.set_machine_var('score_slot_3',self.machine.game.player_list[1]['score'])
                else:  #4 players
                    if self.machine.game.player.number == 1:
                        self.machine.set_machine_var('player_slot_2',2)
                        self.machine.set_machine_var('score_slot_2',self.machine.game.player_list[1]['score'])        
                        self.machine.set_machine_var('player_slot_3',3)
                        self.machine.set_machine_var('score_slot_3',self.machine.game.player_list[2]['score'])        
                        self.machine.set_machine_var('player_slot_4',4)
                        self.machine.set_machine_var('score_slot_4',self.machine.game.player_list[3]['score'])        
                    elif self.machine.game.player.number == 2:
                        self.machine.set_machine_var('player_slot_2',3)
                        self.machine.set_machine_var('score_slot_2',self.machine.game.player_list[2]['score'])        
                        self.machine.set_machine_var('player_slot_3',4)
                        self.machine.set_machine_var('score_slot_3',self.machine.game.player_list[3]['score'])
                        self.machine.set_machine_var('player_slot_4',1)
                        self.machine.set_machine_var('score_slot_4',self.machine.game.player_list[0]['score'])        
                    elif self.machine.game.player.number == 3:
                        self.machine.set_machine_var('player_slot_2',4)
                        self.machine.set_machine_var('score_slot_2',self.machine.game.player_list[3]['score'])        
                        self.machine.set_machine_var('player_slot_3',1)
                        self.machine.set_machine_var('score_slot_3',self.machine.game.player_list[0]['score'])
                        self.machine.set_machine_var('player_slot_4',2)
                        self.machine.set_machine_var('score_slot_4',self.machine.game.player_list[1]['score'])        
                    else:  #player 4 is up
                        self.machine.set_machine_var('player_slot_2',1)
                        self.machine.set_machine_var('score_slot_2',self.machine.game.player_list[0]['score'])        
                        self.machine.set_machine_var('player_slot_3',2)
                        self.machine.set_machine_var('score_slot_3',self.machine.game.player_list[1]['score'])
                        self.machine.set_machine_var('player_slot_4',3)
                        self.machine.set_machine_var('score_slot_4',self.machine.game.player_list[2]['score'])        
            	
        else:
            self.machine.create_machine_var('player_slot_2',2)
            self.machine.create_machine_var('score_slot_2',0)        
            self.machine.create_machine_var('player_slot_3',3)
            self.machine.create_machine_var('score_slot_3',0)        
            self.machine.create_machine_var('player_slot_4',4)
            self.machine.create_machine_var('score_slot_4',0)        

    def player_2_added(self, **kwargs):
        self.log.info('add player 2, set display')    	
        self.machine.set_machine_var('player_slot_2',2)
        self.machine.set_machine_var('score_slot_2',0)        
        
    def player_3_added(self, **kwargs):
        self.machine.set_machine_var('player_slot_3',3)
        self.machine.set_machine_var('score_slot_3',0)        
        
    def player_4_added(self, **kwargs):
        self.machine.set_machine_var('player_slot_4',4)
        self.machine.set_machine_var('score_slot_4',0)        

                    
#self.machine.game.num_players
#self.machine.game.player is the current player
#self.machine.game.player.number is the current player number