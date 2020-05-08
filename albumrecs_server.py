import argparse
import time
import schedule

from albumrecs.album_recs import AlbumRecs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gmail_creds', required=True,
                        help="Path to gmail credentials json file")
    return parser.parse_args()

def serve(album_recs):
    # Add album recs that have been recieved from gmail
    album_recs.add_from_gmail()

    # Add in snoozin's album pick
    album_recs.add_snoozin_rec()

    # Send the recs to those who participated
    album_recs.send()


def main():
    # Parse args
    args = parse_args()

    # Create album recs
    album_recs = AlbumRecs(args.gmail_creds)
    schedule.every().sunday.at("20:00").do(serve, album_recs)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    main()
