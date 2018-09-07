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

import tkFileDialog
import platform
import webbrowser
from editor.editor import *


def show_editor_warning():
    tkMessageBox.showwarning("Warning", "WARNING: This is not a fully functional content editor for " + APP_NAME + "! "
                             "This tool is still in development and should be considered only a helper-tool for SQL "
                             "statement generation. One should have knowledge of SQL and relational database model "
                             "in order to compose produced pieces of SQL code together properly!")


class Window(tk.Tk):
    """Main window of the app"""

    def __init__(self, controller):
        self.controller = controller
        self.is_paused = False
        self.returner = None  # variable to hold returned values TODO very bad workaround

        # Setting up the window and its components
        tk.Tk.__init__(self)
        self.title(APP_NAME)
        self.iconbitmap("icon.ico")
        self.geometry('{}x{}'.format(840, 690))
        self.menu_bar = MenuBar(self)
        self.resizable_panel = tk.PanedWindow(orient=tk.HORIZONTAL, sashrelief=tk.RIDGE, sashwidth=5)
        self.resizable_panel.pack(fill=tk.BOTH, expand=1)
        self.info_area = InfoArea(self.resizable_panel)
        self.resizable_panel.add(self.info_area)
        self.game_area = GameArea(self.resizable_panel)
        self.resizable_panel.add(self.game_area)
        self.resizable_panel.update()
        self.resizable_panel.sash_place(index=0, x=int(self.resizable_panel.winfo_width() * 0.33), y=0)

        # Add menu to the window
        self.config(menu=self.menu_bar)

        # Event bindings
        self.bind("<KeyPress-Left>", self.controller.set_player_move_left)
        self.bind("<KeyPress-Right>", self.controller.set_player_move_right)
        self.bind("<KeyPress-Up>", self.controller.set_player_move_up)
        self.bind("<KeyPress-Down>", self.controller.set_player_move_down)
        self.bind("<KeyPress-Return>", self.controller.set_player_transform)
        self.bind("<KeyPress-1>", self.controller.set_player_perform_command_1)
        self.bind("<KeyPress-2>", self.controller.set_player_perform_command_2)
        self.bind("<KeyPress-3>", self.controller.set_player_perform_command_3)
        self.bind("<KeyPress-4>", self.controller.set_player_perform_command_4)
        self.bind("<KeyPress-5>", self.controller.set_player_perform_command_5)
        self.bind("<KeyPress-6>", self.controller.set_player_perform_command_6)
        self.bind("<KeyPress-7>", self.controller.set_player_perform_command_7)
        self.bind("<KeyPress-8>", self.controller.set_player_perform_command_8)
        self.bind("<KeyPress-9>", self.controller.set_player_perform_command_9)
        self.bind("<KeyPress-0>", self.controller.set_player_perform_command_0)
        self.bind("<KeyRelease-Left>", self.controller.stop_player_move_left)
        self.bind("<KeyRelease-Right>", self.controller.stop_player_move_right)
        self.bind("<KeyRelease-Up>", self.controller.stop_player_move_up)
        self.bind("<KeyRelease-Down>", self.controller.stop_player_move_down)
        self.bind("<KeyPress-p>", self.controller.toggle_pause_mode)

    def start_gui_loop(self, interval_ms, game_loop_function):
        """
        Start window mainloop and make the first run of game's loop function
        :param interval_ms: update interval in milliseconds
        :param game_loop_function: pointer to game loop function
        """
        if not self.is_paused:
            self.after(interval_ms, game_loop_function)
        self.mainloop()

    def show_open_file_dialog(self):
        """
        Open file dialog and pass chosen file path to the controller function
        """
        if self.controller.is_game_already_running():
            if not self.ask_new_gameplay_confirm():
                return

        file_path = tkFileDialog.askopenfilename(title='Choose file for the game')
        if file_path:
            GameSettingsDialog(self, file_path)
        self.focus_set()

    def start_tutorial(self):
        if self.controller.is_game_already_running():
            if not self.ask_new_gameplay_confirm():
                return

        self.controller.start_tutorial()

    def show_about_dialog(self):
        AboutDialog(self)

    def show_choose_word_dialog(self, word_texts_list):
        WordChooseDialog(self, word_texts_list)
        return self.returner

    def set_window_caption(self, file_name, current_part, parts_total, is_paused=False):
        """
        Set caption of main window, i.e. myfile.txt (3 of 5) - Appname
        :param file_name:
        :param current_part:
        :param parts_total:
        :param is_paused: add pause indicating string if set as True
        """
        pause_str = ""
        if is_paused:
            pause_str = "[PAUSED] "

        file_str = ""
        if file_name:
            file_str = str(file_name)

        self.title(pause_str + file_str + " (" + str(current_part) + " of " + str(parts_total) + ") - " + APP_NAME)

    def update_info(self, health, x_energy, y_energy, jump_power, capacity, bullets, coins, words):
        """
        Set info on the information panel
        :param health: player's health value
        :param x_energy: player's X energy value
        :param y_energy: player's Y energy value
        :param jump_power: player's jump power value
        :param capacity: player's capacity value
        :param bullets: player's bullets value
        :param coins: player's coins value
        :param words: list of words the player is currently touching
        """
        self.info_area.attributes_panel.clear_values()

        # Player's actual values
        self.info_area.attributes_panel.health_info.set_value(health)
        self.info_area.attributes_panel.x_energy_info.set_value(x_energy)
        self.info_area.attributes_panel.y_energy_info.set_value(y_energy)
        self.info_area.attributes_panel.jump_power_info.set_value(jump_power)
        self.info_area.attributes_panel.bullets_info.set_value(bullets)
        self.info_area.attributes_panel.capacity_info.set_value(capacity)
        self.info_area.attributes_panel.coins_info.set_value(coins)

        # Potential values from the words player is currently touching that player may get to his attributes when
        # transformed into a word
        word_text = ""
        for word in words:
            if word.meaning:
                word_text += word.text
                self.info_area.attributes_panel.health_info.set_potential_value(
                    word.meaning.immediate_changes.health_change, health,
                    word.meaning.immediate_changes.is_health_change_value_absolute)
                self.info_area.attributes_panel.x_energy_info.set_potential_value(
                    word.meaning.immediate_changes.x_energy_change, x_energy,
                    word.meaning.immediate_changes.is_x_energy_change_value_absolute)
                self.info_area.attributes_panel.y_energy_info.set_potential_value(
                    word.meaning.immediate_changes.y_energy_change, y_energy,
                    word.meaning.immediate_changes.is_y_energy_change_value_absolute)
                self.info_area.attributes_panel.jump_power_info.set_potential_value(
                    word.meaning.immediate_changes.jump_power_change, jump_power,
                    word.meaning.immediate_changes.is_jump_power_change_value_absolute)
                self.info_area.attributes_panel.bullets_info.set_potential_value(
                    word.meaning.immediate_changes.bullets_change, bullets,
                    word.meaning.immediate_changes.is_bullets_change_value_absolute)
                self.info_area.attributes_panel.capacity_info.set_potential_value(
                    word.meaning.immediate_changes.capacity_change, capacity,
                    word.meaning.immediate_changes.is_capacity_change_value_absolute)
                self.info_area.attributes_panel.coins_info.set_potential_value(
                    word.meaning.immediate_changes.coins_change, coins,
                    word.meaning.immediate_changes.is_coins_change_value_absolute)

    def construct_actions_list(self, command_action_map):
        """
        Construct and display list of command_number - action_title on the information panel
        :param command_action_map: dictionary {command_number: [action_title, action_function]}
        """
        for i in range(0, len(self.info_area.command_actions_panel.action_lines)):
            if command_action_map[i]:
                self.info_area.command_actions_panel.action_lines[i].set_title(command_action_map[i].title)
            else:
                self.info_area.command_actions_panel.action_lines[i].set_title("")

    def set_inventory_string(self, inventory_string):
        """Set value inside inventory panel"""
        self.info_area.inventory_panel.word_value.config(text=inventory_string)

    def set_scrollable_area_size(self, text):
        """
        Make scrollbars of the game area adjust to text content size correctly
        :param text: text to adjust to
        """
        self.game_area.set_scrollable_area_size(text)

    def follow_player_y_view(self, offset):
        self.game_area.canvas.yview_moveto(offset)

    def ask_new_gameplay_confirm(self):
        return tkMessageBox.askyesno("New game", "Are you sure you want to cancel current game and start a new one?")

    def show_message(self, text):
        """
        Show message
        :param text: information text
        """
        self.is_paused = True
        tkMessageBox.showinfo("Info", text)

        # The following happens when Ok is clicked on the message box
        self.focus_force()
        self.is_paused = False

    def finish_game(self, success, price_collected, price_total, enemies_eliminated, enemies_total, is_tutorial=False):
        """
        Actions to perform upon successful finishing of the game
        """
        stats = "Bonus points collected: " + str(price_collected) + " of " + str(price_total) + "\n"\
                + "Enemies eliminated: " + str(enemies_eliminated) + " of " + str(enemies_total)
        if success:
            if is_tutorial:
                self.show_message("Well done!\n\nYou have successfully completed the tutorial.\nNow open any text file"
                                  " (File -> New game) and start playing ;)")
            else:
                self.show_message("WELL DONE!\n\n" + stats)
        else:
            if is_tutorial:
                self.show_message("FAIL!\n\nYou have failed to complete the tutorial.\nThis however does not mean you "
                                  "cannot open any text file (File -> New game) and start playing anyway ;)")
            else:
                self.show_message("FAIL!\n\n" + stats)

    def show_settings_dialog(self):
        PreferencesDialog(self)

    def show_word_editor_dialog(self):
        show_editor_warning()
        EditorMainDialog(self, self.controller.connection)

    def show_action_editor_dialog(self):
        show_editor_warning()
        ActionEditorDialog(self, self.controller.connection)

    def show_change_editor_dialog(self):
        show_editor_warning()
        ChangeEditorDialog(self, self.controller.connection)

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    def copy_game_to_clipboard(self):
        self.copy_to_clipboard(self.game_area.canvas.itemcget(self.game_area.text_id, "text"))

    def open_online_help(self):
        webbrowser.open("https://github.com/irrollforwardable/iwillbia/wiki")

    def open_online_source_code(self):
        webbrowser.open("https://github.com/irrollforwardable/iwillbia")


class GameArea(tk.Frame):
    """
    Gaming area
    """
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.font_name = "Courier New"
        self.font_size = 11

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(self, background="#fff")
        self.horizontal_scroll = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.horizontal_scroll.grid(row=1, column=0, sticky=tk.EW)
        self.vertical_scroll = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.vertical_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        self.canvas.configure(xscrollcommand=self.horizontal_scroll.set, yscrollcommand=self.vertical_scroll.set)

        self.text_id = self.canvas.create_text(10, 5, text="", font=(self.font_name, self.font_size), anchor=tk.NW,
                                               justify=tk.LEFT, fill="#000000")

    def render(self, text):
        """
        Update the entire content of text with the text in parameter
        :param text:
        """
        self.canvas.itemconfig(self.text_id, text=text)

    def set_scrollable_area_size(self, text):
        """
        Make scrollbars adjust to text content size correctly
        :param text: text to adjust to
        """
        self.render(text)
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))


class InfoArea(tk.Frame):
    """
    Information area
    """
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, background="#F0F0F0")

        self.attributes_panel = AttributesInfoPanel(self, label_color="#F0F0F0", value_color="#FFF",
                                                    border_color="#F0F0F0")
        self.attributes_panel.pack(expand=False, fill=tk.X, padx=5)

        # Separator(self).pack(fill=tk.X, padx=5, pady=5)

        self.command_actions_panel = ActionInfoPanel(self, label_color="#F0F0F0", value_color="#FFF",
                                                     border_color="#F0F0F0")
        self.command_actions_panel.pack(expand=False, fill=tk.X, padx=5, pady=15)

        # Separator(self).pack(fill=tk.X, padx=5, pady=5)

        self.inventory_panel = InventoryPanel(self, label_color="#F0F0F0", border_color="#F0F0F0")
        self.inventory_panel.pack(expand=False, fill=tk.X, padx=5)

        self.controls_panel = ControlsLegendPanel(self, label_color="#F0F0F0", border_color="#F0F0F0")
        self.controls_panel.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)


class AttributesInfoPanel(tk.Frame):
    """
    Player attributes info
    """
    def __init__(self, parent, label_color, value_color, border_color):
        tk.Frame.__init__(self, parent, background=border_color)

        caption_label = tk.Label(self, text="Player's attributes", background=label_color)
        caption_label.pack(expand=True, fill=tk.X)

        prop_frame = tk.Frame(self, background=border_color)
        prop_frame.grid_columnconfigure(0, weight=1)

        self.health_info = AttributeInfoLine(prop_frame, 0, " " + "Health", label_color, value_color)
        self.x_energy_info = AttributeInfoLine(prop_frame, 1, " " + "X-energy", label_color, value_color)
        self.y_energy_info = AttributeInfoLine(prop_frame, 2, " " + "Y-energy", label_color, value_color)
        self.jump_power_info = AttributeInfoLine(prop_frame, 3, " " + "Jump power", label_color, value_color)
        self.capacity_info = AttributeInfoLine(prop_frame, 4, " " + "Capacity", label_color, value_color)
        self.bullets_info = AttributeInfoLine(prop_frame, 5, " " + "Bullets", label_color, value_color)
        self.coins_info = AttributeInfoLine(prop_frame, 6, " " + "Coins", label_color, value_color)

        prop_frame.pack(expand=True, fill=tk.X)

    def clear_values(self):
        self.health_info.set_value(0, do_value_coloring=False)
        self.health_info.set_potential_value(0)
        self.x_energy_info.set_value(0, do_value_coloring=False)
        self.x_energy_info.set_potential_value(0)
        self.y_energy_info.set_value(0, do_value_coloring=False)
        self.y_energy_info.set_potential_value(0)
        self.jump_power_info.set_value(0, do_value_coloring=False)
        self.jump_power_info.set_potential_value(0)
        self.capacity_info.set_value(0, do_value_coloring=False)
        self.capacity_info.set_potential_value(0)
        self.bullets_info.set_value(0, do_value_coloring=False)
        self.bullets_info.set_potential_value(0)
        self.coins_info.set_value(0, do_value_coloring=False)
        self.coins_info.set_potential_value(0)


class AttributeInfoLine(object):
    """
    Line containing info about a single player attribute
    """
    def __init__(self, parent, row, title, label_color, value_color, higher_color="blue", lower_color="red",
                 default_color="black"):
        self.title = title
        label = tk.Label(parent, text=title, background=label_color, relief=tk.GROOVE, anchor=tk.W)
        label.grid(row=row, column=0, sticky=tk.NSEW)
        self.value = tk.Label(parent, background=value_color, relief=tk.GROOVE, width=7)
        self.value.grid(row=row, column=1, sticky=tk.NSEW)
        self.potential_value = tk.Label(parent, background=value_color, relief=tk.GROOVE, width=7)
        self.potential_value.grid(row=row, column=2, sticky=tk.NSEW)
        self.default_color = default_color
        self.higher_color = higher_color
        self.lower_color = lower_color
        self.saved_int_value = 0  # stores value from the previous update (for comparison)

    def set_value(self, value, do_value_coloring=True):
        """
        Set value in the column of actual values. By default this method assigns a color to the font of the value based
        on whether this value has increased or decreased.
        :param value: int value
        :param do_value_coloring: applies font color if set as True
        """
        if do_value_coloring:
            if value < self.saved_int_value:
                self.value.config(foreground=self.lower_color)
                self.saved_int_value = value
            elif value > self.saved_int_value:
                self.value.config(foreground=self.higher_color)
                self.saved_int_value = value
            else:
                self.value.config(foreground=self.default_color)
        self.value.config(text=value)

    def set_potential_value(self, potential_value, main_value=0, is_potential_value_absolute=False):
        """
        Set value in the column of potential values (the ones that a player may get when transformed to the word)
        :param potential_value: value of the attribute that player can get when transformed into the word
        :param main_value: current actual value of the attribute
        :param is_potential_value_absolute: absolute means that player's current actual value gets replaced by potential
        value, relative means that player's current actual value gets increased by potential value
        """
        if potential_value and not is_potential_value_absolute:
            if potential_value < 0:
                self.potential_value.config(text=u"\u25BC " + str(potential_value), foreground=self.lower_color)
            elif potential_value > 0:
                self.potential_value.config(text=u"\u25B2 +" + str(potential_value), foreground=self.higher_color)
        elif potential_value and is_potential_value_absolute:
            if potential_value < main_value:
                self.potential_value.config(text=str(potential_value), foreground=self.lower_color)
            elif potential_value > main_value:
                self.potential_value.config(text=str(potential_value), foreground=self.higher_color)
        else:
            self.potential_value.config(text="")


class ActionInfoPanel(tk.Frame):
    """
    Actions info (Number - action pairs)
    """
    def __init__(self, parent, label_color, value_color, border_color):
        tk.Frame.__init__(self, parent, background=border_color)

        caption_label = tk.Label(self, text="Available actions", background=label_color)
        caption_label.pack(expand=True, fill=tk.X)

        action_frame = tk.Frame(self, background=border_color)
        action_frame.grid_columnconfigure(1, weight=1)
        self.action_lines = (
            ActionInfoLine(action_frame, 9, 0, label_color, value_color),
            ActionInfoLine(action_frame, 0, 1, label_color, value_color),
            ActionInfoLine(action_frame, 1, 2, label_color, value_color),
            ActionInfoLine(action_frame, 2, 3, label_color, value_color),
            ActionInfoLine(action_frame, 3, 4, label_color, value_color),
            ActionInfoLine(action_frame, 4, 5, label_color, value_color),
            ActionInfoLine(action_frame, 5, 6, label_color, value_color),
            ActionInfoLine(action_frame, 6, 7, label_color, value_color),
            ActionInfoLine(action_frame, 7, 8, label_color, value_color),
            ActionInfoLine(action_frame, 8, 9, label_color, value_color)
        )

        action_frame.pack(expand=True, fill=tk.X)


class ActionInfoLine(object):
    """
    Line containing info about actions assigned to a command number
    """
    def __init__(self, parent, row, command_number, label_color, value_color):
        self.command_label = tk.Label(parent, text=" " + str(command_number) + " ", background=label_color,
                                      relief=tk.GROOVE, anchor=tk.N, width=3)
        self.command_label.grid(row=row, column=0, sticky=tk.NSEW)
        self.action_label = tk.Label(parent, background=value_color, relief=tk.GROOVE, anchor=tk.W)
        self.action_label.grid(row=row, column=1, sticky=tk.NSEW)

    def set_title(self, action_title):
        if not action_title:
            action_title = ""
        self.action_label.config(text=" " + action_title)


class InventoryPanel(tk.Frame):
    """
    List of words in the inventory
    """
    def __init__(self, parent, label_color, border_color):
        tk.Frame.__init__(self, parent, background=border_color)

        tk.Label(self, text="Collected words", background=label_color).pack(expand=True, fill=tk.X)
        self.word_value = tk.Label(self, text=" ", background=label_color, relief=tk.GROOVE)
        self.word_value.pack(expand=True, fill=tk.X)

    def clear_values(self):
        self.word_value.config(text="")


class ControlsLegendPanel(tk.Frame):
    def __init__(self, parent, label_color, border_color):
        tk.Frame.__init__(self, parent, background=border_color)
        tk.Label(self,
                 text=u"\u21E6 \u21E8 - move left and right"
                      u"\n\u21E7 - jump"
                      u"\n\u23CE - transform into word"
                      u"\n\u21E9 - transform into initial form"
                      u"\nP - pause",
                 background=label_color, justify=tk.LEFT).pack(fill=tk.X, side=tk.LEFT)


class MenuBar(tk.Menu):
    """
    Menu bar with menu items
    """
    def __init__(self, parent):
        self.parent = parent

        # Menu bar itself
        tk.Menu.__init__(self, self.parent)

        # OS X application menu
        if platform.system().lower() == "darwin":
            osxmm = tk.Menu(self, name="apple")
            osxmm.add_command(label="About " + APP_NAME)
            osxmm.add_separator()
            osxmm.add_command(label="Preferences...", command=self.parent.show_settings_dialog, accelerator="Command+,")
            self.add_cascade(menu=osxmm)

        # File menu
        self.file_menu = tk.Menu(self, tearoff=0)
        self.file_menu.add_command(label="New game", command=self.parent.show_open_file_dialog)
        self.file_menu.add_command(label="Tutorial", command=self.parent.start_tutorial)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.parent.quit)
        self.add_cascade(label="File", menu=self.file_menu)

        # Edit
        self.edit_menu = tk.Menu(self, tearoff=0)
        self.edit_menu.add_command(label="Copy game to clipboard", command=self.parent.copy_game_to_clipboard)
        if platform.system().lower() != "darwin":  # Windows and Linux
            self.edit_menu.add_separator()
            self.edit_menu.add_command(label="Preferences", command=self.parent.show_settings_dialog)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Increase font", state="disabled")
        self.edit_menu.add_command(label="Shrink font", state="disabled")
        self.edit_menu.add_separator()
        self.content_editor_menu = tk.Menu(self, tearoff=0)
        self.content_editor_menu.add_command(label="New word...", command=self.parent.show_word_editor_dialog)
        self.content_editor_menu.add_command(label="New action...", command=self.parent.show_action_editor_dialog)
        self.content_editor_menu.add_command(label="New change...", command=self.parent.show_change_editor_dialog)
        self.edit_menu.add_cascade(label="Content Editor", menu=self.content_editor_menu)
        self.add_cascade(label="Edit", menu=self.edit_menu)

        # Help
        self.help_menu = tk.Menu(self, tearoff=0)
        self.help_menu.add_command(label="Online Help", command=self.parent.open_online_help)
        self.help_menu.add_command(label="Source Code", command=self.parent.open_online_source_code)
        if platform.system().lower() != "darwin":  # Windows and Linux
            self.help_menu.add_separator()
            self.help_menu.add_command(label="About", command=self.parent.show_about_dialog)
        self.add_cascade(label="Help", menu=self.help_menu)


class PreferencesDialog(tk.Toplevel):

    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.title("Preferences")
        self.iconbitmap("icon.ico")
        self.resizable(width=False, height=False)

        self.parent = parent

        body_panel = tk.Frame(self)

        main_label = tk.Label(body_panel, text="Nothing here yet :)").pack()

        body_panel.pack(fill=tk.BOTH, expand=1, padx=5, pady=10)

        button_panel = tk.Frame(self)
        ok_button = tk.Button(button_panel, text="Ok", width=10, command=self.ok, default=tk.ACTIVE)
        ok_button.pack(side=tk.LEFT, padx=5, pady=5)
        cancel_button = tk.Button(button_panel, text="Cancel", width=10, command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
        button_panel.pack(pady=5)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        self.wait_window(self)

    def ok(self):
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()

    def cancel(self):
        self.parent.focus_set()
        self.destroy()


class GameSettingsDialog(tk.Toplevel):

    def __init__(self, parent, file_name):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.title("New game")
        self.iconbitmap("icon.ico")
        self.resizable(width=False, height=False)

        self.parent = parent
        self.result = None
        self.file_name = file_name

        body_panel = tk.Frame(self)
        body_panel.grid_columnconfigure(1, weight=1)

        # Value variables
        self.language_value = tk.StringVar(body_panel)
        self.language_value.set("English")
        self.difficulty_value = tk.IntVar(body_panel)
        self.difficulty_value.set(30)
        self.line_spacing_value = tk.IntVar(body_panel)
        self.line_spacing_value.set(4)
        self.left_value = tk.IntVar(body_panel)
        self.left_value.set(4)
        self.top_before_start_value = tk.IntVar(body_panel)
        self.top_before_start_value.set(5)
        self.top_after_start_value = tk.IntVar(body_panel)
        self.top_after_start_value.set(3)
        self.right_value = tk.IntVar(body_panel)
        self.right_value.set(15)
        self.bottom_before_finish_value = tk.IntVar(body_panel)
        self.bottom_before_finish_value.set(3)
        self.bottom_after_finish_value = tk.IntVar(body_panel)
        self.bottom_after_finish_value.set(3)
        self.lines_per_chunk_value = tk.IntVar(body_panel)
        self.lines_per_chunk_value.set(10)

        setting_rows = (("Line spacing", self.line_spacing_value),
                        ("Left margin", self.left_value),
                        ("Right margin", self.right_value),
                        ("Rows before start panel", self.top_before_start_value),
                        ("Rows after start panel", self.top_after_start_value),
                        ("Rows before finish panel", self.bottom_before_finish_value),
                        ("Rows after finish panel", self.bottom_after_finish_value),
                        ("Rows per chunk", self.lines_per_chunk_value))

        # Language
        language_label = tk.Label(body_panel, text="Language", anchor=tk.W, justify=tk.LEFT)
        language_label.grid(row=0, column=0, padx=5)
        # TODO import language values from database
        lang_val = tk.StringVar(body_panel)
        lang_val.set("English")
        language_value = tk.OptionMenu(body_panel, lang_val, "English")
        language_value.grid(row=0, column=1, sticky=tk.NSEW, padx=5)

        # Difficulty
        difficulty_label = tk.Label(body_panel, text="Difficulty (%)", anchor=tk.W, justify=tk.LEFT)
        difficulty_label.grid(row=1, column=0, padx=5)
        difficulty_scale = tk.Scale(body_panel, variable=self.difficulty_value, from_=0, to=100, orient=tk.HORIZONTAL)
        difficulty_scale.grid(row=1, column=1, padx=5, pady=5)

        # Margins
        for i in range(0, len(setting_rows)):
            label = tk.Label(body_panel, text=setting_rows[i][0], anchor=tk.W)
            label.grid(row=i+2, column=0, padx=5)
            value = tk.Entry(body_panel, textvariable=setting_rows[i][1], justify=tk.RIGHT)
            value.grid(row=i+2, column=1, sticky=tk.NSEW, padx=5)

        body_panel.focus_set()
        body_panel.pack(fill=tk.X, padx=5, pady=10)

        # Buttons
        button_panel = tk.Frame(self)
        ok_button = tk.Button(button_panel, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        ok_button.pack(side=tk.LEFT, padx=5, pady=5)
        cancel_button = tk.Button(button_panel, text="Cancel", width=10, command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
        default_button = tk.Button(button_panel, text="Defaults", width=10)
        default_button.pack(side=tk.LEFT, padx=5, pady=5)
        button_panel.pack(pady=5)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        self.wait_window(self)

    def ok(self):
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()
        self.parent.controller.create_new_gameplay_from_file(self.file_name, 1, self.difficulty_value.get(),
                                                             self.line_spacing_value.get(), self.left_value.get(),
                                                             self.top_before_start_value.get(),
                                                             self.top_after_start_value.get(), self.right_value.get(),
                                                             self.bottom_before_finish_value.get(),
                                                             self.bottom_after_finish_value.get(),
                                                             self.lines_per_chunk_value.get())

    def cancel(self):
        self.parent.focus_set()
        self.destroy()


class WordChooseDialog(tk.Toplevel):
    def __init__(self, parent, word_texts_list):
        tk.Toplevel.__init__(self, parent)

        self.transient(parent)
        self.title("Choose word(-s)")
        self.parent = parent
        self.parent.returner = None

        self.selection_id = 0
        self.word_texts_list = word_texts_list

        main_panel = tk.Frame(self)

        self.word_listbox = tk.Listbox(main_panel, selectmode=tk.SINGLE)
        for word_string in self.word_texts_list:
            self.word_listbox.insert(tk.END, word_string)

        main_panel.grid_rowconfigure(0, weight=1)
        main_panel.grid_columnconfigure(0, weight=1)
        horizontal_scroll = tk.Scrollbar(main_panel, orient=tk.HORIZONTAL, command=self.word_listbox.xview)
        horizontal_scroll.grid(row=1, column=0, sticky=tk.EW)
        vertical_scroll = tk.Scrollbar(main_panel, orient=tk.VERTICAL, command=self.word_listbox.yview)
        vertical_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.word_listbox.grid(row=0, column=0, sticky=tk.NSEW)
        self.word_listbox.configure(xscrollcommand=horizontal_scroll.set, yscrollcommand=vertical_scroll.set)

        self.bind("<KeyPress-Up>", self.select_one_up)
        self.bind("<KeyPress-Down>", self.select_one_down)
        self.bind("<KeyPress-Return>", self.ok)

        main_panel.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)

        button_panel = tk.Frame(self)
        ok_button = tk.Button(button_panel, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        ok_button.pack(side=tk.LEFT, padx=5, pady=5)
        cancel_button = tk.Button(button_panel, text="Cancel", width=10, command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
        button_panel.pack(pady=5)

        self.word_listbox.focus_set()
        self.word_listbox.select_set(self.selection_id)

        # Set window position relative to parent window
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        self.wait_window(self)

    def select_one_up(self, event):
        if self.selection_id > 0:
            self.selection_id -= 1
        else:
            self.selection_id = len(self.word_texts_list) - 1
        self.word_listbox.selection_clear(0, tk.END)
        self.word_listbox.select_set(self.selection_id)

    def select_one_down(self, event):
        if self.selection_id < len(self.word_texts_list) - 1:
            self.selection_id += 1
        else:
            self.selection_id = 0
        self.word_listbox.selection_clear(0, tk.END)
        self.word_listbox.select_set(self.selection_id)

    def ok(self, event=None):
        self.parent.returner = self.word_listbox.curselection()
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()

    def cancel(self):
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()


class AboutDialog(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)

        self.transient(parent)
        self.title("About " + APP_NAME)
        self.iconbitmap("icon.ico")
        self.resizable(width=False, height=False)
        self.parent = parent

        label = tk.Label(self, font=("Courier New", 11), anchor=tk.W, justify=tk.LEFT,
                         text=" ___  ,-,\n[   ]/ / _    _\n | | \ \| |  | |\n | |  '-| |  | |\n | |    | |  | |"
                              "\n | |    | |  | |\n[___]   \\_\\  \\_\\\n=================\n I W I L L B I A"
                              "\n\nVersion:\n   " + APP_VERSION + "\n\nCreated by:\n   Žans Kļimovičs"
                              "\n\nLicense:\n   GNU GPL v3")
        label.pack(padx=15)
        button = tk.Button(self, text="Ok", width=10, command=self.ok, default=tk.ACTIVE)
        button.pack(pady=20)
        label.focus_set()

        # Set window position relative to parent window
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 80, parent.winfo_rooty() + 20))
        self.wait_window(self)

    def ok(self):
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()


class Separator(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, height=2, bd=1, relief=tk.SUNKEN)
