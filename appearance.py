import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont

# ---------- DATA ----------
info = {f'key{i}': f'value{i}' for i in range(1, 21)}

# ---------- FUNCTIONS ----------
def update_listbox(lb):
    lb.delete(0, tk.END)
    for key in info.keys():
        lb.insert(tk.END, key)

def on_select_view(event):
    selection = listbox_view.curselection()
    if selection:
        key = listbox_view.get(selection[0])
        value_label_view.config(text=f"Value: {info[key]}")
    else:
        value_label_view.config(text="Value: ")

def on_select_update(event):
    selection = listbox_update.curselection()
    if selection:
        key = listbox_update.get(selection[0])
        current_value_label.config(text=f"Current Value: {info[key]}")
    else:
        current_value_label.config(text="Current Value: ")

def save_new_info():
    k = key_entry.get().strip()
    v = value_entry.get().strip()
    rv = repeat_entry.get().strip()
    if not k or not v or not rv:
        feedback_label_add.config(text="Please fill all fields", fg="red")
        return
    if v != rv:
        feedback_label_add.config(text="Values do not match", fg="red")
        return
    info[k] = v
    feedback_label_add.config(text="New info saved", fg="green")
    update_listbox(listbox_view)
    update_listbox(listbox_update)

def save_updated_value():
    selection = listbox_update.curselection()
    if not selection:
        feedback_label_update.config(text="Please select a key", fg="red")
        return
    new_val = new_value_entry.get().strip()
    repeat_val = repeat_value_entry.get().strip()
    if not new_val or not repeat_val:
        feedback_label_update.config(text="Please fill all fields", fg="red")
        return
    if new_val != repeat_val:
        feedback_label_update.config(text="Values do not match", fg="red")
        return
    key = listbox_update.get(selection[0])
    info[key] = new_val
    feedback_label_update.config(text="Updated successfully", fg="green")
    update_listbox(listbox_view)
    update_listbox(listbox_update)
    current_value_label.config(text=f"Current Value: {new_val}")

def delete_selected_key():
    selection = listbox_view.curselection()
    if not selection:
        return
    key = listbox_view.get(selection[0])
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{key}'?")
    if not confirm:
        return
    del info[key]
    update_listbox(listbox_view)
    update_listbox(listbox_update)
    value_label_view.config(text="Value: ")

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

def add_password_toggle(entry):
    toggle_btn = tk.Button(entry.master, text="Show", width=8, font=("Arial", 10))
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

# ---------- MAIN WINDOW ----------
root = tk.Tk()
root.title("Dictionary Manager")
root.resizable(False, False)

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
font_obj = tkFont.Font(family="Arial", size=14)
char_width = font_obj.measure("0")
char_height = font_obj.metrics("linespace")
target_px_width = int(screen_width * 0.3)
target_px_height = int(screen_height * 0.4)
listbox_width = target_px_width // char_width
listbox_height = target_px_height // char_height

# ---------- TAB 1: VIEW ----------
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="View")

frame_view = tk.Frame(tab1)
frame_view.pack(pady=10)
scrollbar_view = tk.Scrollbar(frame_view)
scrollbar_view.pack(side=tk.RIGHT, fill=tk.Y)
listbox_view = tk.Listbox(frame_view, yscrollcommand=scrollbar_view.set, font=("Arial",14), width=listbox_width, height=listbox_height)
listbox_view.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar_view.config(command=listbox_view.yview)
listbox_view.bind("<<ListboxSelect>>", on_select_view)

delete_button = tk.Button(tab1, text="Delete", fg="white", bg="red", font=("Arial",12), command=delete_selected_key)
delete_button.pack(pady=5)

value_label_view = tk.Label(tab1, text="Value: ", font=("Arial",12))
value_label_view.pack(pady=10)

update_listbox(listbox_view)

# ---------- TAB 2: ADD ----------
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Add")

key_entry = tk.Entry(tab2, font=("Arial",12))
key_entry.pack(fill=tk.X, padx=5, pady=5)
add_placeholder(key_entry, "key")

frame_value = tk.Frame(tab2)
frame_value.pack(fill=tk.X, padx=5, pady=5)
value_entry = tk.Entry(frame_value, font=("Arial",12))
value_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_placeholder_password(value_entry, "value")
add_password_toggle(value_entry)

frame_repeat = tk.Frame(tab2)
frame_repeat.pack(fill=tk.X, padx=5, pady=5)
repeat_entry = tk.Entry(frame_repeat, font=("Arial",12))
repeat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_placeholder_password(repeat_entry, "repeat value")
add_password_toggle(repeat_entry)

save_button_add = tk.Button(tab2, text="Save", font=("Arial",12), command=save_new_info)
save_button_add.pack(pady=5)

feedback_label_add = tk.Label(tab2, text="", font=("Arial",12))
feedback_label_add.pack(pady=5)

# ---------- TAB 3: UPDATE ----------
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="Update")

frame_update = tk.Frame(tab3)
frame_update.pack(pady=10)
scrollbar_update = tk.Scrollbar(frame_update)
scrollbar_update.pack(side=tk.RIGHT, fill=tk.Y)
listbox_update = tk.Listbox(frame_update, yscrollcommand=scrollbar_update.set, font=("Arial",14), width=listbox_width, height=listbox_height//2)
listbox_update.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar_update.config(command=listbox_update.yview)
listbox_update.bind("<<ListboxSelect>>", on_select_update)
update_listbox(listbox_update)

current_value_label = tk.Label(tab3, text="Current Value: ", font=("Arial",12))
current_value_label.pack(pady=5)

frame_new_value = tk.Frame(tab3)
frame_new_value.pack(fill=tk.X, padx=5, pady=5)
new_value_entry = tk.Entry(frame_new_value, font=("Arial",12))
new_value_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_placeholder_password(new_value_entry, "new value")
add_password_toggle(new_value_entry)

frame_repeat_new = tk.Frame(tab3)
frame_repeat_new.pack(fill=tk.X, padx=5, pady=5)
repeat_value_entry = tk.Entry(frame_repeat_new, font=("Arial",12))
repeat_value_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
add_placeholder_password(repeat_value_entry, "new value repeat")
add_password_toggle(repeat_value_entry)

save_button_update = tk.Button(tab3, text="Save", font=("Arial",12), command=save_updated_value)
save_button_update.pack(pady=5)

feedback_label_update = tk.Label(tab3, text="", font=("Arial",12))
feedback_label_update.pack(pady=5)

root.mainloop()
