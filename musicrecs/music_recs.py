import random
import re
import time
import copy
import json

import snoozingmail
import musicrecs.spotify.spotify as spotify
import musicrecs.random_words.random_words as random_words


"""Constants"""

"""regex used to find spotify music links in message body of an email"""
ALBUM_LINK_RE = "https:\\/\\/open.spotify.com\\/album\\/.{22}"
TRACK_LINK_RE = "https:\\/\\/open.spotify.com\\/track\\/.{22}"

SNOOZIN_EMAIL = "snoozinforabruisin@gmail.com"
SNOOZIN_CANNED_EMAIL = "snoozinforabruisin+canned.response@gmail.com"

DICTIONARY_FILE = "musicrecs/random_words/dictionary.txt"

SEARCH_TERM_WORD_COUNT = 2


class MusicRecs:
    """Music recommendation manager class. Interfaces with
    gmail through snoozingmail to get recommendations from
    participants. Interfaces with spotify through spotipy to
    get music to add to the mix.
    """

    def __init__(self,
                 gmail_credentials,
                 group_name,
                 music_type,
                 snoozin_rec_type,
                 organizer_email):
        # Variables
        self.music_recs = {}
        self.snoozin = snoozingmail.Snoozin(gmail_credentials)
        self.spotify = spotify.Spotify(music_type)
        self.guess_form_link = None

        # Constants
        self.GROUP_NAME = group_name
        self.MUSIC_TYPE = music_type
        self.SNOOZIN_REC_TYPE = snoozin_rec_type
        self.ORGANIZER_EMAIL = organizer_email

        # Assertions
        assert self.MUSIC_TYPE in ["album", "track"]
        assert self.SNOOZIN_REC_TYPE in ["random", "similar"]

        # Seed the random library with the current time
        random.seed(time.time())

    """Functions that send emails based on self.music_recs"""

    def send_participants_email(self):
        # Set who the email will be sent to
        to = ""
        for participant in self._get_shuffled_participants():
            to += "{}; ".format(participant)

        # Set the subject of the email
        subject = (
            "{}recs by snoozin 'n {}"
        ).format(self.MUSIC_TYPE,
                 self.GROUP_NAME if self.GROUP_NAME != "" else "friends")

        # Fill the message body with form url and the list of music formatted
        # in html
        if self.guess_form_link is not None:
            message_body = (f"Submit your guesses here: {self.guess_form_link}"
                            "<br><br>")
        else:
            message_body = ""
        message_body += "<br><br>".join(self.get_shuffled_music_list("html"))

        # Send the email
        self.snoozin.send(to, subject, message_body, html=True)

    def send_musicrecs_info_to_organizer(self):
        """Send email to organizer with info about the musicrecs"""
        # Get the snoozin rec
        snoozin_rec = self.music_recs[SNOOZIN_EMAIL]

        # Make a dict to hold snoozin rec info, add rec t
        snoozin_rec_info = {}

        # Add rec type and search term (will be None if rec type wasn't
        # random)
        snoozin_rec_info["rec_type"] = self.SNOOZIN_REC_TYPE
        snoozin_rec_info["search_term"] = snoozin_rec.search_term

        # make dictionary to hold musicrecs info
        musicrecs_info = {}

        # Populate musicrecs dictionary with snoozin rec info and submission
        # info
        musicrecs_info["snoozin_rec_info"] = snoozin_rec_info
        musicrecs_info["submission_info"] = self._get_submission_info("text")

        # Send the musicrecs_info in an email to the organizer
        self.snoozin.send(
            self.ORGANIZER_EMAIL,
            f"musicrecs info {self.GROUP_NAME} {self.MUSIC_TYPE}",
            json.dumps(musicrecs_info))

    """Functions to add information to self.music_recs"""

    def add_from_gmail(self):
        # Mark all canned messages as read so they don't
        # interfere with adding the recs
        self._mark_canned_messages_read()

        # Find matching emails
        msg_ids = self._matching_emails()

        # Add the newest rec from each sender
        for msg_id in msg_ids:
            sender = self.snoozin.get_sender(msg_id)
            if sender not in self.music_recs:
                # Mark message as read
                self.snoozin.remove_msg_labels(msg_id, ['UNREAD'])

                # Add music from the message body to the music_recs
                message_body = self.snoozin.get_msg_body(msg_id)
                if message_body:
                    self._add_music_from_message(sender, message_body)

    def add_guess_form(self):
        """Poll for email containing the guess form. Once it is
        received, add the link to the guess form from the email
        """
        print("waiting for guess form email...")
        while True:
            msg_ids = self.snoozin.get_matching_msgs(
                (f"is:unread AND in:inbox AND subject:{self.GROUP_NAME} "
                 f"{self.MUSIC_TYPE} guesses form")
            )
            if len(msg_ids):
                # Use the latest guess form email
                latest_guess_form_msg = msg_ids[0]

                # Mark the guesses form email as read
                self.snoozin.remove_msg_labels(latest_guess_form_msg,
                                               ['UNREAD'])

                # Get the guess form link from the email
                self.guess_form_link = self.snoozin.get_msg_body(
                    latest_guess_form_msg)
                break

            time.sleep(5)
        print("guess form email received.")

    def add_snoozin_rec(self):
        music = None
        if self.SNOOZIN_REC_TYPE == "random":
            rw_gen = random_words.RandomWords(DICTIONARY_FILE)

            while music is None:
                search_term = " ".join(
                    rw_gen.get_random_words(SEARCH_TERM_WORD_COUNT)
                )
                music = self.spotify.search_for_music(search_term)

        elif self.SNOOZIN_REC_TYPE == "similar":
            music_recs_list = list(self.music_recs.values())
            music = self.spotify.recommend_music(music_recs_list)

        self.music_recs[SNOOZIN_EMAIL] = music

    """Getters"""

    def get_shuffled_participants(self):
        return self._get_shuffled_participants()

    def get_shuffled_music_list(self, fmt_type):
        return [
            music.format(fmt_type) for music in self._get_shuffled_music()
        ]

    def get_human_participants(self):
        human_music_recs = copy.deepcopy(self.music_recs)
        human_music_recs.pop(
            SNOOZIN_EMAIL
        )
        return list(human_music_recs.keys())

    """Private Functions"""

    def _get_shuffled_participants(self):
        participants = []
        for participant in self.music_recs.keys():
            participants.append(participant)
        random.shuffle(participants)
        return participants

    def _get_shuffled_music(self):
        music_list = []
        for music in self.music_recs.values():
            music_list.append(music)
        random.shuffle(music_list)
        return music_list

    def _add_music_from_message(self, sender, message_body):
        if self.MUSIC_TYPE == "album":
            link_re = re.search(ALBUM_LINK_RE, message_body)
        elif self.MUSIC_TYPE == "track":
            link_re = re.search(TRACK_LINK_RE, message_body)
        else:
            raise Exception(f"Unknown music type {self.MUSIC_TYPE}")

        if link_re is None:
            raise Exception(
                "Spotify {} link not found for "
                "from {}".format(self.MUSIC_TYPE, sender)
            )
        else:
            # Add sender's music to recs using
            # the link that they sent
            music = self.spotify.get_music_from_link(
                link_re.group(0))
            self.music_recs[sender] = music

    def _mark_canned_messages_read(self):
        canned_unread_messages = self.snoozin.get_matching_msgs(
            f"from:{SNOOZIN_CANNED_EMAIL} AND is:unread"
        )
        for msg_id in canned_unread_messages:
            self.snoozin.remove_msg_labels(msg_id, ['UNREAD'])

    def _matching_emails(self):
        matching_emails = []

        # Get unread inbox emails which match the subject filter
        query = f"is:unread AND in:inbox AND subject:{self.MUSIC_TYPE}rec"

        if self.GROUP_NAME != "":
            query += f":{self.GROUP_NAME}"

        matching_emails.extend(self.snoozin.get_matching_msgs(query))

        # Legacy support for shityo
        if self.GROUP_NAME == "someppl" and self.MUSIC_TYPE == "album":
            query = ("is:unread AND in:inbox AND subject:"
                     f"{self.MUSIC_TYPE}rec:shityo")
            matching_emails.extend(self.snoozin.get_matching_msgs(query))

        return matching_emails

    def _get_submission_info(self, fmt_type):
        """Returns a dictionary showing what particapant submitted what
        music (formatted)
        """
        return {
            participant: music.format(fmt_type)
            for (participant, music) in self.music_recs.items()
        }
