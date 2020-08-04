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
    parser.add_argument('-m', '--manual_run', default=True)

    return parser.parse_args()


def confirm_email(music_recs):
    human_participants = music_recs.get_human_participants()

    print(
        "musicrecs about to be sent to "
        f"{len(human_participants)} participants: "
        f"{', '.join(human_participants)}"
        "\n\nAre you sure you want to send?"
    )

    user_resp = ""
    while user_resp not in ["snoozinsure", "snoozinope"]:
        user_resp = input(
            "\nEnter 'snoozinsure' if yes and "
            "'snoozinope' if no:  "
        )

    if user_resp == "snoozinsure":
        return True
    elif user_resp == "snoozinope":
        return False
    else:
        raise Exception("Unknown response")


"""Main"""

try:
    # Parse args
    args = parse_args()

    # Create album recs
    music_recs = MusicRecs(args.gmail_creds, args.group_name, args.music_type)

    # Add in snoozin's album pick
    music_recs.add_snoozin_rec()

    # Add album recs that have been recieved from gmail
    music_recs.add_from_gmail()

    # Send the recs to those who participated
    if args.manual_run:
        if confirm_email(music_recs):
            music_recs.send()
        else:
            print("You've decided not to send these recs")
    else:
        music_recs.send()

except Exception:
    import traceback
    traceback.print_exc()
