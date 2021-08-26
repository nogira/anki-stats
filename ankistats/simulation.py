from .tables import *


def _simulation(
    days,
    X_ease,
    X_retention,
    X_due,
    X_interval, 
    new_cards_per_day,
    plot_sim=True,
    seed=1
    ):

    len_X = len(X_ease)
    cards = {i: {'ease': E, 'retention': R,'due': D, 'interval': I.days}
                for i, E, R, D, I in zip(
                    range(len_X),
                    X_ease,
                    X_retention,
                    X_due,
                    X_interval
                )}
    assert 0 in cards, f"Error: {cards}"

    # create a set of real-world card 'ease: retention' pairs to 
    # create/select new cards from
    new_card_pool = [(x['ease'], x['retention']) for x in cards.values()]

    np.random.seed(seed)
    random.seed(seed)

    def is_correct(card: dict) -> bool:
        """Check if card is correct"""
        #  gen rand num between 0 and 1 (uniform probability)
        rand = np.random.rand(1)
        return rand < cards[card]['retention']

    all_daily_reps = []

    for d in range(days):   #---------------- 1 LOOP PER DAY ---------------

        # add new cards to dict
        num_cards = len(cards)
        for i in range(new_cards_per_day):
            card_sample = random.sample(new_card_pool, k=1)[0]
            cards[i+num_cards] = {
                'ease': card_sample[0],
                'retention': card_sample[1],
                'due': 0,
                'interval': 0
            }

        # re-get number of cards so can loop through all
        num_cards = len(cards)

        for i in range(num_cards):   # --------- 1 LOOP PER CARD ---------------
            
            if cards[i]['due'] == 0:

                # if new card, ignore correct/false since you review new 
                # cards until remember
                if cards[i]['interval'] == 0:

                    cards[i]['interval'] = 1
                    cards[i]['due'] = 1

                    # ----------track reps----------
                    # add 2 reps since learning
                    all_daily_reps += [d, d]

                else:
                    # ----------track reps----------
                    all_daily_reps += [d]

                    # ---------- if card correct----------
                    if is_correct(i):
                        # need to round up so when cards < 200 ease have review 
                            # after 1 day interval, they don't get stuck in the 
                            # real ease hell
                        new_interval = int(np.ceil(cards[i]['interval'] * cards[i]['ease']))
                        cards[i]['interval'] = new_interval
                        cards[i]['due'] = new_interval
                    
                    # ---------- if card false----------
                    else:
                        cards[i]['interval'] = 1
                        cards[i]['due'] = 1

                        # ----tracking-----
                        # add another rep bc relearning
                        all_daily_reps += [d]


            # increment day of card by 1
            cards[i]['due'] -= 1

    if plot_sim:
        plt.figure(figsize=(16,10))

        plot = sns.histplot(all_daily_reps)
        # plt.title(f"Retention Rate {retention}, Ease Variable")
        plt.ylabel("Number of Reviews", fontsize=18)
        plt.xlabel("Days in the Future", fontsize=18)

        at = AnchoredText(
            f"Total Reps = {len(all_daily_reps)}",
            prop=dict(size=16), frameon=True,loc='upper right',
        )
        plot.add_artist(at)

    else:
        return len(all_daily_reps)


def _calculate_adjusted_ease(
    df,
    new_retention,
    retention_cap
    ) -> list:

    old_eases = df['Card_Last_Know_Ease_Factor'].to_list()
    old_retentions = df['Card_Reviews_Fraction_Correct'].to_list()

    new_eases = []
    for old_ease, old_ret in zip(old_eases, old_retentions):
        # to prevent the equation altering high retention cards too 
        # aggressively, cap the retention adjustment
        if old_ret > retention_cap: old_ret = retention_cap

        new_eases.append((np.log(new_retention) / np.log(old_ret)) * old_ease)

    return new_eases


def _calculate_adjusted_retention(
    df,
    new_ease,
    retention_cap
    ) -> list:

    old_eases = df['Card_Last_Know_Ease_Factor'].to_list()
    old_retentions = df['Card_Reviews_Fraction_Correct'].to_list()

    new_retentions = []
    for old_ease, old_ret in zip(old_eases, old_retentions):
        # to prevent the equation altering high retention cards too 
        # aggressively, cap the retention adjustment
        if old_ret > retention_cap: old_ret = retention_cap

        new_retentions.append(np.exp((new_ease/old_ease) * np.log(old_ret)))

    return new_retentions


def _simulate_init():
    df = cards()

    df = df[df.Card_Queue != 'Suspended']

    time_diff = df['Card_Due_Time'] - pd.Timestamp.now()
    X_due = time_diff.dt.days
    X_interval = df['Card_Last_Know_Interval']

    len_X = len(X_due)

    return df, X_due, X_interval, len_X


def simulate_no_changes(
    days=365,
    new_cards_per_day=0,
    plot_sim=True
    ):
    """
    Simulate future card reviews of your current unsuspended collection, 
    assuming the ease and retention rates stay the same. New cards will 
    randomly be assigned an ease-retention pair 
    from your existing cards.
    """
    df, X_due, X_interval, len_X = _simulate_init()

    X_ease = df.Card_Last_Know_Ease_Factor.to_list()
    X_retention = df.Card_Reviews_Fraction_Correct.to_list()

    return _simulation(days, X_ease, X_retention, X_due, X_interval,
    new_cards_per_day, plot_sim=plot_sim)


def simulate_uniform_retention(
    retention,
    retention_cap=0.9,
    days=365,
    new_cards_per_day=0,
    plot_sim=True
    ):
    """
    Simulate future card reviews of your current unsuspended collection, 
    assuming all cards' ease are adjusted to make each card's retention rate 
    the same. New cards will randomly be assigned an ease-retention pair 
    from your existing cards.
    """
    df, X_due, X_interval, len_X = _simulate_init()

    X_ease = _calculate_adjusted_ease(df, retention, retention_cap)
    X_retention = [retention for _ in range(len_X)]

    return _simulation(days, X_ease, X_retention, X_due, X_interval, 
    new_cards_per_day, plot_sim=plot_sim)


def simulate_uniform_ease(
    ease,
    retention_cap=0.9,
    days=365,
    new_cards_per_day=0,
    plot_sim=True
    ):
    """
    Simulate future card reviews of your current unsuspended collection, 
    assuming all cards' eases are adjusted to be the same. New cards will 
    randomly be assigned an ease-retention pair 
    from your existing cards.

    Ease input must be as a multiplier (i.e. if 250% ease, use 2.5)
    """
    df, X_due, X_interval, len_X = _simulate_init()

    X_ease = [ease for _ in range(len_X)]
    X_retention = _calculate_adjusted_retention(df, ease, retention_cap)

    return _simulation(days, X_ease, X_retention, X_due, X_interval, 
    new_cards_per_day, plot_sim=plot_sim)


# # this doesnt work !!
# def simulate_compare_all_3(days=365, new_cards_per_day=5):
#     min = int(0.7 * 1000)
#     max = int(0.90 * 1000)
#     retention_range = [x / 1000 for x in range(min, max, 1)]

#     retention_reps_tracker = []
#     for retention in retention_range:
#         retention_reps_tracker += [
#             simulate_uniform_retention(
#                 retention, days=days, new_cards_per_day=new_cards_per_day, 
#                 plot_sim=False)
#         ]
#     r_min_reps = min(retention_reps_tracker)
#     r_min_index = retention_reps_tracker.index(r_min_reps)
#     r_min_val = retention_range[r_min_index]

#     min = 200
#     max = 600
#     ease_range = [x for x in range(min, max, 1)]

#     ease_reps_tracker = []
#     for ease in ease_range:
#         # convert to ease as multiplier
#         ease = ease / 100

#         ease_reps_tracker += [
#             simulate_uniform_ease(
#                 ease, days=days, new_cards_per_day=new_cards_per_day, 
#                 plot_sim=False)
#         ]
#     e_min_reps = min(ease_reps_tracker)
#     e_min_index = ease_reps_tracker.index(e_min_reps)
#     e_min_val = ease_range[e_min_index]

#     return pd.DataFrame({'Type': ['No Change', 'Uniform Ease', 'Uniform Retention'],
#     'Min Reps': [
#         simulate_uniform_ease(
#                 ease, days=days, new_cards_per_day=new_cards_per_day, 
#                 plot_sim=False),
#         e_min_reps,
#         r_min_reps
#     ], 'Ease-Factor/Retention': [np.nan, e_min_val, r_min_val]})


def _simulate_uniform_ease_uniform_retention_from_scratch(
    ease,
    retention, 
    days=365,
    new_cards_per_day=5,
    seed=1
    ):

    X_ease = [ease]
    X_retention = [retention]
    X_due = [0]
    X_interval = [pd.Timedelta("0 days")]

    reps = _simulation(days, X_ease, X_retention, X_due, X_interval, 
                        new_cards_per_day, plot_sim=False, seed=seed)
    return reps


def simulate_optimal_ease_per_memory_strength_from_scratch(
    ease,
    retention,
    days=365, 
    new_cards_per_day=5,
    min_retention=0.6,
    max_retention=0.9
    ):
    """
    Perform a simulation to work out the optimal retention rate (and thus 
    ease factor) for each memory strength value, defined as:

    memory_strength = - ease_factor / ln(retention_rate)
    """
    min = int(min_retention * 1000)
    max = int(max_retention * 1000)
    retention_range = [x / 1000  for x in range(min, max, 1)]

    reps_tracker = []
    for new_retention in retention_range:
        new_ease = (np.log(new_retention) / np.log(retention)) * ease

        reps_tracker += [
            _simulate_uniform_ease_uniform_retention_from_scratch(
                new_ease, new_retention, days=days,
                new_cards_per_day=new_cards_per_day)
        ]

    plt.figure(figsize=(16,10))
    plt.plot(retention_range, reps_tracker,
        label=f"Memory Strength of {ease} Ease Factor, {int(retention * 100)}% Retention",
        color="#B06DD8")
    plt.xlabel("Retention Rate", fontsize=18)
    plt.ylabel("Number of Reviews", fontsize=18)
    plt.title("Number of Simulated Reps Per Retention Rate after a Period of Days", fontsize=22)
    plt.legend(loc=9, fontsize=16)

