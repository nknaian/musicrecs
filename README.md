# musicrecs
A Spotify-powered music recommendation game with snoozin 'n friends

# Running locally
## Requirements
- python3
- sqlite3 (ex Ubuntu: `apt-get install sqlite3`)

## Setup
- Make a spotify developer app through "https://developer.spotify.com/dashboard"
    - note the client id and client secret for your new app
- Create a python3 virtual environment `python3 -m venv name-of-venv`
- Activate your virtual environment `source path-to-venv/bin/activate`
- Install required packages with `pip install -r requirements.txt`
- Create a flask 'secret key':
    ```python
    import secrets
    print(secrets.token_urlsafe(16))
    ```
- Create a file named *.env* at the root of your repo, and put in the following export commands
  (replacing placeholder values with your own values):
    ```bash
    export SPOTIPY_CLIENT_ID="insert-spotify-client-id-here"
    export SPOTIPY_CLIENT_SECRET="insert-spotify-client-secret-here"
    export SPOTIPY_REDIRECT_URI="http://localhost:5000/sp_auth_complete"
    export SQLALCHEMY_DATABASE_URI="sqlite:////insert/database/file/path.db"
    export FLASK_SECRET_KEY="insert-your-secret-key"
    export FLASK_APP=musicrecs
    export FLASK_ENV=development
    ```
- **note**: The sqlite database will be created at the path you specify upon the first run of the site.

# Run
## flask localhost
- Activate your virtual environment `source path-to-venv/bin/activate`
- From the top level musicrecs directory, run: `flask run`
- Open "localhost:5000" in your browser

### Using ngrok
ngrok is a tool that creates a tunnel to expose the local flask application
to the public internet. This can be useful for tasks such as mobile testing.

To use ngrok with musicrecs, add `export USE_NGROK=True` to your .env file.
The public url that ngrok creates will be printed to the console upon starting
flask, and it will be available within the application through the "PUBLIC_URL"
entry in the `app.config`.

## unit tests
- Activate your virtual environment `source path-to-venv/bin/activate`
- Run: `python -m unittest`

## syntax and style
- Activate your virtual environment `source path-to-venv/bin/activate`
- Run: `flake8`
