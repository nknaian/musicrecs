# musicrecs
A Spotify-powered music recommendation exchange platform with snoozin 'n friends

# Running locally
## Requirements
- Linux
- python3

## Setup
- Make a spotify developer app through https://developer.spotify.com/
- Create a python3 virtual environment
- Install required packages with `pip install -r requirement.txt`
- install sqlite with `apt-get install sqlite`
- Create an sqlite database: `sqlite3 databasename.db`
- Create a flask 'secret key':
    ```python
    import secrets
    print(secrets.token_urlsafe(16))
    ```
- Set environment variables:
    ```bash
    export SPOTIPY_CLIENT_ID="insert-spotify-client-id-here"
    export SPOTIPY_CLIENT_SECRET="insert-spotify-client-secret-here"
    export SQLALCHEMY_DATABASE_URI="sqlite:////insert/database/file/path.db"
    export FLASK_SECRET_KEY="insert-your-secret-key"
    export FLASK_APP=musicrecs
    export FLASK_ENV=development
    ```

# Run
- Run `flask run`
- Open "localhost:5000" in your browser
