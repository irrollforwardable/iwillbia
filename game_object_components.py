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

import functions


class Action(object):
    """
    self_changes - changes of attributes of self when action is executed
    subject_changes - changes of attributes of subject (game object upon which the action is executed)
    """
    def __init__(self, db_connection, db_pk_id):
        """
        Create new action by setting the fields from database
        :param db_connection: database connection
        :param db_pk_id: database id of the action
        """
        self.db_id = db_pk_id
        self.title = ""
        self.self_changes = Changes()
        self.subject_changes = Changes()
        self.execute = None
        cursor = db_connection.cursor()

        # Action header info
        cursor.execute("select a.title, lower(f.name) " +
                       "from actions a, functions f " +
                       "where a.function_id = f.id and a.id = ?",
                       (db_pk_id,))
        db_rows = cursor.fetchall()

        if db_rows:
            self.title = db_rows[0][0]
            self.execute = getattr(functions, db_rows[0][1])

        # Self changes
        cursor.execute("select ch.health, ch.is_health_absolute, ch.x_energy, ch.is_x_energy_absolute, " +
                       "ch.y_energy, ch.is_y_energy_absolute, ch.jump_power, ch.is_jump_power_absolute, " +
                       "ch.capacity, ch.is_capacity_absolute, ch.bullets, ch.is_bullets_absolute, " +
                       "ch.coins, ch.is_coins_absolute " +
                       "from actions a, changes ch " +
                       "where a.id = ? " +
                       "and a.self_changes_id = ch.id ", (db_pk_id,))
        db_rows = cursor.fetchall()

        if db_rows:
            self.self_changes.set_all_fields(db_rows[0][0], db_rows[0][1], db_rows[0][2], db_rows[0][3], db_rows[0][4],
                                             db_rows[0][5], db_rows[0][6], db_rows[0][7], db_rows[0][8], db_rows[0][9],
                                             db_rows[0][10], db_rows[0][11], db_rows[0][12], db_rows[0][13])

        # Subject changes
        cursor.execute("select ch.health, ch.is_health_absolute, ch.x_energy, ch.is_x_energy_absolute, " +
                       "ch.y_energy, ch.is_y_energy_absolute, ch.jump_power, ch.is_jump_power_absolute, " +
                       "ch.capacity, ch.is_capacity_absolute, ch.bullets, ch.is_bullets_absolute, " +
                       "ch.coins, ch.is_coins_absolute " +
                       "from actions a, changes ch " +
                       "where a.id = ? " +
                       "and a.subject_changes_id = ch.id ", (db_pk_id,))
        db_rows = cursor.fetchall()

        if db_rows:
            self.subject_changes.set_all_fields(db_rows[0][0], db_rows[0][1], db_rows[0][2], db_rows[0][3],
                                                db_rows[0][4], db_rows[0][5], db_rows[0][6], db_rows[0][7],
                                                db_rows[0][8], db_rows[0][9], db_rows[0][10], db_rows[0][11],
                                                db_rows[0][12], db_rows[0][13])

    def __repr__(self):
        return self.db_id


class Changes(object):
    """
    List of changes to attributes of a game object. Contained by word meaning.
    """
    def __init__(self, health_change=0, is_health_change_value_absolute=False,
                 x_energy_change=0, is_x_energy_change_value_absolute=False,
                 y_energy_change=0, is_y_energy_change_value_absolute=False,
                 jump_power_change=0, is_jump_power_change_value_absolute=False,
                 capacity_change=0, is_capacity_change_value_absolute=False,
                 bullets_change=0, is_bullets_change_value_absolute=False,
                 coins_change=0, is_coins_change_value_absolute=False):
        # Absolute value means existing value would be overwritten by this value. Non-absolute value means that existing
        # value would be increased by this value.
        # TODO value + is_absolute should be united into a class
        self.health_change = health_change
        self.is_health_change_value_absolute = is_health_change_value_absolute
        self.x_energy_change = x_energy_change
        self.is_x_energy_change_value_absolute = is_x_energy_change_value_absolute
        self.y_energy_change = y_energy_change
        self.is_y_energy_change_value_absolute = is_y_energy_change_value_absolute
        self.jump_power_change = jump_power_change
        self.is_jump_power_change_value_absolute = is_jump_power_change_value_absolute
        self.capacity_change = capacity_change
        self.is_capacity_change_value_absolute = is_capacity_change_value_absolute
        self.bullets_change = bullets_change
        self.is_bullets_change_value_absolute = is_bullets_change_value_absolute
        self.coins_change = coins_change
        self.is_coins_change_value_absolute = is_coins_change_value_absolute

    def set_all_fields(self, health_change=0, is_health_change_value_absolute=False,
                       x_energy_change=0, is_x_energy_change_value_absolute=False,
                       y_energy_change=0, is_y_energy_change_value_absolute=False,
                       jump_power_change=0, is_jump_power_change_value_absolute=False,
                       capacity_change=0, is_capacity_change_value_absolute=False,
                       bullets_change=0, is_bullets_change_value_absolute=False,
                       coins_change=0, is_coins_change_value_absolute=False):
        """
        Function copies the functionality of the constructor. Created simply to make the code outside cleaner.
        """
        # Absolute value means existing value would be overwritten by this value. Non-absolute value means that existing
        # value would be increased by this value.
        # TODO value + is_absolute should be united into a class
        self.health_change = health_change
        self.is_health_change_value_absolute = is_health_change_value_absolute
        self.x_energy_change = x_energy_change
        self.is_x_energy_change_value_absolute = is_x_energy_change_value_absolute
        self.y_energy_change = y_energy_change
        self.is_y_energy_change_value_absolute = is_y_energy_change_value_absolute
        self.jump_power_change = jump_power_change
        self.is_jump_power_change_value_absolute = is_jump_power_change_value_absolute
        self.capacity_change = capacity_change
        self.is_capacity_change_value_absolute = is_capacity_change_value_absolute
        self.bullets_change = bullets_change
        self.is_bullets_change_value_absolute = is_bullets_change_value_absolute
        self.coins_change = coins_change
        self.is_coins_change_value_absolute = is_coins_change_value_absolute

    def can_apply_health_change_to_object(self, game_object):
        return ((not self.is_health_change_value_absolute and game_object.health + self.health_change >= 0)
                or (self.is_health_change_value_absolute and self.health_change >= 0))

    def can_apply_x_energy_change_to_object(self, game_object):
        return ((not self.is_x_energy_change_value_absolute and game_object.x_energy + self.x_energy_change >= 0)
                or (self.is_x_energy_change_value_absolute and self.x_energy_change >= 0))

    def can_apply_y_energy_change_to_object(self, game_object):
        return ((not self.is_y_energy_change_value_absolute and game_object.y_energy + self.y_energy_change >= 0)
                or (self.is_y_energy_change_value_absolute and self.y_energy_change >= 0))

    def can_apply_jump_power_change_to_object(self, game_object):
        return ((not self.is_jump_power_change_value_absolute
                 and len(game_object.jump_trick.stages) + self.jump_power_change >= 0)
                or (self.is_jump_power_change_value_absolute and self.jump_power_change >= 0))

    def can_apply_capacity_change_to_object(self, game_object):
        return ((not self.is_capacity_change_value_absolute and game_object.capacity + self.capacity_change >= 0)
                or (self.is_capacity_change_value_absolute and self.capacity_change >= 0))

    def can_apply_bullets_change_to_object(self, game_object):
        return ((not self.is_bullets_change_value_absolute and game_object.bullets + self.bullets_change >= 0)
                or (self.is_bullets_change_value_absolute and self.bullets_change >= 0))

    def can_apply_coins_change_to_object(self, game_object):
        return ((not self.is_coins_change_value_absolute and game_object.coins + self.coins_change >= 0)
                or (self.is_coins_change_value_absolute and self.coins_change >= 0))

    def __repr__(self):
        return str(self.health_change) + "_" + str(self.x_energy_change) + "_" + str(self.y_energy_change) + "_" + str(
            self.jump_power_change) + "_" + str(self.capacity_change) + "_" + str(self.bullets_change) + "_" + str(
            self.coins_change)
