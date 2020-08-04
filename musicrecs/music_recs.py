import random
import re
import time
import copy

import snoozingmail
import musicrecs.spotify.spotify as spotify


"""regex used to find spotify music links in message body of an email"""
ALBUM_LINK_RE = "https:\\/\\/open.spotify.com\\/album\\/.{22}"
TRACK_LINK_RE = "https:\\/\\/open.spotify.com\\/track\\/.{22}"


class MusicRecs:
    """Music recommendation manager class. Interfaces with
    gmail through snoozingmail to get recommendations from
    participants. Interfaces with spotify through spotipy to
    get random music to add to the mix.
    """

    def __init__(self, gmail_credentials, group_name, music_type):
        self.music_recs = {}
        self.snoozin = snoozingmail.Snoozin(gmail_credentials)
        self.spotify = spotify.Spotify(music_type)
        self.GROUP_NAME = group_name
        self.MUSIC_TYPE = music_type

        assert self.MUSIC_TYPE in ["album", "track"]

        random.seed(time.time())

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

    def _create_html_message_body(self):
        def get_formatted_music(music):

            artist_names_str = ', '.join(music.artist_names)

            img_link = (
                f"<a href='{music.link}'>"
                f"<img src='{music.img_url}'"
                f"alt='{music.name}"
                f"style='width:{music.IMG_DIMEN}px;"
                f"height:{music.IMG_DIMEN}px;"
                "border:0;'>"
                "</a>"
            )

            return (
                f"<b>{music.name}</b> by {artist_names_str}<br>"
                f"{img_link}<br>"
                "<br>"
            )

        formatted_music = ""
        for music in self._get_shuffled_music():
            formatted_music += get_formatted_music(music)

        return formatted_music

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

    def send(self):
        # Set who the email will be sent to
        to = ""
        for participant in self._get_shuffled_participants():
            to += "{}; ".format(participant)

        # Set the subject of the email
        subject = (
            "{}recs by snoozin 'n {}"
        ).format(self.MUSIC_TYPE,
                 self.GROUP_NAME if self.GROUP_NAME != "" else "friends")

        # Create the body of the email formatted in html
        message_body = self._create_html_message_body()

        # Send the email
        self.snoozin.send(to, subject, message_body, html=True)

        # Send email to snoozin with search term used for the random search
        snoozin_rec = self.music_recs["snoozinforabruisin@gmail.com"]
        self.snoozin.send(
            "snoozinforabruisin@gmail.com",
            f"search term {self.GROUP_NAME} {self.MUSIC_TYPE}",
            f"The search term used was:\n\n{snoozin_rec.search_term}")

    def add_from_gmail(self):
        # Find matching emails
        group_search = ":{}".format(self.GROUP_NAME)
        query = (
            "subject:{}rec{} AND is:unread AND in:inbox "
        ).format(self.MUSIC_TYPE,
                 group_search if self.GROUP_NAME != "" else "")

        msg_ids = self.snoozin.get_matching_msgs(query)

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

    def add_snoozin_rec(self):
        sender = "snoozinforabruisin@gmail.com"
        self.music_recs[sender] = self.spotify.get_random_music()

    def get_human_participants(self):
        human_music_recs = copy.deepcopy(self.music_recs)
        human_music_recs.pop(
            "snoozinforabruisin@gmail.com"
        )
        return list(human_music_recs.keys())
