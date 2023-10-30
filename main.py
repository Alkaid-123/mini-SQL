import re
import os
import datetime

database='test'

def inputCommand():
    command=''
    while command=='':
        command=input("sql> ")
    command+=';'
    command=re.sub(r'[\s]+',' ',command)
    command=command.lower()
    print(command)
    return command


def checkCommand(command):
    create_database = re.compile(r'create database [\w]+[\s]*;')
    use_database = re.compile(r'use [\w]+[\s]*;')
    return_database = re.compile(r'return[\s]*;')
    create_table = re.compile(r'create table [\w]+\(([\w]+\s*(char\(\d+\)|int)( null[\s]*| not null[\s]*)?,[\s]*)*[\w]+\s*(char\(\d+\)|int)( null[\s]*| not null[\s]*)?([\s]*,[\s]*primary key\(([\w]*,)*[\w]*\))?\)[\s]*;')
    insert_into = re.compile(r"insert into [\w]+ values\((('[\w\u4e00-\u9fa5\-]+'|\d+)[\s]*,[\s]*)*('[\w\u4e00-\u9fa5\-]+'|\d+)\)[\s]*;")
    delete_from = re.compile(r'delete from [\w]+ where [\w]+\s*(=|>|<|>=|<=|!=)\s*(\'[\w\u4e00-\u9fa5\-]+\'|\d+)[\s]*;')
    drop_database = re.compile(r'drop database [\w]+[\s]*;')
    drop_table = re.compile(r'drop table [\w]+[\s]*;')

    if create_database.fullmatch(command): return True
    if use_database.fullmatch(command): return True
    if return_database.fullmatch(command): return True
    if create_table.fullmatch(command): return True
    if insert_into.fullmatch(command): return True
    if delete_from.fullmatch(command): return True
    if drop_database.fullmatch(command): return True
    if drop_table.fullmatch(command): return True
    return False

    # if re.match(r'create',command):
    #     if re.match(r'create database',command):
    #         if create_database.fullmatch(command): return True
    #         else: return False
    #     elif re.match(r'create table',command):
    #         if create_table.fullmatch(command): return True
    #         else: return False
    # elif re.match(r'insert',command):
    #     if insert_into.fullmatch(command): return True
    #     else: return False

def create_database(command):
    database_name = re.search(r'create database ([\w]+)',command).group(1)
    print(database_name)
    if os.path.exists(database_name):
        print("Database exists!")
        return
    os.mkdir(database_name)
    with open('system_database.csv','a') as f:
        time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(database_name+','+time+'\n')
    return

def use_database(command):
    global database
    database_name = re.search(r'use ([\w]+)',command).group(1)
    if os.path.exists(database_name)==False:
        print("Database not exists!")
        return
    database = database_name
    return

def return_database():
    global database
    if(database==''):
        print("No database in use!")
        return
    database=''
    return

def create_table(command):
    global database
    if(database==''):
        print("No database in use!")
        return
    table_name = re.search(r'create table ([\w]+)\s*\(',command).group(1)
    if os.path.exists(database+'/'+table_name+'.txt'):
        print("Table exists!")
        return
    table_item=re.findall(r'([\w]+)\s*(char\(\d+\)|int)\s*(null|not null)?',command)
    print(table_item)
    with open(database+'/system_table.csv','a') as f:
        f.write(table_name+'\n')
        for item in table_item:
            f.write(item[0]+','+item[1]+','+item[2]+'\n')
        f.write('/'+table_name+'\n')
    


if __name__ == '__main__':
    while True:
        command = inputCommand()
        if checkCommand(command)==False:
            print("Invalid command!")
            continue
        if(re.match(r'create database',command)):
            create_database(command)
        if(re.match(r'use',command)):
            use_database(command)
        if(re.match(r'return',command)):
            return_database()
        if(re.match(r'create table',command)):
            create_table(command)
