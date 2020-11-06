import pandas as pd
from datetime import datetime, timedelta

# Memory wise very inefficient better to use file I/O instead
def extend_end_datetime(user_discord_id, tipster_discord_id, period : int):
    try:
        df = pd.read_csv('subs_info.xlsx')
        
        df.loc[user_discord_id, tipster_discord_id] = str(datetime.strptime(
            df.loc[user_discord_id, tipster_discord_id], '%Y-%m-%d %H:%M:%S.%f')
            + timedelta(days=period))

        df.to_csv('subs_info.xlsx')
        return ['Extended Successfuly']
    except:
        return ["Unexpected Error at extent_end_datetime method"]

def fetch_tipster_lastdate(tipster_discord_id):
    try:
        df = pd.read_csv('subs_info.xlsx')
        return df.loc[tipster_discord_id]
    except:
        return ["error in fetch_tipster_info"]

def fetch_user_lastdate(user_discord_id):
    try:
        df = pd.read_csv('subs_info.xlsx')
        return df.loc[user_discord_id]
    except:
        return ["error in fetch_user_info"]

def remove_vip(user_discord_id, tipster_discord_id):
    try:
        df = pd.read_csv('subs_info.xlsx')
        
        df.loc[user_discord_id, tipster_discord_id] = "-1"

        df.to_csv('subs_info.xlsx')
        return 1
    except:
        return ["Unexpected Error at remove_vip method"]


def add_vip(user_discord_id, tipster_discord_id):
    # if user does not exist should add the user to the table and the service
    # if user exists should check if already subscribed if not should add the end date
    # if subscribed should return the last valid date of subscription
    # oversubscription or repeated subscription is not allowed
    return [False, "You do not have enough points"]