# ------------------------------------------------------------------------------
#
# MIT License
#
# Copyright (c) 2021 nogira
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# ------------------------------------------------------------------------------

import sqlite3
import pandas as pd
import numpy as np
from collections import defaultdict
import re
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from numpy.polynomial.polynomial import Polynomial
from os.path import abspath
import random

import seaborn as sns


# note: don't try to cache tables; makes notebook slow

# do new adjusted retention rate over last 7 reps instead of over all reps

# change from class to var that stores database path, with all functions being separate


# ------------------------------------------------------------------------------


class DataBase():
    path = 'None'
full_db = DataBase()


# ------------------------------------------------------------------------------


def _query_db(command):
    conn = sqlite3.connect(full_db.path)
    c = conn.cursor()
    c.execute(command)
    db = c.fetchall()
    conn.close()

    return db


def _db_to_dict(
    db,
    df_dict
    ):
    for row in db:
        for entry, key in zip(row, df_dict.keys()):
                if entry != '':
                    df_dict[key] += [entry]
                else:
                    df_dict[key] += [np.nan]

    return df_dict


def _get_field_cols(df):
    field_cols = list(df.columns)
    temp_cols = []
    for col in field_cols:
        # check for exact match to WHOLE string (not just a match to part of string)
        match = re.fullmatch('Note_Field_[0-9]+', col)
        if match:
            temp_cols.append(col)
    field_cols = temp_cols
    del temp_cols

    return field_cols


def _field_to_words(
    df,
    regex_remove=None,
    normal_remove=None
    ):
    """
    If using own list of things to remove, place the the things you want to 
    remove first first, and the things you want to remove last last.
    """

    field_cols = _get_field_cols(df)

    if normal_remove:
        normal_remove = normal_remove
    else:
        normal_remove = ['&nbsp;', '&amp', '&lt', '&gt', '-', ':', ';', '"', "'", '•', '=', '~', '\n',
                        '(', ')', '[', ']', '{', '}', '/', '\\', ',', '.', '?']
    if regex_remove:
        regex_remove = regex_remove
    else:
        regex_remove = [
            '<[^>]*>'      # remove all html tags
        ]

    for col in field_cols:
        new_col = col+"_Stripped"
        df[new_col] = df[col]

        for thing in regex_remove:
            df[new_col] = df[new_col].str.replace(thing, ' ', regex=True)
        for thing in normal_remove:
            df[new_col] = df[new_col].str.replace(thing, ' ', regex=False)

    for col in field_cols:
        new_col = col+"_Stripped"
        # replace all multiple spaces with 1
        df[new_col] = df[new_col].str.replace('\s+', ' ', regex=True)
        # remove side spaces
        df[new_col] = df[new_col].str.strip()

    return df


def _field_features(df):

    field_cols = _get_field_cols(df)

    # col for whether each field has image
    for col in field_cols:
        df[col+'_Has_Image'] =  df[col].str.contains('<img')

    # create char count and word count cols
    for col in field_cols:
        col = col+"_Stripped"
        df[col+'_Char_Count'] = df[col].str.len()
        df[col+'_Word_Count'] = df[col].str.count(r'\s') + 1
    
    df = _word_frequency(df)

    return df


def _word_frequency(df):

    word_count = defaultdict(int)

    field_cols = _get_field_cols(df)
    
    # count the words in every field
    for col in field_cols:
        col = col+"_Stripped"
        for field in df[col].to_list():
            if type(field) != float:   # float is the dtype of np.nan, and can't specify != np.nan for some reason
                word_list = field.split(' ')
                for word in word_list:
                    word = word.lower()
                    word_count[word] += 1


    #import unigram table if doesn't exist
    from os.path import exists, abspath
    from requests import get
    csv_path = abspath(__file__+'/../unigram_freq.csv')
    if exists(csv_path):
        pass
    else:
        with open(csv_path, 'w') as f:
            url = 'https://raw.githubusercontent.com/nogira/anki-stats/main/ankistats/unigram_freq.csv'
            f.write(get(url).text)
            del url
    del csv_path


    # get unigram frequencies
    df_unigram = pd.read_csv(abspath(__file__+'/../unigram_freq.csv'))
    unigram_word_count = {word: count for word, count in zip(
        df_unigram['word'], df_unigram['count']
    )}

    # get lowest freq word per field entry
    for col in field_cols:
        freq_entries = []
        unigram_freq_entries = []
        for field in df[col+"_Stripped"].to_list():

            # if no words, add nan to list of col entries
            if type(field) == float or not(field):
                freq_entries += [np.nan]
                unigram_freq_entries += [np.nan]

            # if words, add min freq to list of col entries
            else:
                word_list = field.split(' ')

                freq_list = []
                unigram_freq_list = []
                for word in word_list:
                    word = word.lower()
                    if word in word_count:
                        freq_list += [word_count[word]]
                    else:
                        # if no frequency, assume frequency is very low; in 
                        # this case we use 0 frequency
                        freq_list += [0]

                    if word in unigram_word_count:
                        unigram_freq_list += [unigram_word_count[word]]
                    elif re.search('^[0-9]$', word) or len(word) < 3:
                        unigram_freq_list += [np.nan]
                    else:
                        # if no frequency, assume frequency is very low; in 
                        # this case we use 0 frequency
                        unigram_freq_list += [0]
                        # print(word, end='  ')

                freq_entries += [min(freq_list)]
                unigram_freq_entries += [min(unigram_freq_list)]


        # now that freq antry list id complete, form a new col with the list
        df[col+"_Lowest_Frequency_Word_From_Collection"] = freq_entries
        df[col+"_Lowest_Frequency_Word_From_Global_Texts"] = unigram_freq_entries

    # do lowest frequency across all cols
    df["Note_Field_All_Lowest_Frequency_Word_From_Collection"] = df.apply(
        lambda x: min(
            [x[col+"_Lowest_Frequency_Word_From_Collection"] for col in field_cols]
        ),
        axis=1
    )
    df["Note_Field_All_Lowest_Frequency_Word_From_Global_Texts"] = df.apply(
        lambda x: min(
            [x[col+"_Lowest_Frequency_Word_From_Global_Texts"] for col in field_cols]
        ),
        axis=1
    )

    return df


def _get_adjusted_ease(df):
    """
    Modify ease to get all cards to a constant retention rate (RR), using 
    the formula:

    log(desired RR) / log(current RR) = new ease / current ease
    """

    # was getting warning about setting values on copy of slice; this fixes that
    df = df.copy()

    # filter out cards that will adversly effect adjusted ease factor
    df = df[(df['Card_Last_Know_Ease_Factor'] != 0) &
            (df['Card_Total_Reviews_Including_Lapses'] > 6)]

    reps = 'Card_Total_Reviews_Including_Lapses'
    lapses = 'Card_Total_Lapses'
    df['Card_Reviews_Fraction_Correct'] = (df[reps] - df[lapses]) / df[reps]

    # 85% retention rate
    desired_RR = 0.85
    old_ease = df['Card_Last_Know_Ease_Factor'].to_list()
    old_retention = df['Card_Reviews_Fraction_Correct'].to_list()
    new_ease = []
    for ease, retention in zip(old_ease, old_retention):
        if retention > 0.9:
            ret = 0.9
        else:
            ret = retention
            
        new_ease.append(calc_new_ease(desired_RR, ease, ret))

    df['Card_Adjusted_Ease_Factor'] = new_ease

    return df


def _intervals_to_timedelta(df):
    cols = list(df.columns)
    for col in cols:
        if 'Interval' in col:
            df[col] = df[col].apply(
                lambda x: pd.Timedelta(f'{abs(x)} seconds') if x < 0 
                else pd.Timedelta(f'{x} days')
            )
    return df


def _unix_IDs_to_datetime(df):
    cols = list(df.columns)
    for col in cols:
        if '_ID' in col and not('Globally' in col):
            df[col] = pd.to_datetime(df[col], unit='ms')
    return df


def _ease_to_multiplier(df):
    cols = list(df.columns)
    for col in cols:
        if 'Ease_Factor' in col:
            df[col] = df[col] / 1000
    return df


# --------------------------------------------------------------------------


def tbl_cards():
    """Get the Cards Table From Database"""

    command = '''
    SELECT id, nid, did, ord, mod, type, queue, due, ivl, factor,
        reps,   --reps = total reps (i.e. failed reps + successful reps)
        lapses, odue, odid, flags
    FROM cards
    '''
    db = _query_db(command)

    df_dict = {
        'Card_ID':[],
        'Note_ID':[],
        'Deck_ID':[],
        'Card_Ordinal':[],
        'Card_Time_Last_Modified':[],
        'Card_Type':[],
        'Card_Queue':[],
        'Card_Due_Time':[],
        'Card_Current_Interval':[],
        'Card_Ease_Factor':[],
        'Card_Total_Reviews_Including_Lapses':[],
        'Card_Total_Lapses':[],
        'Filtered_Card_Original_Due':[],
        'Filtered_Card_Deck_ID':[],
        'Card_Flags':[]                             # should prob convert nums to colors
    }

    df_dict = _db_to_dict(db, df_dict)
    df = pd.DataFrame(df_dict)

    df = _unix_IDs_to_datetime(df)
    df = _intervals_to_timedelta(df)
    df = _ease_to_multiplier(df)

    # convert sec to date/time
    df['Card_Time_Last_Modified'] = pd.to_datetime(df['Card_Time_Last_Modified'],unit='s')

    # convert card type as integer to card type as string
    # 0=new, 1=learning, 2=review, 3=relearning
    df['Card_Type'] = df['Card_Type'].map({
        0: 'New',
        1: 'Learning',
        2: 'Review',
        3: 'Relearning'
    })

    # convert card queue as integer to card queue as string
    # -- -3=user buried(In scheduler 2),
    # -- -2=sched buried (In scheduler 2), 
    # -- -2=buried(In scheduler 1),
    # -- -1=suspended,
    # -- 0=new, 1=learning, 2=review (as for type)
    # -- 3=in learning, next rev in at least a day after the previous review
    # -- 4=preview
    df['Card_Queue'] = df['Card_Queue'].map({
        -3: 'User Buried',
        -2: 'Scheduler Buried',
        -1: 'Suspended',
        0: 'New',
        1: 'Learning (Interval < 1 Day)',
        2: 'Review',
        3: 'Learning (Interval >= 1 Day)',
        4: 'Preview'
    })

    # CONVERT DUE COL TO DUE DATE
    # -- Due is used differently for different card types: 
    # --   new: note id or random int
    # --   due: integer day, relative to the collection's creation time
    # --   learning: integer timestamp in second
    collection_create_time = tbl_collections()['Collection_Creation_Time'][0]
    def due_to_due_date(row):
        if row['Card_Type'] == 'New':
            row['Card_Due_Time'] = np.nan

        elif row['Card_Type'] == 'Learning' or row['Card_Type'] == 'Relearning':
            row['Card_Due_Time'] = pd.to_datetime(row['Card_Due_Time'],unit='s')

        else:
            row['Card_Due_Time'] = collection_create_time + pd.Timedelta(f"{row['Card_Due_Time']} days")

        return row
    df = df.apply(due_to_due_date, axis=1)

    return df


def tbl_collections():
    """Get the Collections Table From Database"""

    command = '''
    SELECT
        crt, mod, scm, ver, ls, conf, models, decks, 
        dconf, tags

    FROM col
    '''

    db = _query_db(command)

    df_dict = {
        'Collection_Creation_Time':[],
        'Collection_Time_Last_Modified':[],
        'Collection_Last_Schema_Modified_Time':[],
        'Collection_Version':[],
        'Collection_Last_Sync_Time':[],
        'Collection_Config_JSON':[],
        'Collection_Note_Type_JSON':[],
        'Collection_Decks_JSON':[],
        'Collection_Deck_Config_JSON':[],
        'Collection_Tags':[]
    }

    df_dict = _db_to_dict(db, df_dict)

    df = pd.DataFrame(df_dict)

    # sec -> date/time
    col = 'Collection_Creation_Time'; df[col] = pd.to_datetime(df[col],unit='s')
    # ms -> to date/time
    col = 'Collection_Time_Last_Modified'; df[col] = pd.to_datetime(df[col],unit='ms')

    return df


def tbl_config():
    """Get the Config Table From Database"""

    command = '''
    SELECT KEY, mtime_secs, val
    FROM config
    '''
    db = _query_db(command)

    df_dict = {
        'Config_Key':[],
        'Config_Time_Last_Modified':[],
        'Config_Value':[]
    }

    df_dict = _db_to_dict(db, df_dict)

    return pd.DataFrame(df_dict)


def tbl_deck_config():
    """Get the Deck Config Table From Database"""

    command = '''
    SELECT id, name, mtime_secs, config
    FROM deck_config
    '''
    db = _query_db(command)

    df_dict = {
        'Deck_ID':[],
        'Deck_Name':[],
        'Deck_Config_Time_Last_Modified':[],
        'Deck_Config':[]
    }

    df_dict = _db_to_dict(db, df_dict)

    df = pd.DataFrame(df_dict)

    df = _unix_IDs_to_datetime(df)

    # sec -> date/time
    col = 'Deck_Config_Time_Last_Modified'; df[col] = pd.to_datetime(df[col],unit='s')

    return df


def tbl_decks():
    """Get the Decks Table From Database"""

    command = '''
    SELECT id, name, mtime_secs, common, kind
    FROM decks
    '''

    db = _query_db(command)

    df_dict = {
        'Deck_ID':[],
        'Deck_Name':[],
        'Deck_Time_Last_Modified':[],
        'Deck_Common':[],
        'Deck_Kind':[]
    }

    df_dict = _db_to_dict(db, df_dict)

    df = pd.DataFrame(df_dict)

    df = _unix_IDs_to_datetime(df)

    # sec -> date/time
    col='Deck_Time_Last_Modified'; df[col] = pd.to_datetime(df[col],unit='s')

    return df


def tbl_note_fields():
    """Get the Note Fields Table From Database"""

    command = '''
    SELECT ntid, ord, name, config
    FROM FIELDS
    '''
    db = _query_db(command)

    df_dict = {
        'Note_Type_ID':[],
        'Note_Field_Ordinal':[],
        'Note_Field_Name':[],
        'Note_Field_Config':[]
    }

    df_dict = _db_to_dict(db, df_dict)

    df = pd.DataFrame(df_dict)

    df = _unix_IDs_to_datetime(df)

    # str1 = tbl1.Config[0].decode('CP1252')
    # print([str1.split('ú')[0].strip()])

    # tbl1.Config[0].decode(errors='replace')

    return df


def tbl_graves():
    """Get the Graves (deleted things) Table From Database"""

    command = '''
    SELECT oid, type
    FROM FIELDS
    '''

    db = _query_db(command)

    df_dict = {
        'Grave_Original_ID':[],
        'Grave_Type':[]
    }

    df_dict = _db_to_dict(db, df_dict)

    df = pd.DataFrame(df_dict)

    df = _unix_IDs_to_datetime(df)

    return df


def tbl_reviews():
    """Get the Review History Table From Database"""

    command = '''
        SELECT id, cid, ease, ivl, lastIvl, factor, time, type
        FROM revlog
        '''
    db = _query_db(command)

    df_dict = {
        'Review_ID':[],
        'Card_ID':[],
        'Review_Answer':[],
        'Review_New_Interval':[],
        'Review_Last_Interval':[],
        'Review_New_Ease_Factor':[],
        'Review_Time_To_Answer':[],
        'Review_Type':[]
    }

    df_dict = _db_to_dict(db, df_dict)

    df = pd.DataFrame(df_dict)

    df = _unix_IDs_to_datetime(df)
    df = _intervals_to_timedelta(df)
    df = _ease_to_multiplier(df)

    # convert review type as integer to review type as string
    # 0=learn, 1=review, 2=relearn, 3=cram
    df['Review_Type'] = df['Review_Type'].map({
        0: 'Learning',
        1: 'Review',
        2: 'Relearning',
        3: 'Cram'
    })

    # convert review answer as integer to review type as string
    # -- which button you pushed to score your recall. 
    # -- 1(wrong), 2(hard), 3(ok), 4(easy)
    df['Review_Answer'] = df['Review_Answer'].map({
        1: 'Wrong',
        2: 'Hard',
        3: 'Ok',       # this is all potentially wrong since the db docs had old info
        4: 'Easy'
    })

    df['Review_Time_To_Answer'] = df['Review_Time_To_Answer'].apply(
            lambda x: pd.Timedelta(f'{x} ms')
        )

    return  df


def tbl_note_types():
    """Get the Note Types Table From Database"""

    command = '''
    SELECT id, name, mtime_secs, config
    FROM notetypes
    '''
    db = _query_db(command)

    df_dict = {
        'Note_Type_ID':[],
        'Note_Type_Name':[],
        'Note_Type_Time_Last_Modified':[],
        'Note_Type_Config':[]
    }

    df_dict = _db_to_dict(db, df_dict)
    df = pd.DataFrame(df_dict)

    df = _unix_IDs_to_datetime(df)

    # convert sec to date/time
    df['Note_Type_Time_Last_Modified'] = pd.to_datetime(df['Note_Type_Time_Last_Modified'],unit='s').to_numpy()

    return df


def tbl_note_templates():
    """Get the Note Templates Table From Database"""

    command = '''
    SELECT ntid, ord, name, mtime_secs, config
    FROM templates
    '''
    db = _query_db(command)

    df_dict = {
        'Note_Type_ID':[],
        'Note_Template_Ordinal':[],
        'Note_Template_Name':[],
        'Note_Template_Time_Last_Modified':[],
        'Note_Template_Config':[]
    }

    df_dict = _db_to_dict(db, df_dict)
    df = pd.DataFrame(df_dict)

    df = _unix_IDs_to_datetime(df)

    # convert sec to date/time
    # df['Note_Template_Time_Last_Modified'] = pd.to_datetime(df['Note_Template_Time_Last_Modified'],unit='s').to_numpy()

    return df


def tbl_notes(
    num_fields=None
    ):
    """Get the Notes Table From Database"""

    command = '''
    SELECT id, guid, mid, mod, tags, flds
    FROM notes
    '''

    db = _query_db(command)

    df_dict = {
        'Note_ID':[],
        'Note_Globally_Unique_ID':[],
        'Note_Type_ID':[],
        'Note_Time_Last_Modified':[],
        'Note_Tags':[],
        'Note_Fields':[]
    }

    df_dict = _db_to_dict(db, df_dict)
    df = pd.DataFrame(df_dict)

    df = _unix_IDs_to_datetime(df)
    
    if num_fields:
        max_num_fields = num_fields
    else:
        max_num_fields = 1 + df['Note_Fields'].str.count('\x1f').max()
    
    fields = df['Note_Fields'].to_list()

    field_cols_dict = defaultdict(list)

    for card in fields:
        # create list of fields
        field_list = card.split('\x1f')
        # pad the end of list with NaN so all cards have equal length list
        if len(field_list) < max_num_fields:
            field_list += [np.nan for _ in range(max_num_fields - len(field_list))]

        # add the fields of the card to the dict
        for i in range(max_num_fields):
            field_cols_dict[f'Note_Field_{i+1}'] += [field_list[i]]

    # add all field cols from dict to df
    for i in range(max_num_fields):
        df[f'Note_Field_{i+1}'] = field_cols_dict[f'Note_Field_{i+1}']

    del df['Note_Fields']

    # convert sec to date/time
    # df['Note_Template_Time_Last_Modified'] = pd.to_datetime(df['Note_Template_Time_Last_Modified'],unit='s').to_numpy()

    return df


# ----------------------SQL QUERIES FOR EXTRA FEATURES----------------------


def _extra_card_features_from_reviews():
    command = '''
        WITH
            last_known AS (
                SELECT
                    DISTINCT cid,
                    LAST_VALUE(revlog.factor)
                        OVER (
                            PARTITION BY revlog.cid
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                        ) AS ease,
                    LAST_VALUE(revlog.ivl)
                        OVER (
                            PARTITION BY revlog.cid
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                        ) AS ivl
                FROM revlog
            ),

            revlog_avg_times AS (
                SELECT cid, AVG(time) AS avg_time
                FROM revlog
                GROUP BY cid
            )
        
        SELECT 
            last_known.cid,
            last_known.ease,
            last_known.ivl,
            revlog_avg_times.avg_time
        FROM last_known
            JOIN revlog_avg_times
                ON last_known.cid = revlog_avg_times.cid
        '''
    db = _query_db(command)

    df_dict = {
        'Card_ID':[],
        'Card_Last_Know_Ease_Factor':[],
        'Card_Last_Know_Interval':[],
        'Card_Average_Review_Time':[]
    }

    df_dict = _db_to_dict(db, df_dict)

    df = pd.DataFrame(df_dict)

    df = _unix_IDs_to_datetime(df)
    df = _intervals_to_timedelta(df)
    df = _ease_to_multiplier(df)

    df['Card_Average_Review_Time'] = df['Card_Average_Review_Time'].apply(
            lambda x: pd.Timedelta(f'{x} ms')
        )

    return df


# --------------------------------------------------------------------------


def reviews(
    num_fields=None
    ):
    """
    Get the Review History Table, and Join the Cards Table & Notes Table onto It
    """

    df = pd.merge(tbl_reviews(), tbl_cards(), on="Card_ID")
    df = pd.merge(df, tbl_notes(num_fields=num_fields), on="Note_ID")
    df = pd.merge(df, tbl_note_types(), on="Note_Type_ID")

    # are there any other tables that should be merged??

    # extra features
    df = _field_to_words(df)
    df = _field_features(df)

    return df


def cards(
    note_types=None,
    num_fields=None,
    regex_remove=None,
    normal_remove=None
    ):
    """
    Get the Review History Table, and Join the Cards Table & Notes Table onto It
    """

    df = pd.merge(tbl_cards(),_extra_card_features_from_reviews(),on="Card_ID")
    df = pd.merge(df, tbl_notes(num_fields=num_fields), on="Note_ID")
    df = pd.merge(df, tbl_note_types(), on="Note_Type_ID")

                # are there any other tables that should be merged??

    # filter notetypes
    if note_types:
        df = df[df['Note_Type_Name'].isin(note_types)]

    # --------------------------------

    # extra features
    df = _field_to_words(df,regex_remove=regex_remove,normal_remove=normal_remove)
    df = _field_features(df)
    df = _get_adjusted_ease(df)

    return df


# -------------------------------- CALCULATIONS --------------------------------

def calc_new_ease(
    new_retention: float,
    old_ease: float,
    old_retention: float
    ):
    """new_retention, old_ease, old_retention"""

    return old_ease * (np.log(new_retention) / np.log(old_retention))


def calc_new_retention(
    new_ease: float,
    old_ease: float,
    old_retention: float
    ):
    """new_ease, old_ease, old_retention"""

    return np.exp((new_ease / old_ease) * np.log(old_retention))