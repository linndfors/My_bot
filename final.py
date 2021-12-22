#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This is an example of a bot for the 3rd project.
    ...a pretty bad bot to be honest -_-
"""
import random
from logging import DEBUG, debug, getLogger
from typing import List

# We use the debugger to print messages to stderr
# You cannot use print as you usually do, the vm would intercept it
# You can hovever do the following:
#
# import sys
# print("HEHEY", file=sys.stderr)

getLogger().setLevel(DEBUG)


def parse_field_info():
    """
    Parse the info about the field.

    However, the function doesn't do anything with it. Since the height of the field is
    hard-coded later, this bot won't work with maps of different height.

    The input may look like this:

    Plateau 15 17:
    """
    l = input()
    elems=l.split(" ")
    height=int(elems[1])
    width=int(elems[2][:-1])
    # debug(f"Description of the field: {l}")
    return (height, width)

def normalize(y, x):
    return y - 1, x - 4


def parse_field(player: int, height, width: int):
    """
    Parse the field.

    First of all, this function is also responsible for determining the next
    move. Actually, this function should rather only parse the field, and return
    it to another function, where the logic for choosing the move will be.

    Also, the algorithm for choosing the right move is wrong. This function
    finds the first position of _our_ character, and outputs it. However, it
    doesn't guarantee that the figure will be connected to only one cell of our
    territory. It can not be connected at all (for example, when the figure has
    empty cells), or it can be connected with multiple cells of our territory.
    That's definitely what you should address.

    Also, it might be useful to distinguish between lowecase (the most recent piece)
    and uppercase letters to determine where the enemy is moving etc.

    The input may look like this:

        01234567890123456
    000 .................
    001 .................
    002 .................
    003 .................
    004 .................
    005 .................
    006 .................
    007 ..O..............
    008 ..OOO............
    009 .................
    010 .................
    011 .................
    012 ..............X..
    013 .................
    014 .................

    :param player int: Represents whether we're the first or second player
    """
    global first_cord
    first_cord=[]

    # debug(f"We got height, width: {height}, {width}")
    map = []
    l = input()
    lines = []
    for y in range(height):
        map_line = []
        l = input()
        # debug(f"Field: {l}")
        for x in range(4, width+4):
            if l.lower()[x] == ".":
                map_line.append(0)
            elif (player == 1 and l.lower()[x] == "o") or (player == 2 and l.lower()[x] == "x"):
                map_line.append(1)
                first_cord.append((y, x))
            else:
                map_line.append(-1)
        # debug(f"Map line : {map_line}, {l}")
        lines.append(l)
        map.append(map_line)
    # Print map
    for y in range(len(map)):
        l = len(map[y])
        # l_original = len(lines[y])
    return map


def parse_figure():
    """
    Parse the figure.

    The function parses the height of the figure (maybe the width would be
    useful as well), and then reads it.
    It would be nice to save it and return for further usage.

    The input may look like this:

    Piece 2 2:
    **
    ..
    """
    figure = []
    l = input()
    debug(f"Piece: {l}")
    # debug(f"parse_figure height: {l.split()}, {l.split()[1]}")
    height = int(l.split()[1])

    for _ in range(height):
        
        l = input()
        figure_line = []
        for x in range(len(l)):
            if l[x] == "*":
                figure_line.append(1)
            else:
                figure_line.append(0)
        figure.append(figure_line)
        debug(f"Piece: {l}")
    # debug(f"Figure: {figure}")
    return figure

def vert_strategy(map, list_of_coordinates, sign_cord):
    y_f_cord= sign_cord[0]
    half_of_field = len(map)/2
    if y_f_cord[0]<half_of_field:
        already_sorted = sorted(list_of_coordinates, key=lambda x: x[0], reverse=True)
    else:
        already_sorted = sorted(list_of_coordinates, key=lambda x: x[0])
    return already_sorted

def goriz_strategy(map, list_of_coordinates, sign_cord):
    x_f_cord= sign_cord[0]
    half_of_field = len(map[2])/2
    if x_f_cord[1]<half_of_field:
        already_sorted = sorted(list_of_coordinates, key=lambda x: x[1], reverse=True)
    else:
        already_sorted = sorted(list_of_coordinates, key=lambda x: x[1])
    return already_sorted


def strategy(map, figure, touch_free_coordinates):
    goriz = len(figure)
    vert = len(figure[0])
    if goriz>vert:
        strategy_coordinates = goriz_strategy(map, touch_free_coordinates, first_cord)
    else:
        strategy_coordinates = vert_strategy(map, touch_free_coordinates, first_cord)
    return strategy_coordinates


def make_move(map, figure):
    touch_free_coordinates = []
    # Find all coordinates that touch free space
    # TODO: fix it, why it takes non accessible coordinates?
    touch_free_coordinates = find_touch_free_coordinates(map)
    touch_free_coordinates = strategy(map, figure, touch_free_coordinates)
    # Sort them
    # debug(f"Touch free coordinates: {touch_free_coordinates}")
    complex_move = try_coordinates(map, touch_free_coordinates, figure)
    debug(f"Complex move: {complex_move}")

    # Try to place the figure on coordiinate in every combination
    my_field_start = map_left_top_corner(map)
    my_figure_end = figure_right_bot_corner(figure)
    # debug(f"my_field_start {my_field_start}")
    # debug(f"my_figure_end {my_figure_end}")
    move = place_figure_on_map(my_figure_end, my_field_start)
    # debug(f"My move {move}")
    # debug(f"Real move: {move}")
    move = complex_move
    return move

def norm(max, val):
    if val>=max:
        return abs(val-max)
    return val

def is_normed(max, val):
    if val>=max:
        return (abs(val-max), True)
    return (val, False)


def try_figure_coordinate_on_map_coordinate(map, map_coordinate, figure, figure_coordinate):
    # debug(f"Try map: {map_coordinate}, figure_coordinate: {figure_coordinate}")
    map_y, map_x = map_coordinate
    figure_y, figure_x = figure_coordinate
    overlaped_times = 0
    tried_coordinates = []
    for y in range(len(figure)):
        for x in range(len(figure[y])):
            if figure[y][x] == 0:
                continue
            # map_y-figure_y+y: Point on map - point of figure + shift inside figure
            # Точка на карті - точка фігури + зсув всередині фігури
            normed_map_y, normed_y = is_normed(len(map), map_y-figure_y+y)
            normed_map_x, normed_x = is_normed(len(map[y]), map_x-figure_x+x)
            tried_coordinates.append(((map_y-figure_y+y, map_x-figure_x+x), (len(map), len(map[y]), (normed_y, normed_x))))
            if figure[y][x] == 1 and (normed_y or normed_x):
                # debug(f"Skipped because value 1 and normed_y: {normed_y}, normed_x: {normed_x}, y,x:{y},{x}")
                return False
            if figure[y][x] == 1 and (normed_map_y < 0 or normed_map_x < 0):
                #debug(f"Skipped because value 1 and normed_map_y: {normed_map_y}, normed_map_x: {normed_map_x}, y,x:{y},{x}")
                return False
            # if figure[y][x] == 1 and (map_y - figure_y < 0 or map_x - figure_x < 0):
            #     debug(f"Skipped because figure[y][x] == 1 and map_y - figure_y: {map_y - figure_y}, map_x - figure_x: {map_x - figure_x}, y,x:{y},{x}")
            #     return False
            if figure[y][x] == 1 and (map_y-figure_y+y < 0 or map_x-figure_x+x < 0):
                #debug(f"Skipped because map_y-figure_y+y: {map_y-figure_y+y}, map_x-figure_x+x: {map_x-figure_x+x}, y,x:{y},{x}")
                return False
            # normed_map_y = norm(len(map), map_y-figure_y+y)
            # normed_map_x = norm(len(map[y]), map_x-figure_x+x)
            map_value = map[normed_map_y][normed_map_x]
            # map_value = map[map_y][map_x]
            figure_value = figure[y][x]
            overlap = overlapping(map_value, figure_value)
            # debug(f"overlap: {overlap}")
            if overlap == -1:
                #debug(f"Skipped overlap == -1: {overlap}")
                return False
            if overlap == 1:
                overlaped_times += 1
            if overlaped_times > 1:
                #debug(f"Skipped overlap > 1: {overlap}")
                return False
    if overlaped_times == 1:
        # print coordinates here
        #debug(f"Tried coordinates: {tried_coordinates}")
        return True
    return False

def overlapping(map_val, figure_val):
    if figure_val == 1:
        if map_val == 1:
            return 1
        if map_val == -1:
            return -1
    return 0


def success_put_figure(map, coordinate, figure):
    for y in range(len(figure)):
        for x in range(len(figure[y])):
            if try_figure_coordinate_on_map_coordinate(map, coordinate, figure, (y, x)):
                coordinate_y, coordinate_x = coordinate
                # debug(f"Success in: y: {coordinate_y} - {y} = {coordinate_y-y}, x: {coordinate_x} - {x} = {coordinate_x-x}")
                return (True, (coordinate_y-y, coordinate_x-x))
    return (False, (0, 0))

def try_coordinates(map, coordinates_list, figure):
    for coordinate in coordinates_list:
        success, success_coordinates = success_put_figure(map, coordinate, figure)
        if success:
            return success_coordinates
    debug(f"Can't make move")
    return None

def is_touch_free_coordinate(map, coordinate):
    y, x = coordinate
    if map[y-1][x] == 0:
        return True

    if y == len(map) - 1:
        if map[0][x] == 0:
            return True
    else:
        if map[y+1][x] == 0:
            return True

    if x == len(map[y]) - 1:
        if map[y][0] == 0:
            return True
    else:
        if map[y][x+1] == 0:
            return True

    if map[y][x-1] == 0:
        return True
    return True

    

def find_touch_free_coordinates(map):
    res = []
    res.clear()
    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[y][x] == 1 and is_touch_free_coordinate(map, (y, x)):
                res.append((y, x))
    return res

def map_left_top_corner(map):
    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[y][x] == 1:
                return (y, x)
    return (0, 0)

def figure_right_bot_corner(figure):
    my_field_end = (0, 0)
    for y in range(len(figure)):
        for x in range(len(figure[y])):
            if figure[y][x] == 1:
                my_field_end = (y, x)
    return my_field_end

def place_figure_on_map(figure_end, field_start):
    field_y, field_x = field_start
    figure_y, figure_x = figure_end
    return (field_y-figure_y, field_x-figure_x)



def step(player: int):
    """
    Perform one step of the game.

    :param player int: Represents whether we're the first or second player
    """
    move = None
    height, width = parse_field_info()
    map = parse_field(player, height, width)
    figure = parse_figure()
    # move is coordinates of left top corner of figure on map
    move = make_move(map, figure)
    return move


def play(player: int):
    """
    Main game loop.

    :param player int: Represents whether we're the first or second player
    """
    # debug(f"Player info: {player}")
    # debug(f"-------------------------Player ${player} move started-------------------------")
    while True:
        move = step(player)
        print(*move)
        # debug(f"-------------------------Player ${player} move ended-------------------------")


def parse_info_about_player():
    """
    This function parses the info about the player

    It can look like this:

    $$$ exec p2 : [./player1.py]
    """
    i = input()
    # debug(f"Info about the player: {i}")
    return 1 if "p1 :" in i else 2


def main():
    player = parse_info_about_player()
    try:
        play(player)
    except TypeError:
        debug("Cannot get input. Seems that we've lost ):")
    except EOFError:
        debug("Cannot get input. Seems that we've lost ):")


if __name__ == "__main__":
    main()
