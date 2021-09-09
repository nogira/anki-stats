<h1 align='center'>
    Anki Stats 📊
</h1>

This is a python package to make it easier to analyse an [anki](https://apps.ankiweb.net/) database.
- SQLite database w/ obscure names → pandas dataframes, w/ intuitive names
  - Get single tables
  - Get combined tables with additional features
- Make plots with a single line of code
- Simulate future reviews

~ Anyone is welcome to submit a PR or suggest anything specific to add :) ~

## Install
```shell
pip install ankistats
```
<details><summary><b>Dependencies</b></summary>
  <ul>
    <li>pandas</li>
    <li>seaborn</li>
  </ul>
</details>

## Use

<details><summary>Copy your anki database (<code>collection.anki2</code>) from its folder.</summary>
  <ul>
    <li>Mac: <code>~/Library/Application Support/Anki2/&lt;profile_name&gt;</code></li>
    <li>Windows: <code>%appdata%/Anki2/&lt;profile_name&gt;</code></li>
    <li>Linux: <code>~/.local/share/Anki2/&lt;profile_name&gt;</code></li>
  </ul>
</details>

```py
import ankistats as ak

# save filepath to collection.anki2
ak.db_path('collection.anki2')

# assign a table from the database to df
df = ak.tbl_cards()

# plot of the adjusted ease vs. field length (default is field 2; usually answer field)
ak.plot_adjusted_ease_vs_field_length(note_types=['Science (Basic)'])
```
<details><summary>Plot Image</summary>
  <img width=600 src="https://i.postimg.cc/4y9VhWtG/plot1.png">
</details>

<br>

### ~ Info on all available functions at [Documentation.md](./Documentation.md) ~

<br>

## Other Anki Databases
(may need to import it into latest version of anki to auto-update the database structure before using it to analyse)

- https://github.com/jpromanonet/myAnkiDataBases
- https://github.com/hochanh/r-anki
- add to this list if you know more !

## Credits
- [Structure of anki database](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure) (slightly outdated, but still super useful)
- [English word frequency data](https://www.kaggle.com/rtatman/english-word-frequency)
