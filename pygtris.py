# This file is part of pygtris.

# pygtris is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pygtris is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pygtris.  If not, see <http://www.gnu.org/licenses/>.

# Copyright Erik Ruiter,  2017

import pyglet
from pyglet.window import key
import random
from shapes import *
from backgrounds import *
from pyglet.gl import *
import os

board_lines = 20
board_cols = 10
block_width = 32
block_height = 32
full_screen = False


class Box():
    def __init__(self, x, y, width, height, border, color, alpha):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.border = border
        self.color = color
        self.alpha = alpha

    def draw(self):
        self.back1 = pyglet.image.SolidColorImagePattern((self.color[0], self.color[1], self.color[2], self.alpha[0])).create_image(self.width, self.height)
        self.back2 = pyglet.image.SolidColorImagePattern((self.color[0], self.color[1], self.color[2], self.alpha[1])).create_image(self.width - (self.border * 2), self.height - (self.border * 2))

        self.back1.blit(self.x, self.y)
        self.back2.blit(self.x + self.border, self.y + self.border)


class Pygtris(pyglet.window.Window):
    def __init__(self, width=900, height=680, fullscreen=full_screen):
        super(Pygtris, self).__init__(width=1000, height=680, fullscreen=full_screen)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.logo = pyglet.resource.image('logo.png')
        self.backgrounds = list()
        self.init_backgrounds()
        self.alphaimage = pyglet.image.SolidColorImagePattern((0, 0, 0, 150)).create_image(self.width, self.height)
        self.alphaimage.width = block_width * board_cols
        self.alphaimage.height = block_height * board_lines

        self.board_x = 10
        self.board_y = 20

        self.scorebox = Box(350, 100, 400, 200, 10, (0, 0, 0), (150, 100))
        self.stats_label = pyglet.text.Label("Press SPACE to start!",
                                             font_name='Times New Roman',
                                             font_size=36,
                                             x=600, y=200,
                                             anchor_x='center', anchor_y='center', multiline=True, width=400)
        self.nextbox = Box(350, 500, 5 * 32, 5 * 32, 10, (0, 0, 0), (150, 100))
        self.tet = Box(0, 0, block_width, block_height, 5, (255, 255, 255), (200, 255))

        pyglet.clock.schedule_interval(self.tick, 0.04)
        self.game_state = "start"
        self.init_game()

    def init_game(self):
        self.level = 1
        self.lines = 0
        self.score = 0
        self.fallscore = 0
        self.repeatdelay = 0
        self.agrid = Grid()
        self.ablock = Block(block_list[random.randint(1, 7)])
        self.nextblock = Block(block_list[random.randint(1, 7)])
        self.falltimer = 0
        self.keypressed = "none"

    def init_backgrounds(self):

        dir = os.getcwd() + "/backgrounds/"
        print dir
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [f for f in listdir(dir) if isfile(join(dir, f))]

        all_backgrounds_present = True
        for i in range(0, len(background_urls)):
            if "level" + str(i + 1) + ".jpg" not in onlyfiles:
                all_backgrounds_present = False

        if all_backgrounds_present is False:
            for i in range(0, len(background_urls)):
                download_background(background_urls[i], dir + "level" + str(i + 1) + ".jpg")
            pyglet.resource.reindex()

        for i in range(0, len(background_urls)):
            self.backgrounds.append(pyglet.resource.image("backgrounds/level" + str(i + 1) + ".jpg"))
        for i in self.backgrounds:
            i.width = self.width
            i.height = self.height

    def on_key_press(self, symbol, modifiers):

        if symbol == key.DOWN:
            self.keypressed = 'down'
        elif symbol == key.LEFT:
            self.keypressed = 'left'
        elif symbol == key.RIGHT:
            self.keypressed = 'right'

        if symbol == key.Q:
            exit()

        if symbol == key.SPACE and self.game_state == "start":
            self.init_game()
            self.agrid.block_action(self.ablock, "lit")
            self.game_state = "running"

        if symbol == key.P and self.game_state == "paused":
            self.game_state = "running"
        elif symbol == key.P and self.game_state == "running":
            self.game_state = "paused"

        if symbol == key.UP and self.game_state == "running":
            self.agrid.block_action(self.ablock, "dim")
            self.handle_block_move(self.ablock, "up")
            self.agrid.block_action(self.ablock, "lit")

    def on_key_release(self, symbol, modifiers):
        if symbol == key.DOWN:
            self.score += round(self.fallscore)
            self.fallscore = 0
        self.keypressed = "none"
        self.repeatdelay = 0

    def handle_keys(self):
        if self.game_state == "running":
            if self.keypressed != 'none':
                self.repeatdelay += 1
                print self.repeatdelay
            if self.repeatdelay == 1 or self.repeatdelay > 3 or self.keypressed == "down":
                self.agrid.block_action(self.ablock, "dim")
                self.handle_block_move(self.ablock, self.keypressed)

                self.agrid.block_action(self.ablock, "lit")

    def tick(self, dt):
        self.handle_keys()
        if self.game_state == "running":
            self.falltimer += (self.level * 1) + 1
        if self.falltimer > 20:
            self.handle_falltimer()

    def handle_falltimer(self):
        if self.game_state == "running":
            self.falltimer = 0

            # move block one row down
            self.agrid.block_action(self.ablock, "dim")
            result = self.handle_block_move(self.ablock, "down")
            self.agrid.block_action(self.ablock, "lit")

            if result is False:

                self.agrid.block_action(self.ablock, "fix")
                if self.ablock.line == 0:
                    self.game_state = "start"
                    self.stats_label.text = "GAME OVER!"
                self.ablock = self.nextblock
                self.nextblock = Block(block_list[random.randint(1, 7)])

                result = self.agrid.check_for_lines()
                self.score += result * 10
                self.lines += result
                self.level = (self.lines / 1) + 1
                self.repeatdelay = 0

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Draw background
        if self.level <= 8:
            self.backgrounds[self.level - 1].blit(0, 0)
        if self.level > 8:
            self.backgrounds[8 - 1].blit(0, 0)

        # Draw logo
        self.logo.blit(320, 300)

        # Draw board box
        self.alphaimage.blit(self.board_x, self.board_y)

        # draw grid including blocks
        self.draw_blocks(self.agrid, self.board_x, self.board_y)

        self.scorebox.draw()
        self.nextbox.draw()
        self.stats_label.draw()
        if self.game_state == "running":
            self.draw_nextblock(350 - 32, 500 - 32)
            self.stats_label.text = "level: %s\nlines: %s\nscore: %s" % (self.level, self.lines, int(self.score))

    def draw_blocks(self, grid, xoffset, yoffset):
        for v in range(1, board_lines + 1):
            for h in range(1, board_cols + 1):
                if grid.grid[v][h] > 0:
                    self.tet.x = (h - 1) * block_width + xoffset
                    self.tet.y = (-v + board_lines) * block_height + yoffset
                    self.tet.color = block_list[int(grid.grid[v][h])]['color']
                    self.tet.draw()

    def draw_nextblock(self, xoffset, yoffset):
        nexttet = Box(0, 0, block_width, block_height, 5, (255, 255, 255), (200, 255))

        x = 1
        y = 1
        for i in self.nextblock.block_data['form'][0]:
            if i == 1:
                nexttet.x = (y * block_width) + xoffset
                nexttet.y = (x * block_height) + yoffset
                nexttet.color = self.nextblock.color
                # print self.nextblock.color, self.nextblock.id, self.nextblock.index
                nexttet.draw()

            x += 1
            if x > 4:
                x = 1
                y += 1

    def handle_block_move(self, block, direction):

        if direction == "down":
            block.line += 1
        if direction == "up":
            block.rotate()
        if direction == "left":
            block.pos -= 1
        if direction == "right":
            block.pos += 1

        block_state = "ok"
        x = 1
        y = 1
        for i in block.form:

            if i == 1:
                if direction == "down" and (y + block.line - 1 > board_lines or x + block.pos - 1 > board_cols):
                    block_state = "bottom_collision"
                if direction == "right" and (y + block.line - 1 > board_lines or x + block.pos - 1 > board_cols):
                    block_state = "right_collision"
                if direction == "left" and (y + block.line - 1 > board_lines or x + block.pos - 1 < 1):
                    block_state = "left_collision"
                if direction == "up" and (y + block.line - 1 > board_lines or x + block.pos - 1 > board_cols):
                    block_state = "rotate_collision"
                if direction == "up" and (y + block.line - 1 > board_lines or x + block.pos - 1 < 1):
                    block_state = "rotate_collision"
                if block_state == "ok" and self.agrid.grid[y + block.line - 1][x + block.pos - 1] != 0:
                    block_state = "block_collision"

                if block_state != "ok":
                    if direction == "down":
                        block.line -= 1
                    if direction == "right":
                        block.pos -= 1
                    if direction == "left":
                        block.pos += 1
                    if direction == "up":
                        block.rotate_back()
                    return False

                if block_state == "ok" and direction == "down":
                    self.fallscore += 0.1

            x += 1
            if x > 4:
                x = 1
                y += 1

        return True


class Grid():

    def __init__(self):
        self.grid = list()
        for i in range(0, board_lines + 1):
            self.grid.append([0] * (board_cols + 1))

    def print_grid(self):
        for x in self.grid:
            strings = map(str, x)
            print "".join(strings)

    def block_action(self, block, action):
        if action == "lit":
            value = block.id
        if action == "dim":
            value = 0
        if action == "fix":
            value = block.id

        x = 1
        y = 1
        for i in block.form:
            if i == 1:
                self.grid[y + block.line - 1][x + block.pos - 1] = value
            x += 1
            if x > 4:
                x = 1
                y += 1

    def check_for_lines(self):
        newgrid = list()
        lineindexes = list()

        # iterate throug all lines, and check,
        # if there a lines having a single 0 (at index 0) on the board

        for index in range(1, board_lines + 1):
            if self.grid[index].count(0) == 1:
                lineindexes.append(index)

        # if there are lines found, generate a new grid with the lines removed,
        # and empty space on top
        print "lineindexes", len(lineindexes)
        if len(lineindexes) > 0:
            newgrid.append([0] * (board_cols + 1))
            for i in lineindexes:
                newgrid.append([0] * (board_cols + 1))

            for index in range(1, board_lines + 1):
                if index not in lineindexes:
                    newgrid.append(self.grid[index])
            self.grid = newgrid

        return len(lineindexes)


class Block():

    def __init__(self, data):
        self.block_data = data
        self.index = 0
        self.id = self.block_data['id']
        self.color = self.block_data['color']
        self.form = self.block_data['form'][0]
        self.line = 0
        self.pos = 4

    def rotate(self):
        if self.index < len(self.block_data['form']) - 1:
            self.index += 1
        else:
            self.index = 0

        self.form = self.block_data['form'][self.index]

    def rotate_back(self):
        if self.index > 0:
            self.index -= 1
        else:
            self.index = len(self.block_data['form']) - 1

        self.form = self.block_data['form'][self.index]


window = Pygtris()
pyglet.app.run()
