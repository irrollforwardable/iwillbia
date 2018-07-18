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

import Tkinter as tk
from constants import *


def predict_next_value(table_name, column_name, db_connection):
    cursor = db_connection.cursor()
    cursor.execute("select max(" + column_name + ") from " + table_name)
    db_rows = cursor.fetchall()

    if db_rows:
        return int(db_rows[0][0]) + 1
    else:
        return None


class ColumnTypeValue(object):
    def __init__(self, column_name, column_type, value):
        self.column_name = column_name.lower()
        self.column_type = column_type
        if value is None or value == "":
            self.column_type = COL_TYPE_NULL
            self.value = "NULL"
        else:
            self.value = value
            if self.column_type == COL_TYPE_CHAR:
                self.value = value.strip()
                # Escape characters
                # for escape_char in ("\\",):
                #     self.value = self.value.replace(escape_char, "\\" + escape_char)
                for quote_char in ("'",):
                    self.value = self.value.replace(quote_char, "'" + quote_char)


class SqlInsertStatement(object):
    def __init__(self, table_name, col_type_value_list):
        self.insert_statement = ""
        if len(col_type_value_list) > 0:
            columns = ""
            values = ""
            self.insert_statement = "INSERT INTO " + table_name + " ("

            for col_type_value in col_type_value_list:
                columns += (col_type_value.column_name + ", ")
                if col_type_value.column_type == COL_TYPE_CHAR:
                    values += ("'" + str(col_type_value.value) + "', ")
                elif col_type_value.column_type == COL_TYPE_NUMBER:
                    values += (str(col_type_value.value) + ", ")
                else:
                    values += (str(col_type_value.value) + ", ")

            if len(columns) >= 2:
                columns = columns[:-2]  # remove last , symbol
                self.insert_statement += columns
            self.insert_statement += ")"
            if len(values) >= 2:
                values = values[:-2]  # remove last , symbol
                self.insert_statement += (" VALUES (" + values + ");")

    def __repr__(self):
        return self.insert_statement


class LabeledEntry(tk.Frame):
    def __init__(self, parent, caption=None, is_right_justify=False, command=None):
        tk.Frame.__init__(self, parent)
        if caption:
            tk.Label(self, text=caption).pack(side=tk.LEFT)
        if is_right_justify:
            value_justification=tk.RIGHT
        else:
            value_justification=tk.LEFT
        self.value = tk.Entry(self, justify=value_justification)
        self.value.pack(side=tk.LEFT)
        # If command is provided in the parameter, then button appears
        if command:
            self.button = tk.Button(self, text="...", command=command)
            self.button.pack(side=tk.LEFT)

    def get_value(self):
        return self.value.get()

    def set_value(self, text):
        self.value.delete(0, tk.END)
        self.value.insert(0, text)


class BrowseEntry(tk.Frame):
    def __init__(self, parent, caption, command):
        tk.Frame.__init__(self, parent)
        self.value_var = ""
        if caption:
            label = tk.Label(self, text=caption).pack(side=tk.LEFT)
        self.value = tk.Label(self, background="#FFF", relief=tk.GROOVE, anchor=tk.W, width=20)
        self.value.pack(side=tk.LEFT)
        self.button = tk.Button(self, text="...", command=command)
        self.button.pack(side=tk.LEFT)

    def set_value(self, text):
        self.value_var = text
        self.value.config(text=text)

    def get_value(self):
        return self.value_var


class NewFindSaveSqlButtonPanel(tk.Frame):
    """
    New, Open, Save, Save As, Sql buttons panel. Commands for these buttons are passed as constructor parameters.
    """
    def __init__(self, parent, new_command=None, find_command=None, save_command=None, save_as_command=None,
                 sql_command=None):
        tk.Frame.__init__(self, parent)

        self.new_btn = tk.Button(self, text="New", width=6, command=new_command)
        self.open_btn = tk.Button(self, text="Find", width=6, command=find_command)
        self.save_btn = tk.Button(self, text="Save", width=6, command=save_command, state=tk.DISABLED)
        self.saveas_btn = tk.Button(self, text="Save As", width=6, command=save_as_command, state=tk.DISABLED)
        self.sql_btn = tk.Button(self, text="Sql", width=6, command=sql_command)

        self.new_btn.grid(row=0, column=0, sticky=tk.E)
        self.open_btn.grid(row=0, column=1, sticky=tk.E)
        self.save_btn.grid(row=0, column=2, sticky=tk.E)
        self.saveas_btn.grid(row=0, column=3, sticky=tk.E)
        self.sql_btn.grid(row=0, column=4, sticky=tk.E)


class OkCancelButtonPanel(tk.Frame):
    def __init__(self, parent, ok_command, cancel_command):
        tk.Frame.__init__(self, parent)

        self.ok_btn = tk.Button(self, text="Ok", width=8, command=ok_command)
        self.cancel_btn = tk.Button(self, text="Cancel", width=8, command=cancel_command)

        self.ok_btn.grid(row=0, column=0, padx=15)
        self.cancel_btn.grid(row=0, column=1)


class Separator(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, height=2, bd=1, relief=tk.SUNKEN)
