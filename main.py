import re
import os
import datetime
import json
import csv

database='test2'

def get_command():
    command = ''
    while not command.strip():
        command = input("sql> ").lower().strip() + ';'
    print(command)
    return command

def check_command(command):
    patterns = [
        re.compile(r'create database [\w]+[\s]*;'),
        re.compile(r'use [\w]+[\s]*;'),
        re.compile(r'return[\s]*;'),
        re.compile(r'create table [\w]+\(([\w]+\s*(char\(\d+\)|int)( null[\s]*| not null[\s]*)?,[\s]*)*[\w]+\s*(char\(\d+\)|int)( null[\s]*| not null[\s]*)?([\s]*,[\s]*primary key\(([\w]*,)*[\w]*\))?\)[\s]*;'),
        re.compile(r"insert into [\w]+ values\((('[\w\u4e00-\u9fa5\-]+'|\d+)[\s]*,[\s]*)*('[\w\u4e00-\u9fa5\-]+'|\d+)\)[\s]*;"),
        re.compile(r'delete from \w+(\s+where (\w+\s*(=|>|<|>=|<=|!=)\s*(\'[\w\u4e00-\u9fa5\-]+\'|\d+),)*\s*\w+\s*(=|>|<|>=|<=|!=)\s*(\'[\w\u4e00-\u9fa5\-]+\'|\d+)\s*)?;'),
        re.compile(r'drop database [\w]+[\s]*;'),
        re.compile(r'drop table [\w]+[\s]*;')
    ]

    for pattern in patterns:
        if pattern.fullmatch(command):
            return True
    return False

def create_database(command):
    database_name = re.search(r'create database ([\w]+)',command).group(1)
    print(database_name)
    if os.path.exists(database_name):
        print("Database exists!")
        return
    os.mkdir(database_name)
    with open('system_database.csv','a',newline='') as f:
        time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer = csv.writer(f)
        writer.writerow([database_name, time])
    with open(database_name+'/system_table.json','w') as f:
        json.dump({},f)
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

    table_item = re.findall(r'([\w]+)\s*(char\(\d+\)|int)\s*(null|not null)?', command)
    print(table_item)
    with open(database+'/'+table_name+'.csv', 'w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow([item[0] for item in table_item])

    match = re.findall(r'primary key\((.*)\)', command)
    primary_key = re.findall(r'([\w]+),?', match[0])

    table_item_dict_list = []
    for item in table_item:
        table_item_dict = {
            'name': item[0],
            'type': 'char' if item[1].startswith('char') else 'int',
            'length': int(re.search(r'\d+', item[1]).group(0)) if item[1].startswith('char') else None,
            'not null': True if item[2] == 'not null' else False,
            'primary_key': True if item[0] in primary_key else False
        }
        table_item_dict_list.append(table_item_dict)

    with open(database+'/system_table.json','r') as f:
        table_dict=json.load(f)

    table_dict[table_name] = table_item_dict_list

    with open(database+'/system_table.json','w') as f:
        json.dump(table_dict,f,indent=4)

def insert_into(command):
    global database
    if(database==''):
        print("No database in use!")
        return
    table_name = re.search(r'insert into ([\w]+) values',command).group(1)
    if os.path.exists(database+'/'+table_name+'.csv')==False:
        print("Table not exists!")
        return

    table_item=re.findall(r'(\'[\w\u4e00-\u9fa5\-]+\'|\d+)',command)
    table_item = [item.strip('\'') for item in table_item]
    print(table_item)
    
    with open(database+'/system_table.json','r') as f:
        table_dict=json.load(f)
    primary_key_indices = [i for i, item in enumerate(table_dict[table_name]) if item['primary_key'] == True]
    # 合法性检查
    for i, item in enumerate(table_item):
        if table_dict[table_name][i]['type'] == 'int' and not item.isdigit():
            print("Invalid input!")
            return
        elif table_dict[table_name][i]['type'] == 'char' and len(item) > table_dict[table_name][i]['length']:
            print("Invalid input!")
            return
        elif table_dict[table_name][i]['not null'] and item == '':
            print("Invalid input!")
            return

    with open(database+'/'+table_name+'.csv','r') as f:
        reader = csv.reader(f)
        table_data = [row for row in reader]
    table_data = table_data[1:]
    # 检查主键
    for item in table_data:
        if all(item[j] == table_item[j] for j in primary_key_indices):
            print("Primary key exists!")
            return

    with open(database+'/'+table_name+'.csv','a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(table_item)

def delete_from(command):
    # TODO 数据库是否选中封装成函数
    global database
    if(database==''):
        print("No database in use!")
        return
    table_name = re.search(r'delete from ([\w]+)',command).group(1)
    if os.path.exists(database+'/'+table_name+'.csv')==False:
        print("Table not exists!")
        return
    is_where = re.search(r'where',command)
    print(is_where)
    if is_where:
        condition = re.search(r'where ([\w]+)\s*(=|>|<|>=|<=|!=)\s*(\'[\w\u4e00-\u9fa5\-]+\'|\d+)',command).group(0)
        condition = condition.split()
        print(condition)
        return;
        if condition[1] == '=':
            condition[1] = '=='
        with open(database+'/'+table_name+'.csv','r') as f:
            reader = csv.reader(f)
            table_data = [row for row in reader]
        table_data = table_data[1:]
        with open(database+'/'+table_name+'.csv','w',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(table_data[0])
            for item in table_data[1:]:
                if eval(item[condition[0]]+condition[1]+condition[2]):
                    writer.writerow(item)
    return;
    table_item=re.findall(r'(\'[\w\u4e00-\u9fa5\-]+\'|\d+)',command)
    table_item = [item.strip('\'') for item in table_item]
    print(table_item)
    
    with open(database+'/system_table.json','r') as f:
        table_dict=json.load(f)
    primary_key_indices = [i for i, item in enumerate(table_dict[table_name]) if item['primary_key'] == True]
    # 合法性检查
    for i, item in enumerate(table_item):
        if table_dict[table_name][i]['type'] == 'int' and not item.isdigit():
            print("Invalid input!")
            return
        elif table_dict[table_name][i]['type'] == 'char' and len(item) > table_dict[table_name][i]['length']:
            print("Invalid input!")
            return
        elif table_dict[table_name][i]['not null'] and item == '':
            print("Invalid input!")
            return

    with open(database+'/'+table_name+'.csv','r') as f:
        reader = csv.reader(f)
        table_data = [row for row in reader]
    table_data = table_data[1:]
    # 检查主键
    for item in table_data:
        if all(item[j] == table_item[j] for j in primary_key_indices):
            print("Primary key exists!")
            return

    with open(database+'/'+table_name+'.csv','a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(table_item)

if __name__ == '__main__':
    while True:
        command = get_command()
        if check_command(command)==False:
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
        if(re.match(r'insert into',command)):
            insert_into(command)
        if(re.match(r'delete from',command)):
            delete_from(command)
