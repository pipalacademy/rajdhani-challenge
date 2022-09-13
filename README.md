# rajdhani-challenge

Challenge to build Rajdhani - a webapp to search for trains in India and book a ticket.

## Usage

Step 1: setup the database

```
$ sqlite3 rajdhani.db < schema.sql
```

Step 2: Create a new app

```
$ python db.py alice
Created new app alice
```

Step 3: Run the app

```
$ python app.py
...
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## Updating the status of a site

Send a post request to the deploy endpoint to update the status of a site.

```
$ curl -X POST http://localhost:5000/<app-name>/deploy
```
