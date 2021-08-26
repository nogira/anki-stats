from .tables import *


# --------------------------------------------------------------------------

#                                    BASE

# --------------------------------------------------------------------------


def base_scatter_2ax(
    note_types,
    x1_axis,
    x2_axis,
    y_axis,
    x1_label,
    x2_label,
    y_label,
    add_conditional_notna=None
    ):
    df = cards(note_types=note_types)

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

    ax1.scatter(x1, y1, alpha=0.1)
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

    ax2.scatter(x2, y2, alpha=0.1)
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


def plot_adjusted_ease_vs_field_length(
    note_types: list,
    field: int = 2
    ):
    
    base_scatter_2ax(
        note_types=note_types,
        x1_axis= f'Note_Field_{field}_Stripped_Char_Count',
        x2_axis = f'Note_Field_{field}_Stripped_Word_Count',
        y_axis = 'Card_Adjusted_Ease_Factor',
        x1_label = 'Character Count',
        x2_label = 'Word Count',
        y_label = 'Adjusted Ease Factor'
    )


def plot_average_answer_time_vs_field_length(
    note_types: list,
    field: int = 2
    ):

    base_scatter_2ax(
        note_types=note_types,
        x1_axis= f'Note_Field_{field}_Stripped_Char_Count',
        x2_axis = f'Note_Field_{field}_Stripped_Word_Count',
        y_axis = 'Card_Average_Review_Time',
        x1_label = 'Character Count',
        x2_label = 'Word Count',
        y_label = 'Average Time to Answer [Seconds]'
    )


def plot_adjusted_ease_vs_word_frequency(
    note_types: list,
    field: int = 2
    ):

    base_scatter_2ax(
        note_types=note_types,
        x1_axis= 'Note_Field_All_Lowest_Frequency_Word_From_Collection',
        x2_axis = 'Note_Field_All_Lowest_Frequency_Word_From_Global_Texts',
        y_axis = 'Card_Adjusted_Ease_Factor',
        x1_label = 'Lowest Frequency Word in Note\n(Based on Frequencies in Anki Collection)',
        x2_label = 'Lowest Frequency Word in Note\n(Based on Global Text Frequencies)',
        y_label = 'Adjusted Ease Factor',
        add_conditional_notna = 'Note_Field_All_Lowest_Frequency_Word_From_Global_Texts'
    )


def plot_adjusted_ease_if_image_present(
    note_types
    ):

    df = cards(note_types=note_types)

    # filter out rows with:
    #  • zero ease, as that means the card was never reviewed, 
    #    and thus has no data
    #  • < 7 reviews so the fraction_reviews_correct has more data to go on
    df = df[(df['Card_Adjusted_Ease_Factor'] != 0) &
            (df['Card_Total_Reviews_Including_Lapses'] > 6)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,10))

    # ----------------------------------------------------------------------

    y1 = [
        df[df['Note_Field_1_Has_Image'] == True]['Card_Adjusted_Ease_Factor'],
        df[df['Note_Field_1_Has_Image'] == False]['Card_Adjusted_Ease_Factor']
    ]

    ax1.violinplot(y1, showmeans=False, showmedians=True)
    ax1.set_xlabel('Question Has Image', fontsize=16)
    ax1.set_ylabel('Adjusted Ease Factor', fontsize=16)
    ax1.set_xticks([1, 2])
    ax1.set_xticklabels(['True', 'False'])

    # ----------------------------------------------------------------------

    y2 = [
        df[df['Note_Field_2_Has_Image'] == True]['Card_Adjusted_Ease_Factor'],
        df[df['Note_Field_2_Has_Image'] == False]['Card_Adjusted_Ease_Factor']
    ]

    ax2.violinplot(y2, showmeans=False, showmedians=True)
    ax2.set_xlabel('Answer Has Image', fontsize=16)
    ax2.set_xticks([1, 2])
    ax2.set_xticklabels(['True', 'False'])


def plot_answer_time_if_image_present(
    note_types
    ):

    df = cards(note_types=note_types)

    # filter out rows with:
    #  • zero ease, as that means the card was never reviewed, 
    #    and thus has no data
    #  • < 7 reviews so the fraction_reviews_correct has more data to go on
    df = df[(df['Card_Adjusted_Ease_Factor'] != 0) &
            (df['Card_Total_Reviews_Including_Lapses'] > 6)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,10))

    # ----------------------------------------------------------------------

    y1 = [
        df[df['Note_Field_1_Has_Image'] == True]['Card_Average_Review_Time'],
        df[df['Note_Field_1_Has_Image'] == False]['Card_Average_Review_Time']
    ]

    ax1.violinplot(y1, showmeans=False, showmedians=True)
    ax1.set_xlabel('Question Has Image', fontsize=16)
    ax1.set_ylabel('Average Review Time per Card [Seconds]', fontsize=16)
    ax1.set_xticks([1, 2])
    ax1.set_xticklabels(['True', 'False'])

    # ----------------------------------------------------------------------

    y2 = [
        df[df['Note_Field_2_Has_Image'] == True]['Card_Average_Review_Time'],
        df[df['Note_Field_2_Has_Image'] == False]['Card_Average_Review_Time']
    ]

    ax2.violinplot(y2, showmeans=False, showmedians=True)
    ax2.set_xlabel('Answer Has Image', fontsize=16)
    ax2.set_xticks([1, 2])
    ax2.set_xticklabels(['True', 'False'])


# --------------------------------------------------------------------------


#                         non-generalised plots


# ak.simulate_optimal_ease_per_memory_strength(250, 0.85, days=365, new_cards_per_day=5)


# def simulate_optimal_ease_per_memory_strength(ease, retention, days=365, 
#                                                         new_cards_per_day=5):
#     # min_retention = 0.600
#     # max_retention = 0.949
#     retention_range = [x / 1000  for x in range(600, 900, 1)]

#     reps_tracker1 = []
#     reps_tracker2 = []
#     reps_tracker3 = []
#     for new_retention in retention_range:
#         new_ease = (np.log(new_retention) / np.log(retention)) * ease

#         reps_tracker1 += [
#             _simulate_uniform_ease_uniform_retention_from_scratch(
#                 new_ease, new_retention, days=days, new_cards_per_day=new_cards_per_day, seed=1
#             )
#         ]
#         reps_tracker2 += [
#             _simulate_uniform_ease_uniform_retention_from_scratch(
#                 new_ease, new_retention, days=50, new_cards_per_day=new_cards_per_day, seed=1
#             )
#         ]
#         reps_tracker3 += [
#             _simulate_uniform_ease_uniform_retention_from_scratch(
#                 new_ease, new_retention, days=100, new_cards_per_day=new_cards_per_day, seed=1
#             )
#         ]

#     plt.figure(figsize=(16,10))
#     plt.plot(retention_range, reps_tracker1, label="365 Days", color="#B06DD8")
#     plt.xlabel("Retention Rate", fontsize=18)
#     plt.ylabel("Number of Reviews", fontsize=18)
#     plt.title("Number of Simulated Reps Per Retention Rate after a Period of Days\nFor Cards at Memory Strength of 2.5 Ease Factor, 85% Retention", fontsize=22)
#     plt.yticks(color="#B06DD8")   # blue
#     plt.twinx()
#     plt.plot(retention_range, reps_tracker3, label="100 Days", color="#D86D6D")
#     plt.yticks(color="#D86D6D")   # red
#     plt.ylim(top=5000)
#     plt.twinx()
#     plt.plot(retention_range, reps_tracker2, label="50 Days", color="#D8D06D")
#     plt.yticks(color="#D8D06D")   # yellow
#     plt.ylim(top=2100)
#     plt.plot([], [], label="100 Days", color="#D86D6D")
#     plt.plot([], [], label="365 Days", color="#B06DD8")
#     plt.legend(loc=9, fontsize=16)


# def simulate_optimal_ease_per_memory_strength(ease, retention, days=365, 
#                                                         new_cards_per_day=5):
#     # min_retention = 0.600
#     # max_retention = 0.949
#     retention_range = [x / 1000  for x in range(600, 900, 1)]

#     reps_tracker1 = []
#     reps_tracker2 = []
#     for new_retention in retention_range:
#         new_ease = (np.log(new_retention) / np.log(retention)) * ease

#         reps_tracker1 += [
#             _simulate_uniform_ease_uniform_retention_from_scratch(
#                 new_ease, new_retention, days=100, new_cards_per_day=new_cards_per_day, seed=1
#             )
#         ]
#         reps_tracker2 += [
#             _simulate_uniform_ease_uniform_retention_from_scratch(
#                 new_ease, new_retention, days=100, new_cards_per_day=new_cards_per_day, seed=100
#             )
#         ]

#     plt.figure(figsize=(16,10))
#     plt.plot(retention_range, reps_tracker1, label="Seed = 100", color="#B06DD8")
#     plt.xlabel("Retention Rate", fontsize=18)
#     plt.ylabel("Number of Reviews", fontsize=18)
#     plt.title("Number of Simulated Reps Per Retention Rate after a Period of Days\nFor Cards at Memory Strength of 2.5 Ease Factor, 85% Retention", fontsize=22)
#     plt.yticks(color="#B06DD8")   # blue
#     plt.twinx()
#     plt.plot(retention_range, reps_tracker2, label="Seed = 1", color="#D8D06D")
#     plt.yticks(color="#D8D06D")   # yellow
#     plt.plot([], [], label="Seed = 100", color="#B06DD8")
#     plt.legend(loc=9, fontsize=16)


# def simulate_optimal_ease_per_memory_strength(ease, retention, days=365, 
#                                                         new_cards_per_day=5):
#     # min_retention = 0.600
#     # max_retention = 0.949
#     retention_range = [x / 1000  for x in range(600, 900, 1)]

#     reps_tracker1 = []
#     reps_tracker2 = []
#     for new_retention in retention_range:
#         new_ease = (np.log(new_retention) / np.log(retention)) * ease

#         reps_tracker1 += [
#             _simulate_uniform_ease_uniform_retention_from_scratch(
#                 new_ease, new_retention, days=100, new_cards_per_day=5, seed=1
#             )
#         ]
#         reps_tracker2 += [
#             _simulate_uniform_ease_uniform_retention_from_scratch(
#                 new_ease, new_retention, days=100, new_cards_per_day=10, seed=1
#             )
#         ]

#     plt.figure(figsize=(16,10))
#     plt.plot(retention_range, reps_tracker1, label="5 New Cards per Day", color="#B06DD8")
#     plt.xlabel("Retention Rate", fontsize=18)
#     plt.ylabel("Number of Reviews", fontsize=18)
#     # plt.xlim(top=)
#     plt.title("Number of Simulated Reps Per Retention Rate after a Period of Days\nFor Cards at Memory Strength of 2.5 Ease Factor, 85% Retention", fontsize=22)
#     plt.yticks(color="#B06DD8")   # blue
#     plt.twinx()
#     plt.plot(retention_range, reps_tracker2, label="10 New Cards per Day", color="#D8D06D")
#     plt.yticks(color="#D8D06D")   # yellow
#     plt.plot([], [], label="5 New Cards per Day", color="#B06DD8")
#     plt.legend(loc=9, fontsize=16)


# def simulate_optimal_ease_per_memory_strength(ease, retention, days=365, 
#                                                         new_cards_per_day=5):
#     # min_retention = 0.600
#     # max_retention = 0.949
#     retention_range = [x / 1000  for x in range(600, 900, 1)]

#     reps_tracker1 = []
#     reps_tracker2 = []
#     for new_retention in retention_range:
#         new_ease = (np.log(new_retention) / np.log(retention)) * ease

#         reps_tracker1 += [
#             _simulate_uniform_ease_uniform_retention_from_scratch(
#                 new_ease, new_retention, days=100, new_cards_per_day=5, seed=1
#             )
#         ]

#     for new_retention in retention_range:
#         new_ease = (np.log(new_retention) / np.log(retention)) * (ease+200)

#         reps_tracker2 += [
#             _simulate_uniform_ease_uniform_retention_from_scratch(
#                 new_ease, new_retention, days=100, new_cards_per_day=10, seed=1
#             )
#         ]

#     plt.figure(figsize=(16,10))
#     plt.plot(retention_range, reps_tracker1, label="Memory Strength of 2.5 Ease Factor, 85% Retention", color="#B06DD8")
#     plt.xlabel("Retention Rate", fontsize=18)
#     plt.ylabel("Number of Reviews", fontsize=18)
#     plt.title("Number of Simulated Reps Per Retention Rate after a Period of Days\nFor Cards at Different Memory Strengths", fontsize=22)
#     plt.yticks(color="#B06DD8")   # blue
#     plt.twinx()
#     plt.plot(retention_range, reps_tracker2, label="Memory Strength of 4.5 Ease Factor, 85% Retention", color="#D8D06D")
#     plt.yticks(color="#D8D06D")   # yellow
#     plt.ylim(top=7600)
#     plt.plot([], [], label="Memory Strength of 2.5 Ease Factor, 85% Retention", color="#B06DD8")
#     plt.legend(loc=9, fontsize=16)

