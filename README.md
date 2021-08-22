# Anki Stats
This is a python package to make it easier to analyse an anki database. Directly querying the database has a bit of a learning curve (especially if you don't know SQL!) due to the obscure names of columns, and the way some of the data is structured within entries; and even if you do know how to do it it's still quite tedious. Instead, this package converts your database straight to pandas dataframes, with very readable column names, and some preprocessing of the entries so you don't have to!

- Call single tables
- Call combined tables with additional features
- Make plots with a single line of code

## Install
```shell
pip install ankistats
```
#### Dependencies
- pandas
- matplotlib

## Use
Copy your anki database (`collection.anki2`) from its folder.
- Mac: `/Users/<user_name>/Library/Application Support/Anki2/<profile_name>`
- Windows: `%appdata%/anki2/<profile_name>`
- Linux: ?
```py
import ankistats as ak

# create database instance by inputting a filepath to collection.anki2
db = ak.read('collection.anki2')

# assign a table from the database to df
df = db.tbl_cards()

# premade plot of the adjusted ease vs. field length (default is field 2; usually answer field)
db.plot_adjusted_ease_vs_field_length(note_types=['Science (Basic)'])
```
<img width=600 src="https://i.postimg.cc/0yWgFvyW/plot.png">

<br>

### ~ Info on all available functions at [Documentation.md](./Documentation.md) ~

<br>

## Other Anki Databases
(may need to import it into latest version of anki to auto-update the database structure before using it to analyse)

- https://github.com/jpromanonet/myAnkiDataBases
- https://github.com/hochanh/r-anki
- add to this list if you know more !

## Roadmap
- Add more features to tables to aid analysis
  - Feautures added thus far:
    - Frequency of word in note field with the lowest frequency
    - Character count (not including html)
    - Word count (not including html)
    - Whether note field has an image or not
- More plots
- ML model to accurately (hopefully) predict probability of recall, allowing ease to be more objectively assigned

~ Anyone is welcome to submit a PR or suggest anything specific to add :) ~

## Credits
- [Structure of anki database](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure) (slightly outdated, but still super useful)
- [English word frequency data](https://www.kaggle.com/rtatman/english-word-frequency)
