import sqlite3
from typing import overload
import pandas as pd
import numpy as np
from collections import defaultdict
import re
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from numpy.polynomial.polynomial import Polynomial
import math
from os.path import abspath

# scrap the cache idea for single tables
# still cache combined tables, but make sure combined tables run their own sql query

# do new adjusted retention rate over last 7 reps instead of over all reps

class read():

    def __init__(self, db_name) -> None:
        self.db_name = db_name

        self.cards_cache = None
        self.cards_cache_note_types = None




        # add caches for the rest




    def query_db(self, command):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(command)
        db = c.fetchall()
        conn.close()

        return db


    def db_to_dict(self, db, df_dict):
        for row in db:
            for entry, key in zip(row, df_dict.keys()):
                    if entry != '':
                        df_dict[key] += [entry]
                    else:
                        df_dict[key] += [np.nan]

        return df_dict


    def get_field_cols(self, df):
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


    def field_to_words(self, df, regex_remove=None, normal_remove=None):
        """
        If using own list of things to remove, place the the things you want to 
        remove first first, and the things you want to remove last last.
        """

        field_cols = self.get_field_cols(df)

        for col in field_cols:
            df[col+'_Has_Image'] =  df[col].str.contains('<img')

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

        reps = 'Card_Total_Reviews_Including_Lapses'
        lapses = 'Card_Total_Lapses'
        df['Card_Reviews_Fraction_Correct'] = (df[reps] - df[lapses]) / df[reps]
        del reps, lapses

        # create char count and word count cols
        for col in field_cols:
            col = col+"_Stripped"
            df[col+'_Char_Count'] = df[col].str.len()
            df[col+'_Word_Count'] = df[col].str.count(r'\s') + 1

        return df


    def word_frequency(self, df):

        word_count = defaultdict(int)

        field_cols = self.get_field_cols(df)
        
        # count the words in every field
        for col in field_cols:
            col = col+"_Stripped"
            for field in df[col].to_list():
                if type(field) != float:   # float is the dtype of np.nan, and can't specify != np.nan for some reason
                    word_list = field.split(' ')
                    for word in word_list:
                        word = word.lower()
                        word_count[word] += 1

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

    # --------------------------------------------------------------------------


    def tbl_cards(self):
        """Get the Cards Table From Database"""

        command = '''
        SELECT id, nid, did, ord, mod, type, queue, due, ivl, factor,
            reps,   --reps = total reps (i.e. failed reps + successful reps)
            lapses, odue, odid, flags
        FROM cards
        '''

        db = self.query_db(command)

        df_dict = {
            'Card_ID':[],
            'Note_ID':[],
            'Deck_ID':[],
            'Card_Ordinal':[],
            'Card_Time_Last_Modified':[],
            'Card_Type':[],
            'Card_Queue':[],
            'Card_Due':[],
            'Card_Current_Interval_In_Minutes':[],
            'Card_Ease_Factor_As_Percentage':[],
            'Card_Total_Reviews_Including_Lapses':[],
            'Card_Total_Lapses':[],
            'Filtered_Card_Original_Due':[],
            'Filtered_Card_Deck_ID':[],
            'Card_Flags':[]                             # should prob convert nums to colors
        }

        df_dict = self.db_to_dict(db, df_dict)
        df = pd.DataFrame(df_dict)

        # unix time -> normal time
        df['Card_ID'] = pd.to_datetime(df['Card_ID'],unit='ms').to_numpy()
        df['Note_ID'] = pd.to_datetime(df['Note_ID'],unit='ms').to_numpy()
        df['Deck_ID'] = pd.to_datetime(df['Deck_ID'],unit='ms').to_numpy()
        df['Filtered_Card_Deck_ID'] = pd.to_datetime(df['Filtered_Card_Deck_ID'],unit='ms').to_numpy()

        # convert sec to date/time
        df['Card_Time_Last_Modified'] = pd.to_datetime(df['Card_Time_Last_Modified'],unit='s').to_numpy()

        # divide ease by ten to get to percentage
        df['Card_Ease_Factor_As_Percentage'] = df['Card_Ease_Factor_As_Percentage'] / 10

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

        # convert intervals to minute timescale
        df['Card_Current_Interval_In_Minutes'] = df['Card_Current_Interval_In_Minutes'].apply(
            lambda x: (abs(x) / 60) if x < 0 else (x * 24 * 60)
        )                                       # day->hr->min


        return df


    def tbl_collections(self):
        """Get the Collections Table From Database"""

        command = '''
        SELECT
            crt, mod, scm, ver, ls, conf, models, decks, 
            dconf, tags

        FROM col
        '''

        db = self.query_db(command)

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

        df_dict = self.db_to_dict(db, df_dict)

        df = pd.DataFrame(df_dict)

        # convert sec to date/time
        df['Collection_Time_Last_Modified'] = pd.to_datetime(df['Collection_Time_Last_Modified'],unit='s').to_numpy()

        return df


    def tbl_config(self):
        """Get the Config Table From Database"""

        command = '''
        SELECT KEY, mtime_secs, val
        FROM config
        '''

        db = self.query_db(command)

        df_dict = {
            'Config_Key':[],
            'Config_Time_Last_Modified':[],
            'Config_Value':[]
        }

        df_dict = self.db_to_dict(db, df_dict)

        return pd.DataFrame(df_dict)


    def tbl_deck_config(self):
        """Get the Deck Config Table From Database"""

        command = '''
        SELECT id, name, mtime_secs, config
        FROM deck_config
        '''

        db = self.query_db(command)

        df_dict = {
            'Deck_ID':[],
            'Deck_Name':[],
            'Deck_Config_Time_Last_Modified':[],
            'Deck_Config':[]
        }

        df_dict = self.db_to_dict(db, df_dict)

        df = pd.DataFrame(df_dict)

        # unix time -> normal time
        df['Deck_ID'] = pd.to_datetime(df['Deck_ID'],unit='ms').to_numpy()

        # convert sec to date/time
        df['Deck_Config_Time_Last_Modified'] = pd.to_datetime(df['Deck_Config_Time_Last_Modified'],unit='s').to_numpy()


        return df


    def tbl_decks(self):
        """Get the Decks Table From Database"""

        command = '''
        SELECT id, name, mtime_secs, common, kind
        FROM decks
        '''

        db = self.query_db(command)

        df_dict = {
            'Deck_ID':[],
            'Deck_Name':[],
            'Deck_Time_Last_Modified':[],
            'Deck_Common':[],
            'Deck_Kind':[]
        }

        df_dict = self.db_to_dict(db, df_dict)

        df = pd.DataFrame(df_dict)

        # unix time -> normal time
        df['Deck_ID'] = pd.to_datetime(df['Deck_ID'],unit='ms').to_numpy()

        # convert sec to date/time
        df['Deck_Time_Last_Modified'] = pd.to_datetime(df['Deck_Time_Last_Modified'],unit='s').to_numpy()


        return df


    def tbl_note_fields(self):
        """Get the Note Fields Table From Database"""

        command = '''
        SELECT ntid, ord, name, config
        FROM FIELDS
        '''

        db = self.query_db(command)

        df_dict = {
            'Note_Type_ID':[],
            'Note_Field_Ordinal':[],
            'Note_Field_Name':[],
            'Note_Field_Config':[]
        }

        df_dict = self.db_to_dict(db, df_dict)

        df = pd.DataFrame(df_dict)

        # unix time -> normal time
        df['Note_Type_ID'] = pd.to_datetime(df['Note_Type_ID'],unit='ms').to_numpy()

        # str1 = tbl1.Config[0].decode('CP1252')
        # print([str1.split('ú')[0].strip()])

        # tbl1.Config[0].decode(errors='replace')

        return df


    def tbl_graves(self):
        """Get the Graves (deleted things) Table From Database"""

        command = '''
        SELECT oid, type
        FROM FIELDS
        '''

        db = self.query_db(command)

        df_dict = {
            'Grave_Original_ID':[],
            'Grave_Type':[]
        }

        df_dict = self.db_to_dict(db, df_dict)

        df = pd.DataFrame(df_dict)

        # unix time -> normal time
        df['Grave_Original_ID'] = pd.to_datetime(df['Grave_Original_ID'],unit='ms').to_numpy()

        return df


    def tbl_reviews(self, extra_features=False):
        """Get the Review History Table From Database"""

        if extra_features:
            command = '''
            WITH last_known_ease AS (
                    SELECT
                        DISTINCT cid,
                        LAST_VALUE(revlog.factor)
                            OVER (
                                PARTITION BY revlog.cid
                                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                            ) AS ease
                    FROM revlog
                ),

                revlog_avg_times AS (
                    SELECT cid, AVG(time) AS avg_time
                    FROM revlog
                    GROUP BY cid
                )
            


            SELECT revlog.id, revlog.cid, revlog.ease, revlog.ivl,
                revlog.lastIvl, revlog.factor, revlog.time, revlog.type,
                last_known_ease.ease, revlog_avg_times.avg_time
            FROM revlog
                JOIN last_known_ease
                    ON revlog.cid = last_known_ease.cid
                JOIN revlog_avg_times
                    ON revlog.cid = revlog_avg_times.cid
            '''

        else:
            command = '''
            SELECT id, cid, ease, ivl, lastIvl, factor, time, type
            FROM revlog
            '''

        db = self.query_db(command)

        df_dict = {
            'Review_ID':[],
            'Card_ID':[],
            'Review_Answer':[],
            'Review_New_Interval_In_Minutes':[],
            'Review_Last_Interval_In_Minutes':[],
            'Review_New_Ease_Factor_As_Percentage':[],
            'Review_Time_To_Answer_In_Seconds':[],
            'Review_Type':[]
        }

        if extra_features:
            df_dict['Card_Last_Know_Ease_Factor_As_Percentage'] = []
            df_dict['Card_Average_Review_Time_In_Seconds'] = []

        df_dict = self.db_to_dict(db, df_dict)

        df = pd.DataFrame(df_dict)

        # unix time -> normal time
        df['Review_ID'] = pd.to_datetime(df['Review_ID'],unit='ms').to_numpy()
        df['Card_ID'] = pd.to_datetime(df['Card_ID'],unit='ms').to_numpy()

        # divide ease by ten to get to percentage
        df['Review_New_Ease_Factor_As_Percentage'] = df['Review_New_Ease_Factor_As_Percentage'] / 10
        if extra_features:
            df['Card_Last_Know_Ease_Factor_As_Percentage'] = df['Card_Last_Know_Ease_Factor_As_Percentage'] / 10

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

        # convert intervals to minute timescale
        for col in ['Review_New_Interval_In_Minutes', 'Review_Last_Interval_In_Minutes']:
            df[col] = df[col].apply(
                lambda x: (abs(x) / 60) if x < 0 else (x * 24 * 60)
            )                                       # day->hr->min

        # convert time to seconds
        df['Review_Time_To_Answer_In_Seconds'] = df['Review_Time_To_Answer_In_Seconds'] / 1000

        if extra_features:
            df['Card_Average_Review_Time_In_Seconds'] = df['Card_Average_Review_Time_In_Seconds'] / 1000


        return  df


    def tbl_note_types(self):
        """Get the Note Types Table From Database"""

        command = '''
        SELECT id, name, mtime_secs, config
        FROM notetypes
        '''

        db = self.query_db(command)

        df_dict = {
            'Note_Type_ID':[],
            'Note_Type_Name':[],
            'Note_Type_Time_Last_Modified':[],
            'Note_Type_Config':[]
        }

        df_dict = self.db_to_dict(db, df_dict)
        df = pd.DataFrame(df_dict)

        # unix time -> normal time
        df['Note_Type_ID'] = pd.to_datetime(df['Note_Type_ID'],unit='ms').to_numpy()

        # convert sec to date/time
        df['Note_Type_Time_Last_Modified'] = pd.to_datetime(df['Note_Type_Time_Last_Modified'],unit='s').to_numpy()


        return df


    def tbl_note_templates(self):
        """Get the Note Templates Table From Database"""

        command = '''
        SELECT ntid, ord, name, mtime_secs, config
        FROM templates
        '''

        db = self.query_db(command)

        df_dict = {
            'Note_Type_ID':[],
            'Note_Template_Ordinal':[],
            'Note_Template_Name':[],
            'Note_Template_Time_Last_Modified':[],
            'Note_Template_Config':[]
        }

        df_dict = self.db_to_dict(db, df_dict)
        df = pd.DataFrame(df_dict)

        # unix time -> normal time
        df['Note_Type_ID'] = pd.to_datetime(df['Note_Type_ID'],unit='ms').to_numpy()

        # convert sec to date/time
        # df['Note_Template_Time_Last_Modified'] = pd.to_datetime(df['Note_Template_Time_Last_Modified'],unit='s').to_numpy()


        return df


    def tbl_notes(self, num_fields=None):
        """Get the Notes Table From Database"""

        command = '''
        SELECT id, guid, mid, mod, tags, flds
        FROM notes
        '''

        db = self.query_db(command)

        df_dict = {
            'Note_ID':[],
            'Note_Globally_Unique_ID':[],
            'Note_Type_ID':[],
            'Note_Time_Last_Modified':[],
            'Note_Tags':[],
            'Note_Fields':[]
        }

        df_dict = self.db_to_dict(db, df_dict)
        df = pd.DataFrame(df_dict)

        # unix time -> normal time
        df['Note_ID'] = pd.to_datetime(df['Note_ID'],unit='ms').to_numpy()
        df['Note_Type_ID'] = pd.to_datetime(df['Note_Type_ID'],unit='ms').to_numpy()
        
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


    # --------------------------------------------------------------------------


    def reviews(self, extra_features=False, num_fields=None):
        """
        Get the Review History Table, and Join the Cards Table & Notes Table onto It
        """

        df = pd.merge(self.tbl_reviews(), self.tbl_cards(), on="Card_ID")
        df = pd.merge(df, self.tbl_notes(num_fields=num_fields), on="Note_ID")
        df = pd.merge(df, self.tbl_note_types(), on="Note_Type_ID")

        # are there any other tables that should be merged??

        if extra_features:
            df = self.field_to_words(df)

        return df


    def cards(
        self,
        note_types,
        num_fields=None,
        regex_remove=None,
        normal_remove=None,
        cache=False):
        """
        Get the Review History Table, and Join the Cards Table & Notes Table onto It
        """

        # query database if no df in cache, or if df in cache has wrong note-types
        if not(self.cards_cache) or self.cards_cache_note_types != note_types:
            df = pd.merge(
                self.tbl_cards(),
                self.tbl_reviews(extra_features=True)[[
                    'Card_ID', 'Card_Last_Know_Ease_Factor_As_Percentage',
                    'Card_Average_Review_Time_In_Seconds'
                ]],
                on="Card_ID"
            )
            df = pd.merge(df, self.tbl_notes(num_fields=num_fields), on="Note_ID")
            df = pd.merge(df, self.tbl_note_types(), on="Note_Type_ID")

            # are there any other tables that should be merged??

            # --------------------------------

            # extra_features:
            df = self.field_to_words(
                df,
                regex_remove=regex_remove,
                normal_remove=normal_remove
            )
            df = self.word_frequency(df)

            # --------------------------------

                        # filter notetypes
            df = df[df['Note_Type_Name'].isin(note_types)]

            # filter out cards that will adversly effect adjusted ease factor
            df = df[(df['Card_Last_Know_Ease_Factor_As_Percentage'] != 0) &
                    (df['Card_Total_Reviews_Including_Lapses'] > 6)]

            # --------------------------------

            # modify ease to get all cards to 85% retention rate (RR)
            # log(desired RR) / log(current RR) = new ease / current ease
            desired_RR = 0.85
            old_ease = df['Card_Last_Know_Ease_Factor_As_Percentage'].to_list()
            old_retention = df['Card_Reviews_Fraction_Correct'].to_list()
            new_ease = []
            for ease, retention in zip(old_ease, old_retention):
                if retention == 1:
                    ret = 0.90
                else:
                    ret = retention
                new_ease.append((math.log(desired_RR) / math.log(ret)) * ease)
            df['Card_Adjusted_Ease_Factor_As_Percentage'] = new_ease

        if cache:
            self.cards_cache = df
            self.cards_cache_note_types = note_types

        return df


    # --------------------------------------------------------------------------

    #                                PLOTTING

    # --------------------------------------------------------------------------


    # ---------------------------------BASE-------------------------------------


    def base_scatter_2ax(self, note_types, x1_axis, x2_axis, y_axis,
                         x1_label, x2_label, y_label,
                         add_conditional_notna=None):
        df = self.cards(note_types=note_types)

        # filter out rows with:
        #  • zero ease, as that means the card was never reviewed, 
        #    and thus has no data
        #  • < 7 reviews so the fraction_reviews_correct has more data to go on
        if add_conditional_notna:
            df = df[df[add_conditional_notna].notna()]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,10))

        # ----------------------------------------------------------------------

        # sort by x so line fit doesnt go crazy
        df = df.sort_values(x1_axis)
        x1 = df[x1_axis]
        y1 = df[y_axis]

        ax1.scatter(x1, y1, alpha=0.01)
        ax1.set_xlabel(x1_label, fontsize=16)
        ax1.set_ylabel(y_label, fontsize=16)

        # linear fit
        b, m = Polynomial.fit(x=x1, y=y1, deg=1).convert().coef
        ax1.plot(x1, m*x1 + b)

        # R² of linear fit
        r = np.corrcoef(x1, y1)[0,1]
        r2 = round(r**2, 4)
        at = AnchoredText(
            f"$y = {round(m, 3)}x + {round(b, 3)}$\n$R² = {r2}$",
            prop=dict(size=14), frameon=True,loc='upper right',
        )
        ax1.add_artist(at)

        # ----------------------------------------------------------------------

        # sort by x so line fit doesnt go crazy
        df = df.sort_values(x2_axis)
        x2 = df[x2_axis]
        y2 = df[y_axis]

        ax2.scatter(x2, y2, alpha=0.01)
        ax2.set_xlabel(x2_label, fontsize=16)

        # linear fit
        b, m = Polynomial.fit(x=x2, y=y2, deg=1).convert().coef
        ax2.plot(x2, m*x2 + b)

        # R² of linear fit
        r = np.corrcoef(x2, y2)[0,1]
        r2 = round(r**2, 4)
        at = AnchoredText(
            f"$y = {round(m, 3)}x + {round(b, 3)}$\n$R² = {r2}$",
            prop=dict(size=14), frameon=True,loc='upper right',
        )
        ax2.add_artist(at)


    # --------------------------------PLOTS-------------------------------------


    def plot_adjusted_ease_vs_field_length(self, note_types: list, field: int = 2):
        
        self.base_scatter_2ax(
            note_types=note_types,
            x1_axis= f'Note_Field_{field}_Stripped_Char_Count',
            x2_axis = f'Note_Field_{field}_Stripped_Word_Count',
            y_axis = 'Card_Adjusted_Ease_Factor_As_Percentage',
            x1_label = 'Character Count',
            x2_label = 'Word Count',
            y_label = 'Adjusted Ease Factor [%]'
        )


    def plot_average_answer_time_vs_field_length(self, note_types: list, field: int = 2):

        self.base_scatter_2ax(
            note_types=note_types,
            x1_axis= f'Note_Field_{field}_Stripped_Char_Count',
            x2_axis = f'Note_Field_{field}_Stripped_Word_Count',
            y_axis = 'Card_Average_Review_Time_In_Seconds',
            x1_label = 'Character Count',
            x2_label = 'Word Count',
            y_label = 'Average Time to Answer [Seconds]'
        )


    def plot_adjusted_ease_vs_word_frequency(self, note_types: list, field: int = 2):

        self.base_scatter_2ax(
            note_types=note_types,
            x1_axis= 'Note_Field_All_Lowest_Frequency_Word_From_Collection',
            x2_axis = 'Note_Field_All_Lowest_Frequency_Word_From_Global_Texts',
            y_axis = 'Card_Adjusted_Ease_Factor_As_Percentage',
            x1_label = 'Lowest Frequency Word in Note\n(Based on Frequencies in Anki Collection)',
            x2_label = 'Lowest Frequency Word in Note\n(Based on Global Text Frequencies)',
            y_label = 'Adjusted Ease Factor [%]',
            add_conditional_notna = 'Note_Field_All_Lowest_Frequency_Word_From_Global_Texts'
        )


    def plot_adjusted_ease_if_image_present(self, note_types):
        df = self.cards(note_types=note_types)

        # filter out rows with:
        #  • zero ease, as that means the card was never reviewed, 
        #    and thus has no data
        #  • < 7 reviews so the fraction_reviews_correct has more data to go on
        df = df[(df['Card_Adjusted_Ease_Factor_As_Percentage'] != 0) &
                (df['Card_Total_Reviews_Including_Lapses'] > 6)]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,10))

        # ----------------------------------------------------------------------

        y1 = [
            df[df['Note_Field_1_Has_Image'] == True]['Card_Adjusted_Ease_Factor_As_Percentage'],
            df[df['Note_Field_1_Has_Image'] == False]['Card_Adjusted_Ease_Factor_As_Percentage']
        ]

        ax1.violinplot(y1, showmeans=False, showmedians=True)
        ax1.set_xlabel('Question Has Image', fontsize=16)
        ax1.set_ylabel('Adjusted Ease Factor [%]', fontsize=16)
        ax1.set_xticks([1, 2])
        ax1.set_xticklabels(['True', 'False'])

        # ----------------------------------------------------------------------

        y2 = [
            df[df['Note_Field_2_Has_Image'] == True]['Card_Adjusted_Ease_Factor_As_Percentage'],
            df[df['Note_Field_2_Has_Image'] == False]['Card_Adjusted_Ease_Factor_As_Percentage']
        ]

        ax2.violinplot(y2, showmeans=False, showmedians=True)
        ax2.set_xlabel('Answer Has Image', fontsize=16)
        ax2.set_xticks([1, 2])
        ax2.set_xticklabels(['True', 'False'])


    def plot_answer_time_if_image_present(self, note_types):
        df = self.cards(note_types=note_types)

        # filter out rows with:
        #  • zero ease, as that means the card was never reviewed, 
        #    and thus has no data
        #  • < 7 reviews so the fraction_reviews_correct has more data to go on
        df = df[(df['Card_Adjusted_Ease_Factor_As_Percentage'] != 0) &
                (df['Card_Total_Reviews_Including_Lapses'] > 6)]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,10))

        # ----------------------------------------------------------------------

        y1 = [
            df[df['Note_Field_1_Has_Image'] == True]['Card_Average_Review_Time_In_Seconds'],
            df[df['Note_Field_1_Has_Image'] == False]['Card_Average_Review_Time_In_Seconds']
        ]

        ax1.violinplot(y1, showmeans=False, showmedians=True)
        ax1.set_xlabel('Question Has Image', fontsize=16)
        ax1.set_ylabel('Average Review Time per Card [Seconds]', fontsize=16)
        ax1.set_xticks([1, 2])
        ax1.set_xticklabels(['True', 'False'])

        # ----------------------------------------------------------------------

        y2 = [
            df[df['Note_Field_2_Has_Image'] == True]['Card_Average_Review_Time_In_Seconds'],
            df[df['Note_Field_2_Has_Image'] == False]['Card_Average_Review_Time_In_Seconds']
        ]

        ax2.violinplot(y2, showmeans=False, showmedians=True)
        ax2.set_xlabel('Answer Has Image', fontsize=16)
        ax2.set_xticks([1, 2])
        ax2.set_xticklabels(['True', 'False'])




