import argparse

from musicrecs.music_recs import MusicRecs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--gmail_creds', required=True,
                        help="Path to gmail credentials json file")
    parser.add_argument('-g', '--group_name', default="",
                        help="Name of the group to run albumrecs for")
    parser.add_argument('-t', '--music_type', default="album",
                        help="Type of music to recommend (album or track)")

    return parser.parse_args()


"""Main"""

# Parse args
args = parse_args()

# Create album recs
album_recs = MusicRecs(args.gmail_creds, args.group_name, args.music_type)

# Add album recs that have been recieved from gmail
album_recs.add_from_gmail()

# Add in snoozin's album pick
album_recs.add_snoozin_rec()

# Send the recs to those who participated
album_recs.send()
