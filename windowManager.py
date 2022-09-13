import json
import tkinter as tk
import tkinter.ttk as ttk

import main

window = tk.Tk()
greeting = ttk.Label(window, text="Type a station to search for")
input = ttk.Entry(window, width=50)
btn = ttk.Button(window, text="Submit")


def create_window() -> tk.Tk:
    btn.configure(command=click_button)

    window.title("Python GUI App")
    window.configure(width=500, height=300)
    window.configure(bg='lightgray')

    # move window center
    winWidth = window.winfo_reqwidth()
    winwHeight = window.winfo_reqheight()
    posRight = int(window.winfo_screenwidth() / 2 - winWidth / 2)
    posDown = int(window.winfo_screenheight() / 2 - winwHeight / 2)
    window.geometry("+{}+{}".format(posRight, posDown))

    greeting.place(x=0, y=0)
    input.place(x=0, y=20)
    btn.place(x=300, y=20)

    window.mainloop()

    return window


def click_button():
    stations_json: json = main.request_station(input.get())

    print("Please select the correct station by typing the number in front:")

    choices = []
    for i in range(min(len(stations_json), 9)):
        curr_station = stations_json[i]
        choices.append(curr_station["name"])
        print(f'{i}: {curr_station["name"]}')

    varList = tk.StringVar(window)
    selector = ttk.OptionMenu(window, varList, *choices)

    btn_search = ttk.Button(window, text="Search Connections")

    selector.place(x=0, y=40)
    btn_search.place(x= 100, y=40)
