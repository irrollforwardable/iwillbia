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

from editor_dialogs import *


def get_language_id_dictionary(db_connection):
    result = {}
    cursor = db_connection.cursor()
    cursor.execute("select id, name from languages")
    db_rows = cursor.fetchall()
    for row in db_rows:
        result[row[1]] = row[0]
    return result


def reverse_string_correctly(string):
    """
    Reverse provided string in the opposite direction, also handling symbols like > and /
    :param string:
    :return: reversed string
    """
    # TODO needs refactoring
    result = ""
    opposites = {">": "<", "<": ">", "/": "\\", "\\": "/", "(": ")", ")": "(", "]": "[", "[": "]", "}": "{", "{": "}"}
    lines = string.split("\n")

    # Get width of the entire group of lines
    width = 0
    for cl2 in lines:
        if len(cl2) > width:
            width = len(cl2)

    # Reverse each line
    for line in lines:
        rev_line = ""
        line = line.rstrip()
        rev_space_count = width - len(line)

        for char in line[::-1]:
            if char in opposites.keys():
                rev_line += opposites[char]
            else:
                rev_line += char
        rev_line = " " * rev_space_count + rev_line
        rev_line = rev_line.rstrip()
        rev_line += "\n"

        result += rev_line

    result = result.rstrip("\n")

    return result


class WordEditorPanel(tk.Frame):
    def __init__(self, parent, db_connection):
        tk.Frame.__init__(self, parent)
        self.opened_item = None

        self.header = Header(self, db_connection)
        self.header.pack(anchor=tk.W)

        Separator(self).pack(fill=tk.X, padx=5, pady=5)

        self.details = Details(self, db_connection)
        self.details.pack(fill=tk.BOTH, expand=1)


class Header(tk.Frame):
    """
    Panel containing header information about word, such as: name, language, immediate change
    """
    def __init__(self, parent, db_connection):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # GUI elements
        self.word_panel = LabeledEntry(self, "Word(-s) (comma-separated): ")
        self.word_panel.pack(side=tk.LEFT, padx=10)

        self.language_panel = OptionEntry(self, get_language_id_dictionary(db_connection), "Language: ")
        self.language_panel.pack(side=tk.LEFT, padx=10)

        self.immediate_changes = BrowseEntry(self, "Immediate changes: ",
                                             command=lambda: ChangeEditorDialog(self, db_connection,
                                                                                self.immediate_changes,
                                                                                self.immediate_changes.get_kept_id()))
        self.immediate_changes.pack(side=tk.LEFT, padx=10)

    def show_immediate_change_editor_dialog(self):
        pointer_to_self_changes = None
        if self.parent.opened_item:
            pointer_to_self_changes = self.parent.opened_item.self_changes
        ChangeEditorDialog(self, self.db_connection, self.self_change_value, pointer_to_self_changes)


class Details(tk.Frame):
    """
    Contains list of word's actions and list of word's lines
    """
    def __init__(self, parent, db_connection):
        tk.Frame.__init__(self, parent)

        self.resizable_panel = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RIDGE, sashwidth=5)
        self.resizable_panel.pack(fill=tk.BOTH, expand=1)

        self.actions_panel = Actions(self, db_connection)
        self.lines_panel = Lines(self)

        self.resizable_panel.add(self.actions_panel)
        self.resizable_panel.add(self.lines_panel)


class Actions(tk.Frame):
    """
    List of word's actions
    """
    def __init__(self, parent, db_connection):
        tk.Frame.__init__(self, parent)

        self.action_1 = BrowseEntry(self, "Action 1: ",
                                    command=lambda: ActionEditorDialog(self, db_connection,
                                                                       self.action_1, self.action_1.get_kept_id()))
        self.action_1.pack(padx=10)
        self.action_2 = BrowseEntry(self, "Action 2: ",
                                    command=lambda: ActionEditorDialog(self, db_connection,
                                                                       self.action_2, self.action_2.get_kept_id()))
        self.action_2.pack(padx=10)
        self.action_3 = BrowseEntry(self, "Action 3: ",
                                    command=lambda: ActionEditorDialog(self, db_connection,
                                                                       self.action_3, self.action_3.get_kept_id()))
        self.action_3.pack(padx=10)
        self.action_4 = BrowseEntry(self, "Action 4: ",
                                    command=lambda: ActionEditorDialog(self, db_connection,
                                                                       self.action_4, self.action_4.get_kept_id()))
        self.action_4.pack(padx=10)
        self.action_5 = BrowseEntry(self, "Action 5: ",
                                    command=lambda: ActionEditorDialog(self, db_connection,
                                                                       self.action_5, self.action_5.get_kept_id()))
        self.action_5.pack(padx=10)
        self.action_6 = BrowseEntry(self, "Action 6: ",
                                    command=lambda: ActionEditorDialog(self, db_connection,
                                                                       self.action_6, self.action_6.get_kept_id()))
        self.action_6.pack(padx=10)
        self.action_7 = BrowseEntry(self, "Action 7: ",
                                    command=lambda: ActionEditorDialog(self, db_connection,
                                                                       self.action_7, self.action_7.get_kept_id()))
        self.action_7.pack(padx=10)
        self.action_8 = BrowseEntry(self, "Action 8: ",
                                    command=lambda: ActionEditorDialog(self, db_connection,
                                                                       self.action_8, self.action_8.get_kept_id()))
        self.action_8.pack(padx=10)
        self.action_9 = BrowseEntry(self, "Action 9: ",
                                    command=lambda: ActionEditorDialog(self, db_connection,
                                                                       self.action_9, self.action_9.get_kept_id()))
        self.action_9.pack(padx=10)
        self.action_0 = BrowseEntry(self, "Action 0: ",
                                    command=lambda: ActionEditorDialog(self, db_connection,
                                                                       self.action_0, self.action_0.get_kept_id()))
        self.action_0.pack(padx=10)


class Lines(tk.Frame):
    """
    Right-looking and left-looking word visual representation
    """
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.resizable_panel_lines = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RIDGE, sashwidth=5)
        self.resizable_panel_lines.pack(fill=tk.BOTH, expand=1)

        self.right_looking_lines = LinesSide(self, RIGHT)
        self.left_looking_lines = LinesSide(self, LEFT)

        self.resizable_panel_lines.add(self.right_looking_lines)
        self.resizable_panel_lines.add(self.left_looking_lines)

    def mirror_copy_from_left_side_to_right_side(self, text, shooting_lines_string):
        self.left_looking_lines.text_area.delete('1.0', tk.END)
        self.left_looking_lines.text_area.insert(tk.END, reverse_string_correctly(text))

        self.left_looking_lines.shooting_lines_numbers.delete(0, tk.END)
        self.left_looking_lines.shooting_lines_numbers.insert(0, shooting_lines_string)

    def mirror_copy_from_right_side_to_left_side(self, text, shooting_lines_string):
        self.right_looking_lines.text_area.delete('1.0', tk.END)
        self.right_looking_lines.text_area.insert(tk.END, reverse_string_correctly(text))

        self.right_looking_lines.shooting_lines_numbers.delete(0, tk.END)
        self.right_looking_lines.shooting_lines_numbers.insert(0, shooting_lines_string)


class LinesSide(tk.Frame):
    """
    Either right or left looking lines
    """
    def __init__(self, parent, direction):
        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.direction = direction

        if self.direction == RIGHT:
            tk.Label(self, text="Looking right -->").pack()
        elif self.direction == LEFT:
            tk.Label(self, text="<-- Looking left").pack()

        Separator(self).pack(fill=tk.X, padx=5, pady=3)

        shooting_lines_panel = tk.Frame(self)
        shooting_lines_panel.pack(fill=tk.BOTH, padx=5)
        word_label = tk.Label(shooting_lines_panel, text="Line number - bullet id pairs (i.e. 2:6, 3:8): ")
        word_label.pack(side=tk.LEFT)
        self.shooting_lines_numbers = tk.Entry(shooting_lines_panel)
        self.shooting_lines_numbers.pack(side=tk.LEFT)
        if self.direction == RIGHT:
            self.mirror_button = tk.Button(shooting_lines_panel, text="Mirror -->",
                                           command=self.mirror_copy_from_left_side_to_right_side)
        elif self.direction == LEFT:
            self.mirror_button = tk.Button(shooting_lines_panel, text="<-- Mirror",
                                           command=self.mirror_copy_from_right_side_to_left_side)
        self.mirror_button.pack(anchor=tk.E)

        self.lines_setting_panel = tk.Frame(self)
        self.lines_setting_panel.pack(fill=tk.BOTH, expand=1)

        self.text_area = tk.Text(self, width=40, height=20)
        self.text_area.pack(fill=tk.BOTH, expand=1)

    def mirror_copy_from_left_side_to_right_side(self):
        text = self.text_area.get("1.0", tk.END)
        shooting_lines = self.shooting_lines_numbers.get()
        self.parent.mirror_copy_from_left_side_to_right_side(text, shooting_lines)

    def mirror_copy_from_right_side_to_left_side(self):
        text = self.text_area.get("1.0", tk.END)
        shooting_lines = self.shooting_lines_numbers.get()
        self.parent.mirror_copy_from_right_side_to_left_side(text, shooting_lines)
