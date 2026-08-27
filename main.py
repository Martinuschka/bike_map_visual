import folium
from folium.plugins import HeatMap
import pandas as pd
import webbrowser
import os
from mysql.connector import connect, Error
import csv


def db_connect():
    try:
        return connect(host="IP", user="USER", password="PW", database="DB")
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
    map_points = folium.Map(location=[0.0, 0.0], zoom_start=15, tiles="Stamen Toner")
    map_heat = folium.Map(location=[0.0, 0.0], zoom_start=15, tiles="Stamen Toner")

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
    file_heat = "map_heat.html"
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
