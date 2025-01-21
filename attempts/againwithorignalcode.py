# imports
import io
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


from flask import Flask, request, render_template, send_file, redirect, url_for, flash, session
import re
import os

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


app = Flask(__name__)
app.secret_key = "W!red_were_the_eyes_of_@_horse_on_a_jet_pilot"

# upload folder used to store the image the user inputs
UPLOAD_FOLDER = "static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return redirect(url_for('show_image', filename=filename))

    return render_template('homepage.html')

@app.route('/show_image/<filename>')
def show_image(filename):
    def get_main_color(image_path):
        color_thief = ColorThief(image_path)
        main_color = color_thief.get_color(quality=1)
        return main_color

    def get_closest_color(main_color):
        """
        In order to find the distance between 2 points,
        the pythagorean theorem can be used.
        pythagorean_theorem = sqrt(distance1^2 + distance2^2)
        However, rgb is 3-dimensional.
        """
        values = [float('inf')]  # basically just largest number rather than what i was doing before
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
    def fetch_table_as_dataframe(color_value):
        session = HTMLSession()
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
        response = session.get(url)

        table = response.html.find('#song-result-table', first=True)
        if not table:
            raise ValueError("Table with ID 'song-result-table' not found!")  # just in case no table

        rows = table.find('tbody tr')
        if not rows:
            raise ValueError("No rows found in the table!")  # in case no rows

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
        return df  # getting dataframe

    # Function to select a random song and video from the DataFrame
    def select_random_song(df):
        if df.empty:
            print("No songs found in the DataFrame.")  # just in case
            return

        random_row = df.sample().iloc[0]
        song = random_row['SONG']  # ranodm song + vid
        video = random_row['VID']
        print(f"SONG: {song}")
        print(f"VIDEO: {video}")

    def main(filename):
        # extracting color
        main_color = get_main_color(filename)
        color_value, color_name = get_closest_color(main_color)
        print(f"The main color in this image is {color_name}.")

        # getting data
        try:
            df = fetch_table_as_dataframe(color_value)
            print("DataFrame fetched successfully!")
            print(df.head())

            # displaying random song
            select_random_song(df)
        except Exception as e:
            print(f"An error occurred: {e}")

    main_color = request.args.get('main_color')
    song = request.args.get('song')
    video = request.args.get('video')
    main(filename)
    return render_template('processingimage.html',
                           filename=filename,
                           color_name=main_color,
                           song_name=song,
                           video_name=video
                           )


if __name__ == '__main__':
    app.run(debug=True)