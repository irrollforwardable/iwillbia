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


# Static functions that are executed upon game object's actions.
# Each function must have a corresponding record in the database 'functions' table.
# Each function name should precisely match the value of 'functions'.'name' column in the database.
# Each function must have the following parameters:
# - game_object: game object that performs the action
# - self_changes: changes that are applied to the game object upon action execution
# - subject_changes: changes that are applied to a game object that is affected by the action
# Function can return a value (i.e. subject_changes) if required.


def do_shoot(game_object, self_changes, subject_changes):
    for line in game_object.lines:
        if line.directional_line.is_for_shooting[game_object.direction]:
            if self_changes.can_apply_bullets_change_to_object(game_object):
                bullet = game_object.gameplay.bullets_pool.fetch_single_available()
                if bullet:
                    bullet.start_shot(shooting_line=line, subject_changes=subject_changes)
                    game_object.apply_changes(self_changes)


def do_explode(game_object, self_changes, subject_changes):
    if self_changes.can_apply_bullets_change_to_object(game_object):
        game_object.explode(radius=5, subject_changes=subject_changes)
        game_object.apply_changes(self_changes)


def do_bite(game_object, self_changes, subject_changes):
    game_object.apply_changes(self_changes)
    return subject_changes


def do_collect(game_object, self_changes, subject_changes):
    if self_changes.can_apply_capacity_change_to_object(game_object):
        game_object.collect_word_under()
        game_object.apply_changes(self_changes)


def do_uncollect(game_object, self_changes, subject_changes):
    if self_changes.can_apply_capacity_change_to_object(game_object):
        game_object.drop_word_from_inventory()
        game_object.apply_changes(self_changes)
