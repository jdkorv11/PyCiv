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

        self.cities[(1, 1)] = City(Player.red, 1, 6, GameConstants.food_focus, GameConstants.archer)
        self.cities[(1, 4)] = City(Player.blue, 1, 6, GameConstants.production_focus, GameConstants.legion)

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
            city.unit_produced = unit_type

    def perform_unit_action_at(self, position):
        return None

    def add_unit_by_city(self, target_city, unit):
        target_position = None
        for position, city in self.cities.items():
            if city == target_city:
                print(position)
                target_position = position

        target_position = self.get_available_position(target_position)
        self.units[target_position] = unit

    def get_available_position(self, target_position):
        test_position = target_position
        target_x = target_position[0]
        target_y = target_position[1]
        can_return = True

        while self.get_unit(test_position) is not None or not can_return:
            old_x = test_position[0]
            old_y = test_position[1]
            radius = self.distance(target_position, test_position)

            if radius == 0:
                test_position = old_x, old_y - 1
            # go to the next ring out
            elif old_x + 1 == target_x and old_y < target_y:
                test_position = old_x + 1, old_y - 1
            # top edge
            elif target_y - old_y == radius:
                if old_x - target_x == radius:
                    test_position = old_x, old_y + 1
                else:
                    test_position = old_x + 1, old_y
            # right edge
            elif old_x - target_x == radius:
                if old_y - target_y == radius:
                    test_position = old_x - 1, old_y
                else:
                    test_position = old_x, old_y + 1
            # bottom edge
            elif old_y - target_y == radius:
                if target_x - old_x == radius:
                    test_position = old_x, old_y - 1
                else:
                    test_position = old_x - 1, old_y
            # left edge
            else:
                if target_y - old_y == radius:
                    test_position = old_x + 1, old_y
                else:
                    test_position = old_x, old_y - 1
            can_return = self.is_valid_position(test_position) and self.can_be_occupied(self.get_tile(test_position))

        return test_position


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
    def __init__(self, owner, size, production, work_focus, unit_produced):
        self.owner = owner
        self.size = size
        self.production = production
        self.work_focus = work_focus
        self.treasury = 0
        self.unit_produced = unit_produced

    def update(self, world):
        self.treasury += self.production
        if self.can_produce_unit():
            self.produce_unit(world)

    def can_produce_unit(self):
        unit_cost = Unit.get_cost(self.unit_produced)
        return self.treasury >= unit_cost

    def produce_unit(self, world):
        new_unit = Unit(self.unit_produced, self.owner)
        world.add_unit_by_city(self, new_unit)
        self.treasury -= Unit.get_cost(self.unit_produced)


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

    @staticmethod
    def get_cost(type):
        if type == GameConstants.archer:
            return 10
        if type == GameConstants.legion:
            return 15
        if type == GameConstants.settler:
            return 30