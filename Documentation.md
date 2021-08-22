# Documentation

<br>

> ⚠️ **Note**: this is incomplete

<br>

```py
import ankistats as ak
db = ak.read('collection.anki2')
```

## Single Tables Direct from Database
```py
db.tbl_cards()
```
- ```py
  # Columns
  
  'Card_ID'
  'Note_ID'
  'Deck_ID'
  'Card_Ordinal'
  'Card_Time_Last_Modified'
  'Card_Type'
  'Card_Queue'
  'Card_Due'
  'Card_Current_Interval_In_Minutes'
  'Card_Ease_Factor_As_Percentage'
  'Card_Total_Reviews_Including_Lapses'
  'Card_Total_Lapses'
  'Filtered_Card_Original_Due'
  'Filtered_Card_Deck_ID'
  'Card_Flags'
  ```

```py
db.tbl_collections()
```

```py
db.tbl_config()
```

```py
db.tbl_deck_config()
```

```py
db.tbl_decks()
```

```py
db.tbl_note_fields()
```

```py
db.tbl_graves()
```

```py
db.tbl_reviews()
```

```py
db.tbl_note_types()
```

```py
db.tbl_note_templates()
```

```py
db.tbl_notes()
```

## Combined Tables
```py
db.cards()        # the combination of the cards table, the notes table
```
#### Additional Columns/Features
- ```py
  'Card_Adjusted_Ease_Factor_As_Percentage'
  ```
  - The expected ease factor if each card had a 85% retention rate; given by the formula:

    <img width="300" src="https://render.githubusercontent.com/render/math?math=\frac{\ln(\text{desired retention rate})}{\ln(\text{current retention rate})} = \frac{\text{new ease}}{\text{current ease}}">

- ```py
  'Note_Field_<x>_Lowest_Frequency_Word_From_Collection'     # where <x> is the number of the field (e.g. <x> = 1)
  ```
  ```py
  'Note_Field_<x>_Lowest_Frequency_Word_From_Global_Texts'   # where <x> is the number of the field (e.g. <x> = 1)
  ```
  ```py
  'Note_Field_All_Lowest_Frequency_Word_From_Collection'
  ```
  ```py
  'Note_Field_All_Lowest_Frequency_Word_From_Global_Texts'
  ```

```py
db.reviews()
```

## Plots
```py
db.plot_adjusted_ease_vs_field_length()
```

```py
db.plot_average_answer_time_vs_field_length()
```

```py
db.plot_adjusted_ease_vs_word_frequency()
```

```py
db.plot_adjusted_ease_if_image_present()
```

```py
db.plot_answer_time_if_image_present()
```
