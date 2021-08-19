# Anki Stats
This is a python package to make it easier to analyse an anki database. Directly querying the database has a bit of a learning curve (especially if you don't know SQL!) due to the obscure names of columns, and the way some of the data is structured within entries; and even if you do know how to do it its still quite tedious. Instead, this package converts your database straight to pandas dataframes, with very readable column names, and some preprocessing of the entries so you don't have to!

So far you can get each of the tables in the database, but you will have to combine the tables yourself.

### Roadmap
- Add more predictive features to combined tables
- Functions to return simple analytical plots
- ML model to accurately (hopefully) predict probability of recall, allowing ease to be more objectively assigned

Anyone is welcome to make a PR or suggest anything specific to add :)

### Dependencies
- pandas

## Install
```
pip install ankistats
```
## Use
Copy your anki database (`collection.anki2`) from its folder.
- Mac: `/Users/<user_name>/Library/Application Support/Anki2/<profile_name>`
- Windows: `%appdata%/anki2/<profile_name>`
- Linux: ?
```py
import ankistats as ak

# create database instance by inputting filepath to collection.anki2
db = ak.read('collection.anki2')

# assign a table from the database to df
df = db.tbl_cards()
```
