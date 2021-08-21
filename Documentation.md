# Documentation

```py
import ankistats as ak
db = ak.read('collection.anki2')
```

## Single Tables Direct from Database
```py
db.tbl_cards()
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
db.tbl_history()
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
db.cards()
```

```py
db.history()
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
