import argparse

from albumrecs.album_recs import AlbumRecs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--gmail_creds', required=True,
                        help="Path to gmail credentials json file")
    parser.add_argument('-g', '--group_name',
                        help="Name of the group to run albumrecs for")

    return parser.parse_args()


"""Main"""

# Parse args
args = parse_args()

# Create album recs
if args.group_name:
    album_recs = AlbumRecs(args.gmail_creds, args.group_name)
else:
    album_recs = AlbumRecs(args.gmail_creds)

# Add album recs that have been recieved from gmail
album_recs.add_from_gmail()

# Add in snoozin's album pick
album_recs.add_snoozin_rec()

# Send the recs to those who participated
album_recs.send()
