from datetime import datetime, timedelta
import json
import tkinter as tk
import tkinter.ttk as ttk
import tkintermapview as tkm

import main

window = tk.Tk()

input = ttk.Entry(window, width=50, )
btn = ttk.Button(window, text="Submit")
varList = tk.StringVar(window)

map_frame = ttk.LabelFrame(window)
map_view = tkm.TkinterMapView(map_frame, width=800, height=800, corner_radius=0)

stations_json: json
stations = []

labels = []
connections_json: json


def create_window() -> tk.Tk:
    btn.configure(command=click_button)

    window.title("Python GUI App")
    window.configure(width=1500, height=800)
    window.configure(bg='lightgray')

    # move window center
    winWidth = window.winfo_reqwidth()
    winwHeight = window.winfo_reqheight()
    posRight = int(window.winfo_screenwidth() / 2 - winWidth / 2)
    posDown = int(window.winfo_screenheight() / 2 - winwHeight / 2)
    window.geometry("+{}+{}".format(posRight, posDown))

    input.insert(0, "Type a station to search for here")
    input.bind("<Button>", remove_text)

    map_view.set_position(51.032926, 10.368287)
    map_view.set_zoom(6)
    map_view.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",max_zoom=22)  # google normal
    #map_view.set_overlay_tile_server("http://a.tiles.openrailwaymap.org/gauge/{z}/{x}/{y}.png")  # railway infrastructure
    map_view.pack()

    input.place(x=0, y=0)
    btn.place(x=300, y=0)
    map_frame.place(x=400, y=0)

    window.mainloop()

    return window


def remove_text(event: tk.Event = None):
    event.widget.delete(0, 'end')


markers = []


def click_button():
    global stations_json
    global markers
    stations_json = main.request_station(input.get())

    print("Please select the correct station by typing the number in front:")

    stations.clear()

    for marker in markers:
        marker.delete()

    markers.clear()
    for i in range(min(len(stations_json), 9)):
        curr_station = stations_json[i]
        stations.append(curr_station["name"])
        tmp_marker = map_view.set_marker(curr_station["lat"], curr_station["lon"], text=curr_station["name"], marker_color_outside="#486da1", marker_color_circle="#6c8dbd", text_color="#484e57")
        markers.append(tmp_marker)
        print(f'{i}: {curr_station["name"]}')

    stations.insert(0, stations[0])
    selector = ttk.OptionMenu(window, varList, *stations)
    selector.configure(width=50)
    varList.trace("w", updateMarkers)

    btn_search = ttk.Button(window, text="Search Connections", command=search_connections)

    selector.place(x=0, y=20)
    btn_search.place(x=300, y=20)

    updateMarkers()


prev_marker = 0


def updateMarkers(event: tk.Event = None, *args):
    global prev_marker

    prev_station = stations_json[prev_marker]

    markers[prev_marker].delete()
    markers[prev_marker] = map_view.set_marker(prev_station["lat"], prev_station["lon"], text=prev_station["name"], marker_color_outside="#486da1", marker_color_circle="#6c8dbd", text_color="#484e57")

    index = max(0, stations.index(varList.get()) - 1)

    curr_station = stations_json[index]

    markers[index].delete()
    markers[index] = map_view.set_marker(curr_station["lat"], curr_station["lon"], text=curr_station["name"], marker_color_outside="#bd7619", marker_color_circle="#9c6d30", text_color="#544633")

    prev_marker = index


def search_connections():
    global labels
    global connections_json

    for label in labels:
        label.destroy()

    station = stations_json[stations.index(varList.get()) - 1]

    connections_json = main.request_connections(station["id"], datetime.now())

    y = 40
    labels = []
    for connection in connections_json:
        dept_date = datetime.strptime(connection["dateTime"], "%Y-%m-%dT%H:%M")

        if dept_date > datetime.now() + timedelta(hours=1):
            continue

        tmp_label = ttk.Label(window, text=f'{connection["name"]} to {connection["direction"]} at {dept_date.strftime("%H:%M")}')
        labels.append(tmp_label)
        tmp_label.bind("<Button>", drawLine)
        tmp_label.place(x=0, y=y)
        y += 20


connection_path: tkm.map_widget.CanvasPath = None


def drawLine(event: tk.Event = None):
    global connection_path

    index = labels.index(event.widget)
    connection = connections_json[index]

    details_json = main.request_details(connection["detailsId"])

    points = []

    for stop in details_json:
        points.append((float(stop["lat"]), float(stop["lon"])))

    if connection_path is not None:
        connection_path.delete()
    connection_path = map_view.set_path(points)