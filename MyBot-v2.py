#!/usr/bin/env python3
#added new structured priority holding the move until after gone through the list
#Priority findHalite, setStatus, exploringMove, exploringCreateDrop,
#returning, safetyCheck, Still, Spawn ship

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants
from hlt.positionals import Direction
from hlt.positionals import Position
import random
import logging


# This game object contains the initial game state.
game = hlt.Game()

#ship status
ship_status = {}
ship_target = {}


def safeMoveCheck(ship):
    for x in range(-5 , 5, 1):
        for y in range(-5 , 5, 1):
            if game_map[Position(x, y)].is_occupied:
                if game_map.calculate_distance(ship.position, Position(x, y)) <= 2.0:
                    command_queue.append(ship.move(Direction.invert(game_map.naive_navigate(ship, Position(x, y)))))

def findHalite(ship):
    #find halite in forloop compare with current
    #if better replace move
    #else done move
    for x in range(-5 , 5, 1):
        for y in range(-5 , 5, 1):
            if game_map[ship.position.directional_offset((x,y))].halite_amount > game_map[ship.position].halite_amount: #and game_map[ship.position.directional_offset((x,y))] not in ship_target:
                ship_target[ship.id] = ship.position.directional_offset((x,y))
                #map = game_map.naive_navigate(ship, ship_target[ship.id])
            #else:
                #map = game_map.naive_navigate(ship, ship_target[ship.id])
                #logging.info("Ship {} has {} target.".format(ship.id, ship_target[ship.id]))

    command_queue.append(ship.move(game_map.naive_navigate(ship, ship_target[ship.id])))

def gpsHome(ship):
    ship_target[ship.id] = me.shipyard.position
    for pDrop in player.get_dropoffs():
        if game_map.calculate_distance(ship.position, ship_target[ship.id]) > game_map.calculate_distance(ship.position, pDrop.position):
            ship_target[ship.id] = pDrop.position
    command_queue.append(ship.move(game_map.naive_navigate(ship.position, ship_target[ship.id])))



# Respond with your name.
game.ready("Ebcodeus-v2")

while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn.
    command_queue = []
    #Spawn ship at 5000 or more
    if game.turn_number < 100 and not game_map[me.shipyard].is_occupied and me.halite_amount >= 1000:        #for x in range(-2 , 2, 1):
       command_queue.append(me.shipyard.spawn())
    elif not game_map[me.shipyard].is_occupied and me.halite_amount >= 5000:        #for x in range(-2 , 2, 1):
       command_queue.append(me.shipyard.spawn())
      #logging.info("Ship spawned{}")

    for ship in me.get_ships():
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"              #default status
            ship_target[ship.id] = me.shipyard.position     #default target
            #safeMoveCheck(ship)                             #check surroundings
            findHalite(ship)                                #find best halite and move
            continue
        elif ship_status[ship.id] == "exploring":
            if ship.halite_amount >= 700:
                ship_status[ship.id] = "returning"
                #safeMoveCheck(ship)
                gpsHome(ship)
                continue
            elif game_map.calculate_distance(ship.position, me.shipyard.position) > 4.0 and ship.halite_amount < 500 and me.halite_amount > 4000:
                command_queue.append(ship.make_dropoff())
                #continue
            else:
                #safeMoveCheck(ship)                             #check surroundings
                if ship.position.x == 31:
                    command_queue.append(ship.move("e"))
                    continue
                if ship.position.y == 0:
                    command_queue.append(ship.move("s"))
                    continue
                findHalite(ship)                                #find best halite and move
                continue
                #print(ship_target[ship.id])
        elif ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"
                #safeMoveCheck(ship)                             #check surroundings
                findHalite(ship)
                continue                                #find best halite and move
            else:
                gpsHome(ship)
                continue
        else:
            ship_status[ship.id] = "exploring"
            gpsHome(ship)
            continue




    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
