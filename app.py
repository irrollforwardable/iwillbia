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

import os
import sqlite3

from window import Window
from logic import Gameplay, Tutorial1, Tutorial2
from constants import *


class Controller(object):
    def __init__(self, _settings):
        self.settings = _settings

        # Game attributes
        self.interval_ms = self.settings.interval_ms
        self.current_file_name = None

        # Input attributes (Tkinter event binding does not have key-just-pressed event)
        self.commands = {CMD_JUMP: False, CMD_LEFT: False, CMD_RIGHT: False, CMD_UP: False, CMD_DOWN: False,
                         CMD_TRANSFORM: False, CMD_1: False, CMD_2: False, CMD_3: False, CMD_4: False, CMD_5: False,
                         CMD_6: False, CMD_7: False, CMD_8: False, CMD_9: False, CMD_0: False}

        # Obtain database connection
        self.connection = sqlite3.connect("data.db")

        # User interface
        self.gui = Window(self)

        # Game objects
        self.active_gameplay_number = 1
        self.gameplays = {}

        # Start tutorial
        self.start_tutorial()

    def update(self):
        """
        Game loop
        """
        if self.gameplays and self.gameplays[self.active_gameplay_number]\
                and self.gameplays[self.active_gameplay_number].is_running:
            self.gameplays[self.active_gameplay_number].update(self.commands)
            self.gui.update_info(health=self.gameplays[self.active_gameplay_number].player.health,
                                 x_energy=self.gameplays[self.active_gameplay_number].player.x_energy,
                                 y_energy=self.gameplays[self.active_gameplay_number].player.y_energy,
                                 jump_power=len(self.gameplays[self.active_gameplay_number].player.jump_trick.stages),
                                 bullets=self.gameplays[self.active_gameplay_number].player.bullets,
                                 capacity=self.gameplays[self.active_gameplay_number].player.capacity,
                                 coins=self.gameplays[self.active_gameplay_number].player.coins,
                                 words=self.gameplays[self.active_gameplay_number].get_words_collided_by_player())
            self.gui.game_area.render(self.gameplays[self.active_gameplay_number].render_string())
            # TODO camera following the player. The solution below is not perfect.
            # self.gui.follow_player_y_view(round(
            #     self.gameplays[self.active_gameplay_number].player.y
            #     / float(len(self.gameplays[self.active_gameplay_number].rows) * 1.1), 2))

        self.gui.after(self.interval_ms, self.update)

    def start(self):
        """
        Start the entire application: both GUI and logic
        """
        self.gui.start_gui_loop(self.interval_ms, self.update)

    def start_tutorial(self):
        """
        Start tutorial session.
        """
        self.active_gameplay_number = 1
        self.gameplays = {
            self.active_gameplay_number: Tutorial1(self),
            self.active_gameplay_number + 1: Tutorial2(self)
        }

        # Start tutorial
        self.gameplays[self.active_gameplay_number].is_running = True
        self.gui.set_scrollable_area_size(self.gameplays[self.active_gameplay_number].render_string())

    def create_new_gameplay_from_file(self, file_name, language_id, difficulty, line_spacing, left, top_before_start,
                                      top_after_start, right, bottom_before_finish, bottom_after_finish,
                                      lines_per_chunk):
        """
        Start new game (gameplay)
        :param file_name: name of the text file to play on
        :param language_id:
        :param difficulty:
        :param line_spacing:
        :param left:
        :param top_before_start:
        :param top_after_start:
        :param right:
        :param bottom_before_finish:
        :param bottom_after_finish:
        :param lines_per_chunk:
        """
        self.current_file_name = None
        self.gameplays.clear()
        gameplay_count = 0
        line_count = 0
        lines = []
        # TODO file opening block needs refactoring
        with open(file_name, "r") as f:
            for line in f:
                line = line.decode(encoding="utf-8", errors="replace")
                if line_count < lines_per_chunk:
                    line_count += 1
                    lines.append(line)
                else:
                    gameplay_count += 1
                    self.gameplays[gameplay_count] = Gameplay(self, gameplay_count, lines, language_id, difficulty,
                                                              line_spacing, left, top_before_start, top_after_start,
                                                              right, bottom_before_finish, bottom_after_finish)
                    del lines[:]
                    line_count = 1
                    lines.append(line)
            # Add last unassigned lines to last gameplay
            if lines:
                gameplay_count += 1
                self.gameplays[gameplay_count] = Gameplay(self, gameplay_count, lines, language_id, difficulty,
                                                          line_spacing, left, top_before_start, top_after_start,
                                                          right, bottom_before_finish, bottom_after_finish,
                                                          is_last_gameplay=True)
            self.current_file_name = os.path.basename(f.name)
            self.active_gameplay_number = 1

        self.gui.set_scrollable_area_size(self.gameplays[self.active_gameplay_number].render_string())
        self.gui.set_window_caption(file_name=self.current_file_name,
                                    current_part=self.gameplays[self.active_gameplay_number].sequence_number,
                                    parts_total=len(self.gameplays))
        for key in self.commands:
            self.commands[key] = False
            self.gameplays[self.active_gameplay_number].is_running = True

    def construct_gui_actions_list(self, command_action_map):
        """
        Construct and display list of command_number - action_title on the information panel
        :param command_action_map: dictionary {command_number: [action_title, action_function]}
        """
        self.gui.construct_actions_list(command_action_map)

    def set_inventory_string(self, inventory_string):
        """
        Set value of the inventory panel
        :param inventory_string:
        """
        self.gui.set_inventory_string(inventory_string)

    def choose_word_id_from_list(self, word_texts_list):
        """
        Show window containing a list of words (passed as parameter) so that user can choose a word from it.
        Returns index of the chosen word.
        :param word_texts_list: list of texts of the words
        :return: index of the chosen word
        """
        for key in self.commands:
            # Corrects the bug of stucking command after word-choosing window is closed
            self.commands[key] = False
        return self.gui.show_choose_word_dialog(word_texts_list)

    def finish_game(self, success, is_tutorial=False):
        price_collected = self.gameplays[self.active_gameplay_number].player.coins
        price_total = 0
        enemies_eliminated = 0
        enemies_total = 0
        for gameplay in self.gameplays.values():
            price_total += gameplay.initial_coins_count * 9
            enemies_total += gameplay.initial_enemies_count
            enemies_eliminated += (gameplay.initial_enemies_count - len(gameplay.enemies))

        self.gui.finish_game(success, price_collected, price_total, enemies_eliminated, enemies_total,
                             is_tutorial=is_tutorial)

    def activate_gameplay(self, number, player):
        """
        Turn off current gameplay (part) and switch on another one
        :param number: gamplay number in the self.gameplays dictionary
        :param player: player instance which should be transferred to next gameplay
        """
        self.gameplays[self.active_gameplay_number].is_running = False
        self.active_gameplay_number = number
        player.move_to_another_gameplay(self.gameplays[self.active_gameplay_number], player.x, 0)
        self.gameplays[self.active_gameplay_number].is_running = True

        # Scroll to the top
        self.gui.follow_player_y_view(0)

        if self.current_file_name:
            self.gui.set_window_caption(file_name=self.current_file_name,
                                        current_part=self.gameplays[self.active_gameplay_number].sequence_number,
                                        parts_total=len(self.gameplays))

    def show_message(self, text):
        """
        Show message on the message panel
        :param text: text
        """
        self.gui.show_message(text)

    def is_game_already_running(self):
        return self.gameplays and self.gameplays[self.active_gameplay_number]\
               and self.gameplays[self.active_gameplay_number].is_running

    def toggle_pause_mode(self, event):
        if self.gameplays[self.active_gameplay_number].is_running:
            self.gameplays[self.active_gameplay_number].is_running = False
            self.gui.set_window_caption(file_name=self.current_file_name,
                                        current_part=self.gameplays[self.active_gameplay_number].sequence_number,
                                        parts_total=len(self.gameplays),
                                        is_paused=True)
        else:
            self.gameplays[self.active_gameplay_number].is_running = True
            self.gui.set_window_caption(file_name=self.current_file_name,
                                        current_part=self.gameplays[self.active_gameplay_number].sequence_number,
                                        parts_total=len(self.gameplays))

    ##################
    # Calls to logic #
    ##################

    def set_player_move_left(self, event):
        self.commands[CMD_LEFT] = True

    def set_player_move_right(self, event):
        self.commands[CMD_RIGHT] = True

    def stop_player_move_left(self, event):
        self.commands[CMD_LEFT] = False

    def stop_player_move_right(self, event):
        self.commands[CMD_RIGHT] = False

    def set_player_move_up(self, event):
        self.commands[CMD_UP] = True

    def stop_player_move_up(self, event):
        self.commands[CMD_UP] = False

    def set_player_move_down(self, event):
        self.commands[CMD_DOWN] = True

    def stop_player_move_down(self, event):
        self.commands[CMD_DOWN] = False

    def set_player_transform(self, event):
        self.commands[CMD_TRANSFORM] = True

    def set_player_perform_command_1(self, event):
        self.commands[CMD_1] = True

    def set_player_perform_command_2(self, event):
        self.commands[CMD_2] = True

    def set_player_perform_command_3(self, event):
        self.commands[CMD_3] = True

    def set_player_perform_command_4(self, event):
        self.commands[CMD_4] = True

    def set_player_perform_command_5(self, event):
        self.commands[CMD_5] = True

    def set_player_perform_command_6(self, event):
        self.commands[CMD_6] = True

    def set_player_perform_command_7(self, event):
        self.commands[CMD_7] = True

    def set_player_perform_command_8(self, event):
        self.commands[CMD_8] = True

    def set_player_perform_command_9(self, event):
        self.commands[CMD_9] = True

    def set_player_perform_command_0(self, event):
        self.commands[CMD_0] = True


class Settings(object):
    def __init__(self):
        self.interval_ms = 100
        self.font_name = "Courier New"
        self.font_size = 11
        self.x_step = 9
        self.y_step = 11
        self.window_x = 0
        self.window_y = 0
        self.window_width = 300
        self.window_height = 200

    def load_from_file(self, file_name):
        pass

    def save_to_file(self, file_name):
        pass


# Application entry point
if __name__ == '__main__':
    settings = Settings()
    settings.load_from_file("settings.txt")
    app_controller = Controller(settings)
    app_controller.start()
