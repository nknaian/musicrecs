# musicrecs
A Gmail-powered Spotify music recommendation exchange platform with snoozin and friends

# setup
- Clone, create a python 3 venv and install the requirements
- See https://github.com/nknaian/snoozingmail for Gmail API setup
- See https://github.com/plamere/spotipy for the Spotify API setup

# usage
Run musicrecs as a module:
```bash
python -m musicrecs --gmail_creds credentials.json --group_name myfriends --music_type album
```
Possible music types are 'album' and 'track'.
