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

#factors
ship_radarRangeMax = 5
ship_haliteRangeMax = 2
ship_distanceRangeMax = 2.0


#ship status
ship_status = {}
ship_target = {}

def navigateShip():
    if game_map[ship.position].halite_amount*.1 <= ship.halite_amount:
        if safeMoveCheck():
            command_queue.append(ship.move(game_map.naive_navigate(ship, ship_target[ship.id])))
        else:
            command_queue.append(ship.move(Direction.invert(game_map.naive_navigate(ship, ship_target[ship.id]))))


def safeMoveCheck():
    safe = bool(1)
    for x in range(-ship_radarRangeMax, ship_radarRangeMax, 1):
        for y in range(-ship_radarRangeMax, ship_radarRangeMax, 1):
            if game_map[Position(x, y)].is_occupied:
                if game_map.calculate_distance(ship.position, Position(x, y)) <= ship_distanceRangeMax:
                    safe = bool(0)
                    ship_target[ship.id] = Position(x, y)
    return safe

def findHalite():
    for x in range(-ship_haliteRangeMax, ship_haliteRangeMax, 1):
        for y in range(-ship_haliteRangeMax , ship_haliteRangeMax, 1):
            if game_map[ship.position.directional_offset((x,y))].halite_amount != 0: #and game_map[ship.position.directional_offset((x,y))] not in ship_target:
                if game_map[ship.position.directional_offset((x,y))].halite_amount > game_map[ship_target[ship.id]].halite_amount: #and game_map[ship.position.directional_offset((x,y))] not in ship_target:
                    if safeMoveCheck():
                        ship_target[ship.id] = ship.position.directional_offset((x,y))

def gpsHome():
    if not me.get_dropoffs():
        ship_target[ship.id] = me.shipyard.position
    else:
        for dropPoint in me.get_dropoffs():
            if game_map.calculate_distance(ship.position, dropPoint.position) <= game_map.calculate_distance(ship.position, me.shipyard.position):
                ship_target[ship.id] = dropPoint.position
            else:
                ship_target[ship.id] = me.shipyard.position


# Respond with your name.
game.ready("Ebcodeus-DropofftestCopyWeb")

while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn.
    command_queue = []



    for ship in me.get_ships():
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"              #default status
            ship_target[ship.id] = me.shipyard.position     #default target
            findHalite()
            navigateShip()
        elif ship_status[ship.id] == "exploring":
            if ship.halite_amount >= constants.MAX_HALITE * 3/4:
                ship_status[ship.id] = "returning"              #default status
                gpsHome()
                navigateShip()
            else:
                findHalite()
                navigateShip()
        elif ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"              #default status
                findHalite()
                navigateShip()
            elif me.halite_amount >= 5000 and len(me.get_ships()) >= 5:
                command_queue.append(ship.make_dropoff())
            else:
                gpsHome()
                navigateShip()
        else:
            command_queue.append(ship.stay_still())

    # Spawn ship if halite is over 3000
    if not game_map[me.shipyard].is_occupied and len(me.get_ships()) <= 5:
        if game.turn_number <= 120 and me.halite_amount >= 2000:
            command_queue.append(me.shipyard.spawn())
        elif me.halite_amount >= len(me.get_ships()) * 2000:
            command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
