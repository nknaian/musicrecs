import datetime
import random
import re
import time

import snoozingmail
import albumrecs.spotify.random_spotify as random_spotify


"""Constants"""

ALBUM_LINK_RE = ("(https:\/\/open.spotify.com\/album\/.+?(?=\?si=))|"
                 "(https:\/\/open.spotify.com\/album\/[^ \n]*)")


"""AlbumRecs"""

class AlbumRecs:
    def __init__(self, gmail_credentials):
        self.album_recs = {}
        self.snoozin = snoozingmail.Snoozin(gmail_credentials)
        self.random_spotify = random_spotify.RandomSpotify()
        random.seed(time.time())
        self.album_link_re = ALBUM_LINK_RE

    def get_shuffled_participants(self):
        participants = []
        for participant in self.album_recs.keys():
            participants.append(participant)
        random.shuffle(participants)
        return participants

    def get_shuffled_album_recs(self):
        recs = []
        for rec in self.album_recs.values():
            recs.append(rec)
        random.shuffle(recs)
        return recs

    def send(self):
        to = ""
        for participant in self.get_shuffled_participants():
            to += "{}; ".format(participant)
        subject = "Album recs for week of {}".format(datetime.date.today())
        message_text = ""
        for i, rec in enumerate(self.get_shuffled_album_recs()):
            message_text += "Album Rec {}:\n{}\n".format(i+1, rec)

        self.snoozin.send(to, subject, message_text)

    def add_from_gmail(self):
        # Find matching albumrec emails within the last 7 days
        query = "subject:albumrec AND is:unread AND in:inbox AND newer_than:7d"
        msg_ids = self.snoozin.get_matching_msgs(query)

        # Add the newest album rec from each sender
        for msg_id in msg_ids:
            sender = self.snoozin.get_sender(msg_id)
            if sender not in self.album_recs:
                # Mark message as read
                self.snoozin.mark_msg_read(msg_id)

                # Add the spotify link from the message body to the album_recs 
                message_body = self.snoozin.get_msg_body(msg_id)
                if message_body:
                    album_link_re = re.search(ALBUM_LINK_RE, message_body)
                    if album_link_re is None:
                        error_msg = ("Error: spotify album link not found for "
                                     "message: {} from: {}".format(msg_id, sender)) 
                        print(error_msg)
                    else:
                        # Add sender's album_link to the album_recs
                        self.album_recs[sender] = album_link_re.group(0)

    def add_snoozin_rec(self):
        sender = "snoozinforabruisin@gmail.com"
        self.album_recs[sender] = self.random_spotify.get_random_album()

