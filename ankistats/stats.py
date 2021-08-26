from .tables import *


def stats_lapse_retention(
    start_date: str = "",
    end_date: str = ""
    ):
    """
    Get the percentage of corrent answers.

    Date input in the format of "DD-MM-YY"
    """

    df = tbl_reviews()

    if start_date:
        date = pd.to_datetime(start_date, format="%d-%m-%y")
        df = df[df.Review_ID > date]
    
    if end_date:
        date = pd.to_datetime(end_date, format="%d-%m-%y")
        df = df[df.Review_ID < date]


    track_lapses = []
    wrong_count = 0
    right_count = 0

    def track_lapse_stats(row) -> None:
        nonlocal track_lapses
        nonlocal wrong_count
        nonlocal right_count

        is_relearning = row['Review_Type'] == 'Relearning'
        if is_relearning:
            track_lapses.append(row['Card_ID'])
        
        # the very next review after card_ID is stored will be the first review 
        # after relearning
        # however, to make sure the card hasnt seen reset to new, check the card 
        # isnt new (i.e. 'Learning'). if new, remove card from list
        elif row['Card_ID'] in track_lapses:
            if row['Review_Type'] == 'Learning':
                track_lapses.remove(row['Card_ID'])
            elif row['Review_Answer'] == 'Wrong':
                wrong_count += 1
            else:
                right_count += 1
                track_lapses.remove(row['Card_ID'])

    df.apply(track_lapse_stats, axis=1)

    print("Right:", right_count)
    print("Wrong:", wrong_count)
    print("Fraction Correct:", right_count / (right_count + wrong_count))


def stats_learning_graduation_retention(
    graduation_interval,
    pre_graduation_interval,
    start_date: str = "",
    end_date: str = ""
    ):
    """
    Get the percentage of corrent answers on learning graduation intervals.

    graduation_interval and pre_graduation_interval in the format "4 days", 
    "10 min", etc

    Date input in the format of "DD-MM-YY"
    """

    df = tbl_reviews()

    if start_date:
        date = pd.to_datetime(start_date, format="%d-%m-%y")
        df = df[df.Review_ID > date]
    
    if end_date:
        date = pd.to_datetime(end_date, format="%d-%m-%y")
        df = df[df.Review_ID < date]


    track_lapses = []
    wrong_count = 0
    right_count = 0

    def track_lapse_stats(row) -> None:
        nonlocal track_lapses
        nonlocal wrong_count
        nonlocal right_count

        is_learning = row['Review_Type'] == 'Learning'
        is_last_step = (
            row['Review_New_Interval'] == pd.Timedelta(graduation_interval) and 
            row['Review_Last_Interval'] == pd.Timedelta(pre_graduation_interval)
        )
        if is_learning and is_last_step:
            track_lapses.append(row['Card_ID'])
        
        # the very next review after card_ID is stored will be the first review 
        # after learning
        # however, to make sure the card hasnt seen reset to new, check the card 
        # isnt new (i.e. 'Learning'). if new, remove card from list
        elif row['Card_ID'] in track_lapses:
            if row['Review_Type'] == 'Learning':
                track_lapses.remove(row['Card_ID'])
            elif row['Review_Answer'] == 'Wrong':
                wrong_count += 1
            else:
                right_count += 1
                track_lapses.remove(row['Card_ID'])

    df.apply(track_lapse_stats, axis=1)

    print("Right:", right_count)
    print("Wrong:", wrong_count)
    print("Fraction Correct:", right_count / (right_count + wrong_count))

