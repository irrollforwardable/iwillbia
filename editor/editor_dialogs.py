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


def generate_where_string(column_name, value):
    result = ""
    if value and value != "0":
        result = " and " + column_name + " = " + str(value)
    return result


class SecondaryDialog(tk.Toplevel):
    def __init__(self, parent, db_connection, caller_field, opened_item_id):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.db_connection = db_connection
        self.caller_field = caller_field
        self.opened_item = None  # Set individually inside each sub-class constructor
        self.opened_item_id = opened_item_id  # Item that is currently open

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
    def __init__(self, parent, db_connection, caller_field=None, opened_item_id=None):
        SecondaryDialog.__init__(self, parent, db_connection, caller_field, opened_item_id)
        self.title("Action")
        self.iconbitmap("icon.ico")

        panel = tk.Frame(self)

        tk.Label(panel, text="Title: ").grid(row=0, column=0, sticky=tk.E)
        self.action_title = LabeledEntry(panel, is_right_justify=False)
        self.action_title.grid(row=0, column=1, sticky=tk.EW, pady=4)

        tk.Label(panel, text="Self changes: ").grid(row=1, column=0, sticky=tk.E)
        self.self_change = BrowseEntry(panel, caption=None,
                                       command=lambda: ChangeEditorDialog(self, db_connection,
                                                                          self.self_change,
                                                                          self.self_change.get_kept_id()))
        self.self_change.grid(row=1, column=1, sticky=tk.EW)

        tk.Label(panel, text="Subject changes: ").grid(row=2, column=0, sticky=tk.E)
        self.subject_change = BrowseEntry(panel, caption=None,
                                          command=lambda: ChangeEditorDialog(self, db_connection,
                                                                             self.subject_change,
                                                                             self.subject_change.get_kept_id()))
        self.subject_change.grid(row=2, column=1, sticky=tk.EW)

        tk.Label(panel, text="Function: ").grid(row=3, column=0, sticky=tk.E)
        self.function = BrowseEntry(panel, caption=None,
                                    command=lambda: FunctionEditorDialog(self, db_connection,
                                                                         self.function,
                                                                         self.function.get_kept_id()))
        self.function.grid(row=3, column=1, sticky=tk.EW)

        panel.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)

        ok_cancel_buttons = OkCancelButtonPanel(self, ok_command=self.click_ok, cancel_command=self.click_cancel)
        ok_cancel_buttons.pack(expand=1, pady=5)

        # Open action-object if one is passed
        if self.opened_item_id:
            self.open(self.opened_item_id)

        # Set window position relative to parent window
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 20, parent.winfo_rooty() + 20))
        self.wait_window(self)

    def open(self, action_id):
        action = Action(self.db_connection, action_id)

        self.action_title.set_value(action.title)
        self.self_change.set_value(text=str(action.self_changes), kept_id=action.self_changes.db_id)
        self.subject_change.set_value(text=str(action.subject_changes), kept_id=action.subject_changes.db_id)
        self.function.set_value(text=action.execute.__name__, kept_id=action.function_id)

        self.opened_item = action
        self.opened_item_id = action_id

    def click_new(self):
        self.action_title.set_value("")
        self.self_change.set_value(text="", kept_id=None)
        self.subject_change.set_value(text="", kept_id=None)
        self.function.set_value(text="", kept_id=None)

        self.opened_item = None
        self.opened_item_id = None

    def click_find(self):
        where_title = ""
        if self.action_title.get_value():
            where_title = " and lower(title) like lower('%" + self.action_title.get_value() + "%')"

        where_self_changes = ""
        if self.self_change.get_kept_id():
            where_self_changes = " and self_changes_id = " + str(self.self_change.get_kept_id())

        where_subject_changes = ""
        if self.subject_change.get_kept_id():
            where_subject_changes = " and subject_changes_id = " + str(self.subject_change.get_kept_id())

        where_function = ""
        if self.function.get_kept_id():
            where_function = " and function_id = " + str(self.function.get_kept_id())

        cursor = self.db_connection.cursor()
        cursor.execute("select id from actions where 1=1"
                       + where_title + where_self_changes + where_subject_changes + where_function)
        db_rows = cursor.fetchall()

        found_actions = []
        for action_id in db_rows:
            found_actions.append(Action(self.db_connection, action_id[0]))

        if found_actions:
            SearchResultDialog(self, found_actions)
        else:
            tkMessageBox.showinfo("No data found", "No data found!")

    def click_save(self):
        pass

    def click_save_as(self):
        pass

    def click_sql(self):
        sql_statement_list = []
        action_id = predict_next_value("actions", "id", self.db_connection)
        actions_insert = SqlInsertStatement("actions", (
            ColumnTypeValue("id", COL_TYPE_NUMBER, action_id),
            ColumnTypeValue("title", COL_TYPE_CHAR, self.action_title.get_value()),
            ColumnTypeValue("self_changes_id", COL_TYPE_NUMBER, self.self_change.get_kept_id()),
            ColumnTypeValue("subject_changes_id", COL_TYPE_NUMBER, self.subject_change.get_kept_id()),
            ColumnTypeValue("function_id", COL_TYPE_NUMBER, self.function.get_kept_id())
        ))
        sql_statement_list.append(actions_insert)
        SqlDialog(self, sql_statement_list)

    def click_ok(self):
        if self.caller_field:
            if self.opened_item_id and self.opened_item:
                self.caller_field.set_value(text=str(self.opened_item), kept_id=self.opened_item_id)
            else:
                self.caller_field.set_value(text="", kept_id=None)
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()

    def click_cancel(self):
        self.parent.focus_set()
        self.destroy()


class ChangeEditorDialog(SecondaryDialog):
    def __init__(self, parent, db_connection, caller_field=None, opened_item_id=None):
        SecondaryDialog.__init__(self, parent, db_connection, caller_field, opened_item_id=opened_item_id)
        self.title("Change")
        self.iconbitmap("icon.ico")

        # Description panel
        description_panel = tk.Frame(self)
        tk.Label(description_panel, text="Description: ").pack()  # TODO left alignment
        self.description_value = tk.Entry(description_panel)
        self.description_value.pack(fill=tk.BOTH, expand=1)
        description_panel.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)

        # Attributes panel
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

        panel.pack(fill=tk.BOTH, expand=1, padx=5)

        ok_cancel_buttons = OkCancelButtonPanel(self, ok_command=self.click_ok, cancel_command=self.click_cancel)
        ok_cancel_buttons.pack(expand=1, pady=10)

        # Open change-object if one is passed
        if self.opened_item_id:
            self.open(self.opened_item_id)

        # Set window position relative to parent window
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 20, parent.winfo_rooty() + 20))
        self.wait_window(self)

    def open(self, change_id):
        change = Changes()
        change.set_all_fields_from_db(self.db_connection, change_id)

        self.description_value.delete(0, tk.END)
        if change.description:
            self.description_value.insert(0, change.description)

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
        self.opened_item_id = change.db_id

    def click_new(self):
        self.description_value.delete(0, tk.END)
        self.health_value.delete(0, tk.END)
        self.health_value.insert(0, 0)
        self.health_cb_var.set(0)
        self.x_energy_value.delete(0, tk.END)
        self.x_energy_value.insert(0, 0)
        self.x_energy_cb_var.set(0)
        self.y_energy_value.delete(0, tk.END)
        self.y_energy_value.insert(0, 0)
        self.y_energy_cb_var.set(0)
        self.jump_value.delete(0, tk.END)
        self.jump_value.insert(0, 0)
        self.jump_value_cb_var.set(0)
        self.capacity_value.delete(0, tk.END)
        self.capacity_value.insert(0, 0)
        self.capacity_cb_var.set(0)
        self.bullets_value.delete(0, tk.END)
        self.bullets_value.insert(0, 0)
        self.bullets_cb_var.set(0)
        self.coins_value.delete(0, tk.END)
        self.coins_value.insert(0, 0)
        self.coins_cb_var.set(0)

        self.opened_item = None
        self.opened_item_id = None

    def click_find(self):
        # TODO Search of changes does not work correctly
        where_description = " "
        if self.description_value.get():
            where_description = " and lower(comments) like lower('%" + self.description_value.get() + "%')"
        where_health = generate_where_string("health", self.health_value.get())
        where_health_absolute = generate_where_string("is_health_absolute", self.health_cb_var.get())
        where_x_energy = generate_where_string("x_energy", self.x_energy_value.get())
        where_x_energy_absolute = generate_where_string("is_x_energy_absolute", self.x_energy_cb_var.get())
        where_y_energy = generate_where_string("y_energy", self.y_energy_value.get())
        where_y_energy_absolute = generate_where_string("is_y_energy_absolute", self.y_energy_cb_var.get())
        where_jump = generate_where_string("jump_power", self.jump_value.get())
        where_jump_absolute = generate_where_string("is_jump_power_absolute", self.jump_value_cb_var.get())
        where_capacity = generate_where_string("capacity", self.capacity_value.get())
        where_capacity_absolute = generate_where_string("is_capacity_absolute", self.capacity_cb_var.get())
        where_bullets = generate_where_string("bullets", self.bullets_value.get())
        where_bullets_absolute = generate_where_string("is_bullets_absolute", self.bullets_cb_var.get())
        where_coins = generate_where_string("coins", self.coins_value.get())
        where_coins_absolute = generate_where_string("is_coins_absolute", self.coins_cb_var.get())

        cursor = self.db_connection.cursor()
        cursor.execute(
            "select id from changes where 1=1 " +
            where_description +
            where_health +
            where_health_absolute +
            where_x_energy +
            where_x_energy_absolute +
            where_y_energy +
            where_y_energy_absolute +
            where_jump +
            where_jump_absolute +
            where_capacity +
            where_capacity_absolute +
            where_bullets +
            where_bullets_absolute +
            where_coins +
            where_coins_absolute
        )
        db_rows = cursor.fetchall()

        found_changes = []
        for change_id in db_rows:
            change = Changes()
            change.set_all_fields_from_db(self.db_connection, change_id[0])
            found_changes.append(change)

        if found_changes:
            SearchResultDialog(self, found_changes)
        else:
            tkMessageBox.showinfo("No data found", "No data found!")

    def click_save(self):
        pass

    def click_save_as(self):
        pass

    def click_sql(self):
        sql_statement_list = []
        change_id = predict_next_value("changes", "id", self.db_connection)
        change_insert = SqlInsertStatement("changes", (
            ColumnTypeValue("id", COL_TYPE_NUMBER, change_id),
            ColumnTypeValue("comments", COL_TYPE_CHAR, self.description_value.get()),
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
        if self.caller_field:
            if self.opened_item_id and self.opened_item:
                self.caller_field.set_value(text=str(self.opened_item), kept_id=self.opened_item_id)
            else:
                self.caller_field.set_value(text="", kept_id=None)
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()

    def click_cancel(self):
        self.parent.focus_set()
        self.destroy()


class FunctionEditorDialog(SecondaryDialog):
    def __init__(self, parent, db_connection, caller_field, opened_item_id):
        SecondaryDialog.__init__(self, parent, db_connection, caller_field, opened_item_id)
        self.title("Function")
        self.iconbitmap("icon.ico")

        # Main panel
        panel = tk.Frame(self)

        function_label = tk.Label(panel, text="Function name: ").grid(row=0, column=0)
        self.function_value = tk.Entry(panel)
        self.function_value.grid(row=0, column=1, sticky=tk.EW)

        panel.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)

        ok_cancel_buttons = OkCancelButtonPanel(self, ok_command=self.click_ok, cancel_command=self.click_cancel)
        ok_cancel_buttons.pack(expand=1, pady=5)

        # Open function-object if one is passed
        if self.opened_item_id:
            self.open(self.opened_item_id)

        # Set window position relative to parent window
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 20, parent.winfo_rooty() + 20))
        self.wait_window(self)

    def open(self, function_id):
        cursor = self.db_connection.cursor()
        cursor.execute("select lower(name) from functions where id = ?", (function_id,))
        db_rows = cursor.fetchall()

        if db_rows:
            self.function_value.delete(0, tk.END)
            self.function_value.insert(0, db_rows[0][0])
            self.opened_item = db_rows[0][0]
            self.opened_item_id = function_id

    def click_new(self):
        self.function_value.delete("1.0", tk.END)
        self.opened_item = None
        self.opened_item_id = None

    def click_find(self):
        cursor = self.db_connection.cursor()
        cursor.execute(
            "select id, name, description from functions where name like '%" + self.function_value.get() + "%'")
        db_rows = cursor.fetchall()

        found_functions = []
        for function_row in db_rows:
            found_functions.append(FunctionContainer(function_row[0], function_row[1], function_row[2]))

        if found_functions:
            SearchResultDialog(self, found_functions)
        else:
            tkMessageBox.showinfo("No data found", "No data found!")

    def click_save(self):
        pass

    def click_save_as(self):
        pass

    def click_sql(self):
        pass

    def click_ok(self):
        if self.caller_field:
            if self.opened_item_id and self.opened_item:
                self.caller_field.set_value(text=str(self.opened_item), kept_id=self.opened_item_id)
            else:
                self.caller_field.set_value(text="", kept_id=None)
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()

    def click_cancel(self):
        self.parent.focus_set()
        self.destroy()


class FunctionContainer(object):
    """
    This container is used only in FunctionEditorDialog and is not used in game logic, that's why it is declared here.
    """
    def __init__(self, db_id, name, description):
        self.db_id = db_id
        self.name = name
        self.description = description

    def __repr__(self):
        return self.name


class SearchResultDialog(tk.Toplevel):
    def __init__(self, parent, sql_result_list):
        tk.Toplevel.__init__(self, parent)
        self.title("Search results")
        self.iconbitmap("icon.ico")
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
        selected_object = self.actual_objects[int(self.listbox.curselection()[0])]
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()
        self.destroy()
        self.parent.open(selected_object.db_id)

    def click_cancel(self):
        self.parent.focus_set()
        self.destroy()


class SqlDialog(tk.Toplevel):
    def __init__(self, parent, sql_statement_list):
        tk.Toplevel.__init__(self, parent)
        self.title("SQL")
        self.iconbitmap("icon.ico")
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
