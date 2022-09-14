from datetime import datetime, timedelta
import http.client
import json
import folium

import windowManager


id: int = 8000105
date: str = "2022-07-25"
time: str = "14:15"

headers = {
    'DB-Client-Id': "cf5b42daa27e794c289e40856e603428",
    'DB-Api-Key': "fde59a6c188b28d1e4aa756558982c2b",
    'accept': "application/json"
}


def main():
    windowManager.create_window()

    st_map = createMap()

    print("Type a station name to search for stations")
    station_req = input()

    stations_json: json = request_station(station_req)

    print("Please select the correct station by typing the number in front:")

    for i in range(min(len(stations_json), 9)):
        curr_station = stations_json[i]
        add_marker(curr_station["lat"], curr_station["lon"], str(i) + ": " + curr_station["name"], st_map)
        print(f'{i}: {curr_station["name"]}')

    number = input()

    if number == "":
        index = 0
    else:
        index = int(number)

    station = stations_json[index]

    add_marker(station["lat"], station["lon"], station["name"], st_map)

    connections_json: json = request_connections(station["id"], datetime.now())

    print("Found the following connections in the next hour:")

    for connection in connections_json:
        dept_date = datetime.strptime(connection["dateTime"], "%Y-%m-%dT%H:%M")

        if dept_date > datetime.now() + timedelta(hours=1):
            continue

        print(f'{connection["name"]} to {connection["direction"]} at {dept_date.strftime("%H:%M")}')

    st_map.save("./map.html")


def createMap() -> folium.Map:
    map = folium.Map(
        location=[51.032926, 10.368287],
        tiles="OpenStreetMap",
        zoom_start=5
    )

    return map


def add_marker(lat: float, lon: float, content: str, base_map: folium.Map):
    folium.CircleMarker(
        location=[lat, lon],
        color='#c0392b',
        fill=True,
        fillColor='#c0392b',
        opacity=0.5,
        fillOpacity=0.3,
        popup=content
    ).add_to(base_map)


def request_station(station: str) -> json:
    conn = http.client.HTTPSConnection("apis.deutschebahn.com")

    station = station.replace(" ", "%20")

    conn.request("GET", f'/db-api-marketplace/apis/fahrplan/v1/location/{station}',
                 headers=headers)

    res = conn.getresponse()
    data = res.read()

    return json.loads(data.decode("utf-8"))


def request_connections(station_id: int, dept_datetime) -> json:
    conn = http.client.HTTPSConnection("apis.deutschebahn.com")

    dept_dt = dept_datetime.strftime("%Y-%m-%dT%H:%M")

    conn.request("GET", f'/db-api-marketplace/apis/fahrplan/v1/departureBoard/{station_id}?date={dept_dt}',
                 headers=headers)

    res = conn.getresponse()
    data = res.read()

    return json.loads(data.decode("utf-8"))


def request_details(details_id: str) -> json:
    conn = http.client.HTTPSConnection("apis.deutschebahn.com")

    conn.request("GET", f'/db-api-marketplace/apis/fahrplan/v1/journeyDetails/{details_id}', headers=headers)

    res = conn.getresponse()
    data = res.read()

    return json.loads(data.decode("utf-8"))


if __name__ == '__main__':
    main()
