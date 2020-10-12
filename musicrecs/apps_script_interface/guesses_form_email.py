def send_guesses_form_email(music_recs):
    """Sends email to nickknaian@gmail.com with formatted
    information such that Google Apps Script
    https://script.google.com/home/projects/1EtzRjZJ2cVxiiJeyfkuQamG0qgA1h71K4LtIF0m7xcTMnAjry-MICgRX
    can create a form for users to guess

    Args:
        music_recs: The music_recs di
    """

    to = "nickknaian@gmail.com"
    subject = (
        f"{music_recs.GROUP_NAME} {music_recs.MUSIC_TYPE}recs "
        "guesses form"
    )
    participants = ",".join(music_recs.get_all_participants())
    music_list = "\n".join(music_recs.get_music_list("text"))
    message_body = f"{participants}\n{music_list}"

    music_recs.snoozin.send(to, subject, message_body)
