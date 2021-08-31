from .tables import *


# ------------------------------------------------------------------------------

# the purpose of functions in this file is to derive deck settings, and 
# changes to deck settings, from the revision log

# ------------------------------------------------------------------------------


def config_history():
    df = tbl_reviews()

    dict_config = {   # setting: {datetime: value, datetime: value, ..etc}
        'Starting Ease': _get_starting_ease(df)
    }

    return _dict_config_to_df(dict_config)

    # return a df that has a col for each config option, and a new line 
    # everytime a config changes


def _dict_config_to_df(dict_input):
    settings = dict_input.keys()

    # get all dates
    unique_dates = set()
    for setting in settings:
        for entry in dict_input[setting].keys():
            unique_dates.add(entry)

    dict_config = defaultdict(list)

    for date in unique_dates:
        dict_config['Date'] += [date]
        for setting in settings:
            if date in dict_input[setting]:
                dict_config[setting] += [dict_input[setting][date]]
            else:
                dict_config[setting] += [np.nan]

    df_config = pd.DataFrame(dict_config)

    return df_config


def _get_starting_ease(df):
    starting_ease = {}
    last_ease = 0.0

    def go(row):
        nonlocal last_ease
        ease = row['Review_New_Ease_Factor']
        is_learning = row['Review_Type'] == 'Learning'
        has_ease = ease != 0
        ease_has_changed = ease != last_ease
        if is_learning and has_ease and ease_has_changed:
            time = row['Review_ID']
            starting_ease[time] = ease

            last_ease = ease

    df.apply(go, axis=1)

    return starting_ease