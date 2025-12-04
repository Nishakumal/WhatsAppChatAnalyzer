from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

# ---------------------------------------------------------
# BASIC STATS
# ---------------------------------------------------------

def fetch_stats(selected_user, df):

    # FIX: ensure message is string always
    df["message"] = df["message"].astype(str)

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    num_messages = df.shape[0]

    words = []
    for message in df["message"]:
        words.extend(message.split())

    # WhatsApp media messages (FIX applied)
    num_media_messages = df[df["message"].str.contains("Media omitted", case=False, na=False)].shape[0]

    # URL extraction
    links = []
    for message in df["message"]:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


# ---------------------------------------------------------
# BUSIEST USERS
# ---------------------------------------------------------

def most_busy_users(df):
    x = df["user"].value_counts().head()

    percent_df = (
        df["user"].value_counts(normalize=True) * 100
    ).round(2).reset_index()

    percent_df.columns = ["name", "percent"]

    return x, percent_df


# ---------------------------------------------------------
# WORDCLOUD
# ---------------------------------------------------------

def create_wordcloud(selected_user, df):

    df["message"] = df["message"].astype(str)

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    temp = df[df["user"] != "group_notification"]
    temp = temp[~temp["message"].str.contains("Media omitted", na=False)]

    stop_words = open("stop_hinglish.txt", "r", encoding="utf-8").read().split()

    def remove_stop_words(message):
        words = []
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
        return " ".join(words)

    temp["clean"] = temp["message"].apply(remove_stop_words)

    wc = WordCloud(width=500, height=500, background_color="white")
    df_wc = wc.generate(temp["clean"].str.cat(sep=" "))

    return df_wc


# ---------------------------------------------------------
# MOST COMMON WORDS
# ---------------------------------------------------------

def most_common_words(selected_user, df):

    df["message"] = df["message"].astype(str)

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    temp = df[df["user"] != "group_notification"]
    temp = temp[~temp["message"].str.contains("Media omitted", na=False)]

    stop_words = open("stop_hinglish.txt", "r", encoding="utf-8").read().split()

    words = []

    for message in temp["message"]:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    common_df = pd.DataFrame(Counter(words).most_common(20))

    return common_df


# ---------------------------------------------------------
# EMOJI ANALYSIS
# ---------------------------------------------------------

def emoji_helper(selected_user, df):

    df["message"] = df["message"].astype(str)

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    emojis = []

    for message in df["message"]:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    return pd.DataFrame(Counter(emojis).most_common())


# ---------------------------------------------------------
# TIMELINES
# ---------------------------------------------------------

def monthly_timeline(selected_user, df):

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    timeline = df.groupby(["year", "month_num", "month"]).count()["message"].reset_index()

    timeline["time"] = timeline["month"] + "-" + timeline["year"].astype(str)

    return timeline


def daily_timeline(selected_user, df):

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    return df.groupby("only_date").count()["message"].reset_index()


# ---------------------------------------------------------
# ACTIVITY MAPS
# ---------------------------------------------------------

def week_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]
    return df["day_name"].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]
    return df["month"].value_counts()


def activity_heatmap(selected_user, df):

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    heatmap = df.pivot_table(
        index="day_name",
        columns="period",
        values="message",
        aggfunc="count",
        fill_value=0
    )

    return heatmap
