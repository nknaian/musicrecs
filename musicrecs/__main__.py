import argparse

from musicrecs.music_recs import MusicRecs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--gmail_creds', required=True,
                        help="Path to gmail credentials json file")
    parser.add_argument('-g', '--group_name', default="",
                        help="Name of the group to run albumrecs for")
    parser.add_argument('-m', '--music_type', default="album",
                        help="Type of music to recommend (album or track)")
    parser.add_argument('-r', '--snoozin_rec_type', default="random",
                        help="Method that snoozin uses to recommend music"
                             "(random or similar)")
    parser.add_argument('--confirm_send', action='store_true', default=False)

    return parser.parse_args()


def confirm_send(music_recs):
    """Dispaly the list of human participants that have been
    included in this round. And give user an option to confirm
    or deny that they want to continue.
    """
    human_participants = music_recs.get_human_musicrecs().keys()

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

    # Create music recs
    music_recs = MusicRecs(
        args.gmail_creds,
        args.group_name,
        args.music_type,
        args.snoozin_rec_type,
        "nickknaian@gmail.com")

    # Add music recs that have been recieved from gmail
    music_recs.add_from_gmail()

    # Add in snoozin's music pick
    music_recs.add_snoozin_rec()

    # Bail if something doesn't look right
    if args.confirm_send:
        if not confirm_send(music_recs):
            raise Exception("You've decided not to send these recs!")

    # Save the recs to the history data
    music_recs.save_musicrecs_to_history()

    # Send an email to organizer with info about musicrecs
    music_recs.send_musicrecs_info_to_organizer()

    # Get guesses form link from organizer
    music_recs.add_guess_form()

    # Send email to those who participated
    music_recs.send_participants_email()

except Exception:
    import traceback
    traceback.print_exc()
