from hot_civ.constants import Player
from hot_civ.world import World
from hot_civ.window import Window


class Game:
    def __init__(self, initial_player):
        self.current_player = initial_player

    def get_winner(self):
        return self.current_player

    def end_of_turn(self):
        if self.current_player == Player.red:
            self.current_player = Player.blue
        else:
            self.current_player = Player.red


def main():
    game = Game(Player.red)
    world = World()

    window = Window()
    window.draw(world)

    while 1:
        i = 1

if __name__ == "__main__":
    main()
