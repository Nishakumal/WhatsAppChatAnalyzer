import re
import pandas as pd


def preprocess(data):

    # WhatsApp format:
    # 7/12/25, 5:35 PM - Name: Message

    pattern = r'(\d{1,2}/\d{1,2}/\d{2}),\s(\d{1,2}:\d{2})\s*[AP]M\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Build proper records
    records = []
    for i in range(0, len(messages), 3):
        full_date = f"{messages[i]},{messages[i+1]}"
        time = messages[i+1]

        ampm_search = re.search(r'(AM|PM)', data)
        ampm = ampm_search.group(1) if ampm_search else ""

        date_string = f"{messages[i]} {messages[i+1]} {ampm}"

        msg = messages[i+2].strip()
        records.append([date_string, msg])

    df = pd.DataFrame(records, columns=['date', 'user_message'])

    # Convert date
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y %I:%M %p', errors='coerce')

    # Extract User & Message
    users = []
    messages_list = []

    for message in df['user_message']:
        parts = re.split(r'([^:]+):\s', message, maxsplit=1)
        if len(parts) > 2:
            users.append(parts[1])
            messages_list.append(parts[2])
        else:
            users.append('group_notification')
            messages_list.append(parts[0])

    df['user'] = users
    df['message'] = messages_list
    df.drop(columns=['user_message'], inplace=True)

    # Date columns
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Period column for heatmap
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(f"{hour}-{hour+1}")
    df['period'] = period

    return df
