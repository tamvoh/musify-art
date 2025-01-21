# Imports
import io
from colorthief import ColorThief
import math
import random
import pandas as pd
import os
from flask import Flask, request, render_template, redirect, url_for, flash, session
from requests_html import AsyncHTMLSession
import asyncio
import nest_asyncio

nest_asyncio.apply()

# Flask App Configuration
app = Flask(__name__)
app.secret_key = "W!red_were_the_eyes_of_@_horse_on_a_jet_pilot"
UPLOAD_FOLDER = "static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# RGB Colors and Rainbow Colors
rainbow_colors = [
    (255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0),
    (48, 213, 200), (0, 0, 255), (75, 0, 130), (148, 0, 211),
    (255, 141, 161), (0, 0, 0), (255, 255, 255)
]
color_names = [
    "red", "orange", "yellow", "green", "turquoise",
    "blue", "indigo", "violet", "pink", "black", "white"
]

# Helper Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash("No file selected!")
        return redirect(request.url)

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return redirect(url_for('show_image', filename=filename))

    flash("Invalid file type! Only PNG, JPG, or JPEG allowed.")
    return redirect(request.url)

@app.route('/show_image/<filename>')
def show_image(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        flash("File not found!")
        return redirect(url_for('homepage'))

    color_thief = ColorThief(filepath)
    main_color = color_thief.get_color(quality=1)

    # Color Matching Logic
    values = [float('inf')]
    colors = []
    r_value, g_value, b_value = main_color

    for color in rainbow_colors:
        r, g, b = color
        distance = math.sqrt((r - r_value) ** 2 + (g - g_value) ** 2 + (b - b_value) ** 2)
        if distance < values[-1]:
            values.append(distance)
            colors.append(color)

    color_value = colors[-1]
    color_name = color_names[rainbow_colors.index(color_value)]

    # Find Songs Based on Color
    async def fetch_songs_for_color():
        session = AsyncHTMLSession()
        base_url = "https://www.chordgenome.com/result/?querychrd="

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
        await response.html.arender(timeout=30, sleep=5)
        return response.html.find('#song-result-table', first=True)

    # Load Songs Data
    try:
        songs_table_url = pd.read_csv("../songs_table_with_vids.csv")
        genre_list = songs_table_url["GENRE"].unique().tolist()
        random.shuffle(genre_list)
    except Exception as e:
        flash(f"Error loading songs database: {e}")
        genre_list = []

    session['filename'] = filename
    session['color_name'] = color_name
    session['genre_list'] = genre_list
    session['songs_table_url'] = songs_table_url.to_csv(index=False)

    return render_template(
        'processingimage.html',
        filename=filename,
        color_name=color_name,
        genres=genre_list
    )

@app.route('/select_genre', methods=['POST'])
def select_genre():
    selected_genre = request.form.get('genre', '').strip().lower()
    csv_data = session.get('songs_table_url', None)

    if not csv_data:
        flash("Songs database is not available. Please start over.")
        return redirect(url_for('homepage'))

    songs_table_url = pd.read_csv(io.StringIO(csv_data))
    songs_in_genre = songs_table_url[songs_table_url['GENRE'].str.strip().str.lower() == selected_genre]

    if songs_in_genre.empty:
        flash(f"No songs found for the genre: {selected_genre.capitalize()}")
        return redirect(url_for('show_image', filename=session.get('filename', '')))

    random_song_entry = songs_in_genre.sample(n=1).iloc[0]
    random_song = random_song_entry['SONG']
    random_vid = random_song_entry['VID']

    return render_template(
        'processingimage.html',
        filename=session.get('filename', ''),
        color_name=session.get('color_name', ''),
        genres=session.get('genre_list', []),
        song_name=random_song,
        video_name=random_vid
    )

if __name__ == '__main__':
    app.run(debug=True)
