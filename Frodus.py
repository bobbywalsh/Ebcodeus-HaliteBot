#!/usr/bin/env python3

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants
from hlt.positionals import Direction
import random
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# Create a place to store missions for each ship.
ship_status = {}
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("Frodus")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    for ship in me.get_ships():
        # Save a message to yourself in the log file with some important information.
        #   Here, you log the halite amount in the ship's cargo.
        logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount))

        # Save location of richest halite
        target_location_offset = (0,0)

        # If ship is not on a mission, tell it to explore
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"
        # If ship is returning and is on shipyard, tell it to explore
        #   Else, move toward shipyard
        if ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"
            else:
                move = game_map.naive_navigate(ship, me.shipyard.position)
                command_queue.append(ship.move(move))
                continue
        # If ship's cargo is 1/4 full, tell it to return
        elif ship.halite_amount >= constants.MAX_HALITE*3 / 4:
            ship_status[ship.id] = "returning"

        #Scan nearby map cells for largest amount of halite
        for x_cell in range(-10,11,1):
            for y_cell in range(-10,11,1):
                #logging.info(game_map[ship.position.directional_offset(target_location_offset)])
                if game_map[ship.position.directional_offset((x_cell,y_cell))].halite_amount > game_map[ship.position.directional_offset(target_location_offset)].halite_amount:
                    target_location_offset = (x_cell,y_cell)

        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        if game_map[ship.position].halite_amount*.1 <= ship.halite_amount and game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
            command_queue.append(ship.move(game_map.naive_navigate(ship, ship.position.directional_offset(target_location_offset))))
        else:
            command_queue.append(ship.stay_still())

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
