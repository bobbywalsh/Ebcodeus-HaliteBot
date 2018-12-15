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

def navigateShip():
    if safeMoveCheck():
        command_queue.append(ship.move(game_map.naive_navigate(ship, ship_target[ship.id])))
    else:
        command_queue.append(ship.move(Direction.invert(game_map.naive_navigate(ship, ship_target[ship.id]))))


def safeMoveCheck():
    safe = bool(1)
    for x in range(-5 , 5, 1):
        for y in range(-5 , 5, 1):
            if game_map[Position(x, y)].is_occupied:
                if game_map.calculate_distance(ship.position, Position(x, y)) <= 2.0:
                    safe = bool(0)
                    ship_target[ship.id] = Position(x, y)
    return safe

def findHalite():
    for x in range(-2 , 2, 1):
        for y in range(-2 , 2, 1):
            if game_map[ship.position.directional_offset((x,y))].halite_amount > game_map[ship_target[ship.id]].halite_amount: #and game_map[ship.position.directional_offset((x,y))] not in ship_target:
                ship_target[ship.id] = ship.position.directional_offset((x,y))

def gpsHome():
    ship_target[ship.id] = me.shipyard.position


# Respond with your name.
game.ready("Ebcodeus-v1")

while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn.
    command_queue = []

    # Spawn ship if halite is over 3000
    if not game_map[me.shipyard].is_occupied and me.halite_amount >= 2000:
       command_queue.append(me.shipyard.spawn())


    for ship in me.get_ships():
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"              #default status
            ship_target[ship.id] = me.shipyard.position     #default target
            findHalite()
            navigateShip()
        elif ship_status[ship.id] == "exploring":
            if ship.halite_amount >= 700:
                ship_status[ship.id] = "returning"              #default status
                gpsHome()
                navigateShip()
            else:
                findHalite()
                navigateShip()
        else:
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"              #default status
                findHalite()
                navigateShip()
            else:
                #ship_status[ship.id] = "returning"              #default status
                gpsHome()
                navigateShip()


    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
