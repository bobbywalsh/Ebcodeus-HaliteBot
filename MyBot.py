#!/usr/bin/env python3

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants
import random
import logging


# This game object contains the initial game state.
game = hlt.Game()

#ship status
ship_status = {}

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


    for ship in me.get_ships():
        logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount))

        #ship status
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"

        if ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"
            else:
                move = game_map.naive_navigate(ship, me.shipyard.position)
                command_queue.append(ship.move(move))
                continue
        elif ship.halite_amount >= constants.MAX_HALITE / 4:
            ship_status[ship.id] = "returning"
            move = game_map.naive_navigate(ship, me.shipyard.position)
            command_queue.append(ship.move(move))
            continue



        #ship movement
        if ship.position == me.shipyard.position:
            command_queue.append(ship.move(random.choice(["n", "s", "e", "w"])))
        elif game_map[ship.position.directional_offset((0, -1))].is_occupied:
            command_queue.append(ship.move("s"))
        elif game_map[ship.position.directional_offset((0, 1))].is_occupied:
            command_queue.append(ship.move("n"))
        elif game_map[ship.position.directional_offset((1, 0))].is_occupied:
            command_queue.append(ship.move("w"))
        elif game_map[ship.position.directional_offset((-1, 0))].is_occupied:
            command_queue.append(ship.move("e"))
        else:
            command_queue.append(ship.move("s"))



    # If you're on the first turn and have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though.
    if me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(game.me.shipyard.spawn())
    #if game.turn_number > 2 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
     #   command_queue.append(game.me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
