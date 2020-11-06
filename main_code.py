import connection_db as db
import subscriber_map
from datetime import datetime, timedelta
import subscriber_map as smap



############## Tipster Functions ##############


# work is pending in this
def update_tipster(tipster_discord_id, tipster_message_id, tipster_price: int, period: int, points: int):
    
    cur = db.cnx.cursor()
    
    cur.execute(f'''
    select tipster_discord_id from tipster_data 
    where tipster_discord_id = {tipster_discord_id};
    ''')
    
    myres = cur.fetchall()

    if not len(myres):
        cur.execute(f'''
        insert into tipster_data values({tipster_discord_id}, {tipster_message_id},
        "{str(datetime.now() + timedelta(days = period))}", {points}, {tipster_price});
        ''')
        
    else:

        cur.execute(f'''
        select tipster_period from tipster_data
        where tipster_discord_id = {tipster_discord_id};
        ''')
        
        myres = cur.fetchall()
        # Have to write the datetime part of this logic

        cur.execute(f'''
        update tipster_data set tipster_period = 
        "{str(datetime.now() + timedelta(days = period))}", 
        tipster_points = {points}, tipster_price = {tipster_price} 
        where tipster_discord_id = {tipster_discord_id};
        ''')
        
    db.cnx.commit()

def del_tipster(tipster_discord_id):

    cur = db.cnx.cursor()

    cur.execute(f"""
    DELETE FROM tipster_data WHERE tipster_discord_id = {tipster_discord_id};
    """)

    db.cnx.commit()

def set_tipster_price(tipster_discord_id, price: int):
    cur = db.cnx.cursor()

    cur.execute(f"""
    update tipster_data set tipster_price={price} 
    where tipster_discord_id = {tipster_discord_id};
    """)

    db.cnx.commit()

def set_tipster_period(tipster_discord_id, period: int):
    cur = db.cnx.cursor()

    cur.execute(f"""
    update tipster_data set tipster_period={period} 
    where tipster_discord_id = {tipster_discord_id};
    """)

    db.cnx.commit()

def set_tipster_points(tipster_discord_id, points : int):
    cur = db.cnx.cursor()

    cur.execute(f"""
    update tipster_data set tipster_points={points} 
    where tipster_discord_id = {tipster_discord_id};
    """)

    db.cnx.commit()

def show_tipster_info(tipster_discord_id):
    cur = db.cnx.cursor()

    cur.execute(f"""
    select * from tipster_data 
    where tipster_discord_id = {tipster_discord_id};
    """)

    return cur.fetchall()

def discord_to_msg_id(tipster_discord_id):
    cur = db.cnx.cursor()

    cur.execute(f"""
    select tipster_message_id from tipster_data 
    where tipster_discord_id = {tipster_discord_id};
    """)

    return cur.fetchall()

def msg_to_discord_id(msg_id: int):
    cur = db.cnx.cursor()

    cur.execute(f"""
    select tipster_discord_id from tipster_data 
    where tipster_message_id = {msg_id};
    """)

    return cur.fetchall()



############## User Functions ##############


def set_user_points(user_discord_id, points: int):
    cur = db.cnx.cursor()

    cur.execute(f'''
    select user_discord_id from user_data
    where user_discord_id = {user_discord_id};
    ''')

    myres = cur.fetchall()

    if not len(myres):
        cur.execute(f'''
        insert into user_data values(
        {user_discord_id}, {points});
        ''')

    else:
        cur.execute(f"""
        update user_data set user_points={points} 
        where user_discord_id = {user_discord_id};
        """)

    db.cnx.commit()

def show_user_points(user_discord_id):
    cur = db.cnx.cursor()

    cur.execute(f"""
    select user_points from user_data 
    where user_discord_id = {user_discord_id};
    """)

    x = cur.fetchall()

    db.cnx.commit()

    return x

def del_user(user_discord_id):

    cur = db.cnx.cursor()

    cur.execute(f"""
    DELETE FROM user_data WHERE user_discord_id = {user_discord_id};
    """)

    db.cnx.commit()

def add_vip_days(user_discord_id, tipster_discord_id, period: int):
    smap.extend_end_datetime(user_discord_id, tipster_discord_id, period)