import pandas as pd
import json
from mysql.connector import connect


class DatabaseOperations(object):
    def connect_to_database(self):
        with open('db_credentials.json','r') as f:
            _creds=json.load(f)
        _connection=connect(host=_creds['host'],
                             user=_creds['username'],
                             password=_creds['password'],
                             database=_creds['database'])
        _cursor=_connection.cursor()
        return _cursor,_connection
                  
    def insert_student_data(self): 
        students_data = pd.read_csv('student_marks.csv')
        _columns = list(students_data)
        data= [list(students_data[_rec]) for _rec in students_data]
        final_stu_data= list(zip(*data))
        _query = f'create table if not exists student_data ({_columns[0]} INT,\
                {_columns[1]} VARCHAR(55),\
                {_columns[2]} INT,\
                {_columns[3]} INT)'
        _cursor, connection = self.connect_to_database()
        _query = f'insert into student_data ({_columns[0]}, {_columns[1]}, {_columns[2]}, {_columns[3]}) values (%s, %s, %s, %s)'
        for record in final_stu_data:
            _cursor.execute(_query, record)
        connection.commit()
        connection.close()
    def drop_tables(self):
        connection, cursor = self.connect_to_database()
        if connection is None:
            return
        cursor, connection = self.connect_to_database()
        query = 'Drop table students_data;'
        cursor.execute(query)
        query_one = 'Drop table subjects_data;'
        cursor.execute(query_one)
        connection.commit()
        connection.close()
    def insert_faculty(self):
        pass
    def insert_subject_data(self):
        faculty_data=pd.read_csv("subjects.csv")
        _columns=list(faculty_data)
        print(_columns)
        _data=[list(faculty_data[_rec]) for _rec in faculty_data]
        print(_data)
        final_stu_data=list(zip(*_data))
        #print(final_stu_data)
        _query=f'CREATE TABLE IF NOT EXISTS faculty_data({_columns[0]} INT,\
                                                           {_columns[1]} VARCHAR(100),\
                                                            {_columns[2]} VARCHAR(100));'
                
        _cursor,_connection=self.connect_to_database()
        _cursor.execute(_query)
        for _rec in final_stu_data:
            print(_rec)
            _query_one=f'insert into faculty_data ({_columns[0]},{_columns[1]},{_columns[2]}) values (%s,%s,%s);'
            _cursor.execute(_query_one,_rec)
        _connection.commit()
        _connection.close()

class AcademicReport(DatabaseOperations):
    def first_problem(self):
        cursor,connection = self.connect_to_database()
        query = '''
                    select sub.faculty_name
                    from subjects_data sub 
                    join 
                    students_data stu 
                    on sub.subject_id = stu.subject_id
                    where stu.marks > 90
                    group by sub.faculty_name
                    order by count(*) desc
                    limit 1;
                '''
        cursor.execute(query)
        result = list(cursor)
        connection.close()
        return result
    def second_problem(self):
        cursor,connection = self.connect_to_database()
        query = '''
                   select sub.faculty_name
                    from subjects_data sub 
                    join 
                    students_data stu 
                    on sub.subject_id = stu.subject_id
                    where stu.marks > 40
                    group by sub.faculty_name
                    order by count(*) desc
                    limit 1; 

                '''
        cursor.execute(query)
        result = list(cursor)
        connection.close()
        return result
    





o=DatabaseOperations().insert_student_data()