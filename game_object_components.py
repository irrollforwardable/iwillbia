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
        self.function_id = -1
        cursor = db_connection.cursor()

        # Action header info
        cursor.execute("select a.title, a.function_id, lower(f.name) " +
                       "from actions a, functions f " +
                       "where a.function_id = f.id and a.id = ?",
                       (db_pk_id,))
        db_rows = cursor.fetchall()

        if db_rows:
            self.title = db_rows[0][0]
            self.function_id = db_rows[0][1]
            self.execute = getattr(functions, db_rows[0][2])

        # Self changes and Subject changes
        cursor.execute("select a.self_changes_id, a.subject_changes_id " +
                       "from actions a " +
                       "where a.id = ? ", (db_pk_id,))
        db_rows = cursor.fetchall()

        if db_rows:
            self.self_changes.set_all_fields_from_db(db_connection, change_pk_id=db_rows[0][0])
            self.subject_changes.set_all_fields_from_db(db_connection, change_pk_id=db_rows[0][1])

    def __repr__(self):
        return self.title


class Changes(object):
    """
    List of changes to attributes of a game object. Contained by word meaning.
    """
    def __init__(self, description=None,
                 health_change=0, is_health_change_value_absolute=False,
                 x_energy_change=0, is_x_energy_change_value_absolute=False,
                 y_energy_change=0, is_y_energy_change_value_absolute=False,
                 jump_power_change=0, is_jump_power_change_value_absolute=False,
                 capacity_change=0, is_capacity_change_value_absolute=False,
                 bullets_change=0, is_bullets_change_value_absolute=False,
                 coins_change=0, is_coins_change_value_absolute=False):
        # Absolute value means existing value would be overwritten by this value. Non-absolute value means that existing
        # value would be increased by this value.
        # TODO value + is_absolute should be united into a class
        self.db_id = -1
        self.description = description

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

    def set_all_fields(self, description=None,
                       health_change=0, is_health_change_value_absolute=False,
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
        self.description = description
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

    def set_all_fields_from_db(self, db_connection, change_pk_id):
        """
        Set values of Changes object from database.
        :param db_connection: database connection
        :param change_pk_id: change id in the database
        """
        cursor = db_connection.cursor()

        # Action header info
        cursor.execute("select ch.health, ch.is_health_absolute, ch.x_energy, ch.is_x_energy_absolute, " +
                       "ch.y_energy, ch.is_y_energy_absolute, ch.jump_power, ch.is_jump_power_absolute, " +
                       "ch.capacity, ch.is_capacity_absolute, ch.bullets, ch.is_bullets_absolute, " +
                       "ch.coins, ch.is_coins_absolute, ch.id, ch.comments " +
                       "from changes ch " +
                       "where ch.id = ?",
                       (change_pk_id,))
        db_rows = cursor.fetchall()

        if db_rows:
            self.db_id = db_rows[0][14]
            self.set_all_fields(
                description=db_rows[0][15],
                health_change=db_rows[0][0],
                is_health_change_value_absolute=db_rows[0][1],
                x_energy_change=db_rows[0][2],
                is_x_energy_change_value_absolute=db_rows[0][3],
                y_energy_change=db_rows[0][4],
                is_y_energy_change_value_absolute=db_rows[0][5],
                jump_power_change=db_rows[0][6],
                is_jump_power_change_value_absolute=db_rows[0][7],
                capacity_change=db_rows[0][8],
                is_capacity_change_value_absolute=db_rows[0][9],
                bullets_change=db_rows[0][10],
                is_bullets_change_value_absolute=db_rows[0][11],
                coins_change=db_rows[0][12],
                is_coins_change_value_absolute=db_rows[0][13]
            )

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
        empty = ""
        absolute = "a"

        health_absolute = empty
        if self.is_health_change_value_absolute:
            health_absolute = absolute

        x_absolute = empty
        if self.is_x_energy_change_value_absolute:
            x_absolute = absolute

        y_absolute = empty
        if self.is_y_energy_change_value_absolute:
            y_absolute = absolute

        jump_absolute = empty
        if self.is_jump_power_change_value_absolute:
            jump_absolute = absolute

        capacity_absolute = empty
        if self.is_capacity_change_value_absolute:
            capacity_absolute = absolute

        bullet_absolute = empty
        if self.is_bullets_change_value_absolute:
            bullet_absolute = absolute

        coins_absolute = empty
        if self.is_coins_change_value_absolute:
            coins_absolute = absolute

        return ("h" + str(self.health_change) + health_absolute + "_x" + str(self.x_energy_change) + x_absolute +
                "_y" + str(self.y_energy_change) + y_absolute + "_j" + str(self.jump_power_change) + jump_absolute +
                "_c" + str(self.capacity_change) + capacity_absolute + "_b" + str(self.bullets_change) +
                bullet_absolute + "_$" + str(self.coins_change) + coins_absolute)
