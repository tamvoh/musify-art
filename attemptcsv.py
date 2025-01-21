# imports

import os
import math
import time
import random
import requests
import pandas as pd
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
from colorthief import ColorThief
from PIL import Image


app = Flask(__name__)
app.secret_key = "W!red_were_the_eyes_of_@_horse_on_a_jet_pilot"

# RGB values and rainbow colors
rainbow_colors = [
    (255, 0, 0), (242, 140, 40), (251, 211, 36), (147, 187, 31),
    (100,149,237), (75, 0, 130), (148, 0, 211), (255, 141, 161), (0, 0, 0), (255, 255, 255)
]

# creating an uploads folder for user to upload image
UPLOAD_FOLDER = "static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# checking if file is image
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# homepage
@app.route('/')
def homepage():
    return render_template('homepage.html')

# saving image that user uploads --> if it isn't an image it will rreturn back to home
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    try:
        if file and allowed_file(file.filename):
            if file.mode == 'RGBA':
                # new image with solid bg
                background = Image.new('RGB', file.size, (255, 255, 255))  # white background
                # paste original image on bg
                background.paste(file, mask=file.split()[3])  # Alpha channel is index 3
                file = background
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('show_image', filename=filename))
        else:
            flash("Invalid file format. Please upload a valid image.", category="error")
            return render_template('homepage.html')  # redirect to the upload page
    except Exception as e:
        flash("Please upload a valid image! Extremely small images do not work.", category="error")
    return render_template('homepage.html')

# getting closest color
def get_closest_color(main_color):
    """
        In order to find the distance between 2 points,
        the pythagorean theorem can be used.
        pythagorean_theorem = sqrt(distance1^2 + distance2^2)
        However, rgb is 3-dimensional.
    """
    values = [float('inf')] # instead of using 10000000 the float('inf') is basically infinity
    closest_color = None # setting original value as None
    r_value, g_value, b_value = main_color # getting rgb of main color
    for color in rainbow_colors:
        r, g, b = color # getting rgb of raimbow color
        distance = math.sqrt((r - r_value) ** 2 + (g - g_value) ** 2 + (b - b_value) ** 2) # 3-dimensional distance calculation
        if distance < values[-1]:
            values.append(distance)
            closest_color = color
    print(closest_color)
    return closest_color

def get_color_name(color_value):
    # mapping out color rgb codes to names
    color_names = {
        (255, 0, 0): "red",
        (242, 140, 40): "orange",
        (251, 211, 36): "yellow",
        (147, 187, 31): "green",
        # (8, 143, 143): "blue-green",
        (100,149,237): "blue",
        (75, 0, 130): "indigo",
        (148, 0, 211): "violet",
        (255, 141, 161): "pink",
        (0, 0, 0): "black",
        (255, 255, 255): "white"
    }
    print(color_names.get(color_value))
    return color_names.get(color_value, "unknown")



@app.route('/show_image/<filename>')
def show_image(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    color_thief = ColorThief(filepath)

    main_color = color_thief.get_color(quality=1) # retrieving main color using colorthief
    color_value = get_closest_color(main_color)
    print(color_value)
    color_name = get_color_name(color_value)

    base_url = "song-table-url-"
    # mapping out rgb to what to add to file name
    urls = {
        (255, 0, 0): "red",
        (242, 140, 40): "orange",
        (251, 211, 36): "yellow",
        (147, 187, 31): "green",
        # (8, 143, 143): "blue-green",
        (100,149,237): "blue",
        (75, 0, 130): "indigo",
        (148, 0, 211): "violet",
        (255, 141, 161): "pink",
        (0, 0, 0): "black",
        (255, 255, 255): "white"
    }

    print(urls.get(color_value))
    file_path = base_url + urls.get(color_value) + ".csv"
    print(f"color_value_thing: {file_path}")
    data = pd.read_csv(file_path)
    print(data.head())
    random_song = data.sample(n=1)  # .sample(n=1) to pick one random row

    # Display the random song
    song = random_song['SONG'].iloc[0] # just using that one random row to get song + artist
    artist = random_song['ARTIST'].iloc[0]
    print(song, artist)
    video_link = "https://www.youtube.com/results?search_query=" + "+" + song + "+" + artist  # original thingy was just a yt search query



    return render_template('processingimage.html', filename=filename, color_name=color_name, song_name=song, artist_name=artist, video=video_link)

if __name__ == '__main__':
    app.run(debug=True)
