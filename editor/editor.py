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

from edit_word_panel import *


class EditorMainDialog(tk.Toplevel):

    def __init__(self, parent, connection):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.transient(parent)  # One window in task bar
        self.grab_set()         # Modal
        self.title("Game Content Editor")
        self.iconbitmap("icon.ico")

        self.db_connection = connection

        self.new_find_save_sql_btns = NewFindSaveSqlButtonPanel(self, new_command=self.click_new,
                                                                find_command=self.click_find,
                                                                save_command=self.click_save,
                                                                save_as_command=self.click_save_as,
                                                                sql_command=self.click_sql)
        self.new_find_save_sql_btns.pack(anchor=tk.W, padx=5, pady=5)

        self.word_editor_panel = WordEditorPanel(self, self.db_connection)
        self.word_editor_panel.pack(fill=tk.BOTH, expand=1)

        # Set window position relative to parent window
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 20, parent.winfo_rooty() + 20))
        self.wait_window(self)

    def click_new(self):
        print "New"

    def click_find(self):
        SearchResultDialog(self, ("One", "Two", "Three", "Four"))

    def click_save(self):
        print "Save"

    def click_save_as(self):
        print "Save As"

    def click_sql(self):
        sql_statement_list = []

        # words
        word_id = predict_next_value("words", "id", self.db_connection)
        words_insert = SqlInsertStatement("words", (
            ColumnTypeValue("id", COL_TYPE_NUMBER, word_id),
            ColumnTypeValue("name", COL_TYPE_CHAR, self.word_editor_panel.header.word_panel.get_value().lower()),
            ColumnTypeValue("language_id", COL_TYPE_NUMBER, self.word_editor_panel.header.language_panel.get_value()),
            ColumnTypeValue("immediate_changes_id", COL_TYPE_NUMBER,
                            self.word_editor_panel.header.immediate_changes.get_value()),
            ColumnTypeValue("command_1_action_id", COL_TYPE_NUMBER,
                            self.word_editor_panel.details.actions_panel.action_1.get_value()),
            ColumnTypeValue("command_2_action_id", COL_TYPE_NUMBER,
                            self.word_editor_panel.details.actions_panel.action_2.get_value()),
            ColumnTypeValue("command_3_action_id", COL_TYPE_NUMBER,
                            self.word_editor_panel.details.actions_panel.action_3.get_value()),
            ColumnTypeValue("command_4_action_id", COL_TYPE_NUMBER,
                            self.word_editor_panel.details.actions_panel.action_4.get_value()),
            ColumnTypeValue("command_5_action_id", COL_TYPE_NUMBER,
                            self.word_editor_panel.details.actions_panel.action_5.get_value()),
            ColumnTypeValue("command_6_action_id", COL_TYPE_NUMBER,
                            self.word_editor_panel.details.actions_panel.action_6.get_value()),
            ColumnTypeValue("command_7_action_id", COL_TYPE_NUMBER,
                            self.word_editor_panel.details.actions_panel.action_7.get_value()),
            ColumnTypeValue("command_8_action_id", COL_TYPE_NUMBER,
                            self.word_editor_panel.details.actions_panel.action_8.get_value()),
            ColumnTypeValue("command_9_action_id", COL_TYPE_NUMBER,
                            self.word_editor_panel.details.actions_panel.action_9.get_value()),
            ColumnTypeValue("command_0_action_id", COL_TYPE_NUMBER,
                            self.word_editor_panel.details.actions_panel.action_0.get_value())))
        sql_statement_list.append(words_insert)

        # lines
        line_id = predict_next_value("lines", "id", self.db_connection) - 1
        lines_word_map_id = predict_next_value("lines", "word_map_id", self.db_connection)
        right_lines = self.word_editor_panel.details.lines_panel.right_looking_lines.text_area.get("1.0", tk.END)\
            .split("\n")
        left_lines = self.word_editor_panel.details.lines_panel.left_looking_lines.text_area.get("1.0", tk.END)\
            .split("\n")
        lines_to_iterate = right_lines
        if len(left_lines) > len(right_lines):
            lines_to_iterate = left_lines

        # -- shooting lines
        # TODO: needs refactoring
        right_line_bullet_pairs = {}
        right_shoot_string = self.word_editor_panel.details.lines_panel.right_looking_lines.shooting_lines_numbers.get()
        for right_line_bullet_string in right_shoot_string.replace(" ", "").split(";"):
            right_linestr_bullet = right_line_bullet_string.split(":")
            right_line_bullet_pairs[int(right_linestr_bullet[0])] = right_linestr_bullet[1]
        left_line_bullet_pairs = {}
        left_shoot_string = self.word_editor_panel.details.lines_panel.left_looking_lines.shooting_lines_numbers.get()
        for left_line_bullet_string in left_shoot_string.replace(" ", "").split(";"):
            left_linestr_bullet = left_line_bullet_string.split(":")
            left_line_bullet_pairs[int(left_linestr_bullet[0])] = left_linestr_bullet[1]

        for line_num in range(0, len(lines_to_iterate) - 1):
            line_id += 1
            right_line_text_only = right_lines[line_num].lstrip().rstrip()
            left_line_text_only = left_lines[line_num].lstrip().rstrip()
            right_x_offset = len(right_lines[line_num]) - len(right_line_text_only)
            left_x_offset = len(left_lines[line_num]) - len(left_line_text_only)
            right_bullet_id = None
            if (line_num + 1) in right_line_bullet_pairs:
                right_bullet_id = right_line_bullet_pairs[line_num + 1]
            left_bullet_id = None
            if (line_num + 1) in left_line_bullet_pairs:
                left_bullet_id = left_line_bullet_pairs[line_num + 1]
            lines_insert = SqlInsertStatement("lines", (
                ColumnTypeValue("id", COL_TYPE_NUMBER, line_id),
                ColumnTypeValue("word_map_id", COL_TYPE_NUMBER, lines_word_map_id),
                ColumnTypeValue("right_text", COL_TYPE_CHAR, right_line_text_only),
                ColumnTypeValue("right_x_offset", COL_TYPE_NUMBER, right_x_offset),
                ColumnTypeValue("right_is_for_shooting", COL_TYPE_NUMBER, right_bullet_id),
                ColumnTypeValue("left_text", COL_TYPE_CHAR, left_line_text_only),
                ColumnTypeValue("left_x_offset", COL_TYPE_NUMBER, left_x_offset),
                ColumnTypeValue("left_is_for_shooting", COL_TYPE_NUMBER, left_bullet_id),
                ColumnTypeValue("y_offset", COL_TYPE_NUMBER, line_num)
            ))
            sql_statement_list.append(lines_insert)

        # word_lines_map
        word_lines_map_insert = SqlInsertStatement("word_lines_map", (
            ColumnTypeValue("word_id", COL_TYPE_NUMBER, word_id),
            ColumnTypeValue("lines_id", COL_TYPE_NUMBER, lines_word_map_id)
        ))
        sql_statement_list.append(word_lines_map_insert)

        SqlDialog(self, sql_statement_list)
