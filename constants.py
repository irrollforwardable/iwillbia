# -*- coding: utf8 -*-

# Iwillbia
# Copyright (C) 2018 Žans Kļimovičs
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

APP_NAME = "Iwillbia"
APP_VERSION = "Pre-Alpha"
LEFT = 0
RIGHT = 1
PUNCTUATION_MARKS = ('.', ',', ';', '-', ':')
SEPARATORS = (' ', '\n')
ACTION_TITLE = 0
ACTION_FUNCTION = 1
HIDE_X = 30  # used for Poolables in order to hide outside the "viewport"
HIDE_Y = 1
FIRST_GAMEPLAY_SEQUENCE_NUM = 1

# Commands
CMD_JUMP = 100
CMD_LEFT = 101
CMD_RIGHT = 102
CMD_UP = 103
CMD_DOWN = 104
CMD_TRANSFORM = 105
CMD_1 = 1
CMD_2 = 2
CMD_3 = 3
CMD_4 = 4
CMD_5 = 5
CMD_6 = 6
CMD_7 = 7
CMD_8 = 8
CMD_9 = 9
CMD_0 = 0

# Blinking
BLINK_DIE = 1
BLINK_HURT = 2
BLINK_EXPLODE = 3

# Editor windows
DLG_ACTIONS = 1
DLG_CHANGES = 2
DLG_FUNCTIONS = 3

# DB column types
COL_TYPE_NULL = 0
COL_TYPE_CHAR = 1
COL_TYPE_NUMBER = 2
