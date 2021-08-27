# Documentation
- [Stats](#stats)
- [Plots](#plots)
- [Simulations](#simulations)
- [Single Tables Direct from Database](#single-tables-direct-from-database)
- [Combined Tables](#combined-tables)


<br>

> ⚠️ **Note**: this is incomplete

<br>

```py
import ankistats as ak
ak.db_path('collection.anki2')
```


## Stats
```py
ak.stats_lapse_retention()
# -> Right: 1303
#    Wrong: 0
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

## Simulations

Note: Does not yet simulate changes in ease/retention, or current deck settings for things like learning/lapse steps.

```py
ak.simulate_no_changes(
    days=365,             # optional
    new_cards_per_day=0   # optional
)
```
<img width=600 src="https://i.imgur.com/ItIqVsh.png">

```py
ak.simulate_uniform_retention(![image](https://user-images.githubusercontent.com/83847986/131071669-05edeb20-a5f6-48ca-8f8b-c172b433e53f.png)

    retention=0.85,
    retention_cap=0.9,    # optional
    days=365,             # optional
    new_cards_per_day=0   # optional
)
```
<img width=600 src="https://i.imgur.com/cVwAO8P.png">

```py
ak.simulate_uniform_ease(
    ease=2.5,
    retention_cap=0.9,    # optional
    days=365,             # optional
    new_cards_per_day=0   # optional
)
```
<img width=600 src="https://i.imgur.com/cY2tM35.png">

```py
ak.simulate_optimal_ease_per_memory_strength_from_scratch(
    ease,
    retention,
    days=365,              # optional
    new_cards_per_day=5,   # optional
    min_retention=0.6,     # optional
    max_retention=0.9      # optional
)
```
<img width=600 src="https://i.imgur.com/r9VbLRh.png">


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
- ```py
  # Columns
  
  'Collection_Creation_Time'
  'Collection_Time_Last_Modified'
  'Collection_Last_Schema_Modified_Time'
  'Collection_Version'
  'Collection_Last_Sync_Time'
  'Collection_Config_JSON'
  'Collection_Note_Type_JSON'
  'Collection_Decks_JSON'
  'Collection_Deck_Config_JSON'
  'Collection_Tags'
  ```

```py
ak.tbl_config()
```
- ```py
  # Columns
  
  'Config_Key'
  'Config_Time_Last_Modified'
  'Config_Value'
  ```

```py
ak.tbl_deck_config()
```
- ```py
  # Columns
  
  'Deck_ID'
  'Deck_Name'
  'Deck_Config_Time_Last_Modified'
  'Deck_Config'
  ```

```py
ak.tbl_decks()
```
- ```py
  # Columns
  
  'Deck_ID'
  'Deck_Name'
  'Deck_Time_Last_Modified'
  'Deck_Common'
  'Deck_Kind'
  ```

```py
ak.tbl_note_fields()
```
- ```py
  # Columns
  
  'Note_Type_ID'
  'Note_Field_Ordinal'
  'Note_Field_Name'
  'Note_Field_Config'
  ```

```py
ak.tbl_graves()
```
- ```py
  # Columns
  
  'Grave_Original_ID'
  'Grave_Type'
  ```

```py
ak.tbl_reviews()
```
- ```py
  # Columns
  
  'Review_ID'
  'Card_ID'
  'Review_Answer'
  'Review_New_Interval'
  'Review_Last_Interval'
  'Review_New_Ease_Factor'
  'Review_Time_To_Answer'
  'Review_Type'
  ```

```py
ak.tbl_note_types()
```
- ```py
  # Columns
  
  'Note_Type_ID'
  'Note_Type_Name'
  'Note_Type_Time_Last_Modified'
  'Note_Type_Config'
  ```

```py
ak.tbl_note_templates()
```
- ```py
  # Columns
  
  'Note_Type_ID'
  'Note_Template_Ordinal'
  'Note_Template_Name'
  'Note_Template_Time_Last_Modified'
  'Note_Template_Config'
  ```

```py
ak.tbl_notes()
```
- ```py
  # Columns
  
  'Note_ID'
  'Note_Globally_Unique_ID'
  'Note_Type_ID'
  'Note_Time_Last_Modified'
  'Note_Tags'
  'Note_Fields'
  ```


## Combined Tables
```py
ak.cards()        # the combination of the cards table, the notes table
```
#### Additional Columns/Features
- ```py
  'Card_Adjusted_Ease_Factor'
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
