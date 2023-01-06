import folium
from folium.plugins import HeatMap
# import osmnx as ox
import pandas as pd
import webbrowser
import os
from mysql.connector import connect, Error
# from mariadb.connector import connect, Error
import csv


def db_connect():
    try:
        # 192.168.178.36
        # localhost
        # mysql -u root -p
        # grant all privileges on *.* to 'root'@'localhost' identified by password 'bike_map_db_root' with grant option;
        # grant all privileges on *.* to 'root'@'192.168.178.%' identified by password 'bike_map_db_root' with grant option;
        # FLUSH PRIVILEGES;
        # 50 conf: # vor bind address, port=3306, systemctl restart mariadb
        return connect(host="192.168.178.36", user="root", password="bike_map_db_root", database="bike_map")
    except Error as e:
        print(e)


def db_export(cnx):
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM measurements;")
    with open("measurements.csv", "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(cursor)


def load_data():
    data_path = "measurements.csv"
    return pd.read_csv(data_path)


def plot_map():
    print("Initializing...")
    # place = "Berlin, Germany"  # [52.51650031757565, 13.44113051062602], ox.geocode(place)
    map_points = folium.Map(location=[52.51650031757565, 13.44113051062602], zoom_start=15, tiles="Stamen Toner")
    map_heat = folium.Map(location=[52.51650031757565, 13.44113051062602], zoom_start=15, tiles="Stamen Toner")
    # OpenStreetMap, Stamen Toner, Stamen Terrain, CartoDB positron, CartoDB dark_matter

    print("Loading Data...")
    df = load_data()
    smooth_value = 10.0
    nasty_value = 30.0

    print("Plotting...")
    heat_data = []
    # heat_data = [[item["latitude"], item["longitude"], item["vibration"]] for row, item in df.iterrows()]
    # heat_data = [df.latitude.loc[df["vibration"] >= nasty_value], df.longitude.loc[df["vibration"] >= nasty_value]]

    for row, item in df.iterrows():
        if item["vibration"] < 1.0:
            marker = folium.Circle(location=(item["latitude"], item["longitude"]), radius=1, color="blue", fill=True, tooltip=("vibration="+str(item["vibration"])))
            marker.add_to(map_points)
        if (item["vibration"] >= 1.0) & (item["vibration"] < smooth_value):
            marker = folium.Circle(location=(item["latitude"], item["longitude"]), radius=1, color="green", fill=True, tooltip=("vibration="+str(item["vibration"])))
            marker.add_to(map_points)
        if (item["vibration"] >= smooth_value) & (item["vibration"] < nasty_value):
            marker = folium.Circle(location=(item["latitude"], item["longitude"]), radius=1, color="yellow", fill=True, tooltip=("vibration="+str(item["vibration"])))
            marker.add_to(map_points)
        if item["vibration"] >= nasty_value:
            marker = folium.Circle(location=(item["latitude"], item["longitude"]), radius=1, color="red", fill=True, tooltip=("vibration="+str(item["vibration"])))
            marker.add_to(map_points)
            heat_data.append([item["latitude"], item["longitude"], item["vibration"]])  # HEATMAP

    HeatMap(heat_data).add_to(map_heat)

    print("Writing to disk...")
    file_points = "map_points.html"
    # file_points = "/home/pi/share/map_points.html"
    file_heat = "map_heat.html"
    # file_heat = "/home/pi/share/map_heat.html"
    map_points.save(file_points)
    map_heat.save(file_heat)
    print("Opening in browser...")
    webbrowser.open_new_tab("file://"+os.path.realpath(file_points))
    # webbrowser.open_new_tab("file://" + os.path.realpath(file_heat))
    print("Finished.")


if __name__ == '__main__':
    connection = db_connect()
    print("Connection: ", connection)
    db_export(connection)
    plot_map()
