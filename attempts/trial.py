import math
import random
import asyncio
import pandas as pd
from colorthief import ColorThief
from requests_html import AsyncHTMLSession

import nest_asyncio

nest_asyncio.apply()

# color mappings --> each index corresponds to the respective color value
rainbow_colors = [
    (255, 0, 0), (255, 127, 0), (255, 255, 0),
    (0, 255, 0), (48, 213, 200), (0, 0, 255),
    (75, 0, 130), (148, 0, 211), (255, 141, 161),
    (0, 0, 0), (255, 255, 255)
]
color_names = [
    "red", "orange", "yellow", "green", "turquoise",
    "blue", "indigo", "violet", "pink", "black", "white"
]


# finding main color
def get_main_color(image_path):
    color_thief = ColorThief(image_path)
    main_color = color_thief.get_color(quality=1)
    return main_color


# getting the closest color from rainbow_colors
def get_closest_color(main_color):
    """
    In order to find the distance between 2 points,
    the pythagorean theorem can be used.
    pythagorean_theorem = sqrt(distance1^2 + distance2^2)
    However, rgb is 3-dimensional.
    """
    values = [float('inf')] # basically just largest number rather than what i was doing before
    colors = []
    r_value, g_value, b_value = main_color

    # finding smallest 3-dimensional distance
    for j in rainbow_colors:
        r, g, b = j
        distance = math.sqrt((r - r_value) ** 2 + (g - g_value) ** 2 + (b - b_value) ** 2)

        if distance < values[-1]:
            values.append(distance)
            colors.append(j)

    # using that to get corresponding rainbow color
    closest_color = colors[-1]
    color_index = rainbow_colors.index(closest_color)
    closest_color_name = color_names[color_index]
    return closest_color, closest_color_name


# Fetch table data and convert to DataFrame
async def fetch_table_as_dataframe(color_value):
    session = AsyncHTMLSession()
    base_url = "https://www.chordgenome.com/result/?querychrd="
    url_mapping = {
        (255, 0, 0): "C,G,Am,F,G,C",
        (255, 127, 0): "C,F,Am,G",
        (255, 255, 0): "C,F,G",
        (0, 255, 0): "Em,D,C,G,G/F#",
        (48, 213, 200): "C,F,Dm,G",
        (0, 0, 255): "C,Am,E,G",
        (75, 0, 130): "Am,F,C,Em",
        (148, 0, 211): "Am,E,F,Dm",
        (255, 141, 161): "C,G/B,Am,Em/G,F,C/E,Dm,G",
        (0, 0, 0): "Am,Dm,Em",
        (255, 255, 255): "A,C,Em,D",
    }

    url = base_url + url_mapping[color_value]
    response = await session.get(url)
    await response.html.arender(timeout=30, sleep=5)

    table = response.html.find('#song-result-table', first=True)
    if not table:
        raise ValueError("Table with ID 'song-result-table' not found!") # just in case no table

    rows = table.find('tbody tr')
    if not rows:
        raise ValueError("No rows found in the table!") # in case no rows

    data = []
    for row in rows:
        columns = row.find('td')
        row_data = []
        for idx, col in enumerate(columns):
            if idx == 2:
                link = col.find('a', first=True)
                row_data.append(link.attrs['href'] if link and 'href' in link.attrs else None)
            else:
                row_data.append(col.text.strip())
        data.append(row_data)

    column_headers = ["SONG", "ARTIST", "VID", "GENRE", "DECADE", "Chords", "#"]
    df = pd.DataFrame(data, columns=column_headers[:len(data[0])])
    return df #getting dataframe


# Function to select a random song and video from the DataFrame
def select_random_song(df):
    if df.empty:
        print("No songs found in the DataFrame.") # just in case
        return

    random_row = df.sample().iloc[0]
    song = random_row['SONG'] #ranodm song + vid
    video = random_row['VID']
    print(f"SONG: {song}")
    print(f"VIDEO: {video}")


# main async function
async def main():
    # extracting color
    main_color = get_main_color("../imagestotest/starrynight.jpg")
    color_value, color_name = get_closest_color(main_color)
    print(f"The main color in this image is {color_name}.")

    # getting data
    try:
        df = await fetch_table_as_dataframe(color_value)
        print("DataFrame fetched successfully!")
        print(df.head())

        # displaying random song
        select_random_song(df)
    except Exception as e:
        print(f"An error occurred: {e}")


# running async function
asyncio.run(main())
