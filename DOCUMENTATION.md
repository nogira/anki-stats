# Documentation

<br>

> ⚠️ **Note**: this is incomplete

<br>

```py
import ankistats as ak
ak.db_path('collection.anki2')
```

## Single Tables Direct from Database
```py
ak.tbl_cards()
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
  'Card_Current_Interval'
  'Card_Ease_Factor_As_Percentage'
  'Card_Total_Reviews_Including_Lapses'
  'Card_Total_Lapses'
  'Filtered_Card_Original_Due'
  'Filtered_Card_Deck_ID'
  'Card_Flags'
  ```

```py
ak.tbl_collections()
```

```py
ak.tbl_config()
```

```py
ak.tbl_deck_config()
```

```py
ak.tbl_decks()
```

```py
ak.tbl_note_fields()
```

```py
ak.tbl_graves()
```

```py
ak.tbl_reviews()
```

```py
ak.tbl_note_types()
```

```py
ak.tbl_note_templates()
```

```py
ak.tbl_notes()
```

## Combined Tables
```py
ak.cards()        # the combination of the cards table, the notes table
```
#### Additional Columns/Features
- ```py
  'Card_Adjusted_Ease_Factor_As_Percentage'
  ```
  - This is the expected ease factor if each card had a 85% retention rate. We do this to be able to use ease factor as a measure of card difficulty, as the adjustment removes the variability of retention rate from ease factor. The calculation to get the adjusted ease factor is given by the formula:

    <img width="300" src="https://render.githubusercontent.com/render/math?math=\frac{\ln(\text{new retention rate})}{\ln(\text{current retention rate})} = \frac{\text{new ease factor}}{\text{current ease factor}}">
    
    Which is derived from the equation of [the forgetting curve](https://supermemo.guru/wiki/Forgetting_curve):
    
    <img width="90" src="https://render.githubusercontent.com/render/math?math=R = \exp(\frac{-t}{s})">

  ```py
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
ak.reviews()
```

## Plots
```py
ak.plot_adjusted_ease_vs_field_length()
```
<img width=600 src="https://i.postimg.cc/4y9VhWtG/plot1.png">

```py
ak.plot_average_answer_time_vs_field_length()
```
<img width=600 src="https://i.postimg.cc/zG5KVSfm/plot2.png">

```py
ak.plot_adjusted_ease_vs_word_frequency()
```
<img width=600 src="https://i.postimg.cc/Pr11XFTz/plot3.png">

```py
ak.plot_adjusted_ease_if_image_present()
```
<img width=600 src="https://i.postimg.cc/jqpzrr0S/plot4.png">

```py
ak.plot_answer_time_if_image_present()
```
<img width=600 src="https://i.postimg.cc/gcXv5277/plot5.png">

## Stats
```py
ak.stats_lapse_retention()
# -> Right: 1303
#    Wrong: 10
#    Fraction Correct: 1.0
```

```py
ak.stats_learning_graduation_retention(
    graduation_interval="1 day",
    pre_graduation_interval="10 min"
)
# -> Right: 7042
#    Wrong: 0
#    Fraction Correct: 1.0
```
