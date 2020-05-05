import random
import re
import time
import schedule

from spotify.random_music import get_random_album

### Serving Function ###

class AlbumRecs:
    def __init__(self, gmail_iface):
        self.gmail_iface = gmail_iface
        self.album_recs = {}
        random.seed(time.time())
        self.END_DELIMS = '(enjoy \|)([—–-]|[—–-][—–-])(\|)'

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

        self.gmail_iface.send(to, subject, message_text)

    def add_from_gmail(self):
        # Find matching albumrec emails within the last 7 days
        matches = self.gmail_iface.get_matches("albumrec", 7)

        # Add the newest album rec from each sender
        for match in matches:
            sender = self.gmail_iface.get_sender(match)
            if sender not in self.album_recs:
                message_body = self.gmail_iface.read_message(match)
                if message_body:
                     # Search for end delimiter in message body using regex
                    end_delim = re.search(self.END_DELIMS, message_body, flags=re.IGNORECASE)
                    if end_delim is None:
                        print("Error: bad formatting, end delimiter not found")
                    else:
                        # Only get part of message before end delimiter
                        end_delim_str = end_delim.group(0)
                        rec = message_body.split(end_delim_str, maxsplit=1)[0]
                        rec_without_si = rec.split('?si=', maxsplit=1)[0]
                        self.album_recs[sender] = rec_without_si
    
    def add_snoozin_rec(self, rec):
        self.album_recs["snoozinforabruisin@gmail.com"] = rec


### Serving Function ###

def serve_album_recs():
    # Create gmail interface
    gmail_iface = Snoozin()

    # Create album recs
    album_recs = AlbumRecs(gmail_iface) 

    # Add album recs that have been recieved from gmail
    album_recs.add_from_gmail()

    # Add in snoozin's album pick
    album_recs.add_snoozin_rec(get_random_album())

    # Send the recs to those who participated
    album_recs.send()

### Main ###

def main():
    schedule.every().sunday.at("20:00").do(serve_album_recs)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    main()