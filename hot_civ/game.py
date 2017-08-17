from hot_civ.constants import Player
from hot_civ.world import World
from hot_civ.window import Window
import pygame, sys


class Game:
    def __init__(self, initial_player):
        self.current_player = initial_player
        self.world = World()
        self.focused_position = None

    def get_winner(self):
        if self.world.age == 0:
            return Player.red
        return None

    def end_of_turn(self):
        # age the world
        self.world.age += 100

        # check for winner
        winner = self.get_winner()
        if winner is not None:
            print(winner + ' Wins!')

        # reset the movement count of all units
        for unit in self.world.units.values():
            unit.move_count = unit.speed

        # update all the cities of the player who just completed his turn
        for city in self.world.cities.values():
            if city.owner == self.current_player:
                city.update(self.world)

        # change the current player
        if self.current_player == Player.red:
            self.current_player = Player.blue
        else:
            self.current_player = Player.red

    def selection_at(self, position):
        self.focused_position = position

    def action_at(self, position):
        if self.focused_position is not None:
            unit = self.world.get_unit(self.focused_position)
            if unit is not None and unit.owner == self.current_player:
                self.world.move_unit(self.focused_position, position)
            self.focused_position = None


def main():
    pygame.init()

    game = Game(Player.red)

    window = Window()

    while 1:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                position = window.get_world_position(event.pos)
                print(position)
                if position[0] > 15:
                    game.end_of_turn()
                if event.button == 1:
                    game.selection_at(position)
                if event.button == 3:
                    game.action_at(position)

        window.draw(game)

if __name__ == "__main__":
    main()
