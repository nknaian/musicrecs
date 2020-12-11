import random
from flask import render_template

import musicrecs.spotify.spotify as spotify
import musicrecs.random_words.random_words as random_words

from musicrecs import app
from musicrecs import db
from musicrecs.sql_models import User, Submission, Round, RecGroup

'''ROUTES'''
# TODO routes for login...and maybe hiding/restricting things
# based on user group membership

@app.route('/')
@app.route('/index')
def index():
    # Button to add a new group
    # List / navigation of groups
    # Ability to go to group pages
    # possibly there is a button to 'join' a group?
    return render_template('index.html')

@app.route('/about')
def about():
    # Description of site
    return render_template('about.html')

# @app.route('/<str:group_name>')
# def group_page(group_name):
#     # Description of group
#     # Button to submit track or album
#     # show who's "in" for next track and album rounds
#     # Navigator to take you to page for rounds
#     # Button to progress album/track rounds (only for group admin)
#     pass

# @app.route('/<str:group_name>/<int:round_num>')
# def submit_music(group_name, round_num):
#     # Display the music for this round....different info based upon
#     # whether past, current or next round
#     # Also, probably navigator bar should still be there to switch between rounds
#     pass

# @app.route('/<str:group_name>/submit_music')
# def submit_music():
#     # Form to create a new group (possibly this needs approval by me?)
#     pass

# @app.route('/create_group')
# def create_group():
#     # Form to create a new group (possibly this needs approval by me?)
#     pass


'''PRIVATE FUNCTIONS'''

def _get_snoozin_rec(spotify_iface, rec_type):
    music = None
    if rec_type == "random":
        rw_gen = random_words.RandomWords()

        while music is None:
            search_term = " ".join(
                rw_gen.get_random_words(random.randint(1, 2))
            )
            music = spotify_iface.search_for_music(search_term)

    # TODO: get music recs from database probably
    # elif rec_type == "similar":
    #     music_recs_list = list(music_recs.values())
    #     music = spotify_iface.recommend_music(music_recs_list)

    return music