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

import tkMessageBox

from components import *
from game_object_components import *


class SecondaryDialog(tk.Toplevel):
    def __init__(self, parent, db_connection, caller_field, opened_item):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.db_connection = db_connection
        self.caller_field = caller_field
        self.opened_item = opened_item  # Item that is currently open

        # Dialog
        self.transient(parent)  # One window in task bar
        self.grab_set()  # Modal
        self.resizable(False, False)

        # Buttons
        self.new_find_save_sql_btns = NewFindSaveSqlButtonPanel(self, new_command=self.click_new,
                                                                find_command=self.click_find,
                                                                save_command=self.click_save,
                                                                save_as_command=self.click_save_as,
                                                                sql_command=self.click_sql)
        self.new_find_save_sql_btns.pack(anchor=tk.W, padx=5, pady=5)

        def open(self):
            pass

        def click_new(self):
            pass

        def click_find(self):
            pass

        def click_save(self):
            pass

        def click_save_as(self):
            pass

        def click_sql(self):
            pass


class ActionEditorDialog(SecondaryDialog):
    def __init__(self, parent, db_connection, caller_field=None, opened_item=None):
        SecondaryDialog.__init__(self, parent, db_connection, caller_field, opened_item)
        self.title("Action")
        self.iconbitmap("icon.ico")

        panel = tk.Frame(self)

        # title_label = tk.Label(panel, text="Title: ").grid(row=0, column=0, sticky=tk.E)
        # self.title_value = tk.Entry(panel)
        # self.title_value.grid(row=0, column=1, sticky=tk.EW, pady=4)
        tk.Label(panel, text="Title: ").grid(row=0, column=0, sticky=tk.E)
        self.title = LabeledEntry(panel, is_right_justify=False)
        self.title.grid(row=0, column=1, sticky=tk.EW, pady=4)

        # self_change_label = tk.Label(panel, text="Self change: ").grid(row=1, column=0, sticky=tk.E)
        # self.self_change_value = BrowseEntry(panel, None, self.show_self_change_editor_dialog)
        # self.self_change_value.grid(row=1, column=1, sticky=tk.EW)
        tk.Label(panel, text="Self change ID: ").grid(row=1, column=0, sticky=tk.E)
        self.self_change = LabeledEntry(panel, is_right_justify=True, command=lambda: None)
        self.self_change.grid(row=1, column=1, sticky=tk.EW)

        # subject_change_label = tk.Label(panel, text="Subject change: ").grid(row=2, column=0, sticky=tk.E)
        # self.subject_change_value = BrowseEntry(panel, None, self.show_subject_change_editor_dialog)
        # self.subject_change_value.grid(row=2, column=1, sticky=tk.EW)
        tk.Label(panel, text="Subject change ID: ").grid(row=2, column=0, sticky=tk.E)
        self.subject_change = LabeledEntry(panel, is_right_justify=True, command=lambda: None)
        self.subject_change.grid(row=2, column=1, sticky=tk.EW)

        # function_label = tk.Label(panel, text="Function: ").grid(row=3, column=0, sticky=tk.E)
        # self.function_value = BrowseEntry(panel, None, self.show_function_editor_dialog)
        # self.function_value.grid(row=3, column=1, sticky=tk.EW)
        tk.Label(panel, text="Function ID: ").grid(row=3, column=0, sticky=tk.E)
        self.function = LabeledEntry(panel, is_right_justify=True, command=lambda: None)
        self.function.grid(row=3, column=1, sticky=tk.EW)

        panel.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)

        ok_cancel_buttons = OkCancelButtonPanel(self, ok_command=self.click_ok, cancel_command=self.click_cancel)
        ok_cancel_buttons.pack(expand=1, pady=5)

        # Open action-object if one is passed
        if self.opened_item:
            self.open(self.opened_item)

        # Set window position relative to parent window
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 20, parent.winfo_rooty() + 20))
        self.wait_window(self)

    def open(self, action):
        # self.title_value.delete(0, tk.END)
        # self.title_value.insert(0, action.title)
        # self.self_change_value.set_value(action.self_changes)
        # self.subject_change_value.set_value(action.subject_changes)
        # self.function_value.set_value(action.execute)
        # self.opened_item = action
        self.title.set_value(action.title)
        self.self_change.set_value(action.self_changes)
        self.subject_change.set_value(action.subject_changes)
        self.function.set_value(action.execute)
        self.opened_item = action

    def click_new(self):
        # self.title_value.delete(0, tk.END)
        # self.self_change_value.set_value("")
        # self.subject_change_value.set_value("")
        # self.function_value.set_value("")
        # self.opened_item = None
        self.title.set_value("")
        self.self_change.set_value("")
        self.subject_change.set_value("")
        self.function.set_value("")
        self.opened_item = None

    def click_find(self):
        cursor = self.db_connection.cursor()
        cursor.execute("select id from actions where lower(title) like lower('%" + self.title.get_value() + "%')")
        db_rows = cursor.fetchall()

        found_actions = []
        for action_id in db_rows:
            found_actions.append(Action(self.db_connection, action_id[0]))

        if found_actions:
            SearchResultDialog(self, found_actions)
        else:
            tkMessageBox.showinfo("No data found", "No data found!")

    def click_save(self):
        print "Save"

    def click_save_as(self):
        print "Save As"

    def click_sql(self):
        sql_statement_list = []
        action_id = predict_next_value("actions", "id", self.db_connection)
        actions_insert = SqlInsertStatement("actions", (
            ColumnTypeValue("id", COL_TYPE_NUMBER, action_id),
            ColumnTypeValue("title", COL_TYPE_CHAR, self.title.get_value()),
            ColumnTypeValue("self_changes_id", COL_TYPE_NUMBER, self.self_change.get_value()),
            ColumnTypeValue("subject_changes_id", COL_TYPE_NUMBER, self.subject_change.get_value()),
            ColumnTypeValue("function_id", COL_TYPE_NUMBER, self.function.get_value())
        ))
        sql_statement_list.append(actions_insert)
        SqlDialog(self, sql_statement_list)

    def click_ok(self):
        # if self.opened_item:
        #     self.caller_field.set_value(self.opened_item)
        # else:
        #     self.caller_field.set_value("")
        # self.withdraw()
        # self.update_idletasks()
        # self.parent.focus_set()
        # self.destroy()
        self.parent.focus_set()
        self.destroy()

    def click_cancel(self):
        self.parent.focus_set()
        self.destroy()

    def show_self_change_editor_dialog(self):
        pointer_to_self_changes = None
        if self.opened_item:
            pointer_to_self_changes = self.opened_item.self_changes
        ChangeEditorDialog(self, self.db_connection, self.self_change, pointer_to_self_changes)

    def show_subject_change_editor_dialog(self):
        pointer_to_subject_changes = None
        if self.opened_item:
            pointer_to_subject_changes = self.opened_item.subject_changes
        ChangeEditorDialog(self, self.db_connection, self.self_change, pointer_to_subject_changes)

    def show_function_editor_dialog(self):
        pointer_to_function = None
        if self.opened_item:
            pointer_to_function = self.opened_item.execute
        FunctionEditorDialog(self, self.db_connection, self.function, pointer_to_function)


class ChangeEditorDialog(SecondaryDialog):
    def __init__(self, parent, db_connection, caller_field=None, opened_item=None):
        SecondaryDialog.__init__(self, parent, db_connection, caller_field, opened_item)
        self.title("Change")
        self.iconbitmap("icon.ico")

        # Main panel
        panel = tk.Frame(self)

        health_label = tk.Label(panel, text="Health: ").grid(row=0, column=0, sticky=tk.E)
        self.health_value = tk.Entry(panel, justify=tk.RIGHT)
        self.health_value.insert(0, "0")
        self.health_value.grid(row=0, column=1, sticky=tk.EW)
        self.health_cb_var = tk.IntVar()
        self.is_health_absolute = tk.Checkbutton(panel, text="Absolute", variable=self.health_cb_var)
        self.is_health_absolute.grid(row=0, column=2)

        x_energy_label = tk.Label(panel, text="X-Energy: ").grid(row=1, column=0, sticky=tk.E)
        self.x_energy_value = tk.Entry(panel, justify=tk.RIGHT)
        self.x_energy_value.insert(0, "0")
        self.x_energy_value.grid(row=1, column=1, sticky=tk.EW)
        self.x_energy_cb_var = tk.IntVar()
        self.is_x_energy_absolute = tk.Checkbutton(panel, text="Absolute", variable=self.x_energy_cb_var)
        self.is_x_energy_absolute.grid(row=1, column=2)

        y_energy_label = tk.Label(panel, text="Y-Energy: ").grid(row=2, column=0, sticky=tk.E)
        self.y_energy_value = tk.Entry(panel, justify=tk.RIGHT)
        self.y_energy_value.insert(0, "0")
        self.y_energy_value.grid(row=2, column=1, sticky=tk.EW)
        self.y_energy_cb_var = tk.IntVar()
        self.is_y_energy_absolute = tk.Checkbutton(panel, text="Absolute", variable=self.y_energy_cb_var)
        self.is_y_energy_absolute.grid(row=2, column=2)

        jump_label = tk.Label(panel, text="Jump power: ").grid(row=3, column=0, sticky=tk.E)
        self.jump_value = tk.Entry(panel, justify=tk.RIGHT)
        self.jump_value.insert(0, "0")
        self.jump_value.grid(row=3, column=1, sticky=tk.EW)
        self.jump_value_cb_var = tk.IntVar()
        self.is_jump_absolute = tk.Checkbutton(panel, text="Absolute", variable=self.jump_value_cb_var)
        self.is_jump_absolute.grid(row=3, column=2)

        capacity_label = tk.Label(panel, text="Capacity: ").grid(row=4, column=0, sticky=tk.E)
        self.capacity_value = tk.Entry(panel, justify=tk.RIGHT)
        self.capacity_value.insert(0, "0")
        self.capacity_value.grid(row=4, column=1, sticky=tk.EW)
        self.capacity_cb_var = tk.IntVar()
        self.is_capacity_absolute = tk.Checkbutton(panel, text="Absolute", variable=self.capacity_cb_var)
        self.is_capacity_absolute.grid(row=4, column=2)

        bullets_label = tk.Label(panel, text="Bullets: ").grid(row=5, column=0, sticky=tk.E)
        self.bullets_value = tk.Entry(panel, justify=tk.RIGHT)
        self.bullets_value.insert(0, "0")
        self.bullets_value.grid(row=5, column=1, sticky=tk.EW)
        self.bullets_cb_var = tk.IntVar()
        self.is_bullets_absolute = tk.Checkbutton(panel, text="Absolute", variable=self.bullets_cb_var)
        self.is_bullets_absolute.grid(row=5, column=2)

        coins_label = tk.Label(panel, text="Coins: ").grid(row=6, column=0, sticky=tk.E)
        self.coins_value = tk.Entry(panel, justify=tk.RIGHT)
        self.coins_value.insert(0, "0")
        self.coins_value.grid(row=6, column=1, sticky=tk.EW)
        self.coins_cb_var = tk.IntVar()
        self.is_coins_absolute = tk.Checkbutton(panel, text="Absolute", variable=self.coins_cb_var)
        self.is_coins_absolute.grid(row=6, column=2)

        panel.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)

        ok_cancel_buttons = OkCancelButtonPanel(self, ok_command=self.click_ok, cancel_command=self.click_cancel)
        ok_cancel_buttons.pack(expand=1, pady=5)

        # Open change-object if one is passed
        if self.opened_item:
            self.open(self.opened_item)

        # Set window position relative to parent window
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 20, parent.winfo_rooty() + 20))
        self.wait_window(self)

    def open(self, change):
        self.health_value.delete(0, tk.END)
        self.health_value.insert(0, change.health_change)
        self.health_cb_var.set(change.is_health_change_value_absolute)

        self.x_energy_value.delete(0, tk.END)
        self.x_energy_value.insert(0, change.x_energy_change)
        self.x_energy_cb_var.set(change.is_x_energy_change_value_absolute)

        self.y_energy_value.delete(0, tk.END)
        self.y_energy_value.insert(0, change.y_energy_change)
        self.y_energy_cb_var.set(change.is_y_energy_change_value_absolute)

        self.jump_value.delete(0, tk.END)
        self.jump_value.insert(0, change.jump_power_change)
        self.jump_value_cb_var.set(change.is_jump_power_change_value_absolute)

        self.capacity_value.delete(0, tk.END)
        self.capacity_value.insert(0, change.capacity_change)
        self.capacity_cb_var.set(change.is_capacity_change_value_absolute)

        self.bullets_value.delete(0, tk.END)
        self.bullets_value.insert(0, change.bullets_change)
        self.bullets_cb_var.set(change.is_bullets_change_value_absolute)

        self.coins_value.delete(0, tk.END)
        self.coins_value.insert(0, change.coins_change)
        self.coins_cb_var.set(change.is_coins_change_value_absolute)

        self.opened_item = change

    def click_new(self):
        self.health_value.delete(0, tk.END)
        self.health_cb_var.set(0)
        self.x_energy_value.delete(0, tk.END)
        self.x_energy_cb_var.set(0)
        self.y_energy_value.delete(0, tk.END)
        self.y_energy_cb_var.set(0)
        self.jump_value.delete(0, tk.END)
        self.jump_value_cb_var.set(0)
        self.capacity_value.delete(0, tk.END)
        self.capacity_cb_var.set(0)
        self.bullets_value.delete(0, tk.END)
        self.bullets_cb_var.set(0)
        self.coins_value.delete(0, tk.END)
        self.coins_cb_var.set(0)

        self.opened_item = None

    def click_find(self):
        SearchResultDialog(self, ("One", "Two", "Three", "Four"))

    def click_save(self):
        print "Save"

    def click_save_as(self):
        print "Save As"

    def click_sql(self):
        sql_statement_list = []
        change_id = predict_next_value("changes", "id", self.db_connection)
        change_insert = SqlInsertStatement("changes", (
            ColumnTypeValue("id", COL_TYPE_NUMBER, change_id),
            ColumnTypeValue("health", COL_TYPE_NUMBER, self.health_value.get()),
            ColumnTypeValue("is_health_absolute", COL_TYPE_NUMBER, self.health_cb_var.get()),
            ColumnTypeValue("x_energy", COL_TYPE_NUMBER, self.x_energy_value.get()),
            ColumnTypeValue("is_x_energy_absolute", COL_TYPE_NUMBER, self.x_energy_cb_var.get()),
            ColumnTypeValue("y_energy", COL_TYPE_NUMBER, self.y_energy_value.get()),
            ColumnTypeValue("is_y_energy_absolute", COL_TYPE_NUMBER, self.y_energy_cb_var.get()),
            ColumnTypeValue("jump_power", COL_TYPE_NUMBER, self.jump_value.get()),
            ColumnTypeValue("is_jump_power_absolute", COL_TYPE_NUMBER, self.jump_value_cb_var.get()),
            ColumnTypeValue("capacity", COL_TYPE_NUMBER, self.capacity_value.get()),
            ColumnTypeValue("is_capacity_absolute", COL_TYPE_NUMBER, self.capacity_cb_var.get()),
            ColumnTypeValue("bullets", COL_TYPE_NUMBER, self.bullets_value.get()),
            ColumnTypeValue("is_bullets_absolute", COL_TYPE_NUMBER, self.bullets_cb_var.get()),
            ColumnTypeValue("coins", COL_TYPE_NUMBER, self.coins_value.get()),
            ColumnTypeValue("is_coins_absolute", COL_TYPE_NUMBER, self.coins_cb_var.get()),
        ))
        sql_statement_list.append(change_insert)
        SqlDialog(self, sql_statement_list)

    def click_ok(self):
        # if self.opened_item:
        #     self.caller_field.set_value(self.opened_item)
        # else:
        #     self.caller_field.set_value("")
        # self.withdraw()
        # self.update_idletasks()
        # self.parent.focus_set()
        # self.destroy()
        self.parent.focus_set()
        self.destroy()

    def click_cancel(self):
        self.parent.focus_set()
        self.destroy()


class FunctionEditorDialog(SecondaryDialog):
    def __init__(self, parent, db_connection, caller_field, opened_item):
        SecondaryDialog.__init__(self, parent, db_connection, caller_field, opened_item)
        self.title("Function")

        # Main panel
        panel = tk.Frame(self)

        function_label = tk.Label(panel, text="Function name: ").grid(row=0, column=0)
        self.function_value = tk.Entry(panel).grid(row=0, column=1, sticky=tk.EW)

        panel.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)

        ok_cancel_buttons = OkCancelButtonPanel(self, ok_command=self.click_ok, cancel_command=self.click_cancel)
        ok_cancel_buttons.pack(expand=1, pady=5)

        # Open function-object if one is passed
        if self.opened_item:
            self.open(self.opened_item)

        # Set window position relative to parent window
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 20, parent.winfo_rooty() + 20))
        self.wait_window(self)

    def open(self, function):
        print "Opening function: " + str(function)

    def click_new(self):
        print "New"

    def click_find(self):
        SearchResultDialog(self, ("One", "Two", "Three", "Four"))

    def click_save(self):
        print "Save"

    def click_save_as(self):
        print "Save as"

    def click_sql(self):
        print "Sql"

    def click_ok(self):
        print "Ok"

    def click_cancel(self):
        print "Cancel"


class SearchResultDialog(tk.Toplevel):
    def __init__(self, parent, sql_result_list):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.actual_objects = sql_result_list

        # Dialog
        self.transient(parent)  # One window in task bar
        self.grab_set()  # Modal
        self.resizable(False, False)

        # Main panel
        panel = tk.Frame(self)
        self.listbox = tk.Listbox(panel, selectmode=tk.SINGLE)
        for result in sql_result_list:
            self.listbox.insert(tk.END, result)
        self.listbox.pack(fill=tk.BOTH, expand=1)
        panel.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)

        # Button panel
        ok_cancel_buttons = OkCancelButtonPanel(self, ok_command=self.click_ok, cancel_command=self.click_cancel)
        ok_cancel_buttons.pack(expand=1, pady=5)

        # Set window position relative to parent window
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 20, parent.winfo_rooty() + 20))
        self.wait_window(self)

    def click_ok(self):
        selected_object = self.actual_objects[self.listbox.curselection()[0]]
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()
        self.parent.open(selected_object)

    def click_cancel(self):
        self.parent.focus_set()
        self.destroy()


class SqlDialog(tk.Toplevel):
    def __init__(self, parent, sql_statement_list):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent

        # Dialog
        self.transient(parent)  # One window in task bar
        self.grab_set()  # Modal

        button_panel = tk.Frame(self)
        copy_to_clipboard_button = tk.Button(button_panel, text="Copy to clipboard", command=self.copy_to_clipboard)
        copy_to_clipboard_button.pack(fill=tk.X, padx=3, pady=3)
        button_panel.pack(fill=tk.BOTH)

        main_panel = tk.Frame(self)
        main_panel.pack(fill=tk.BOTH, expand=1)
        main_panel.grid_rowconfigure(0, weight=1)
        main_panel.grid_columnconfigure(0, weight=1)
        self.text_area = tk.Text(main_panel, wrap=tk.NONE)
        self.horizontal_scroll = tk.Scrollbar(main_panel, orient=tk.HORIZONTAL, command=self.text_area.xview)
        self.horizontal_scroll.grid(row=1, column=0, sticky=tk.EW)
        self.vertical_scroll = tk.Scrollbar(main_panel, orient=tk.VERTICAL, command=self.text_area.yview)
        self.vertical_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.text_area.grid(row=0, column=0, sticky=tk.NSEW)
        self.text_area.configure(xscrollcommand=self.horizontal_scroll.set, yscrollcommand=self.vertical_scroll.set)

        self.text_area.delete("1.0", tk.END)
        for sql_statement in sql_statement_list:
            self.text_area.insert(tk.INSERT, str(sql_statement) + "\n")

        # Set window position relative to parent window
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 20, parent.winfo_rooty() + 20))
        self.wait_window(self)

    def copy_to_clipboard(self):
        self.parent.parent.copy_to_clipboard(self.text_area.get("1.0", tk.END))
