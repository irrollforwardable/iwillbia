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

# TODO split this enormous module into smaller ones
import re
import random
from operator import attrgetter

from constants import *
from game_object_components import *


# Functions
def get_max_length(lines_list, direction):
    """
    Return max length found in a list of either DirectionalTextLines or ObjectLines
    :param lines_list: list of either DirectionalTextLines or ObjectLines
    :param direction: direction of the object
    :return: max length
    """
    max_length = 0
    for line in lines_list:
        if isinstance(line, ObjectLine):
            line = line.directional_line
        if len(line.texts[direction]) > max_length:
            max_length = len(line.texts[direction])
    return max_length


def get_max_width_of_lines(lines):
    """
    Get max line length.
    :param lines: list of text lines
    :return: width
    """
    width = 0
    for line in lines:
        if len(line) > width:
            width = len(line)
    return width


def get_list_of_empty_strings_of_various_length(max_length):
    """
    Generate list of empty strings of various length. String position in the list corresponds to its length.
    Used for performance improvement (I think so) during game "rendering", so that empty string are not generated
    on the fly.
    ["", " ", "  ", "   ", "    "]
    :param max_length: max empty string length
    :return: list of empty strings
    """
    result = [""]
    for i in range(1, max_length + 1):
        result.append(" " * i)
    return result


def generate_string_line(object_lines_list, max_length):
    """
    Produce single-line string from provided list of object lines.
    :param object_lines_list: list of object_lines for each line
    :param max_length: max width of the string line
    :return: single-row string
    """
    result = ""
    for object_line in object_lines_list:
        if len(result) < object_line.x:
            # Length of current result string is shorter than element position
            spaces_to_add = " " * (object_line.x - len(result))
            result += spaces_to_add + object_line.directional_line.texts[object_line.parent.direction]
        else:
            # Length of current result string allows standard inserting
            result = result[:object_line.x] + object_line.directional_line.texts[object_line.parent.direction] \
                     + result[(object_line.x + len(object_line.directional_line.texts[object_line.parent.direction])):]

        # Append spaces to fill the whole line
        diff = max_length - len(result)
        if diff > 0:
            result += (" " * diff)
    return result


def generate_string_line2(object_lines_list, max_length, empty_strings):
    """
    Produce list of strings like ["---", "      ", "/  \", "        "]
    :param object_lines_list: list of object_lines for each row
    :param max_length: max width of the row
    :param empty_strings: list of predefined empty strings of various length
    :return: list of strings representing current row
    """
    result = []
    current_x_pointer = 0

    # Sort object lines by X in current line
    object_lines_list.sort(key=attrgetter('x'))

    # Generate list of string representing current row
    for object_line in object_lines_list:
        if current_x_pointer == 0:
            # If first line in the row, append appropriate empty string before it
            result.append(empty_strings[object_line.x])
        else:
            # If not first line in the row, append empty string of length between previous and current object lines
            result.append(empty_strings[object_line.x - current_x_pointer])
        result.append(object_line.directional_line.texts[object_line.parent.direction])
        current_x_pointer = (object_line.x + len(object_line.directional_line.texts[object_line.parent.direction]))

    # Append empty string till the end of current row
    result.append(empty_strings[max_length - current_x_pointer])

    # Append new line character
    result.append("\n")

    return result


class DirectionalLine(object):
    """
    Contains information about single text line in both directions
    """
    def __init__(self, left_text, left_x_offset, right_text, right_x_offset, y_offset, left_is_for_shooting=False,
                 right_is_for_shooting=False):
        """
        Create new instance of DirectionalLine
        :param left_text: text when parent object is looking left
        :param left_x_offset: x offset (from parent object x) when parent object is looking left
        :param right_text: text when parent object is looking right
        :param right_x_offset: x offset (from parent object x) when parent object is looking right
        :param y_offset: y offset from parent object y
        :param left_is_for_shooting: True if line is used to shoot bullets when object is looking left
        :param right_is_for_shooting: True if line is used to shoot bullets when object is looking right
        """
        self.texts = [left_text, right_text]  # texts to actually render: texts[0] for left, texts[1] for right
        self.original_texts = (left_text, right_text)
        self.hurt_texts = self._generate_hurt_texts(left_text, right_text)
        self.empty_texts = self._generate_empty_texts(left_text, right_text)
        self.explode_texts = self._generate_explode_texts(left_text, right_text)
        self.x_offsets = (left_x_offset, right_x_offset)  # x_offsets[0] for left, x_offsets[1] for right
        self.y_offset = y_offset
        self.is_for_shooting = [left_is_for_shooting, right_is_for_shooting]

    def _generate_hurt_texts(self, left_text, right_text):
        l_txt = self._replace_non_empty_characters(left_text, ".")
        r_txt = self._replace_non_empty_characters(right_text, ".")
        return l_txt, r_txt

    def _generate_empty_texts(self, left_text, right_text):
        l_txt = " " * len(left_text)
        r_txt = " " * len(right_text)
        return l_txt, r_txt

    def _generate_explode_texts(self, left_text, right_text):
        l_txt = self._replace_non_empty_characters(left_text, "*")
        r_txt = self._replace_non_empty_characters(right_text, "*")
        return l_txt, r_txt

    def _replace_non_empty_characters(self, string, replacement):
        result = ""
        for char in string:
            if char == " ":
                result += " "
            else:
                result += replacement
        return result


class ObjectLine(object):
    """
    Contains information about single line of a game object: DirectionalLine and coordinates
    """
    def __init__(self, game_object, directional_line):
        """
        Create new instance of ObjectLine
        :param game_object: parent game object that current ObjectLine is a part of
        :param directional_line: DirectionalLine instance containing information about text of line in both  directions
        """
        self.parent = game_object
        self.directional_line = directional_line
        self.x = self.parent.x + self.directional_line.x_offsets[self.parent.direction]  # Changed with parent movements
        self.y = self.parent.y + self.directional_line.y_offset  # Changed with parent movements
        self.potential_x, self.potential_y = self.x, self.y
        self.parent.gameplay.rows[self.y].append(self)

        # Set parent object's length
        if self.parent.length < len(self.directional_line.texts[self.parent.direction]):
            self.parent.length = len(self.directional_line.texts[self.parent.direction])

    def set_x_no_collision_detection(self, x):
        self.x = x + self.directional_line.x_offsets[self.parent.direction]

    def set_x_with_collision_detection(self, x):
        """
        Try to set provided x of the line. Returns object that is touched by the line in case of collision.
        :param x: potential x
        :return: collided line of another GameObject
        """
        new_x = (x + self.directional_line.x_offsets[self.parent.direction])

        # Special case: colliding with either right or left side of the game area
        if new_x < 0 or new_x + len(self.directional_line.texts[self.parent.direction]) > self.parent.gameplay.width:
            # Return first line of a dummy platform
            return self.parent.gameplay.dummy_side_platform.lines[0]

        # Check for collision in rows occupied by current object
        for other_object_line in self.parent.gameplay.rows[self.y]:
            # TODO reformat to make it more readable (automatic formatting is applied currently)
            if other_object_line != self and (other_object_line.x <= new_x <= other_object_line.x + len(
                    other_object_line.directional_line.texts[
                        other_object_line.parent.direction]) - 1 or other_object_line.x <= new_x + len(
                    self.directional_line.texts[self.parent.direction]) - 1 <= other_object_line.x):
                return other_object_line

        self.potential_x = new_x
        return None

    def set_y_no_collision_detection(self, y):
        self.parent.gameplay.rows[self.y].remove(self)
        self.y = y + self.directional_line.y_offset
        self.parent.gameplay.rows[self.y].append(self)

    def set_y_with_collision_detection(self, y):
        """
        Try to set provided y of the lines. Returns object that is touched by the line in case of collision.
        :param y: potential y
        :return: collided GameObject
        """
        new_y = (y + self.directional_line.y_offset)

        # Check for collision in rows occupied by current object
        for other_object_line in self.parent.gameplay.rows[new_y]:
            # TODO reformat to make it more readable (automatic formatting is applied currently)
            if other_object_line != self and other_object_line.parent != self.parent and (
                                other_object_line.x <= self.x < other_object_line.x + len(
                                other_object_line.directional_line.texts[
                                    other_object_line.parent.direction]) or other_object_line.x <= self.x + len(
                            self.directional_line.texts[self.parent.direction]) - 1 < other_object_line.x + len(
                            other_object_line.directional_line.texts[
                                other_object_line.parent.direction]) -1 or self.x <= other_object_line.x < self.x + len(
                        self.directional_line.texts[self.parent.direction]) - 1 or self.x <= other_object_line.x + len(
                    other_object_line.directional_line.texts[other_object_line.parent.direction]) - 1 < self.x + len(
                    self.directional_line.texts[self.parent.direction]) - 1):
                return other_object_line

        # Special case: reaching the top border
        if new_y < 0:
            return self.parent.gameplay.dummy_top_platform.lines[0]

        # Special case: reaching the bottom border
        if new_y == len(self.parent.gameplay.rows) - 1:
            # Return first line of a dummy platform that calls a function to handle falling down to the bottom
            return self.parent.gameplay.dummy_bottom_platform.lines[0]

        self.potential_y = new_y
        return None

    def delete(self):
        """
        Delete ObjectLine from the gameplay
        """
        self.parent.gameplay.rows[self.y].remove(self)

        # TODO add other types
        if isinstance(self, Enemy):
            self.parent.gameplay.enemies.remove(self)
        elif isinstance(self, Coin):
            self.parent.gameplay.coins.remove(self)


class GameObject(object):
    """
    Base class for any object in the game
    """
    def __init__(self, gameplay, directional_lines, x, y,
                 initial_health=100, initial_x_energy=50, initial_y_energy=50, initial_jump_power=2, initial_bullets=0,
                 initial_capacity=3, initial_coins=0):
        """
        Create new instance of GameObject
        :param gameplay: instance of Gameplay object - the game that this object appears in
        :param directional_lines: list of directional lines that this object consists of
        :param x: x coordinate
        :param y: y coordinate
        """
        # TODO Divide class into two separate classes: base (for Word) and movable (for Player and Enemy)
        self.gameplay = gameplay
        self.x, self.y = x, y
        self.length = 0             # Set during lines creation
        self.direction = RIGHT      # 0 - left, 1 - right. Look right by default.
        self.lines = self._create_object_lines(directional_lines)
        self.jump_trick = Trick([])
        self.jump_trick.set_repeated_stages((0, -gameplay.y_gravity * 2), initial_jump_power)
        self.touching_enemies = []  # List of enemies the object is touching in a particular moment
        self.touching_words = []    # List of words the object is touching in a particular moment
        self.is_on_ground = False
        self.current_transformation = None
        self.is_transformed = False  # True - transformed to a word, False - in its initial shape
        self.initial_directional_lines = directional_lines  # object's initial appearance
        self.blinking = Blink(self)
        self.inventory = []
        self.widths = self._generate_widths_list()

        # Keep initial values
        self.initial_health = initial_health
        self.initial_x_energy = initial_x_energy
        self.initial_y_energy = initial_y_energy
        self.initial_jump_power = initial_jump_power
        self.initial_bullets = initial_bullets
        self.initial_capacity = initial_capacity
        self.initial_coins = initial_coins

        # Attributes
        self.health = self.initial_health
        self.x_energy = self.initial_x_energy
        self.y_energy = self.initial_y_energy
        self.bullets = self.initial_bullets
        self.capacity = self.initial_capacity
        self.coins = self.initial_coins

        # Command button number - [action title - action]. For enemy simply use the list of values.
        self.command_action_map = {
            1: None,
            2: None,
            3: None,
            4: None,
            5: None,
            6: None,
            7: None,
            8: None,
            9: None,
            0: None
        }

        if isinstance(self, Player) or isinstance(self, Enemy):
            self.command_action_map[1] = Action(self.gameplay.controller.connection, 4)  # Collect by default
            self.command_action_map[2] = Action(self.gameplay.controller.connection, 5)  # Uncollect by default

        if isinstance(self, Player):
            self.gameplay.controller.construct_gui_actions_list(self.command_action_map)

    def set_x_no_collision_detection(self, new_x):
        for line in self.lines:
            line.set_x_no_collision_detection(new_x)

    def set_x_with_collision_detection(self, new_x):
        """
        Try to set potential x coordinate for all object lines. If any of object lines collides with lines of other
        object, reset position of all other lines.
        :param new_x: potential new x of the line
        :return True if new x is was set, False if collision occurred
        """
        self._clear_touching_lists()

        for line in self.lines:
            touching_line_x = line.set_x_with_collision_detection(new_x)
            if touching_line_x:
                self._handle_touched_object(touching_line_x.parent)
                # Reset potential X coordinate of object's lines, that have already been moved (in logic)
                for line_to_reset in self.lines:
                    if line_to_reset != line:
                        line_to_reset.x = line_to_reset.potential_x = self.x + line_to_reset.directional_line.x_offsets[
                            self.direction]
                    else:
                        # No need to reset lines after current line, as those have not yet been modified
                        break
                return False

        # Set all lines' actual x coordinate (value of potential x) if no collision was detected
        for line_to_actually_move in self.lines:
            line_to_actually_move.x = line_to_actually_move.potential_x

        # Set x coordinate of the object itself
        self.x = new_x

        # Consume energy
        change = 1
        if self.is_transformed:
            change *= -1
        self.update_attributes(energy_increase=change)

        return True

    def set_y_no_collision_detection(self, new_y):
        for line in self.lines:
            line.set_y_no_collision_detection(new_y)

    def set_y_with_collision_detection(self, new_y):
        """
        Try to set potential y coordinate for all object lines. If any of object lines collides with lines of other
        object, reset position of all other lines.
        :param new_y: potential new y of the line
        """
        self._clear_touching_lists()

        for line in self.lines:
            touching_line_y = line.set_y_with_collision_detection(new_y)
            if touching_line_y:
                self._handle_touched_object(touching_line_y.parent)
                # Reset potential Y coordinate of object's lines, that have already been moved (in logic)
                for line_to_reset in self.lines:
                    if line_to_reset != line:
                        line_to_reset.y = line_to_reset.potential_y = self.y + line_to_reset.directional_line.y_offset
                    else:
                        # No need to reset lines after current line, as those have not yet been modified
                        break
                # Mark object as standing on the ground (used to identify whether object can jump)
                if touching_line_y.y > line.y and not self.is_on_ground:
                    self.is_on_ground = True

                return

        # Set all lines' actual y coordinate (value of potential y) if no collision was detected
        for line_to_actually_move in self.lines:
            # Move references to object lines to the appropriate gameplay rows
            self.gameplay.rows[line_to_actually_move.y].remove(line_to_actually_move)
            if line_to_actually_move not in self.gameplay.rows[line_to_actually_move.potential_y]:
                self.gameplay.rows[line_to_actually_move.potential_y].append(line_to_actually_move)

            # Set the actual y coordinate of the object line
            line_to_actually_move.y = line_to_actually_move.potential_y

            # Mark object as flying in the air (not touching ground)
            if self.is_on_ground:
                self.is_on_ground = False

        # Set y coordinate of the object itself
        self.y = new_y

        # Consume energy
        change = 1
        if self.is_transformed:
            change *= -1
        self.update_attributes(jumping_energy_increase=change)

    def move_to_another_gameplay(self, new_gameplay, new_x, new_y):
        """
        Remove lines of GameObject from its current gameplay (part) and move those to the provided gameplay (part) at
        the provided coordinates. No collision detection is performed.
        :param new_gameplay: gameplay to which the object is to be moved
        :param new_x: X in the new gameplay
        :param new_y: Y in the new gameplay
        """
        for line in self.lines:
            self.gameplay.rows[line.y].remove(line)
        new_gameplay.add_object(self)
        self.x, self.y = new_x, new_y
        self.add_lines_to_gameplay(self.gameplay, new_x, new_y)

    def add_lines_to_gameplay(self, gameplay, x, y):
        """
        Physically add lines of the game object to the provided gameplay (part) at provided coordinates
        :param gameplay:
        :param x:
        :param y:
        """
        for line in self.lines:
            line.y = y + line.directional_line.y_offset
            line.x = x + line.directional_line.x_offsets[self.direction]
            gameplay.rows[line.y].append(line)

    def set_look_right(self):
        self.direction = RIGHT
        self._clear_touching_lists()

    def set_look_left(self):
        self.direction = LEFT
        self._clear_touching_lists()

    def can_apply_changes(self, changes):
        """
        Check whether provided changes can be applied to the game object by comparing its attribute values to changes'
        :param changes: Changes to apply
        :return: true if changes can be applied, false if not
        """
        return (changes.can_apply_health_change_to_object(self)
                and changes.can_apply_x_energy_change_to_object(self)
                and changes.can_apply_y_energy_change_to_object(self)
                and changes.can_apply_jump_power_change_to_object(self)
                and changes.can_apply_capacity_change_to_object(self)
                and changes.can_apply_bullets_change_to_object(self)
                and changes.can_apply_coins_change_to_object(self))

    def apply_changes(self, changes):
        """
        Apply provided changes to game object's attributes
        :param changes: Changes to apply
        """
        if not changes:
            return

        if changes.is_health_change_value_absolute:
            if changes.health_change < self.health:
                self.start_blinking(3, BLINK_HURT)
            self.health = changes.health_change
        else:
            if changes.health_change < 0:
                self.start_blinking(3, BLINK_HURT)
            self.health += changes.health_change

        if changes.is_x_energy_change_value_absolute:
            self.x_energy = changes.x_energy_change
        else:
            self.x_energy += changes.x_energy_change

        if changes.is_y_energy_change_value_absolute:
            self.y_energy = changes.y_energy_change
        else:
            self.y_energy += changes.y_energy_change

        if changes.is_jump_power_change_value_absolute:
            self.jump_trick.set_repeated_stages((0, -self.gameplay.y_gravity * 2), changes.jump_power_change)
        else:
            self.jump_trick.append_repeated_stages((0, -self.gameplay.y_gravity * 2), changes.jump_power_change)

        if changes.is_capacity_change_value_absolute:
            self.capacity = changes.capacity_change
        else:
            self.capacity += changes.capacity_change

        if changes.is_bullets_change_value_absolute:
            self.bullets = changes.bullets_change
        else:
            self.bullets += changes.bullets_change

        if changes.is_coins_change_value_absolute:
            self.coins = changes.coins_change
        else:
            self.coins += changes.coins_change

    def transform(self, word=None):
        """
        Start new transformation process.
        The transformation process is updated several times after that by gameplay.
        :param word: if specified - transform to this word, if not - transform to initial appearance
        """
        # TODO do not create new transformation instance, use the same
        if word and word.is_consumable and self.can_apply_changes(word.meaning.immediate_changes):
            if word.meaning.directional_lines:
                self.current_transformation = Transformation(self, word.meaning.directional_lines, word=word)

            # TODO for future: the Word should not be deleted, but be made invisible + assigned to GameObject
            word.delete()
            # TODO message that transformation is impossible
        elif not word:
            # Transform to initial appearance
            self.current_transformation = Transformation(self, self.initial_directional_lines)
        else:
            self.gameplay.controller.show_message("Not able to transform!")

    def perform_post_transformation_modifications(self, word):
        """
        Actions to perform right after transformation. Run once transformation is finished.
        :param word: if specified - transformation has been to this word, if not - transformation to initial appearance
        """
        if word:
            # Right after transformation to a word

            # Update attributes
            self.apply_changes(word.meaning.immediate_changes)

            # Assign actions from word meaning to the object command-action slots
            for key in self.command_action_map:
                if word.meaning.command_action_map[key]:
                    self.command_action_map[key] = word.meaning.command_action_map[key]

            self.is_transformed = True
        else:
            # Right after transformation to initial appearance
            if self.x_energy < 1:
                self.x_energy = 1
            if self.y_energy < 1:
                self.y_energy = 1
            self.jump_trick.set_repeated_stages((0, -self.gameplay.y_gravity * 2), self.initial_jump_power)
            self.capacity = self.initial_capacity
            self.bullets = 0

            # Reset actions
            self.remove_actions()

            self.is_transformed = False

        self.widths = self._generate_widths_list()

        # For player only - construct list of action_number - action_title somewhere in GUI.
        # FYI: In my opinion, a better solution than loop through construct_actions_list every frame update
        if isinstance(self, Player):
            self.gameplay.controller.construct_gui_actions_list(self.command_action_map)

    def update_attributes(self, energy_increase=0, jumping_energy_increase=0, bullets_increase=0):
        if energy_increase:
            self.x_energy += energy_increase
        if jumping_energy_increase:
            self.y_energy += jumping_energy_increase
        if bullets_increase:
            self.bullets += bullets_increase

    def start_blinking(self, times_to_blink, blinking_type):
        self.blinking.start(times_to_blink, blinking_type)

    def blink(self, blinking_type, is_set_original_texts=False):
        """
        Switch text of all object lines to the one that corresponds to the blinking type passed in the parameter
        :param blinking_type: either BLINK_DIE, BLINK_HURT or BLINK_EXPLODE
        :param is_set_original_texts: if True, "un-blink" to the original line texts
        """
        # TODO there is probably a better way to write the following peace of code
        for line in self.lines:
            left_text = line.directional_line.original_texts[LEFT]
            right_text = line.directional_line.original_texts[RIGHT]
            if not is_set_original_texts:
                if blinking_type == BLINK_DIE:
                    left_text = line.directional_line.empty_texts[LEFT]
                    right_text = line.directional_line.empty_texts[RIGHT]
                elif blinking_type == BLINK_HURT:
                    left_text = line.directional_line.hurt_texts[LEFT]
                    right_text = line.directional_line.hurt_texts[RIGHT]
                elif blinking_type == BLINK_EXPLODE:
                    left_text = line.directional_line.explode_texts[LEFT]
                    right_text = line.directional_line.explode_texts[RIGHT]
            line.directional_line.texts[LEFT] = left_text
            line.directional_line.texts[RIGHT] = right_text

    def explode(self, radius=5, subject_changes=None, is_transform_to_initial_state=True):
        """
        Make explosion with itself in the epicenter.
        :param radius: explosion wave radius
        :param subject_changes: changes to be applied to GameObjects that are contacted by explosion wave
        :param is_transform_to_initial_state: if True, transform back to initial state
        """
        self.gameplay.explosions.append(Explosion(gameplay=self.gameplay, x=self.x, y=self.y,
                                                  epicenter_width=self.widths[self.direction],
                                                  epicenter_height=len(self.lines), radius=radius,
                                                  subject_changes=subject_changes))
        if is_transform_to_initial_state:
            self.transform()

    def become_visible(self):
        """
        Make object visible - set texts of directional lines as original texts
        """
        for line in self.lines:
            line.directional_line.texts[LEFT] = line.directional_line.original_texts[LEFT]
            line.directional_line.texts[RIGHT] = line.directional_line.original_texts[LEFT]

    def become_invisible(self):
        """
        Make game object invisible. Game object is NOT deleted or removed from the game.
        """
        for line in self.lines:
            line.directional_line.texts[LEFT] = line.directional_line.empty_texts[LEFT]
            line.directional_line.texts[RIGHT] = line.directional_line.empty_texts[LEFT]

    def delete(self):
        """
        Delete GameObject from the gameplay
        """
        for line in self.lines:
            line.delete()
        if isinstance(self, Enemy):
            self.gameplay.enemies.remove(self)
        elif isinstance(self, Coin):
            self.gameplay.coins.remove(self)
        elif isinstance(self, Word):
            self.gameplay.words.remove(self)
        elif isinstance(self, Platform):
            self.gameplay.platforms.remove(self)
        elif isinstance(self, Explosion):
            self.gameplay.explosions.remove(self)

    def execute_action_by_command_number(self, action_number):
        """
        Execute action function ("execute" is the pointer to that function) that is assigned to the command number
        given in the argument.
        :param action_number: command number that action is assigned to
        """
        if self.command_action_map[action_number]:
            return self.command_action_map[action_number].execute(self,
                                                                  self.command_action_map[action_number].self_changes,
                                                                  self.command_action_map[action_number].subject_changes
                                                                  )

    def remove_actions(self):
        """
        Remove all actions from available actions list
        """
        for command_number in self.command_action_map:
            self.command_action_map[command_number] = None

        # Restore default actions after clearing (TODO: should be rewritten)
        if isinstance(self, Player) or isinstance(self, Enemy):
            self.command_action_map[1] = Action(self.gameplay.controller.connection, 4)
            self.command_action_map[2] = Action(self.gameplay.controller.connection, 5)

    def get_action_number_by_title(self, action_title):
        for command_num in self.command_action_map.keys():
            if self.command_action_map[command_num] and self.command_action_map[command_num].title == action_title:
                return command_num

    def collect_word_under(self):
        """
        Collect word on which the GameObject is currently standing to inventory
        """
        if self.touching_words:
            self.inventory.append(self.touching_words[0])
            self.touching_words[0].delete()
            if isinstance(self, Player):
                self.update_gui_inventory_info()

    def drop_word_from_inventory(self):
        """
        Remove previously collected word from the inventory and place it under game object
        """
        is_player = isinstance(self, Player)
        chosen_word = None

        # Choose the word to drop from inventory
        if is_player:
            word_text_list = [word.lines[0].directional_line.texts[word.direction] for word in self.inventory]
            chosen_word_id = self.gameplay.controller.choose_word_id_from_list(word_text_list)
            if chosen_word_id:
                chosen_word = self.inventory[int(chosen_word_id[0])]

        # Drop the chosen word
        if chosen_word:
            self.inventory.remove(chosen_word)
            self.gameplay.add_object(chosen_word)
            chosen_word.add_lines_to_gameplay(self.gameplay, self.x, self.y + 1)
            if is_player:
                self.update_gui_inventory_info()

    def append_new_line(self, directional_line):
        """
        Create new ObjectLine from provided DirectionalLine and append it to GameObject list of lines.
        :param directional_line: DirectionalLine
        """
        self.lines.append(ObjectLine(self, directional_line))

    def _create_object_lines(self, directional_lines):
        result = []
        for directional_line in directional_lines:
            result.append(ObjectLine(self, directional_line))
        return result

    def _generate_widths_list(self):
        return [get_max_length(self.lines, LEFT), get_max_length(self.lines, RIGHT)]

    def _handle_touched_object(self, touched_object):
        """
        Actions upon collision between two game objects depending on their types
        :param touched_object: the object that is touched by this game object
        """
        # TODO the whole collision handling method needs refactoring
        if isinstance(touched_object, Bullet):
            # This ensures that GameObject cannot hurt itself with its own bullet (when shooting line X is "deep")
            if not touched_object.shooter == self:
                self.apply_changes(touched_object.subject_changes)
                touched_object.put_back_into_pool()
        elif isinstance(touched_object, Explosion):
            self.apply_changes(touched_object.subject_changes)
        elif isinstance(touched_object, Enemy):
            if touched_object not in self.touching_enemies:
                self.touching_enemies.append(touched_object)
        elif isinstance(self, Enemy) and isinstance(touched_object, Player):
            # TODO need a method to search for command number by providing action name
            subject_changes = self.execute_action_by_command_number(self.get_action_number_by_title("Bite"))
            if subject_changes:
                touched_object.apply_changes(subject_changes)
        elif isinstance(touched_object, Coin) and isinstance(self, Player):
            touched_object.grant_price_to_object(self)
            touched_object.delete()
        elif isinstance(touched_object, Word):
            if touched_object not in self.touching_words:
                self.touching_words.append(touched_object)
        elif isinstance(touched_object, Platform):
            touched_object.execute_function(self)

    def _clear_touching_lists(self):
        del self.touching_enemies[:]
        del self.touching_words[:]


class Player(GameObject):
    def __init__(self, gameplay, lines, x, y):
        super(Player, self).__init__(gameplay, lines, x, y)

    def update_gui_inventory_info(self):
        """
        Update inventory info in the GUI
        """
        inventory_string = ""
        for word in self.inventory:
            inventory_string += word.lines[0].directional_line.texts[word.direction] + ", "
        inventory_string = inventory_string[:-2]
        self.gameplay.controller.set_inventory_string(inventory_string)


class Coin(GameObject):
    def __init__(self, gameplay, lines, start_price, x, y, price_change_time=1):
        super(Coin, self).__init__(gameplay, lines, x, y)
        self.price = start_price
        self.price_change_time = price_change_time
        self.delta_time = 0

    def update_state(self):
        self.delta_time += 1
        if self.delta_time == self.price_change_time:
            self.update_to_next_price()
            self.delta_time = 0

    def update_to_next_price(self):
        self.price += 1
        if self.price > 9:
            self.price = 0
        self.lines[0].directional_line.texts[self.direction] = "(" + str(self.price) + ")"

    def grant_price_to_object(self, game_object):
        game_object.coins += self.price


class Enemy(GameObject):
    def __init__(self, gameplay, lines, x, y):
        super(Enemy, self).__init__(gameplay, lines, x, y)
        self.default_attack_action = Action(self.gameplay.controller.connection, 3)  # Action to be the first one b.d.
        self.remove_actions()

    def remove_actions(self):
        super(Enemy, self).remove_actions()
        self.command_action_map[CMD_1] = self.default_attack_action


class Word(GameObject):
    def __init__(self, gameplay, text, language_id, x, y, db_connection=None):
        super(Word, self).__init__(gameplay, (DirectionalLine(text, 0, text, 0, 0),), x, y)
        self.text = text
        self.is_consumable = False  # Defines whether the word can be used for transformation or attribute change
        self.meaning = None
        self.meaning = Meaning(self, db_connection, text, language_id)


class Platform(GameObject):
    def __init__(self, gameplay, text, x, y, function_to_run,
                 move_x_from=None, move_x_to=None):
        super(Platform, self).__init__(gameplay, (DirectionalLine(text, 0, text, 0, 0),), x, y)
        self.function_to_run = function_to_run

        # Movement (if required)
        self.max_width = get_max_length(self.lines, self.direction)
        self.move_x_from = move_x_from  # min x on left side of gameplay
        self.move_x_to = move_x_to      # max x on right side of gameplay

    def execute_function(self, *args):
        if self.function_to_run:
            self.function_to_run(*args)

    def update_x_position(self):
        """
        Move platform horizontally between move_x_from and move_x_to
        """
        if self.move_x_from is not None and self.move_x_to is not None:
            if self.direction == RIGHT:
                if self.x + self.max_width < self.move_x_to:
                    self.set_x_with_collision_detection(self.x + 1)
                else:
                    self.direction = LEFT
            elif self.direction == LEFT:
                if self.x > self.move_x_from:
                    self.set_x_with_collision_detection(self.x - 1)
                else:
                    self.direction = RIGHT


class Explosion(GameObject):
    """
    Wave released from epicenter and applying changes (either destructive or not) to all objects that it touches.
    """
    def __init__(self, gameplay, x, y, epicenter_width, epicenter_height, radius, subject_changes,
                 horizontal_char="-", vertical_char="|"):
        """
         ------r------
        | -----a----- |
        ||.----d---- ||
        |||  safe   |||
        |||epicenter|||
        ||'---------'||
        |'-----------'|
        '-------------'
        :param x: safe epicenter top left X coordinate
        :param y: safe epicenter top left Y coordinate
        :param epicenter_width: width of safe epicenter (area in the center in which no harm is done)
        :param epicenter_height: height of safe epicenter (area in the center in which no harm is done)
        :param radius: how far should explosion go away from its safe epicenter
        :param subject_changes: changes to be applied to GameObjects that are touched by the wave
        :param horizontal_char: single character representing horizontal wave
        :param vertical_char: single character representing vertical wave
        """
        super(Explosion, self).__init__(
            gameplay,
            (
                DirectionalLine(horizontal_char * (epicenter_width - 2),  # TODO Fail if epicenter_width < 2
                                1,
                                horizontal_char * (epicenter_width - 2),
                                1,
                                0),
                DirectionalLine(horizontal_char * (epicenter_width - 2),
                                1,
                                horizontal_char * (epicenter_width - 2),
                                1,
                                epicenter_height),
            ),
            x,
            y)

        # Add vertical wave lines
        for vl_y in range(1, epicenter_height + 1):
            self.append_new_line(DirectionalLine(vertical_char, -1, vertical_char, epicenter_width, vl_y))
            self.append_new_line(DirectionalLine(vertical_char, epicenter_width, vertical_char, -1, vl_y))

        self.x = x
        self.y = y
        self.epicenter_width = epicenter_width
        self.epicenter_height = epicenter_height
        self.radius = radius
        self.subject_changes = subject_changes
        self.current_radius = 0
        self.horizontal_char = horizontal_char
        self.vertical_char = vertical_char

    def update_state(self):
        if self.current_radius < self.radius:

            # Top horizontal line
            self.lines[0].directional_line.texts[0] += (self.horizontal_char * 2)
            self.lines[0].directional_line.texts[1] += (self.horizontal_char * 2)
            self.lines[0].set_x_no_collision_detection(self.lines[0].x - 2)
            self.lines[0].set_y_no_collision_detection(self.lines[0].y - 1)

            # Add one more pair of vertical line segments to the top
            self.append_new_line(DirectionalLine(self.vertical_char, -1, self.vertical_char, self.epicenter_width,
                                                 -self.current_radius))
            self.append_new_line(DirectionalLine(self.vertical_char, self.epicenter_width, self.vertical_char,
                                                 -1, -self.current_radius))

            # Bottom horizontal line
            self.lines[1].directional_line.texts[0] += (self.horizontal_char * 2)
            self.lines[1].directional_line.texts[1] += (self.horizontal_char * 2)
            self.lines[1].set_x_no_collision_detection(self.lines[1].x - 2)
            self.lines[1].set_y_no_collision_detection(self.y + self.current_radius)

            # Add one more pair of vertical line segments to the bottom
            self.append_new_line(DirectionalLine(self.vertical_char, -1, self.vertical_char, self.epicenter_width,
                                                 self.current_radius + self.epicenter_height - 1))
            self.append_new_line(DirectionalLine(self.vertical_char, self.epicenter_width, self.vertical_char,
                                                 -1, self.current_radius + self.epicenter_height - 1))

            for line_id in range(2, len(self.lines)):
                if line_id % 2 == 0:
                    self.lines[line_id].set_x_no_collision_detection(self.x + self.current_radius)
                else:
                    self.lines[line_id].set_x_no_collision_detection(self.x - self.current_radius)

            self.current_radius += 1
        else:
            self.delete()


class Meaning(object):
    """
    Contains information about the meaning of the word: it's visual representation and all its parameters
    """
    def __init__(self, word, db_connection, text, language_id):
        self.directional_lines = []

        # Changes of object's attributes immediately after transformation to a word
        self.immediate_changes = Changes()

        # Actions
        self.command_action_map = {CMD_1: None, CMD_2: None, CMD_3: None, CMD_4: None, CMD_5: None, CMD_6: None,
                                   CMD_7: None, CMD_8: None, CMD_9: None, CMD_0: None}

        if not db_connection:
            return

        # TODO refactor: extract to separate method
        cursor = db_connection.cursor()
        cursor.execute("select lin.right_text, lin.right_x_offset, lin.left_text, lin.left_x_offset, lin.y_offset, " +
                       "ch.health, ch.is_health_absolute, ch.x_energy, ch.is_x_energy_absolute, " +
                       "ch.y_energy, ch.is_y_energy_absolute, ch.jump_power, ch.is_jump_power_absolute, " +
                       "ch.capacity, ch.is_capacity_absolute, ch.bullets, ch.is_bullets_absolute, " +
                       "ch.coins, ch.is_coins_absolute, " +
                       "w.command_1_action_id, w.command_2_action_id, w.command_3_action_id, w.command_4_action_id, "
                       "w.command_5_action_id, w.command_6_action_id, w.command_7_action_id, w.command_8_action_id, "
                       "w.command_9_action_id, w.command_0_action_id, "
                       "lin.left_is_for_shooting, lin.right_is_for_shooting "
                       "from languages lang, word_lines_map map, words w, lines lin, changes ch " +
                       "where w.language_id = lang.id " +
                       "and w.id = map.word_id " +
                       "and lin.word_map_id = map.lines_id " +
                       "and w.immediate_changes_id = ch.id " +
                       "and lang.id = ? " +
                       "and lower(w.name) = ? " +
                       "order by lin.y_offset", (language_id, text.lower()))
        db_rows = cursor.fetchall()

        # Set properties and actions
        if db_rows:
            word.is_consumable = True
            self.immediate_changes.set_all_fields(None, db_rows[0][5], db_rows[0][6] > 0, db_rows[0][7],
                                                  db_rows[0][8] > 0, db_rows[0][9], db_rows[0][10] > 0, db_rows[0][11],
                                                  db_rows[0][12] > 0, db_rows[0][13], db_rows[0][14] > 0,
                                                  db_rows[0][15], db_rows[0][16] > 0, db_rows[0][17],
                                                  db_rows[0][18] > 0)
            if db_rows[0][19]:
                self.command_action_map[CMD_1] = Action(db_connection, db_rows[0][19])
            if db_rows[0][20]:
                self.command_action_map[CMD_2] = Action(db_connection, db_rows[0][20])
            if db_rows[0][21]:
                self.command_action_map[CMD_3] = Action(db_connection, db_rows[0][21])
            if db_rows[0][22]:
                self.command_action_map[CMD_4] = Action(db_connection, db_rows[0][22])
            if db_rows[0][23]:
                self.command_action_map[CMD_5] = Action(db_connection, db_rows[0][23])
            if db_rows[0][24]:
                self.command_action_map[CMD_6] = Action(db_connection, db_rows[0][24])
            if db_rows[0][25]:
                self.command_action_map[CMD_7] = Action(db_connection, db_rows[0][25])
            if db_rows[0][26]:
                self.command_action_map[CMD_8] = Action(db_connection, db_rows[0][26])
            if db_rows[0][27]:
                self.command_action_map[CMD_9] = Action(db_connection, db_rows[0][27])
            if db_rows[0][28]:
                self.command_action_map[CMD_0] = Action(db_connection, db_rows[0][28])

        # Set lines
        for db_row in db_rows:
            self.directional_lines.append(DirectionalLine(left_text=db_row[2], left_x_offset=db_row[3],
                                                          right_text=db_row[0], right_x_offset=db_row[1],
                                                          y_offset=db_row[4],
                                                          left_is_for_shooting=db_row[29] > 0,
                                                          right_is_for_shooting=db_row[30] > 0))


class Gameplay(object):
    """
    Represents current gaming session. Each time a new file is open, a new Gameplay is created.
    """
    def __init__(self, controller, sequence_num, lines, language_id, difficulty, line_spacing, left, top_before_start,
                 top_after_start, right, bottom_before_finish, bottom_after_finish, is_last_gameplay=False,
                 is_custom_game_builder=False):
        self.controller = controller
        self.is_running = False
        self.sequence_number = sequence_num
        self.is_last_gameplay = is_last_gameplay

        self.difficulty = difficulty
        self.width = left + get_max_width_of_lines(lines) + right
        # List of empty strings of various length (used for "rendering" of game as a string)
        self.empty_strings = get_list_of_empty_strings_of_various_length(self.width)
        self.y_gravity = 1

        self.rows = None  # Array of object lists per each line
        self.player = None
        self.coins = None
        self.enemies = None
        self.words = None
        self.platforms = None
        self.explosions = None
        self.bottom = None
        self.dummy_bottom_platform = None  # Platform to be returned by ObjectLine when hitting the bottom of the game
        self.dummy_top_platform = None  # Platform to be returned by ObjectLine when hitting the top of the game space
        self.dummy_side_platform = None  # Platform to be returned by ObjectLine when colliding with left/right sides

        # Pools
        self.bullets_pool = None

        if not is_custom_game_builder:  # FYI: is_custom_game_builder=True only for tutorials
            GameBuilder(self, lines, language_id, line_spacing, left, top_before_start, top_after_start,
                        right, bottom_before_finish, bottom_after_finish)

            self.initial_enemies_count = len(self.enemies)
            self.initial_coins_count = len(self.coins)

    def add_object(self, game_object):
        """
        Correctly add provided game object to the gameplay.
        WARNING: The object is NOT placed physically, that means object lines are not added to gameplay's rows! In order
        to add lines, thus making the object visible, use GameObject::add_lines_to_gameplay() method!
        :param game_object:
        """
        game_object.gameplay = self

        if isinstance(game_object, Player):
            self.player = game_object
        elif isinstance(game_object, Enemy):
            self.enemies.append(game_object)
        elif isinstance(game_object, Word):
            self.words.append(game_object)
        elif isinstance(game_object, Platform):
            self.platforms.append(game_object)
        elif isinstance(game_object, Coin):
            self.coins.append(game_object)

    def update(self, commands):
        potential_x = self.player.x
        potential_y = self.player.y
        if commands[CMD_RIGHT]:
            if self.player.direction == LEFT:
                self.player.set_look_right()
            if self.player.x_energy > 0:
                potential_x += 1
        elif commands[CMD_LEFT]:
            if self.player.direction == RIGHT:
                self.player.set_look_left()
            if self.player.x_energy > 0:
                potential_x -= 1
        if commands[CMD_UP]:
            if not self.player.jump_trick.is_active and self.player.is_on_ground and self.player.y_energy > 0:
                self.player.jump_trick.start()
        elif commands[CMD_DOWN]:
            if self.player.is_transformed:
                self.player.transform()
            self.controller.commands[CMD_TRANSFORM] = False
        if commands[CMD_TRANSFORM]:
            if self.player.touching_words:
                self.player.transform(self.player.touching_words[0])
            self.controller.commands[CMD_TRANSFORM] = False
        if commands[CMD_1]:
            self.player.execute_action_by_command_number(CMD_1)
            commands[CMD_1] = False
        if commands[CMD_2]:
            self.player.execute_action_by_command_number(CMD_2)
            commands[CMD_2] = False
        if commands[CMD_3]:
            self.player.execute_action_by_command_number(CMD_3)
            commands[CMD_3] = False
        if commands[CMD_4]:
            self.player.execute_action_by_command_number(CMD_4)
            commands[CMD_4] = False
        if commands[CMD_5]:
            self.player.execute_action_by_command_number(CMD_5)
            commands[CMD_5] = False
        if commands[CMD_6]:
            self.player.execute_action_by_command_number(CMD_6)
            commands[CMD_6] = False
        if commands[CMD_7]:
            self.player.execute_action_by_command_number(CMD_7)
            commands[CMD_7] = False
        if commands[CMD_8]:
            self.player.execute_action_by_command_number(CMD_8)
            commands[CMD_8] = False
        if commands[CMD_9]:
            self.player.execute_action_by_command_number(CMD_9)
            commands[CMD_9] = False
        if commands[CMD_0]:
            self.player.execute_action_by_command_number(CMD_0)
            commands[CMD_0] = False

        if not self.player.current_transformation or self.player.current_transformation.status == 0:
            potential_y += self.y_gravity
        if self.player.jump_trick.is_active:
            (force_x, force_y) = self.player.jump_trick.get_next_xy_forces()
            potential_x += force_x
            potential_y += force_y

        # Set actual coordinates of the player
        if potential_x != self.player.x:
            self.player.set_x_with_collision_detection(potential_x)
        if potential_y != self.player.y:
            self.player.set_y_with_collision_detection(potential_y)

        # TODO The rest should be put inside some kind of GameObject::update method
        if self.player.blinking.is_active:
            self.player.blinking.perform_next_blink_actions()

        if self.player.health <= 0:
            self.kill(self.player)

        # Update of transformation should be performed after actual x and y of the object have been set
        # TODO this probably can be written in a better way using potential x and y
        if self.player.current_transformation and self.player.current_transformation.status != 0:
            self.player.current_transformation.update()

        for enemy in self.enemies:
            potential_x = enemy.x
            potential_y = enemy.y

            if enemy.x <= self.player.x and (enemy.is_on_ground or enemy.jump_trick.is_active):
                if enemy.direction == LEFT:
                    enemy.set_look_right()
                if enemy.x_energy > 0:
                    potential_x += 1
            elif enemy.x >= self.player.x + self.player.length and (enemy.is_on_ground or enemy.jump_trick.is_active):
                if enemy.direction == RIGHT:
                    enemy.set_look_left()
                if enemy.y_energy > 0:
                    potential_x -= 1

            if enemy.is_on_ground and enemy.y_energy > 0:
                enemy.jump_trick.start()

            if not enemy.current_transformation or enemy.current_transformation.status == 0:
                potential_y += self.y_gravity
            if enemy.jump_trick.is_active:
                (force_x, force_y) = enemy.jump_trick.get_next_xy_forces()
                potential_x += force_x
                potential_y += force_y

            # Set actual coordinates of the enemy
            if potential_x != enemy.x:
                enemy.set_x_with_collision_detection(potential_x)
            if potential_y != enemy.y:
                enemy.set_y_with_collision_detection(potential_y)

            # Update of transformation should be performed after actual x and y of the object have been set
            if enemy.current_transformation and enemy.current_transformation.status != 0:
                # TODO this probably can be written in a better way using potential x and y
                enemy.current_transformation.update()

            # TODO The rest should be put inside som kind of GameObject::update method
            if enemy.blinking.is_active:
                enemy.blinking.perform_next_blink_actions()

            if enemy.health <= 0 and not enemy.blinking.is_active:  # TODO: blinking condition probably can be removed
                self.kill(enemy)

        for coin in self.coins:
            coin.update_state()

        for explosion in self.explosions:
            explosion.update_state()

        for bullet in self.bullets_pool:
            if not bullet.is_available:  # This means "not available in pool", thus currently active in the game
                bullet.update()

        for platform in self.platforms:
            platform.update_x_position()

    def render_string(self):
        result = ""
        for object_lines_in_row in self.rows:
            result += generate_string_line(object_lines_in_row, self.width) + "\n"
        return result

    def render_string2(self):
        """
        I thought this approach would be faster than simple render_string, however their speeds are equal
        :return:
        """
        render_rows = []
        for object_lines_in_row in self.rows:
            render_rows.extend(generate_string_line2(object_lines_in_row, self.width, self.empty_strings))
        return "".join(render_rows)

    def get_words_collided_by_player(self):
        return self.player.touching_words

    def step_on_finish_platform(self, game_object):
        """
        Actions to perform when game object is standing on the finish platform
        :param game_object: GameObject that caused the call of this function
        """
        if isinstance(game_object, Player):
            self.is_running = False
            self.controller.finish_game(success=True,
                                        is_tutorial=(isinstance(self, Tutorial1) or isinstance(self, Tutorial2)))

    def kill(self, game_object):
        """
        Actions to perform when game object is being "killed"
        :param game_object: GameObject to kill
        """
        game_object.delete()  # TODO Should be more interesting, like blinking before disappearing
        if isinstance(game_object, Player):
            self.is_running = False
            self.controller.finish_game(success=False,
                                        is_tutorial=(isinstance(self, Tutorial1) or isinstance(self, Tutorial2)))

    def kill_or_pass_to_next_part(self, game_object):
        """
        When a player reaches the dummy bottom platform, transfer it to the next part of the gameplay, if it is not the
        last one, otherwise kill any game object that touches it.
        :param game_object: GameObject that touches the platform
        """
        if isinstance(game_object, Player) and not self.is_last_gameplay:
            self.controller.activate_gameplay(self.sequence_number + 1, game_object)
        else:
            self.kill(game_object)

    def is_enough_space(self, directional_lines, x, y):
        """
        Check whether list of directional lines can be placed at provided coordinates without colliding
        :param directional_lines: list of directional lines
        :param x: X coordinate
        :param y: Y coordinate
        :return: True if there is enough space to place an object consisting of provided directional lines
        """
        for dline in directional_lines:
            check_y = y + dline.y_offset
            for check_x in range(x + dline.x_offsets[RIGHT], x + dline.x_offsets[RIGHT] + len(dline.texts[RIGHT])):
                # TODO currently assumed RIGHT direction
                for other_object_line in self.rows[check_y]:
                    if other_object_line.x <= check_x <= other_object_line.x + len(
                            other_object_line.directional_line.texts[other_object_line.parent.direction]):
                        return False
        return True


class GameBuilder(object):
    """
    Builds all game objects from input file.
    """
    def __init__(self, gameplay, lines, language_id, line_spacing, left, top_before_start, top_after_start, right,
                 bottom_before_finish, bottom_after_finish):
        self.gameplay = gameplay
        self.lines = lines

        self.gameplay.rows = []
        self.gameplay.coins = []
        self.gameplay.enemies = []
        self.gameplay.words = []
        self.gameplay.platforms = []
        self.gameplay.explosions = []

        # Top indentation before start-platform
        # TODO check whether player height + jump fits here
        if top_before_start > 0:
            for t in range(0, top_before_start):
                self.gameplay.rows.append([])

        # Start-platform
        if self.gameplay.sequence_number == FIRST_GAMEPLAY_SEQUENCE_NUM:
            self.gameplay.platforms.append(Platform(self.gameplay, "--------", left, len(self.gameplay.rows) - 1, None))

        # Top indentation after start-platform
        if top_after_start > 0:
            for t in range(0, top_after_start):
                self.gameplay.rows.append([])

        regex = re.compile(
            "([.,#!?~@$%^&*()_+={}:;/<>'\[\]\"\-])|(\d+)|([^.,#!?~@$%^&*()_+={}:;/<>'\[\]\"\-\d\s]+)")
        for line in lines:
            line = line.encode(encoding="utf-8", errors="replace")
            line = line.decode(encoding="utf-8", errors="replace")
            self._create_words_from_string(line, language_id, left, len(self.gameplay.rows) - 1, regex,
                                           self.gameplay.controller.connection)
            if line_spacing >= 0:
                for l in range(0, line_spacing + 1):
                    self.gameplay.rows.append([])

        # Create player only in the first gameplay (part)
        if self.gameplay.sequence_number == FIRST_GAMEPLAY_SEQUENCE_NUM:
            self.gameplay.player = Player(self.gameplay, (DirectionalLine("<", 0, ">", 0, 0),), 4, 1)

        self._place_coins()
        self._place_enemies()

        # Pool collections
        bullets = []
        for b in range(0, (len(self.gameplay.enemies) + 1) * 10):  # Approx. 10 bullets per each enemy and player
            bullets.append(Bullet(self.gameplay, (DirectionalLine("*", 0, "*", 0, 0),)))
        self.gameplay.bullets_pool = Pool(bullets)

        # Bottom indentation before finish-platform
        if bottom_before_finish > 0:
            for b in range(0, bottom_before_finish):
                self.gameplay.rows.append([])

        # Finish-platform
        if self.gameplay.is_last_gameplay:
            p_text = "========"
            start_x = random.randrange(left, self.gameplay.width - right - len(p_text))
            self.gameplay.platforms.append(Platform(self.gameplay, p_text, start_x, len(self.gameplay.rows) - 1,
                                                    self.gameplay.step_on_finish_platform,
                                                    move_x_from=left,  move_x_to=self.gameplay.width - right))

        # Dummy platforms
        self.gameplay.dummy_bottom_platform = Platform(self.gameplay, "", 0, len(self.gameplay.rows) - 1,
                                                       self.gameplay.kill_or_pass_to_next_part)
        self.gameplay.dummy_top_platform = Platform(self.gameplay, "", 0, 0, None)
        self.gameplay.dummy_side_platform = Platform(self.gameplay, "", 0, 0, None)

        # Bottom indentation after finish-platform
        if bottom_after_finish > 0:
            for b in range(0, bottom_after_finish):
                self.gameplay.rows.append([])

    def _create_words_from_string(self, string, language_id, left, y, regex_pattern, connection):
        for w in regex_pattern.finditer(string):
            self.gameplay.words.append(Word(self.gameplay, w.group(), language_id, left + w.start(), y, connection))

    def _place_coins(self):
        """
        Search for suitable coordinates to place coins and create Coin objects. Quantity depends on difficulty level.
        """
        if self.gameplay.difficulty > 0:
            potential_coordinates = []
            potential_words = []
            directional_lines = (DirectionalLine("(0)", 0, "(0)", 0, 0),)
            for word in self.gameplay.words:
                potential_y = word.y - len(directional_lines)
                for potential_x in range(word.x, word.x + len(word.text)):
                    if self.gameplay.is_enough_space(directional_lines, potential_x, potential_y):
                        potential_coordinates.append((potential_x, potential_y))
                        if word not in potential_words:
                            potential_words.append(word)

            # Number of coins for selected difficulty
            c_count = int(len(potential_words) * float(self.gameplay.difficulty) / 600)  # 600 is got experimentally

            if c_count == 0:
                c_count = 1  # Eliminating division by zero

            # Step to iterate over coin coordinates
            step = int(len(potential_coordinates) / c_count)

            # Index of first potential coin coordinate
            for c_coord in potential_coordinates[::step]:
                start_price = random.randrange(0, 9)
                self.gameplay.coins.append(Coin(self.gameplay, directional_lines, start_price, c_coord[0], c_coord[1],
                                                price_change_time=2))

    def _place_enemies(self):
        """
        Search for suitable coordinates to place enemies and create Enemy objects. Quantity depends on difficulty level.
        """
        if self.gameplay.difficulty > 0:
            potential_coordinates = []
            potential_words = []
            e_directional_lines = (DirectionalLine("__/\"\"|", 1, "|\"\"\__", 0, 0),
                                   DirectionalLine("(___._|", 0, "|_.___)", 0, 1))
            for word in self.gameplay.words:
                potential_y = word.y - len(e_directional_lines)
                for potential_x in range(word.x, word.x + len(word.text)):
                    if self.gameplay.is_enough_space(e_directional_lines, potential_x, potential_y):
                        potential_coordinates.append((potential_x, potential_y))
                        if word not in potential_words:
                            potential_words.append(word)

            # Number of enemies for selected difficulty
            e_count = int(len(potential_words) * float(self.gameplay.difficulty) / 500)  # 500 is got experimentally

            if e_count == 0:
                e_count = 1  # Eliminating division by zero

            # TODO add randomness
            # So that first enemy does not appear right near player's starting position
            start_coord_index = 0
            if len(potential_coordinates) > 1:
                start_coord_index = int(len(potential_coordinates) * 0.3)  # TODO 0.3 is not good in case of many lines

            # Step to iterate over enemy coordinates
            step = int((len(potential_coordinates) - start_coord_index) / e_count)

            # Index of first potential enemy coordinate
            for e_coord in potential_coordinates[start_coord_index::step]:
                self.gameplay.enemies.append(Enemy(self.gameplay, e_directional_lines, e_coord[0], e_coord[1]))


class Tutorial1(Gameplay):
    # TODO very bad solution
    def __init__(self, controller):
        Gameplay.__init__(self, controller, 1, [], 1, 0, 1, 1, 0, 0, 0, 0, 0, False, is_custom_game_builder=True)

        self.rows = []
        for r in range(0, 38):
            self.rows.append([])
        self.width = 56

        self.coins = []
        self.enemies = []
        self.explosions = []
        self.words = [
            Word(self, "Welcome to " + APP_NAME + "!", 1, x=12, y=0),
            Word(self, "Let us walk you through the basics of this game:", 1, x=0, y=1),
            Word(self, "1. That is  you  down there standing on the platform.", 1, x=0, y=5),
            Word(self, "   This is   |  a place where every game begins.", 1, x=0, y=6),
            Word(self, "   Your goal |  is to reach another platform", 1, x=0, y=7),
            Word(self, "   in the    |  end of the file." , 1, x=0, y=8),
            Word(self, "             |", 1, x=0, y=9),
            Word(self, "             |", 1, x=0, y=10),
            Word(self, "             V", 1, x=0, y=11),
            Word(self, "------.   .--------.", 1, x=27, y=13), Word(self, "|___|        |", 1, x=33, y=14),
            Word(self, "|", 1, x=46, y=15), Word(self, "V", 1, x=46, y=16),
            Word(self, "2.", 1, x=0, y=20), Word(self, "Try", 1, x=3, y=20), Word(self, "to", 1, x=7, y=20),
            Word(self, "jump", 1, x=10, y=20), Word(self, "down", 1, x=15, y=20), Word(self, "to", 1, x=20, y=20),
            Word(self, "this", 1, x=23, y=20), Word(self, "paragraph.", 1, x=28, y=20),
            Word(self, " -", 1, x=2, y=21), Word(self, "use", 1, x=5, y=21), Word(self, "arrow", 1, x=9, y=21),
            Word(self, "keys", 1, x=15, y=21), Word(self, "on", 1, x=20, y=21), Word(self, "your", 1, x=23, y=21),
            Word(self, "keyboard", 1, x=28, y=21), Word(self, "to", 1, x=37, y=21), Word(self, "move", 1, x=40, y=21),
            Word(self, "right/left;", 1, x=45, y=21),
            Word(self, "-", 1, x=3, y=22), Word(self, "use", 1, x=5, y=22), Word(self, "up", 1, x=9, y=22),
            Word(self, "arrow", 1, x=12, y=22), Word(self, "key", 1, x=18, y=22), Word(self, "to", 1, x=22, y=22),
            Word(self, "jump;", 1, x=25, y=22),
            Word(self, "See", 1, x=3, y=23), Word(self, "how", 1, x=7, y=23), Word(self, "attributes", 1, x=11, y=23),
            Word(self, "change", 1, x=22, y=23), Word(self, "on", 1, x=29, y=23), Word(self, "the", 1, x=32, y=23),
            Word(self, "panel", 1, x=36, y=23), Word(self, "when", 1, x=42, y=23), Word(self, "you", 1, x=47, y=23),
            Word(self, "move.", 1, x=51, y=23),
            Word(self, "Find", 1, x=3, y=24), Word(self, "your", 1, x=8, y=24), Word(self, "way", 1, x=13, y=24),
            Word(self, "through", 1, x=17, y=24), Word(self, "this", 1, x=25, y=24),
            Word(self, "paragraph", 1, x=30, y=24), Word(self, "to", 1, x=40, y=24), Word(self, "the", 1, x=43, y=24),
            Word(self, "next", 1, x=47, y=24), Word(self, "one!", 1, x=52, y=24),
            Word(self, "--------.", 1, x=47, y=27),
            Word(self, "|", 1, x=55, y=28), Word(self, "|", 1, x=55, y=29), Word(self, "|", 1, x=55, y=30),
            Word(self, "|", 1, x=55, y=31), Word(self, "|", 1, x=55, y=32), Word(self, "|", 1, x=55, y=33),
            Word(self, "|", 1, x=55, y=34), Word(self, "|", 1, x=55, y=35), Word(self, "V", 1, x=55, y=36),
            Word(self, "3.", 1, x=0, y=30), Word(self, "The", 1, x=3, y=30), Word(self, "content", 1, x=7, y=30),
            Word(self, "of", 1, x=15, y=30), Word(self, "the", 1, x=18, y=30), Word(self, "file", 1, x=22, y=30),
            Word(self, "can", 1, x=27, y=30), Word(self, "be", 1, x=31, y=30), Word(self, "split", 1, x=34, y=30),
            Word(self, "into", 1, x=40, y=30), Word(self, "parts.", 1, x=45, y=30),
            Word(self, "If", 1, x=3, y=31), Word(self, "you", 1, x=6, y=31), Word(self, "don't", 1, x=10, y=31),
            Word(self, "see", 1, x=16, y=31), Word(self, "moving", 1, x=20, y=31), Word(self, "finish", 1, x=27, y=31),
            Word(self, "platform", 1, x=34, y=31), Word(self, "in", 1, x=43, y=31), Word(self, "the", 1, x=46, y=31),
            Word(self, "bottom,", 1, x=3, y=32), Word(self, "that", 1, x=11, y=32), Word(self, "means", 1, x=16, y=32),
            Word(self, "you", 1, x=22, y=32), Word(self, "have", 1, x=26, y=32), Word(self, "not", 1, x=31, y=32),
            Word(self, "yet", 1, x=35, y=32), Word(self, "reached", 1, x=39, y=32), Word(self, "the", 1, x=47, y=32),
            Word(self, "final", 1, x=3, y=33), Word(self, "part", 1, x=9, y=33), Word(self, "of", 1, x=14, y=33),
            Word(self, "the", 1, x=17, y=33), Word(self, "file.", 1, x=21, y=33),
            Word(self, "Feel", 1, x=3, y=34), Word(self, "free", 1, x=8, y=34), Word(self, "to", 1, x=13, y=34),
            Word(self, "jump", 1, x=16, y=34), Word(self, "down", 1, x=21, y=34), Word(self, "anywhere", 1, x=26, y=34),
            Word(self, "in", 1, x=35, y=34), Word(self, "order", 1, x=38, y=34), Word(self, "to", 1, x=44, y=34),
            Word(self, "go", 1, x=47, y=34),
            Word(self, "to", 1, x=3, y=35), Word(self, "the", 1, x=6, y=35), Word(self, "next", 1, x=10, y=35),
            Word(self, "part!", 1, x=15, y=35),
        ]
        self.platforms = [
            Platform(self, "=========", 9, 15, None)
        ]

        # Create player only in the first tutorial part
        if self.sequence_number == FIRST_GAMEPLAY_SEQUENCE_NUM:
            self.player = Player(self, (DirectionalLine("<", 0, ">", 0, 0),), 13, 11)
            self.player.x_energy = 200
            self.player.y_energy = 197

        # Create bullets
        bullets = []
        for b in range(0, 20):
            bullets.append(Bullet(self, (DirectionalLine("*", 0, "*", 0, 0),)))
        self.bullets_pool = Pool(bullets)

        # Dummy platforms
        self.dummy_bottom_platform = Platform(self, "", 0, len(self.rows) - 1, self.kill_or_pass_to_next_part)
        self.dummy_top_platform = Platform(self, "", 0, 0, None)
        self.dummy_side_platform = Platform(self, "", 0, 0, None)

        self.initial_coins_count = 0
        self.initial_enemies_count = 0


class Tutorial2(Gameplay):
    # TODO very bad solution
    def __init__(self, controller):
        Gameplay.__init__(self, controller, 1, [], 1, 0, 1, 1, 0, 0, 0, 0, 0, True, is_custom_game_builder=True)

        self.rows = []
        for r in range(0, 32):
            self.rows.append([])
        self.width = 57

        self.coins = []
        self.explosions = []

        enemy = Enemy(self,
                      (
                          DirectionalLine(".===.", 2, ".===.", 2, 0),
                          DirectionalLine("\\_[o o]_/", 0, "\\_[o o]_/", 0, 1),
                          DirectionalLine("\\_/", 3, "\\_/", 3, 2),
                      ),
                      x=3,
                      y=20)
        enemy.health = 50
        self.enemies = [enemy]

        self.words = [
            Word(self, "----.", 1, x=53, y=3), Word(self, "|", 1, x=57, y=4), Word(self, "|", 1, x=57, y=5),
            Word(self, "|", 1, x=57, y=6), Word(self, "|", 1, x=57, y=7), Word(self, "|", 1, x=57, y=8),
            Word(self, "|", 1, x=57, y=9), Word(self, "|", 1, x=57, y=10), Word(self, "|", 1, x=57, y=11),
            Word(self, "|", 1, x=57, y=12), Word(self, "|", 1, x=57, y=13), Word(self, "|", 1, x=57, y=14),
            Word(self, "|", 1, x=57, y=15), Word(self, "<----'", 1, x=52, y=16),
            Word(self, "Now", 1, x=0, y=5), Word(self, "see", 1, x=4, y=5), Word(self, "this", 1, x=8, y=5),
            Word(self, "bad", 1, x=13, y=5), Word(self, "guy", 1, x=17, y=5), Word(self, "waiting", 1, x=21, y=5),
            Word(self, "for", 1, x=29, y=5), Word(self, "you", 1, x=33, y=5), Word(self, "a", 1, x=37, y=5),
            Word(self, "few", 1, x=39, y=5), Word(self, "lines", 1, x=43, y=5), Word(self, "below?", 1, x=49, y=5),
            Word(self, "Those", 1, x=0, y=6), Word(self, "can", 1, x=6, y=6), Word(self, "either", 1, x=10, y=6),
            Word(self, "be", 1, x=17, y=6), Word(self, "attacked", 1, x=20, y=6), Word(self, "or", 1, x=29, y=6),
            Word(self, "avoided.", 1, x=32, y=6), Word(self, "Let's", 1, x=0, y=7), Word(self, "attack", 1, x=6, y=7),
            Word(self, "that", 1, x=13, y=7), Word(self, "one!", 1, x=18, y=7),
            Word(self, "Words", 1, x=0, y=9), Word(self, "can", 1, x=6, y=9), Word(self, "be", 1, x=10, y=9),
            Word(self, "used", 1, x=13, y=9), Word(self, "to", 1, x=18, y=9), Word(self, "transform ", 1, x=21, y=9),
            Word(self, "and ", 1, x=31, y=9), Word(self, "gain ", 1, x=35, y=9), Word(self, "new ", 1, x=40, y=9),
            Word(self, "abilities:", 1, x=44, y=9),
            Word(self, "-", 1, x=0, y=10), Word(self, "jump", 1, x=2, y=10), Word(self, "on", 1, x=7, y=10),
            Word(self, "the", 1, x=10, y=10), Word(self, "\"GUN\"", 1, x=14, y=10), Word(self, "word", 1, x=20, y=10),
            Word(self, "below", 1, x=25, y=10),
            Word(self, "-", 1, x=0, y=11), Word(self, "press", 1, x=2, y=11), Word(self, "Enter", 1, x=8, y=11),
            Word(self, "once", 1, x=14, y=11), Word(self, "standing", 1, x=19, y=11),
            Word(self, "on", 1, x=28, y=11), Word(self, "it", 1, x=31, y=11),
            Word(self, "Ability", 1, x=0, y=13), Word(self, "to", 1, x=8, y=13), Word(self, "shoot", 1, x=11, y=13),
            Word(self, "will", 1, x=17, y=13), Word(self, "be", 1, x=22, y=13), Word(self, "assigned", 1, x=25, y=13),
            Word(self, "to", 1, x=0, y=14), Word(self, "action", 1, x=3, y=14), Word(self, "number", 1, x=10, y=14),
            Word(self, "1.", 1, x=17, y=14),
            Word(self, "-", 1, x=0, y=15), Word(self, "press", 1, x=2, y=15), Word(self, "1", 1, x=8, y=15),
            Word(self, "to", 1, x=10, y=15), Word(self, "shoot", 1, x=13, y=15), Word(self, "and", 1, x=19, y=15),
            Word(self, "defeat", 1, x=2, y=16), Word(self, "the", 1, x=9, y=16), Word(self, "bad", 1, x=13, y=16),
            Word(self, "guy!", 1, x=17, y=16), Word(self, "*****", 1, x=47, y=17),
            Word(self, "When", 1, x=0, y=24), Word(self, "the", 1, x=5, y=24), Word(self, "bad", 1, x=9, y=24),
            Word(self, "guy", 1, x=13, y=24), Word(self, "is", 1, x=17, y=24), Word(self, "defeated", 1, x=20, y=24),
            Word(self, "use", 1, x=29, y=24), Word(self, "down", 1, x=33, y=24), Word(self, "arrow", 1, x=38, y=24),
            Word(self, "key", 1, x=44, y=24), Word(self, "to", 1, x=48, y=24),
            Word(self, "transform", 1, x=0, y=25), Word(self, "back", 1, x=10, y=25), Word(self, "to", 1, x=15, y=25),
            Word(self, "your", 1, x=18, y=25), Word(self, "initial", 1, x=23, y=25),
            Word(self, "appearance", 1, x=31, y=25), Word(self, "(if", 1, x=42, y=25), Word(self, "you", 1, x=46, y=25),
            Word(self, "want).", 1, x=50, y=25),
            Word(self, "Then", 1, x=0, y=27), Word(self, "jump", 1, x=5, y=27), Word(self, "on", 1, x=10, y=27),
            Word(self, "the", 1, x=13, y=27), Word(self, "finish", 1, x=17, y=27),
            Word(self, "platform,", 1, x=24, y=27), Word(self, "but", 1, x=34, y=27), Word(self, "try", 1, x=38, y=27),
            Word(self, "not", 1, x=42, y=27), Word(self, "to", 1, x=46, y=27), Word(self, "miss", 1, x=49, y=27),
            Word(self, "it!", 1, x=54, y=27),
        ]

        gun_word = Word(self, "GUN", 1, x=48, y=16)
        gun_word.meaning.directional_lines = (
            DirectionalLine(",__________/_", 0, "_\\__________,", 1, 0),
            DirectionalLine("|________    |", 0, "|    ________|", 0, 1, 1, 1),
            DirectionalLine("\\'|  |", 8, "|  |'/", 0, 2),
            DirectionalLine("'|__|", 9, "|__|'", 0, 3),
        )
        gun_word.meaning.immediate_changes.bullets_change = 25
        gun_word.meaning.command_action_map[1] = Action(controller.connection, 1)
        gun_word.meaning.command_action_map[2] = None
        gun_word.is_consumable = True
        self.words.append(gun_word)

        self.platforms = [
            Platform(self, "=========", 9, 31, self.step_on_finish_platform, move_x_from=1,  move_x_to=self.width - 1)
        ]

        # Create bullets
        bullets = []
        for b in range(0, 20):
            bullets.append(Bullet(self, (DirectionalLine("*", 0, "*", 0, 0),)))
        self.bullets_pool = Pool(bullets)

        # Dummy platforms
        self.dummy_bottom_platform = Platform(self, "", 0, len(self.rows) - 1, self.kill_or_pass_to_next_part)
        self.dummy_top_platform = Platform(self, "", 0, 0, None)
        self.dummy_side_platform = Platform(self, "", 0, 0, None)

        self.initial_coins_count = 0
        self.initial_enemies_count = 0


class Transformation(object):
    """
    Process of transformation from one object to another.
    """
    def __init__(self, game_object, new_lines, word=None):
        self.game_object = game_object
        self.gameplay_rows = game_object.gameplay.rows
        self.old_lines = game_object.lines
        self.old_lines_init_length = len(self.old_lines)
        self.new_lines = new_lines
        self.new_lines_init_length = len(self.new_lines)
        self.currently_deleted_line_id = 0
        self.currently_added_line_id = None
        self.remember_y = None
        self.status = 1  # 1 - deletion, 2 - addition, 0 - finished
        self.word = word

        # Get new game_object x
        self.new_object_x = game_object.x + (get_max_length(game_object.lines, self.game_object.direction)
                                             - get_max_length(self.new_lines, self.game_object.direction)) / 2
        self.game_object.length = get_max_length(self.new_lines, self.game_object.direction)

    def update(self):
        # Remove from_lines one by one from top to bottom
        if self.status == 1:
            if self.old_lines:
                currently_deleted_line = self.old_lines[self.currently_deleted_line_id]
                self.remember_y = currently_deleted_line.y
                self.gameplay_rows[self.remember_y].remove(currently_deleted_line)
                self.old_lines.remove(currently_deleted_line)  # TODO ObjectLine.delete() method
            else:
                # Prepare for the next phase - addition of the new lines
                self.currently_deleted_line_id = self.old_lines_init_length
                self.currently_added_line_id = self.new_lines_init_length - 1

                # Change object's coordinates when all old lines are deleted but before addition of new ones
                self.game_object.x = self.new_object_x
                self.game_object.y = self.remember_y + 1 - self.new_lines_init_length

                # Set "addition" status
                self.status = 2
        elif self.status == 2:
            # Add to_lines one by one from bottom to top
            if self.currently_added_line_id >= 0:
                currently_added_line = ObjectLine(self.game_object,
                                                  self.new_lines[self.currently_added_line_id])

                self.game_object.lines.insert(0, currently_added_line)

                self.currently_added_line_id -= 1
            else:
                # Finish transformation and perform post-transformation modifications
                self.status = 0
                self.game_object.perform_post_transformation_modifications(self.word)


class Trick(object):
    """
    Represents collection of sequential coordinate changes (or forces applied to object coordinates)
    """
    def __init__(self, stages):
        """
        Create new trick
        :param stages: list of forces applied to x-y respectively (e.g. ((0, -2), (0, -2)))
        """
        self.stages = stages
        self.current_stage_id = 0
        self.is_active = False

    def start(self):
        self.is_active = True

    def get_next_xy_forces(self):
        try:
            result = self.stages[self.current_stage_id]
        except IndexError:
            # Do nothing in case of changing the quantity of stages while being in the process of jumping
            return
        self.current_stage_id += 1
        if self.current_stage_id == len(self.stages):
            self.reset()
        return result

    def reset(self):
        self.current_stage_id = 0
        self.is_active = False

    def set_repeated_stages(self, stage, quantity):
        """
        Delete all stages in the list of trick's stages and then append new stage N times
        :param stage: stage represented as (x force, y force) tuple
        :param quantity: number of repeats
        """
        del self.stages[:]
        self.stages.extend([stage for s in range(quantity)])

    def append_repeated_stages(self, stage, quantity):
        """
        Append new stage N times in case of positive quantity;
        Delete last stages in the list in case of negative quantity
        :param stage: stage represented as (x force, y force) tuple
        :param quantity: number of repeats
        """
        if quantity > 0:
            self.stages.extend([stage for s in range(quantity)])
        elif quantity < 0:
            if -quantity > len(self.stages):
                quantity = -self.stages
            del self.stages[quantity]  # del list[-X] deletes last X values from list


class Blink(object):
    """
    First "blink", then "un-blink" - this is a single phase of the Blink
    """
    def __init__(self, game_object):
        self.game_object = game_object
        self.times_to_blink = 0
        self.blinking_type = 0
        self.is_active = False
        self.is_unblinking = False  # If True - the "un-blinking" phase of switching to original texts is performed

    def start(self, times_to_blink, blinking_type):
        self.times_to_blink = times_to_blink
        self.blinking_type = blinking_type
        self.is_active = True

    def perform_next_blink_actions(self):
        if self.times_to_blink > 0:
            self.game_object.blink(blinking_type=self.blinking_type, is_set_original_texts=self.is_unblinking)
            if self.is_unblinking:
                self.times_to_blink -= 1
            self.is_unblinking = not self.is_unblinking
        else:
            self.stop_and_reset()

    def stop_and_reset(self):
        self.times_to_blink = 0
        self.blinking_type = 0
        self.is_active = False


class Pool(object):
    """
    Collection and handler of reusable instances of game objects. Number of instances is limited that helps avoid
    creation of a large number of instances during the game play (i.e. shooting bullets)
    """
    def __init__(self, poolables):
        """
        :param poolables: list of object that extend Poolable class
        """
        self.poolables = poolables

    def fetch_single_available(self):
        """
        Fetch available instance from the pool.
        :return: instance of the available object. Return None if none of objects in the pool is available.
        """
        for poolable in self.poolables:
            if poolable.is_available:
                poolable.is_available = False
                return poolable
        return None

    def __iter__(self):
        """
        Make Pool object iterable
        """
        return iter(self.poolables)


class Poolable(GameObject):
    """
    Game object that is available for pooling: to be part of a collection of reusable instances of game objects.
    Used to avoid creation of a large number of instances. In this case number of instances is limited.
    """
    def __init__(self, gameplay, lines):
        super(Poolable, self).__init__(gameplay, lines, HIDE_X, HIDE_Y)
        self.is_available = True
        self.become_invisible()

    def put_back_into_pool(self):
        """
        Set poolable object available again and hide it outside the "viewport"
        """
        self.set_x_no_collision_detection(HIDE_X)
        self.set_y_no_collision_detection(HIDE_Y)
        self.is_available = True
        self.become_invisible()


class Bullet(Poolable):

    def __init__(self, gameplay, lines):
        super(Bullet, self).__init__(gameplay, lines)
        self.subject_changes = None
        self.shooter = None

    def start_shot(self, shooting_line, subject_changes):
        """
        Position the bullet at the starting coordinates of the shot
        :param shooting_line: game object line from which the shot is performed
        :param subject_changes: changes that would be applied to the subject (game object that is shot by the bullet)
        """
        self.shooter = shooting_line.parent
        self.subject_changes = subject_changes
        self.direction = shooting_line.parent.direction
        self.become_visible()  # TODO maybe call this inside Pool::fetch_single_available?

        if self.direction == RIGHT:
            self.set_x_with_collision_detection(
                shooting_line.x + len(shooting_line.directional_line.texts[RIGHT]))
        elif self.direction == LEFT:
            self.set_x_with_collision_detection(shooting_line.x - 1)
        self.set_y_with_collision_detection(shooting_line.y)

    def update(self):
        """
        Update during flight
        """
        # Collision with other objects is handled inside set_x_with_collision_detection method
        if self.direction == RIGHT:
            if not self.set_x_with_collision_detection(self.x + 1):
                self.put_back_into_pool()
        elif self.direction == LEFT:
            if not self.set_x_with_collision_detection(self.x - 1):
                self.put_back_into_pool()
