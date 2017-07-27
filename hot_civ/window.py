import pygame
from hot_civ.constants import *


class Window:
    TILE_WIDTH = 30
    black = (123, 0, 123)

    def __init__(self):
        pygame.init()

        screen_size = self.TILE_WIDTH * GameConstants.worldsize
        self.screen = pygame.display.set_mode([screen_size, screen_size])

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

        self.red_background = pygame.image.load('resource/red.gif')
        self.blue_background = pygame.image.load('resource/blue.gif')
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

    def draw(self, world):
        self.screen.fill(self.black)
        pygame.display.flip()
        self.draw_tiles(world.tiles)
        self.draw_cities(world.cities)
        self.draw_units(world.units)
        pygame.display.flip()

    def draw_tiles(self, tiles):
        for key in tiles.keys():
            x_offset = key[1] * self.TILE_WIDTH
            y_offset = key[0] * self.TILE_WIDTH
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
            x_offset = key[1] * self.TILE_WIDTH
            y_offset = key[0] * self.TILE_WIDTH

            city = cities[key]
            if city is None:
                return

            city_rect = self.city_img.get_rect()
            city_rect.x = x_offset
            city_rect.y = y_offset

            owner = city.owner
            if owner == Player.red:
                self.screen.blit(self.red_background, city_rect)
            else:
                self.screen.blit(self.blue_background, city_rect)

            self.screen.blit(self.city_img, city_rect)

    def draw_units(self, units):
        for key in units.keys():
            x_offset = key[1] * self.TILE_WIDTH
            y_offset = key[0] * self.TILE_WIDTH

            unit = units[key]
            if unit is None:
                return

            unit_rect = self.city_img.get_rect()
            unit_rect.x = x_offset
            unit_rect.y = y_offset

            self.screen.blit(self.unit_images[unit.type][unit.owner], unit_rect)

    def get_ocean_image(self, key, tiles):
        row = key[0]
        column = key[1]

        land_north = False if row == 0 else tiles[(row - 1, column)].type != GameConstants.oceans
        land_east = False if column == GameConstants.worldsize else tiles[
                                                                        (row, column + 1)].type != GameConstants.oceans
        land_south = False if row == GameConstants.worldsize else tiles[(row + 1, column)].type != GameConstants.oceans
        land_west = False if column == 0 else tiles[(row, column - 1)].type != GameConstants.oceans

        return self.ocean_images.get((land_north, land_east, land_south, land_west))
