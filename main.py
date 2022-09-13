from datetime import datetime, timedelta
import http.client
import json

id: int = 8000105
date: str = "2022-07-25"
time: str = "14:15"

headers = {
    'DB-Client-Id': "cf5b42daa27e794c289e40856e603428",
    'DB-Api-Key': "fde59a6c188b28d1e4aa756558982c2b",
    'accept': "application/json"
}


def main():
    print("Type a station name to search for stations")
    station_req = input()

    stations_json: json = request_station(station_req)

    stations: list = []

    for station in stations_json:
        stations.append(station["name"])

    print("Please select the correct station by typing the number in front:")

    for i in range(min(len(stations), 9)):
        print(f'{i}: {stations[i]}')

    number = input()

    if number == "":
        index = 0
    else:
        index = int(number)

    station = stations_json[index]

    connections_json: json = request_connections(station["id"], datetime.now())

    print("Found the following connections in the next hour:")

    for connection in connections_json:
        dept_date = datetime.strptime(connection["dateTime"], "%Y-%m-%dT%H:%M")

        if dept_date > datetime.now() + timedelta(hours=1):
            continue

        print(f'{connection["name"]} to {connection["direction"]} at {dept_date.strftime("%H:%M")}')


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

    conn.request("GET", f'/db-api-marketplace/apis/fahrplan/v1/departureBoard/{station_id}?date={dept_dt}', headers=headers)

    res = conn.getresponse()
    data = res.read()

    return json.loads(data.decode("utf-8"))


if __name__ == '__main__':
    main()