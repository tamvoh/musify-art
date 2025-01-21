import io
import math
import time
import random
import requests
import os
import pandas as pd
from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_socketio import SocketIO
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from colorthief import ColorThief
from selenium import webdriver

# Selenium Manager automatically fetches the correct WebDriver
driver = webdriver.Chrome()
driver.get("https://example.com")


app = Flask(__name__)
app.secret_key = "W!red_were_the_eyes_of_@_horse_on_a_jet_pilot"

# RGB values and rainbow colors
rainbow_colors = [
    (255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (48, 213, 200),
    (0, 0, 255), (75, 0, 130), (148, 0, 211), (255, 141, 161), (0, 0, 0), (255, 255, 255)
]

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



def get_closest_color(main_color):
    values = [10000000000]
    closest_color = None
    for color in rainbow_colors:
        distance = calculate_color_distance(main_color, color)
        if distance < values[-1]:
            values.append(distance)
            closest_color = color
    return closest_color


def calculate_color_distance(color1, color2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(color1, color2)))


def get_color_name(color_value):
    color_names = {
        (255, 0, 0): "red",
        (255, 127, 0): "orange",
        (255, 255, 0): "yellow",
        (0, 255, 0): "green",
        (48, 213, 200): "turquoise",
        (0, 0, 255): "blue",
        (75, 0, 130): "indigo",
        (148, 0, 211): "violet",
        (255, 141, 161): "pink",
        (0, 0, 0): "black",
        (255, 255, 255): "white"
    }
    return color_names.get(color_value, "unknown")


def fetch_table_as_dataframe(color_value):
    session = HTMLSession()
    base_url = "https://www.chordgenome.com/result/?querychrd="
    urls = {
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
        (255, 255, 255): "A,C,Em,D"
    }
    url = base_url + urls.get(color_value, "C,F,G")
    print(f"url: {url}")
    response = requests.get(url)


    soup = BeautifulSoup(response.text, 'html.parser')
    time.sleep(10)
    #print(soup.prettify())  # This will print the full HTML structure of the page
    table = soup.find(id='song-result-table')
    print(f"table: {table}")

    data = []
    headers = [th.text.strip() for th in table.find_all('th')]

    for row in table.find_all('tr')[1:]:
        cells = [td.text.strip() for td in row.find_all('td')]
        data.append(cells)

    print(f"data: {data}")
    #print(soup.prettify())  # This will print the full HTML structure of the page

    df = pd.DataFrame(data, columns=headers)
    df.to_csv('table_data.csv', index=False)
    print("Table saved as 'table_data.csv'")
    return df

@app.route('/show_image/<filename>')
def show_image(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    color_thief = ColorThief(filepath)

    main_color = color_thief.get_color(quality=1)
    color_value = get_closest_color(main_color)
    color_name = get_color_name(color_value)

    # Fetch table data
    try:
        df = fetch_table_as_dataframe(color_value)
        print("DataFrame fetched successfully!")

        if not df.empty:
            random_row = df.sample().iloc[0]
            song = random_row['SONG']
            video = random_row['VID']
            print(f"SONG: {song}")
            print(f"VIDEO: {video}")
        else:
            song = "No songs found"
            video = "#"

    except Exception as e:
        print(f"An error occurred: {e}")
        song = "Error: No song found"
        video = "#"

    return render_template('processingimage.html', filename=filename, color_name=color_name, song_name=song,
                           video_name=video)

if __name__ == '__main__':
    app.run(debug=True)
