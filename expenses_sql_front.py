from functools import partial
import expenses_sql_back
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import calendar
from datetime import datetime, date

root = Tk()

root.title("Expenses tracker")

# current day, month, year
today_date = date.today()
today = today_date.day
month = today_date.month
year = today_date.year


# generate available days according to current month
def day_selector_1(selected_month, selected_year):
    if month_combo.get() != "Select month":
        "converting month string to integer"
        datetime_object = datetime.strptime(selected_month, "%B")
        "getting a tuple which contains number of days in current month"
        t = calendar.monthrange(int(selected_year), datetime_object.month)
        days = list(range(1, t[1] + 1))
        days.insert(0, "Select day")
        return days


# update day combobox when a month is selected
def update_day(event):
    day_combo['value'] = day_selector_1(month_combo.get(), year_combo.get())
    day_combo.current(0)


# clears entry when is clicked
def entry_clear(*args):
    if args[0].get() == "Enter value" or "Enter expense category":
        args[0].delete(0, "end")


# fills value entry with hint
def value_fill(event):
    if value_entry.get() == "":
        value_entry.insert(0, "Enter value")


# fills category entry with hint
def category_fill(event):
    if category_entry.get() == "":
        category_entry.insert(0, "Enter expense category")

new_window_counter = 0


# function that clears note entry and open a new window with a text widget when is clicked
def note_clear(event):
    global new_window_counter
    if note_entry.get() == "Enter note (optional)":
        note_entry.delete(0, "end")

    if new_window_counter == 0:
        new_window = Toplevel(root)
        new_window.title("Note")

        # function that decrease the global counter and close window
        def new_window_counter_decrease():
            global new_window_counter
            new_window_counter -= 1
            new_window.destroy()

        "method that link exit button to counter decreasing function"
        new_window.protocol("WM_DELETE_WINDOW", new_window_counter_decrease)
        new_window_counter += 1

        text = Text(new_window, font=("Arial", 11), width=50, height=20)
        text.insert(END, note_entry.get())
        text.pack(padx=20, pady=20)

        ok_button = Button(new_window, font=("Arial", 12), text="Done", command=lambda: (note_entry.delete(0, END),
                                        note_entry.insert(0, text.get("1.0", "end-1c")), new_window_counter_decrease()))
        ok_button.pack(pady=(0, 20))


# fills entry with hint
def note_fill(event):
    if note_entry.get() == "":
        note_entry.insert(0, "Enter note (optional)")


# function that evaluates entries and send values if ok to expenses_sql_back.insert
def insert_db():
    if day_combo.get() == "Select day" or month_combo.get() == "Select month":
        messagebox.showinfo("Info", "Month and day should be selected")
    elif category_entry.get() == "Enter expense category":
        messagebox.showinfo("Info", "An expense category should be introduced")
    else:
        try:
            if note_entry.get() == "Enter note (optional)":
                note_entry.delete(0, "end")
            insertion_list = [day_combo.get(), month_combo.get(), year_combo.get(), float(value_entry.get()),
                              category_entry.get(), note_entry.get()]
            expenses_sql_back.insert(insertion_list)
        except ValueError:
            messagebox.showinfo("Info", "An valid number should be introduced")


# add data from database to the tree
def add_data(*args):
    """deletes tree data if exists"""
    for record in tree.get_children():
        tree.delete(record)

    "insert data from database to tree"
    values = expenses_sql_back.db_show(month_combo2.get(), year_combo.get())
    for row in values:
        tree.insert('', index='end', values=row)

    "updates statistics every time tree is updated"
    expense_details_f()


# deletes records from database and tree
def delete_record():
    if tree.selection():
        question = messagebox.askquestion("Confirmation", "Are you sure you want to delete?")
        if question == "yes":
            for record in tree.selection():
                expenses_sql_back.delete(tree.item(record)['values'][6])
                tree.delete(record)

            "updates statistics"
            expense_details_f()

new_window2_counter = 0


# function that open a new window in order to modify the selected record and update the database
def modify_window():
    global new_window2_counter
    if new_window2_counter == 0:
        try:
            # function that evaluates entries and send values if ok to expenses_sql_back.modify
            def modify_db():
                if category_entry2.get() == "":
                    messagebox.showinfo("Info", "An expense category should be introduced")

                else:
                    try:
                        modify_l = [float(value_entry2.get()), category_entry2.get(), note_entry2.get("1.0", "end-1c"),
                                       tree.item(selection)['values'][6]]
                        expenses_sql_back.modify(modify_l)
                    except ValueError:
                        messagebox.showinfo("Info", "An valid number should be introduced")

            # function that decrease the global counter and close window
            def new_window2_counter_decrease():
                global new_window2_counter
                new_window2_counter -= 1
                new_window2.destroy()

            # function that update note visualisation of modified record
            def update_note():
                text_var = StringVar()
                text_var.set(note_entry2.get("1.0", "end-1c"))
                note_view_label["textvariable"] = text_var

            "if many rows selected, only the first will be modified"
            selection = tree.selection()[0]

            new_window2 = Toplevel(root)
            new_window2.title("Modify")

            new_window2_counter += 1

            "method that link exit button to counter decreasing function"
            new_window2.protocol("WM_DELETE_WINDOW", new_window2_counter_decrease)

            "creating labels"
            value_label = Label(new_window2, text="Value", font=("Arial", 10))
            value_label.grid(row=0, column=0)

            category_label = Label(new_window2, text="Category", font=("Arial", 10))
            category_label.grid(row=0, column=1)

            note_label = Label(new_window2, text="Note", font=("Arial", 10))
            note_label.grid(row=2, column=0, columnspan=2, pady=(20, 0))

            "creating entries"
            value_entry2 = Entry(new_window2, font=("Arial", 10), width=10)
            value_entry2.insert(0, tree.item(selection)['values'][3])
            value_entry2.grid(row=1, column=0, padx=10, sticky=N)

            category_entry2 = Entry(new_window2, font=("Arial", 10), width=20)
            category_entry2.insert(0, tree.item(selection)['values'][4])
            category_entry2.grid(row=1, column=1, padx=10, sticky=N)

            note_entry2 = Text(new_window2, font=("Arial", 11), width=50, height=20)
            note_entry2.insert(END, tree.item(selection)['values'][5])
            note_entry2.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 20))

            modify_button2 = Button(new_window2, text="Modify record", font=("Arial", 12),
                                command=lambda: (modify_db(), add_data(), update_note(), new_window2_counter_decrease()))
            modify_button2.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 20))

        except IndexError:
            messagebox.showinfo("Info", "A record should be selected")


# function that shows selected record's note
def see_note():
    if tree.selection():
        selection = tree.selection()[0]
        text_var = StringVar()
        text_var.set(tree.item(selection)["values"][5])
        note_view_label["textvariable"] = text_var

        note_view_label.grid(row=4, column=0, columnspan=3, pady=10)
        hide_note_visualization.grid(row=5, column=0, pady=10, columnspan=3)
    else:
        messagebox.showinfo("Info", "An record should be selected")

# list that contain every label from frame 3
labels_list = []


# function that shows expense sum for each category, total expense amount, and percent for each category
def expense_details_f():
    """deletes every label if exists"""
    for label in labels_list:
        label.destroy()

    labels_list.clear()

    query_result = expenses_sql_back.statistics(month_combo2.get(), year_combo.get())

    tittle = "Expense details: {} {}".format(month_combo2.get(), year_combo.get())
    expense_details = Label(frame3, font=("Arial", 14), text=tittle)
    expense_details.grid(row=0, column=0, columnspan=2, pady=(10, 20))
    labels_list.append(expense_details)

    try:
        footer = "Total expense amount: {}".format(query_result[0][3])
        total_amount = Label(frame3, font=("Arial", 11), text=footer)
        total_amount.grid(row=8, column=0, padx=10, pady=10)
        labels_list.append(total_amount)
    except IndexError:
        pass

    r = 1
    c = 0

    "creating labels for each category"
    for row in query_result:
        if r == 7 and c == 0:
            r = 1
            c = 1
        elif r == 7 and c == 1:
            r = 1
            c = 2

        label_text = "{}: {} ({}%)".format(row[0], row[1], round(row[2], 2))
        x = Label(frame3, font=("Arial", 11), text=label_text)
        x.grid(row=r, column=c, sticky=W, padx=(10, 30))
        labels_list.append(x)
        r += 1
        # print("bineee")

# creating frames
frame1 = LabelFrame(root, width=750, height=100)
frame1.grid(padx=10, pady=10, row=0, column=0, sticky=N)
frame1.grid_propagate(FALSE)

frame2 = LabelFrame(root)
frame2.grid(padx=10, pady=10, row=0, column=1, rowspan=3, sticky=N)

frame3 = LabelFrame(root, width=750, height=240)
frame3.grid(padx=10, pady=(0, 10), row=1, column=0, sticky=NW)
frame3.grid_propagate(FALSE)

# creating labels
#   frame 1
insert_label = Label(frame1, text="Insert:", font=("Arial", 14))
insert_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=W)

year_label = Label(frame1, text="Year  ", font=("Arial", 14))
year_label.grid(row=0, column=4, sticky=E, pady=(10, 0))

#   frame 2
records_label = Label(frame2, text="Records", font=("Arial", 14)).grid(row=0, column=0, columnspan=3)
note_view_label = Label(frame2, justify=LEFT, wraplength=400, font=("Arial", 11))

# creating combobox
# frame1
months = list(calendar.month_name[1:])
months.insert(0, "Select month")

month_combo = ttk.Combobox(frame1, value=months, font=("Arial", 10), state="readonly", width=12)
month_combo.current(month)
month_combo.bind("<<ComboboxSelected>>", update_day)
month_combo.grid(row=1, column=0, padx=10)

# year
year_combo = ttk.Combobox(frame1, value=[2021, 2022], font=("Arial", 10), state="readonly", width=5)
year_combo.set(year)
year_combo.grid(row=0, column=5, padx=10, pady=(10, 0))

# days
day_combo = ttk.Combobox(frame1, value=day_selector_1(month_combo.get(), year_combo.get()),
                         font=("Arial", 10), state="readonly", width=10)
day_combo.current(today)
day_combo.grid(row=1, column=1, padx=10)

# frame2
month_combo2 = ttk.Combobox(frame2, value=months, font=("Arial", 10), state="readonly", width=12)
month_combo2.current(month)
month_combo2.bind("<<ComboboxSelected>>", add_data)
month_combo2.grid(row=1, column=0, padx=10, pady=10, sticky=W)

# creating entries
# frame 1
value_entry = Entry(frame1, font=("Arial", 10), width=10)
value_entry.insert(0, 'Enter value')
value_entry.grid(row=1, column=2, padx=10)
value_entry.bind("<Button-1>", partial(entry_clear, value_entry))
value_entry.bind("<FocusOut>", value_fill)

category_entry = Entry(frame1, font=("Arial", 10), width=20)
category_entry.insert(0, "Enter expense category")
category_entry.grid(row=1, column=3, padx=10)
category_entry.bind("<Button-1>", partial(entry_clear, category_entry))
category_entry.bind("<FocusOut>", category_fill)

note_entry = Entry(frame1, font=("Arial", 10))
note_entry.insert(0, "Enter note (optional)")
note_entry.grid(row=1, column=4, padx=10)
note_entry.bind("<Button-1>", note_clear)
note_entry.bind("<FocusOut>", note_fill)

# creating buttons
insert_button = Button(frame1, text="Insert", font=("Arial", 12), command=lambda: (insert_db(), add_data()))
insert_button.grid(row=1, column=5, padx=10, pady=10)

delete_button = Button(frame2, text="Delete record", font=("Arial", 12), command=delete_record)
delete_button.grid(column=0, row=3, pady=10)

modify_button = Button(frame2, text="Modify record", font=("Arial", 12), command=modify_window)
modify_button.grid(column=1, row=3, pady=10)

see_note_button = Button(frame2, text="See note", font=("Arial", 12), command=see_note)
see_note_button.grid(column=2, row=3, padx=(0, 10))

hide_note_visualization = Button(frame2, text="Hide", font=("Arial", 12), command=lambda: (note_view_label.grid_remove(),
                                            hide_note_visualization.grid_remove()))

# creating tree
tree = ttk.Treeview(frame2, columns=(0, 1, 2, 3, 4, 5), show='headings')

    # format columns
tree.column(0, width=50, minwidth=30, anchor=CENTER)
tree.column(1, width=100, minwidth=65, anchor=CENTER)
tree.column(2, width=50, minwidth=30, anchor=CENTER)
tree.column(3, width=100, minwidth=30, anchor=CENTER)
tree.column(4, width=100, minwidth=30, anchor=CENTER)
tree.column(5, width=170, minwidth=30, anchor=CENTER)

    # create headings
tree.heading(0, text="Day")
tree.heading(1, text="Month")
tree.heading(2, text="Year")
tree.heading(3, text="Value")
tree.heading(4, text="Category")
tree.heading(5, text="Note")

tree.grid(row=2, column=0, columnspan=3, padx=10)

# adding data to the tree
add_data()

root.mainloop()
