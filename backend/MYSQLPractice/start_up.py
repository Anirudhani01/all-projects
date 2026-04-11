from mysql.connector import connect
import pandas as pd
import pprint

_connection=connect(host='localhost',
                                user='anirudh',
                                password='password123',
                                database='tempdb')
_cursor=_connection.cursor()
_data=pd.read_csv('/home/anirudh/MYSQLPractice/sample_db_data.csv')
print(_data)
act_data = [list(_data[_rec]) for  _rec in _data]
columns_data=list(_data)
print(columns_data)
pprint.pprint(act_data)


def insert_data_into_database():
    _query="""CREATE TABLE IF NOT EXISTS temp_data1 (
                                                Eid INT, 
                                                Name VARCHAR(100), 
                                                Company VARCHAR(100)
                                                );"""
    _cursor.execute(_query)
    for rec in list(zip(act_data[0],act_data[1],act_data[2])):
        print(rec)
        _query_one='INSERT INTO temp_data1 (Eid,Name,Company) VALUES(%s,%s,%s);'
        _cursor.execute(_query_one,rec)
    
#Read the existing data    
       
def read_data_into_database(eid,*args,**kwargs):
    print(eid)
    _query='select * from temp_data1 where Eid = (%s);' %eid
    _cursor.execute(_query)
    _data=list(_cursor)
    return _data  

#update the existing data

def update_data_into_database(pay_load,*args,**kwargs):
    _query='update temp_data1 set Name="%s", Company="%s" where Eid="%s";'\
                %(pay_load['Name'],pay_load['Company'],pay_load['Eid'])
    _cursor.execute(_query)
 
# update_data_into_database(pay_load={'Eid':6,'Name':'anirudh','Company':'abcd'})   

#Delete the existing data

def delete_data_from_the_database(eid,*args,**kwargs):
    _query='delete from temp_data1 where Eid="%s";' %eid
    _cursor.execute(_query)
    
delete_data_from_the_database(eid=1)


# insert_data_into_database()
# _data_id = read_data_into_database(5)
# print(_data_id)
_connection.commit()
_connection.close()
#_cursor=_connection.execute('')