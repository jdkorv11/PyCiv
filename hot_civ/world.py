from hot_civ.constants import *
import math


class World:
    size = GameConstants.world_size

    tiles = {}
    units = {}
    cities = {}

    age = None

    def __init__(self):
        for row in range(self.size):
            for column in range(self.size):
                self.tiles[(row, column)] = Tile(GameConstants.plains)
        self.tiles[(1, 0)] = Tile(GameConstants.hills)
        self.tiles[(0, 1)] = Tile(GameConstants.oceans)
        self.tiles[(2, 2)] = Tile(GameConstants.mountains)

        self.units[(0, 2)] = Unit(GameConstants.archer, Player.red)
        self.units[(2, 3)] = Unit(GameConstants.legion, Player.blue)
        self.units[(3, 4)] = Unit(GameConstants.settler, Player.red)

        self.cities[(1, 1)] = City(Player.red, 1, 6, GameConstants.food_focus)
        self.cities[(1, 4)] = City(Player.blue, 1, 6, GameConstants.production_focus)

        self.age = -2000

    def get_tile(self, position):
        return self.tiles.get(position)

    def get_unit(self, position):
        return self.units.get(position)

    def get_city(self, position):
        return self.cities.get(position)

    def move_unit(self, position_from, position_to):
        # if position to is a valid position
        tile_to = self.get_tile(position_to)
        if tile_to is None:
            return False
        # if position to is able to be occupied
        if not self.can_be_occupied(tile_to):
            return False
        # if position from has a unit
        unit = self.get_unit(position_from)
        if unit is None:
            return False
        # if path between positions is able to be moved by unit
        if self.distance(position_from, position_to) > unit.move_count:
            return False
        # move unit and lower unit move_count
        self.units[position_to] = self.units.pop(position_from)
        unit.move_count -= self.distance(position_from, position_to)

        return True

    def change_work_force_focus_in_city_at(self, position, balance):
        city = self.get_city(position)
        if city is not None:
            city.work_focus = balance

    def change_production_in_city(self, position, unit_type):
        city = self.get_city(position)
        if city is not None:
            city.production = unit_type

    def perform_unit_action_at(self, position):
        return None

    def is_valid_position(self, position):
        return 0 <= position[0] < self.size and 0 <= position[1] < self.size

    @staticmethod
    def can_be_occupied(tile):
        if GameConstants.plains == tile.type or \
                        GameConstants.forest == tile.type or \
                        GameConstants.hills == tile.type:
            return True
        return False

    @staticmethod
    def distance(position_from, position_to):
        row_distance = math.fabs(position_from[0] - position_to[0])
        column_distance = math.fabs(position_from[1] - position_to[1])
        if row_distance > column_distance:
            return math.trunc(row_distance)
        return math.trunc(column_distance)


class City:
    def __init__(self, owner, size, production, work_focus):
        self.owner = owner
        self.size = size
        self.production = production
        self.work_focus = work_focus


class Tile:
    def __init__(self, type):
        self.type = type


class Unit:
    def __init__(self, type, owner):
        self.type = type
        self.owner = owner
        if self.type == GameConstants.archer:
            self.move_count = 1
            self.speed = 1
            self.defense = 3
            self.attack = 2
        elif self.type == GameConstants.legion:
            self.move_count = 1
            self.speed = 1
            self.defense = 2
            self.attack = 4
        elif self.type == GameConstants.settler:
            self.move_count = 1
            self.speed = 1
            self.defense = 3
            self.attack = 0
