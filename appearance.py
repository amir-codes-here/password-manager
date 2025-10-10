import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
import _backend as b

# ---------- DATA ----------
passwords = {}

font_big = ("Arial", 14)
font_medium = ("Arial", 12)
font_small = ("Arial", 10)

# ---------- UTILITY FUNCTIONS ----------
def update_listbox(lb):
    lb.delete(0, tk.END)
    for key in passwords.keys():
        lb.insert(tk.END, key)

def add_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry.config(fg="grey")
    entry.is_placeholder = True

    def on_focus_in(event):
        if entry.is_placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="black")
            entry.is_placeholder = False

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg="grey")
            entry.is_placeholder = True

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def add_placeholder_password(entry, placeholder):
    entry.insert(0, placeholder)
    entry.config(fg="grey", show="")
    entry.is_placeholder = True

    def on_focus_in(event):
        if entry.is_placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="black", show="*")
            entry.is_placeholder = False

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg="grey", show="")
            entry.is_placeholder = True

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def add_show_hide_toggle(entry):
    toggle_btn = tk.Button(entry.master, text="Show", width=8, font=font_small)
    toggle_btn.pack(side=tk.RIGHT, padx=5)

    def toggle():
        if entry.is_placeholder:
            return
        if entry.cget('show') == '*':
            entry.config(show='')
            toggle_btn.config(text='Hide')
        else:
            entry.config(show='*')
            toggle_btn.config(text='Show')

    toggle_btn.config(command=toggle)

def show_login_after_time():
    set_pass_frame.pack_forget()
    app_frame.pack_forget()
    login_frame.pack(fill=tk.BOTH, expand=True)

# ---------- APP LOGIC FUNCTIONS ----------
def on_listbox_key_select__view(event):
    selection = listbox__view.curselection()
    if selection:
        key = listbox__view.get(selection[0])
        password_var__view.set(passwords[key])
    else:
        password_var__view.set("")

def copy_selected_password__view():
    password = password_var__view.get()
    if password:
        root.clipboard_clear()
        root.clipboard_append(password)
        root.update()

def on_listbox_key_select__update(event):
    selection = listbox__update.curselection()
    if selection:
        key = listbox__update.get(selection[0])
        current_password_label__update.config(text=f"Current Password: {passwords[key]}")
    else:
        current_password_label__update.config(text="Current Password: ")

def add_new_password():
    key = key_entry__add.get().strip()
    if passwords.get(key, False):
        feedback_label__add.config(
            text="Key already exists. Visit update tab to update it's password",
            fg="red"
            )
        return
    password = password_entry__add.get()
    password_repeat = repeat_entry__add.get()
    if not key or not password or not password_repeat:
        feedback_label__add.config(text="Please fill all fields", fg="red")
        return
    if password != password_repeat:
        feedback_label__add.config(text="Passwords do not match", fg="red")
        return
    passwords[key] = password
    feedback_label__add.config(text="New password saved", fg="green")
    update_listbox(listbox__view)
    update_listbox(listbox__update)

def save_updated_password__update():
    selection = listbox__update.curselection()
    if not selection:
        feedback_label__update.config(text="Please select a key", fg="red")
        return
    new_password = new_password_entry__update.get()
    repeat_password = repeat_password_entry__update.get()
    if not new_password or not repeat_password:
        feedback_label__update.config(text="Please fill all fields", fg="red")
        return
    if new_password != repeat_password:
        feedback_label__update.config(text="Passwords do not match", fg="red")
        return
    key = listbox__update.get(selection[0])
    passwords[key] = new_password
    feedback_label__update.config(text="Paasword updated successfully", fg="green")
    update_listbox(listbox__view)
    update_listbox(listbox__update)
    current_password_label__update.config(text=f"Current Password: {new_password}")

def delete_selected_key():
    selection = listbox__view.curselection()
    if not selection:
        return
    key = listbox__view.get(selection[0])
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{key}'?\nThis action can not be reversed.")
    if not confirm:
        return
    del passwords[key]
    update_listbox(listbox__view)
    update_listbox(listbox__update)
    password_var__view.set("")

# ---------- LOGIN & SET PASSWORD SCREENS ----------
def show_main_app():
    global passwords
    passwords = b.get_passwords_from_vault()
    login_frame.pack_forget()
    set_pass_frame.pack_forget()
    app_frame.pack(fill=tk.BOTH, expand=True)

def check_login():
    pwd = password_entry__login.get()
    if b.app_pass_is_correct(pwd):
        show_main_app()
    else:
        feedback_label__login.config(text="Wrong password", fg="red")

# this is called on app open when password does not exist
def set_app_pass__set_pass():
    pwd = new_password_entry__set_pass.get()
    pwd2 = repeat_password_entry__set_pass.get()

    if not (pwd and pwd2):
        msg = "Please fill out all fields"
    elif pwd != pwd2:
        msg = "Passwords do not match"
    elif b.set_new_app_pass(pwd):
        show_main_app()
        return
    else:
        msg = "Something went wrong"

    feedback_label__set_pass.config(text=msg, fg='red')

# this is called when user changes app password in settings tab
def set_app_pass__settings():
    pwd = new_password_entry__settings.get()
    pwd2 = repeat_password_entry__settings.get()

    if not (pwd and pwd2):
        feedback_label__settings.config(text="Please fill out all fields", fg='red')
    elif pwd != pwd2:
        feedback_label__settings.config(text="Passwords do not match", fg='red')
    elif b.set_new_app_pass(pwd):
        feedback_label__settings.config(text="New password set successfully", fg='green')
    else:
        feedback_label__settings.config(text="Something went wrong", fg='red')

# ---------- MAIN WINDOW ----------
root = tk.Tk()
root.title("Password Manager")
root.geometry("500x500")
root.resizable(False, False)

root.bind_class("Button", "<Return>", lambda e: e.widget.invoke())

# ---------- LOGIN FRAME ----------
login_frame = tk.Frame(root)

label__login = tk.Label(login_frame, text="Enter Password", font=font_big)
label__login.pack(pady=20)

password_entry_frame__login = tk.Frame(login_frame)
password_entry_frame__login.pack(pady=10, fill=tk.X, padx=50)
password_entry__login = tk.Entry(password_entry_frame__login, font=font_medium)
password_entry__login.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_placeholder_password(password_entry__login, "password")
add_show_hide_toggle(password_entry__login)

login_button = tk.Button(login_frame, text="Login", font=font_medium, command=check_login)
login_button.pack(pady=10)

feedback_label__login = tk.Label(login_frame, text="", font=font_medium)
feedback_label__login.pack()

# ---------- SET APP PASSWORD FRAME ----------
set_pass_frame = tk.Frame(root)

label__set_pass = tk.Label(set_pass_frame, text="Set App Password", font=font_big)
label__set_pass.pack(pady=20)

new_password_entry_frame__set_pass = tk.Frame(set_pass_frame)
new_password_entry_frame__set_pass.pack(fill=tk.X, padx=50, pady=5)
new_password_entry__set_pass = tk.Entry(new_password_entry_frame__set_pass, font=font_medium)
new_password_entry__set_pass.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_placeholder_password(new_password_entry__set_pass, "new password")
add_show_hide_toggle(new_password_entry__set_pass)

repeat_password_entry_frame__set_pass = tk.Frame(set_pass_frame)
repeat_password_entry_frame__set_pass.pack(fill=tk.X, padx=50, pady=5)
repeat_password_entry__set_pass = tk.Entry(repeat_password_entry_frame__set_pass, font=font_medium)
repeat_password_entry__set_pass.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_placeholder_password(repeat_password_entry__set_pass, "repeat new password")
add_show_hide_toggle(repeat_password_entry__set_pass)

save_button__set_password = tk.Button(set_pass_frame, text="Save Password", font=font_medium, command=set_app_pass__set_pass)
save_button__set_password.pack(pady=10)

feedback_label__set_pass = tk.Label(set_pass_frame, text="", font=font_medium)
feedback_label__set_pass.pack()

# ---------- MAIN APP FRAME ----------
app_frame = tk.Frame(root)

notebook = ttk.Notebook(app_frame)
notebook.pack(fill=tk.BOTH, expand=True)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
font_obj = tkFont.Font(family=font_big[0], size=font_big[1])
char_width = font_obj.measure("0")
char_height = font_obj.metrics("linespace")
target_px_width = int(screen_width * 0.3)
target_px_height = int(screen_height * 0.34)
listbox_width = target_px_width // char_width
listbox_height = target_px_height // char_height

# ---------------TAB 1: VIEW--------------------
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="View")

search_frame__view = tk.Frame(tab1)
search_frame__view.pack(fill="x", padx=10, pady=(10, 0))

search_var__view = tk.StringVar()
search_entry__view = tk.Entry(
    search_frame__view,
    textvariable=search_var__view,
    font=font_medium
)
search_entry__view.pack(side="left", fill="x", expand=True)

search_button__view = tk.Button(
    search_frame__view,
    text="🔍",
    font=font_small,
    # command=lambda: search_items(search_var__view.get())
)
search_button__view.pack(side="right", padx=(5, 0))

frame__view = tk.Frame(tab1)
frame__view.pack(pady=10)
scrollbar__view = tk.Scrollbar(frame__view)
scrollbar__view.pack(side=tk.RIGHT, fill=tk.Y)
listbox__view = tk.Listbox(frame__view, yscrollcommand=scrollbar__view.set,
                          font=font_big, width=listbox_width, height=listbox_height)
listbox__view.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar__view.config(command=listbox__view.yview)
listbox__view.bind("<<ListboxSelect>>", on_listbox_key_select__view)

delete_button__view = tk.Button(tab1, text="Delete", fg="white", bg="red",
                          font=font_medium, command=delete_selected_key)
delete_button__view.pack(pady=5)

show_password_frame__view = tk.Frame(tab1)
show_password_frame__view.pack(fill="x", padx=10, pady=10)

password_label__view = tk.Label(show_password_frame__view, text="Password: ", font=font_small)
password_label__view.pack(side="left")

password_var__view = tk.StringVar()
password_entry__view = tk.Entry(
    show_password_frame__view,
    textvariable=password_var__view,
    font=font_medium,
    state="readonly"
)
password_entry__view.pack(side="left", fill="x", expand=True, padx=(5,5))

copy_button__view = tk.Button(show_password_frame__view, text="Copy",
                        font=font_small, command=copy_selected_password__view)
copy_button__view.pack(side="right", padx=(5,0))

update_listbox(listbox__view)

# ---------------TAB 2: ADD--------------------
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Add")

label__add = tk.Label(tab2, text="Add new password", font=font_medium)
label__add.pack(pady=5)

key_entry__add = tk.Entry(tab2, font=font_medium)
key_entry__add.pack(fill=tk.X, padx=5, pady=5)
add_placeholder(key_entry__add, "key")

password_entry_frame__add = tk.Frame(tab2)
password_entry_frame__add.pack(fill=tk.X, padx=5, pady=5)
password_entry__add = tk.Entry(password_entry_frame__add, font=font_medium)
password_entry__add.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_placeholder_password(password_entry__add, "value")
add_show_hide_toggle(password_entry__add)

repeat_entry_frame__add = tk.Frame(tab2)
repeat_entry_frame__add.pack(fill=tk.X, padx=5, pady=5)
repeat_entry__add = tk.Entry(repeat_entry_frame__add, font=font_medium)
repeat_entry__add.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_placeholder_password(repeat_entry__add, "repeat value")
add_show_hide_toggle(repeat_entry__add)

save_button__add = tk.Button(tab2, text="Save", font=font_medium, command=add_new_password)
save_button__add.pack(pady=5)

feedback_label__add = tk.Label(tab2, text="", font=font_medium)
feedback_label__add.pack(pady=5)

# ---------------TAB 3: UPDATE--------------------
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="Update")

search_frame__update = tk.Frame(tab3)
search_frame__update.pack(fill="x", padx=10, pady=(10, 0))

search_var__update = tk.StringVar()
search_entry__update = tk.Entry(
    search_frame__update,
    textvariable=search_var__update,
    font=font_medium
)
search_entry__update.pack(side="left", fill="x", expand=True)

search_button__update = tk.Button(
    search_frame__update,
    text="🔍",
    font=font_small,
    # command=lambda: search_items(search_var__update.get())
)
search_button__update.pack(side="right", padx=(5, 0))

frame__update = tk.Frame(tab3)
frame__update.pack(pady=10)
scrollbar__update = tk.Scrollbar(frame__update)
scrollbar__update.pack(side=tk.RIGHT, fill=tk.Y)
listbox__update = tk.Listbox(frame__update, yscrollcommand=scrollbar__update.set,
                            font=font_big, width=listbox_width, height=listbox_height - 4)
listbox__update.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar__update.config(command=listbox__update.yview)
listbox__update.bind("<<ListboxSelect>>", on_listbox_key_select__update)
update_listbox(listbox__update)

current_password_label__update = tk.Label(tab3, text="Current Password: ", font=font_medium)
current_password_label__update.pack(pady=5)

new_password_entry_frame__update = tk.Frame(tab3)
new_password_entry_frame__update.pack(fill=tk.X, padx=5, pady=5)
new_password_entry__update = tk.Entry(new_password_entry_frame__update, font=font_medium)
new_password_entry__update.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_placeholder_password(new_password_entry__update, "new password")
add_show_hide_toggle(new_password_entry__update)

repeat_entry_frame__update = tk.Frame(tab3)
repeat_entry_frame__update.pack(fill=tk.X, padx=5, pady=5)
repeat_password_entry__update = tk.Entry(repeat_entry_frame__update, font=font_medium)
repeat_password_entry__update.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_placeholder_password(repeat_password_entry__update, "repeat new password")
add_show_hide_toggle(repeat_password_entry__update)

save_button__update = tk.Button(tab3, text="Save", font=font_medium, command=save_updated_password__update)
save_button__update.pack(pady=5)

feedback_label__update = tk.Label(tab3, text="", font=font_medium)
feedback_label__update.pack(pady=5)

# --------------------TAB 4: SETTINGS------------------
tab4 = ttk.Frame(notebook)
notebook.add(tab4, text="Settings")

label__settings = tk.Label(tab4, text="Set new password for the app", font=font_medium)
label__settings.pack(pady=5)

password_entry_frame__settings = tk.Frame(tab4)
password_entry_frame__settings.pack(fill=tk.X, padx=5, pady=5)
new_password_entry__settings = tk.Entry(password_entry_frame__settings, font=font_medium)
new_password_entry__settings.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_placeholder_password(new_password_entry__settings, "new password")
add_show_hide_toggle(new_password_entry__settings)

repeat_entry_frame__settings = tk.Frame(tab4)
repeat_entry_frame__settings.pack(fill=tk.X, padx=5, pady=5)
repeat_password_entry__settings = tk.Entry(repeat_entry_frame__settings, font=font_medium)
repeat_password_entry__settings.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_placeholder_password(repeat_password_entry__settings, "repeat new password")
add_show_hide_toggle(repeat_password_entry__settings)

save_button__settings = tk.Button(tab4, text="Save", font=font_medium, command=set_app_pass__settings)
save_button__settings.pack(pady=5)

feedback_label__settings = tk.Label(tab4, text="", font=font_medium)
feedback_label__settings.pack(pady=5)

# ---------- Decide Start Screen ----------
b.initiate_files()

if b.app_pass_exists():
    login_frame.pack(fill=tk.BOTH, expand=True)
else:
    b.reset_all()
    set_pass_frame.pack(fill=tk.BOTH, expand=True)


root.after(300_000, show_login_after_time)  # app returns to login frame after 5 minutes (300_000 mili seconds)

root.mainloop()
