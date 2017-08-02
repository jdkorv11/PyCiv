import pygame
from hot_civ.constants import *
import math


class Window:
    TILE_WIDTH = 30
    black = (0, 0, 0)
    BOARDER_TOP_MARGIN = 15
    BOARDER_LEFT_MARGIN = 19
    BACKGROUND_WIDTH = 665
    BACKGROUND_HEIGHT = 510

    def __init__(self):
        pygame.init()

        self.background_img = pygame.image.load('resource/hotciv-background.gif')

        self.screen = pygame.display.set_mode([self.BACKGROUND_WIDTH, self.BACKGROUND_HEIGHT])

        self.shield_images = {
            Player.red: pygame.image.load('resource/shield_red.gif'),
            Player.blue: pygame.image.load('resource/shield_blue.gif')
        }

        self.ocean_images = {
            (True, True, True, True): pygame.image.load('resource/ocean1111.gif'),
            (True, True, True, False): pygame.image.load('resource/ocean1110.gif'),
            (True, True, False, True): pygame.image.load('resource/ocean1101.gif'),
            (True, True, False, False): pygame.image.load('resource/ocean1100.gif'),
            (True, False, True, True): pygame.image.load('resource/ocean1011.gif'),
            (True, False, True, False): pygame.image.load('resource/ocean1010.gif'),
            (True, False, False, True): pygame.image.load('resource/ocean1001.gif'),
            (True, False, False, False): pygame.image.load('resource/ocean1000.gif'),
            (False, True, True, True): pygame.image.load('resource/ocean0111.gif'),
            (False, True, True, False): pygame.image.load('resource/ocean0110.gif'),
            (False, True, False, True): pygame.image.load('resource/ocean0101.gif'),
            (False, True, False, False): pygame.image.load('resource/ocean0100.gif'),
            (False, False, True, True): pygame.image.load('resource/ocean0011.gif'),
            (False, False, True, False): pygame.image.load('resource/ocean0010.gif'),
            (False, False, False, True): pygame.image.load('resource/ocean0001.gif'),
            (False, False, False, False): pygame.image.load('resource/ocean0000.gif'),
        }

        self.plains_img = pygame.image.load('resource/plains.gif')
        self.mountain_img = pygame.image.load('resource/mountain.gif')
        self.forest_img = pygame.image.load('resource/forest.gif')
        self.hills_img = pygame.image.load('resource/hills.gif')

        self.city_backgrounds = {
            Player.red:  pygame.image.load('resource/red.gif'),
            Player.blue:  pygame.image.load('resource/blue.gif')
        }
        self.city_img = pygame.image.load('resource/city.gif')

        self.unit_images = {}
        archers = {Player.red: pygame.image.load('resource/archer_red.gif'),
                   Player.blue: pygame.image.load('resource/archer_blue.gif'),
                   Player.yellow: pygame.image.load('resource/archer_yellow.gif'),
                   Player.green: pygame.image.load('resource/archer_green.gif')}
        self.unit_images[GameConstants.archer] = archers
        legions = {Player.red: pygame.image.load('resource/legion_red.gif'),
                   Player.blue: pygame.image.load('resource/legion_blue.gif'),
                   Player.yellow: pygame.image.load('resource/legion_yellow.gif'),
                   Player.green: pygame.image.load('resource/legion_green.gif')}
        self.unit_images[GameConstants.legion] = legions
        settlers = {Player.red: pygame.image.load('resource/settler_red.gif'),
                    Player.blue: pygame.image.load('resource/settler_blue.gif'),
                    Player.yellow: pygame.image.load('resource/settler_yellow.gif'),
                    Player.green: pygame.image.load('resource/settler_green.gif')}
        self.unit_images[GameConstants.settler] = settlers

    def get_world_position(self, pos):
        row = math.floor((pos[0] - self.BOARDER_LEFT_MARGIN) / self.TILE_WIDTH)
        column = math.floor((pos[1] - self.BOARDER_TOP_MARGIN) / self.TILE_WIDTH)
        return row, column

    def draw(self, game):
        self.screen.blit(self.background_img, self.background_img.get_rect())
        self.draw_world(game.world)
        self.draw_side_menu(game)
        pygame.display.flip()

    def draw_world(self, world):
        self.draw_tiles(world.tiles)
        self.draw_cities(world.cities)
        self.draw_units(world.units.copy())

    def draw_side_menu(self, game):
        self.draw_current_player(game.current_player)
        self.draw_selected_unit(game)
        self.draw_selected_city(game)

    def draw_selected_city(self, game):
        if game.focused_position is not None and game.world.get_city(game.focused_position) is not None:
            city = game.world.get_city(game.focused_position)

            city_background = self.city_backgrounds[city.owner]
            city_rect = city_background.get_rect()
            city_rect.x = 535
            city_rect.y = 365

            self.screen.blit(city_background, city_rect)
            self.screen.blit(self.city_img, city_rect)

            shield_img = self.shield_images[city.owner]
            shield_rect = shield_img.get_rect()
            shield_rect.x = 595
            shield_rect.y = 342
            self.screen.blit(shield_img, shield_rect)



    def draw_selected_unit(self, game):
        if game.focused_position is not None and game.world.get_unit(game.focused_position) is not None:
            unit = game.world.get_unit(game.focused_position)
            unit_image = self.unit_images[unit.type][unit.owner]

            rect = unit_image.get_rect()
            rect.x = 535
            rect.y = 190
            self.screen.blit(unit_image, rect)

            shield_img = self.shield_images[unit.owner]
            rect = shield_img.get_rect()
            rect.x = 594
            rect.y = 188
            self.screen.blit(shield_img, rect)

            # TODO render moves left

    def draw_current_player(self, player):
        rect = self.shield_images[player].get_rect()
        rect.x = 558
        rect.y = 65
        self.screen.blit(self.shield_images[player], rect)

    def draw_tiles(self, tiles):
        for key in tiles.keys():
            x_offset = key[0] * self.TILE_WIDTH + self.BOARDER_LEFT_MARGIN
            y_offset = key[1] * self.TILE_WIDTH + self.BOARDER_TOP_MARGIN
            tile_type = tiles[key].type

            if tile_type == GameConstants.plains:
                image = self.plains_img
            elif tile_type == GameConstants.oceans:
                image = self.get_ocean_image(key, tiles)
            elif tile_type == GameConstants.forest:
                image = self.forest_img
            elif tile_type == GameConstants.hills:
                image = self.hills_img
            else:
                image = self.mountain_img

            tile_rect = image.get_rect()
            tile_rect.x = x_offset
            tile_rect.y = y_offset

            self.screen.blit(image, tile_rect)

    def draw_cities(self, cities):
        for key in cities.keys():
            x_offset = key[0] * self.TILE_WIDTH + self.BOARDER_LEFT_MARGIN
            y_offset = key[1] * self.TILE_WIDTH + self.BOARDER_TOP_MARGIN

            city = cities[key]
            if city is None:
                return

            city_rect = self.city_img.get_rect()
            city_rect.x = x_offset
            city_rect.y = y_offset

            self.screen.blit(self.city_backgrounds[city.owner], city_rect)
            self.screen.blit(self.city_img, city_rect)

    def draw_units(self, units):
        keys = units.keys()
        for key in keys:
            unit = units.get(key)
            if unit is None:
                return

            x_offset = key[0] * self.TILE_WIDTH + self.BOARDER_LEFT_MARGIN
            y_offset = key[1] * self.TILE_WIDTH + self.BOARDER_TOP_MARGIN

            image = self.unit_images[unit.type][unit.owner]
            unit_rect = image.get_rect()
            unit_rect.x = x_offset
            unit_rect.y = y_offset

            self.screen.blit(image, unit_rect)

    def get_ocean_image(self, key, tiles):
        x = key[0]
        y = key[1]

        land_north = False if y == 0 else tiles[(y - 1, x)].type != GameConstants.oceans
        land_east = False if x == GameConstants.world_size else tiles[
                                                                         (y, x + 1)].type != GameConstants.oceans
        land_south = False if y == GameConstants.world_size else tiles[(y + 1, x)].type != GameConstants.oceans
        land_west = False if x == 0 else tiles[(y, x - 1)].type != GameConstants.oceans

        return self.ocean_images.get((land_north, land_east, land_south, land_west))
