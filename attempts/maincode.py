# imports
# color
from colorthief import ColorThief

# calculations
import math
import time

# finding song
import random
import requests
import webbrowser
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
import asyncio
import pandas as pd

import nest_asyncio
nest_asyncio.apply()

# rgb values

red = (255, 0, 0)
orange = (255, 127, 0)
yellow = (255, 255, 0)
green = (0, 255, 0)
turquoise = (48, 213, 200)
blue = (0, 0, 255)
indigo = (75, 0, 130)
violet = (148, 0, 211)
pink = (255, 141, 161)
black = (0, 0, 0)
white = (255, 255, 255)

rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (48, 213, 200), (0, 0, 255), (75, 0, 130), (148, 0, 211), (255, 141, 161), (0, 0, 0), (255, 255, 255)]

# extracting the color palette

color_thief = ColorThief("../imagestotest/starrynight.jpg")

main_color = color_thief.get_color(quality=1)

"""
In order to find the distance between 2 points, 
the pythagorean theorem can be used.
pythagorean_theorem = sqrt(distance1^2 + distance2^2)
However, rgb is 3 dimensional.
"""

final_colors = []

values = [10000000000]
colors = []
r_value = main_color[0]
g_value = main_color[1]
b_value = main_color[2]

for j in rainbow_colors:
    r = j[0]
    g = j[1]
    b = j[2]

    distance = math.sqrt((r - r_value) ** 2 + (g - g_value) ** 2 + (b - b_value) ** 2)

    if distance < values[-1]:
        values.append(distance)
        colors.append(j)

color_value = colors[-1]

if color_value == rainbow_colors[0]:
    color_name = "red"
elif color_value == rainbow_colors[1]:
    color_name = "orange"
elif color_value == rainbow_colors[2]:
    color_name = "yellow"
elif color_value == rainbow_colors[3]:
    color_name = "green"
elif color_value == rainbow_colors[4]:
    color_name = "turquoise"
elif color_value == rainbow_colors[5]:
    color_name = "blue"
elif color_value == rainbow_colors[6]:
    color_name = "indigo"
elif color_value == rainbow_colors[7]:
    color_name = "violet"
elif color_value == rainbow_colors[8]:
    color_name = "pink"
elif color_value == rainbow_colors[9]:
    color_name = "black"
elif color_value == rainbow_colors[10]:
    color_name = "white"

print("The main color in this image is " + color_name + ".")

# Allow nested event loops
nest_asyncio.apply()

# fetch table data and convert to dataframe
async def fetch_table_as_dataframe():
    session = AsyncHTMLSession()

    # finding the correct URL based on the colors
    base_url = "https://www.chordgenome.com/result/?querychrd="
    print(base_url)

    if color_value == (255, 0, 0):
        url = base_url + "C,G,Am,F,G,C"

    elif color_value == (255, 127, 0):
        url = base_url + "C,F,Am,G"

    elif color_value == (255, 255, 0):
        url = base_url + "C,F,G"

    elif color_value == (0, 255, 0):
        url = base_url + "Em,D,C,G,G/F#"

    elif color_value == (48, 213, 200):
        url = base_url + "C,F,Dm,G"

    elif color_value == (0, 0, 255):
        url = base_url + "C,Am,E,G"

    elif color_value == (75, 0, 130):
        url = base_url + "Am,F,C,Em"

    elif color_value == (148, 0, 211):
        url = base_url + "Am,E,F,Dm"

    elif color_value == (255, 141, 161):
        url = base_url + "C,G/B,Am,Em/G,F,C/E,Dm,G"

    elif color_value == (0, 0, 0):
        url = base_url + "Am,Dm,Em"

    elif color_value == (255, 255, 255):
        url = base_url + "A,C,Em,D"


    response = await session.get(url)

    # render javascript content --> timeout gives enough space to load, sleep allows it to fully render
    await response.html.arender(timeout=30, sleep=5)

    # locates table with the id "song-result-table" found in html of website
    table = response.html.find('#song-result-table', first=True)
    if not table:
        raise ValueError("Table with ID 'song-result-table' not found!")

    # extracting all rows
    rows = table.find('tbody tr')
    if not rows:
        raise ValueError("No rows found in the table!")

    # extracting data from columns + rows
    data = []
    for row in rows:
        columns = row.find('td')  # finding all columns in each row of the for loop
        row_data = []

        for idx, col in enumerate(columns):
            # checking which column it is
            if idx == 2:  # column 2 is video
                link = col.find('a', first=True)  #finding the <a> tag to find the video link
                if link and 'href' in link.attrs:
                    row_data.append(link.attrs['href'])  #getting the href link
                else:
                    row_data.append(None)
            else:
                row_data.append(col.text.strip())  #for other columns, normal text can be extracted rather than href

        if row_data:
            data.append(row_data)

    # column headers based on <thead> in table
    column_headers = ["SONG", "ARTIST", "VID", "GENRE", "DECADE", "Chords", "#"]

    # converting data into panda dataframe + returning it
    df = pd.DataFrame(data, columns=column_headers[:len(data[0])])
    return df

    # retrieving random song!!
    songs_table_url = pd.read_csv("../songs_table_with_vids.csv")
    genre_list = songs_table_url["GENRE"].unique()
    for i in range(len(genre_list)):
        print(str(i+1) + ". " + genre_list[i])

    while True:
        try:
            genre_input = int(input("Enter the number of the genre you want: "))
            if 0 < genre_input <= len(genre_list)+1:
                break
            else:
                print("Enter a valid number.")
                print("")
        except ValueError:
            print("Please enter a number.")
            print("")

    print("")

    genre = genre_list[genre_input-1]

    songs_in_genre = []
    vids_in_genre = []

    for i in range(len(songs_table_url)):
        if songs_table_url["GENRE"][i] == genre:
            songs_in_genre.append(songs_table_url["SONG"][i])
            vids_in_genre.append(songs_table_url["VID"][i])


    song_index = random.randint(0, len(songs_in_genre)-1)


    print("SONG: " + songs_table_url["SONG"][song_index])
    print("VIDEO: " + songs_table_url["VID"][song_index])

try:
    df = asyncio.run(fetch_table_as_dataframe())
    print("DataFrame fetched successfully!")
    print(df.head())  # Print the first few rows of the DataFrame for verification
except Exception as e:
    print(f"An error occurred: {e}")