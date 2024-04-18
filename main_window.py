from tkinter import *
from tkinter import Tk
from datetime import datetime, timedelta
import re
import json
import requests


class MainWindow:
    def __init__(self):
        self.discords_ids = {
            'pimba': 377215592421261313,
            'imake': 336943409707089921,
            'yenthi': 263317662593974274,
            'telmo': 927964333584039997
        }
        
        self.main_window = Tk()
        self.ammount_ms_lbl = Label(self.main_window, text= "Tree List Time")
        self.ammount_ms_lbl.grid(row=0, column=0)
        self.text_widget = Text(self.main_window, width=50, height=10)
        self.text_widget.grid(row=1, column=0, sticky="nsew")

        self.webhook_entry = Entry(self.main_window, width=50)
        self.webhook_entry.grid(row=4, column=0, sticky="ws", pady=20)
        self.webhook_entry.insert(0, "Enter Discord webhook URL here")
        self.webhook_entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.webhook_entry.bind("<FocusOut>", self.on_entry_focus_out)
        final_row = 5
        self.clicked_discord_ids = []

        for discord_id in self.discords_ids:
            cb = Checkbutton(self.main_window, text=discord_id, variable=IntVar(), command=lambda discord_id=discord_id: self.on_discord_checkbox_click(discord_id))
            cb.grid(row=final_row, column=0, sticky="w")
            final_row += 1
        
        self.add_ms_btn = Button(self.main_window, text="Generate Timers", command=self.on_button_click)
        self.add_ms_btn.grid(row=final_row+1, column=0, sticky="ws",pady=20)

        self.main_window.rowconfigure(0, weight=1)
        self.main_window.columnconfigure(0, weight=1)

        

    def on_text_change(self,event):
        self.text_widget.configure(height=1 + len(self.text_widget.get("1.0", "end-1c")) // self.text_widget.cget("width"))

    def on_button_click(self):
        ms_to_add = 26100000
        lines = self.text_widget.get("1.0", "end-1c")
        lines = lines.replace('\n', '')
        island_code = re.search(r'Farm Land #(\d+)', lines).group(1)
        lastchops = re.findall(r'lastChop\x01(\d+)', lines)
        valid_lines = []
        island_code_msg = f"--- Island Code: {island_code} ---"
        last_chops_msg =""
        for i, chopTime in enumerate(lastchops, 1):
            unix_timestamp = float(chopTime) / 1000
            time_obj = datetime.fromtimestamp(unix_timestamp)
            time_obj += timedelta(milliseconds=ms_to_add)  # Add the milliseconds
            time_format = "%Y-%m-%d | %H:%M:%S.%f"
            new_time_str = time_obj.strftime(time_format)
            valid_lines.append(f'{new_time_str[:-7]}')
        #order list
        timestamps = [datetime.strptime(ts, '%Y-%m-%d | %H:%M:%S') for ts in valid_lines]
        timestamps.sort(reverse=False)
        timestamps = [f"Tree {j}: {ts.strftime('%Y-%m-%d | %H:%M:%S')}" for j, ts in enumerate(timestamps,1)]
        last_chops_msg = "\n".join(timestamps)
        #create message
        msg = f"{island_code_msg}\n{last_chops_msg}"
        if len(self.clicked_discord_ids) > 0:
            discord_ids = ['<@' + str(id) + '>' for id in self.clicked_discord_ids]
            discord_ids_string = ', '.join(discord_ids)
            msg += f"\n{discord_ids_string}"
        msg_json = json.dumps({
            "username": "Tree Notifications",
            "avatar_url": "",
            "content": msg
        })
        webhook = self.webhook_entry.get()
        #send message
        request = requests.post(webhook, data=msg_json, headers={'Content-Type': 'application/json'})
        if request.status_code == 204:
            print("Message sent to Discord webhook")
        else:
            print(f"Error sending message to Discord webhook: {request.status_code}")

    def on_entry_focus_in(self, event):
        if self.webhook_entry.get() == "Enter Discord webhook URL here":
            self.webhook_entry.delete(0, END)
            self.webhook_entry.config(fg="black")

    def on_entry_focus_out(self, event):
        if self.webhook_entry.get() == "":
            self.webhook_entry.insert(0, "Enter Discord webhook URL here")

    def on_discord_checkbox_click(self, discord_id):
        if self.discords_ids[discord_id] in self.clicked_discord_ids:
            self.clicked_discord_ids.remove(self.discords_ids[discord_id])
        else:
            self.clicked_discord_ids.append(self.discords_ids[discord_id])
