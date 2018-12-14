#!/usr/bin/env python3
#added new structured priority holding the move until after gone through the list
#Priority findHalite, setStatus, exploringMove, exploringCreateDrop,
#returning, safetyCheck, Still, Spawn ship

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants
from hlt.positionals import Direction
import random
import logging


# This game object contains the initial game state.
game = hlt.Game()

#ship status
ship_status = {}
ship_target = {}

#Halite Finder
#might have to move this below?
def findHalite(shipTest):
    newTarget = shipTest.position
    #Scan nearby map cells for largest amount of halite
    for x_cell in range(-10,10,1):
        for y_cell in range(-10,10,1):
            #logging.info(game_map[ship.position.directional_offset(target_location_offset)])
            if game_map[shipTest.position.directional_offset((x_cell,y_cell))].halite_amount > game_map[shipTest.position].halite_amount:
                newTarget = (x_cell,y_cell)

    return newTarget

#Home GPS
#might have to move this below?
def gpsHome(shipGps):
    #Scan nearby map cells for largest amount of halite
    newTarget = me.shipyard.position
    for dropOff in me.get_dropoffs():
        if game_map.calculate_distance(ship, dropOff.position) < game_map.calculate_distance(ship, me.shipyard.position):
            newTarget = dropOff.position

    return newTarget

#Area Checker
#might have to move this below?
def safeCheck(shipPos):
    newTarget = "w"
    #Scan nearby map cells for largest amount of halite
    for x_cell in range(-5,5,1):
        for y_cell in range(-5,5,1):
            tempCell = shipPos.position.directional_offset((x_cell,y_cell))
            if game_map[tempCell].is_occupied and game_map.calculate_distance(shipPos.position, tempCell) < 2:
                newTarget = str(Direction.invert((x_cell,y_cell)))
    return newTarget

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



    for ship in me.get_ships():
        #logging
        logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount))
        moveChoice = "o"
        ship_target[ship.id] = findHalite(ship) #find halite

        #ship status
        if ship.id not in ship_status:              #set defaults
            ship_status[ship.id] = "exploring"
            ship_target[ship.id] = (0, 0)
            logging.info("Ship {} target {}.")
        elif ship_status[ship.id] == "returning":     #return
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"
                logging.info("Ship {} target {}.".format(ship_target[ship.id]))

        if ship_status[ship.id] == "exploring":
            if ship.is_full:
                logging.info("Ship {} target {}.".format(ship_target[ship.id]))
                ship_status[ship.id] = "returning"
                ship_target[ship.id] = me.shipyard
                command_queue.append(ship.move(game_map.naive_navigate(ship, ship_target[ship.id])))
            else:
                logging.info("Ship Move")
                command_queue.append(ship.move(game_map.naive_navigate(ship, ship_target[ship.id])))
        #moveChoice = safeCheck(ship)
        #command_queue.append(ship.move(moveChoice))


    #Spawn ship at 3001 or more
    if me.halite_amount >= 3001 and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())
        logging.info("Ship spawned{}")

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
