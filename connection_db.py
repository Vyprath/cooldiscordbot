import mysql.connector as sql

# Connection to DB
print('Attempting Connection to DB...')

try:
    cnx = sql.connect(host='localhost', user='Vyprath',
    passwd='skiddy123', database='test', auth_plugin='mysql_native_password')
    print('Connection Succesful...')

except sql.Error as err:
    if err.errno == sql.errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == sql.errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print("Unresolved error : " + str(err))
    exit(1)

else:
    # main code
    cusr = cnx.cursor()

    create_tipster_data = """
        create table tipster_data (
        tipster_discord_id bigint primary key,
        tipster_message_id bigint,
        tipster_period varchar(40),
        tipster_points int,
        tipster_price int);
        """

    create_user_data = """
        create table user_data (
        user_discord_id bigint primary key,
        user_points int);
        """
    
    # Table creation/establishment if not existing
    try:
        cusr.execute(create_tipster_data)
    except sql.Error as err:
        print('Caught error : ' + str(err) + '\nBypassed...')
    else:
        print('tipster_data Created')

    try:
        cusr.execute(create_user_data)  
    except sql.Error as err:
        print('Caught error : ' + str(err) + '\nBypassed...')
    else:
        print('user_data Created')

def close_connection2db(cnx):
    print('Closing Connection to DB...')
    cnx.close()