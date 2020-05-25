import random
import re
import time

import snoozingmail
import albumrecs.spotify.spotify as spotify


"""regex used to find spotify album link in message body of an email"""
ALBUM_LINK_RE = "https:\\/\\/open.spotify.com\\/album\\/.{22}"


class AlbumRecs:
    """Album recommendation manager class. Interfaces with
    gmail through snoozingmail to get recommendations from
    participants. Interfaces with spotify through spotipy to
    get a random album to add to the mix.
    """

    def __init__(self, gmail_credentials, group_name=None):
        self.album_recs = {}
        self.snoozin = snoozingmail.Snoozin(gmail_credentials)
        self.spotify = spotify.Spotify()

        if group_name:
            self.GROUP_NAME = group_name
        else:
            self.GROUP_NAME = ""

        random.seed(time.time())

    def _get_shuffled_participants(self):
        participants = []
        for participant in self.album_recs.keys():
            participants.append(participant)
        random.shuffle(participants)
        return participants

    def _get_shuffled_albums(self):
        albums = []
        for album in self.album_recs.values():
            albums.append(album)
        random.shuffle(albums)
        return albums

    def send(self):
        def create_html_message_body():
            def get_formatted_album(album):

                artist_names_str = ', '.join(album.artist_names)

                img_link = (
                    f"<a href='{album.link}'>"
                    f"<img src='{album.img_url}'"
                    f"alt='{album.name}"
                    f"style='width:{album.IMG_DIMEN}px;"
                    f"height:{album.IMG_DIMEN}px;"
                    "border:0;'>"
                    "</a>"
                )

                return (
                    f"<b>{album.name}</b> by {artist_names_str}<br>"
                    f"{img_link}<br>"
                    "<br>"
                )

            formatted_albums = ""
            for album in self._get_shuffled_albums():
                formatted_albums += get_formatted_album(album)

            return formatted_albums

        # Set who the email will be sent to
        to = ""
        for participant in self._get_shuffled_participants():
            to += "{}; ".format(participant)

        # Set the subject of the email
        subject = (
            "albumrecs by snoozin 'n {}"
        ).format(self.GROUP_NAME if self.GROUP_NAME != "" else "friends")

        # Create the body of the email formatted in html
        message_body = create_html_message_body()

        # Send the email
        self.snoozin.send(to, subject, message_body, html=True)

    def add_from_gmail(self):
        # Find matching albumrec emails
        group_search = ":{}".format(self.GROUP_NAME)
        query = (
            "subject:albumrec{} AND is:unread AND in:inbox "
        ).format(group_search if self.GROUP_NAME != "" else "")

        msg_ids = self.snoozin.get_matching_msgs(query)

        # Add the newest album rec from each sender
        for msg_id in msg_ids:
            sender = self.snoozin.get_sender(msg_id)
            if sender not in self.album_recs:
                # Mark message as read
                self.snoozin.remove_msg_labels(msg_id, ['UNREAD'])

                # Add the spotify link from the message body to the albums
                message_body = self.snoozin.get_msg_body(msg_id)
                if message_body:
                    album_link_re = re.search(ALBUM_LINK_RE, message_body)
                    if album_link_re is None:
                        error_msg = (
                            "Error: spotify album link not found for "
                            "message: {} from: {}"
                        ).format(msg_id, sender)
                        print(error_msg)
                    else:
                        # Add sender's album rec to the albums using
                        # the spotify album link that they sent
                        album = self.spotify.get_album_from_link(
                            album_link_re.group(0))
                        self.album_recs[sender] = album

    def add_snoozin_rec(self):
        sender = "snoozinforabruisin@gmail.com"
        self.album_recs[sender] = self.spotify.get_random_album()
