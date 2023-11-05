import re
import os
import datetime
import json
import csv
from prettytable import PrettyTable


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
        re.compile(r'drop database [\w]+[\s]*;'),
        re.compile(r'desc [\w]+[\s]*;'),
        re.compile(r'create table [\w]+\(([\w]+\s*(char\(\d+\)|int)( null[\s]*| not null[\s]*)?,[\s]*)*[\w]+\s*(char\(\d+\)|int)( null[\s]*| not null[\s]*)?([\s]*,[\s]*primary key\(([\w]*,)*[\w]*\))?\)[\s]*;'),
        re.compile(r"insert into [\w]+ values\((('[\w\u4e00-\u9fa5\-]+'|\d+)[\s]*,[\s]*)*('[\w\u4e00-\u9fa5\-]+'|\d+)\)[\s]*;"),
        re.compile(r'delete from \w+(\s+where (\w+\s*(=|>|<|>=|<=|!=)\s*(\'[\w\u4e00-\u9fa5\-]+\'|\d+)\s*and\s*)*\s*\w+\s*(=|>|<|>=|<=|!=)\s*(\'[\w\u4e00-\u9fa5\-]+\'|\d+)\s*)?;'),
        re.compile(r'drop database [\w]+[\s]*;'),
        re.compile(r'drop table [\w]+[\s]*;'),
        re.compile(r'select ([\w]+(,[\w]+)*|\*) from [\w]+(\s+where (\w+\s*(=|>|<|>=|<=|!=)\s*(\'[\w\u4e00-\u9fa5\-]+\'|\d+)\s*and\s*)*\s*\w+\s*(=|>|<|>=|<=|!=)\s*(\'[\w\u4e00-\u9fa5\-]+\'|\d+)\s*)?;'),
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

def use_database(command):
    global database
    database_name = re.search(r'use ([\w]+)',command).group(1)
    if os.path.exists(database_name)==False:
        print("Database not exists!")
        return
    database = database_name

def return_database():
    global database
    if(database==''):
        print("No database in use!")
        return
    database=''
    return

def drop_database(command):
    database_name = re.search(r'drop database ([\w]+)',command).group(1)
    if os.path.exists(database_name)==False:
        print("Database not exists!")
        return
    for file in os.listdir(database_name):
        os.remove(database_name+'/'+file)
    os.rmdir(database_name)
    with open('system_database.csv','r') as f:
        reader = csv.reader(f)
        database_list = [row for row in reader]
    database_list = [item for item in database_list if item[0] != database_name]
    with open('system_database.csv','w',newline='') as f:
        writer = csv.writer(f)
        for item in database_list:
            writer.writerow(item)

def desc(command):
    global database
    if(database==''):
        print("No database in use!")
        return
    table_name = re.search(r'desc ([\w]+)',command).group(1)
    if os.path.exists(database+'/'+table_name+'.csv')==False:
        print("Table not exists!")
        return
    with open(database+'/system_table.json','r') as f:
        table_dict=json.load(f)
    print(table_dict[table_name])
    data = []
    data.append(['Name', 'Type', 'Length', 'Not Null', 'Primary Key'])
    # TODO not_null not null
    for item in table_dict[table_name]:
        data.append([item['name'], item['type'], item['length'], item['not null'], item['primary_key']])
    # column_widths = [max(len(str(item)) for item in column) for column in zip(*data)]
    # separator = "+".join("-" * (width + 2) for width in column_widths)
    # print("+" + separator + "+")
    # print("| " + " | ".join(str(item).ljust(width) for item, width in zip(data[0], column_widths)) + " |")
    # print("+" + separator + "+")
    # data=data[1:]
    # for row in data:
    #     print("| " + " | ".join(str(item).ljust(width) for item, width in zip(row, column_widths)) + " |")
    # print("+" + separator + "+")
    table = PrettyTable()
    table.field_names = data[0]
    for row in data[1:]:
        table.add_row(row)
    print(table)

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
    with open(database+'/'+table_name+'.csv','r') as f:
        reader = csv.reader(f)
        table_data = [row for row in reader]
    is_where = re.search(r'where (.*);',command)
    if is_where:
        return
        where=is_where.group(1)
        # 将操作数和操作符提取出来
        where_list=re.findall(r'(\w+)\s*(=|>|<|>=|<=|!=)\s*(\'[\w\u4e00-\u9fa5\-]+\'|\d+)',where)
        # 将字符串中多余引号去掉
        print(where_list)
    else:
        # 清空文件除第一行以外的内容
        with open(database+'/'+table_name+'.csv','w',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(table_data[0])
    return

def select(command):
    global database
    if(database==''):
        print("No database in use!")
        return
    table_name = re.search(r'select ([\w]+|\*) from ([\w]+)',command).group(2)
    if os.path.exists(database+'/'+table_name+'.csv')==False:
        print("Table not exists!")
        return
    with open(database+'/'+table_name+'.csv','r') as f:
        reader = csv.reader(f)
        table_data = [row for row in reader]
    is_where = re.search(r'where (.*);',command)
    if is_where:
        return
        where=is_where.group(1)
        # 将操作数和操作符提取出来
        where_list=re.findall(r'(\w+)\s*(=|>|<|>=|<=|!=)\s*(\'[\w\u4e00-\u9fa5\-]+\'|\d+)',where)
        # 将字符串中多余引号去掉
        print(where_list)
    else:
        # TODO 封装函数
        data = table_data
        # 考虑中文情况
        

        # column_widths = [max(len(str(item)) for item in column) for column in zip(*data)]

        # column_widths = [0] * len(data[0])
        # for row in data:
        #     for i, cell in enumerate(row):
        #         cell_length = sum(2 if ord(c) > 127 else 1 for c in cell)
        #         column_widths[i] = max(column_widths[i], cell_length)

        # print(column_widths)
        # separator = "+".join("-" * (width + 2) for width in column_widths)
        # print("+" + separator + "+")
        # print("|" + "|".join(str(item).ljust(width,chr(12288)) for item, width in zip(data[0], column_widths)) + "|")
        # print("+" + separator + "+")
        # data=data[1:]
        # for row in data:
        #     print("|" + "|".join(str(item).ljust(width,chr(12288)) for item, width in zip(row, column_widths)) + "|")
        # print("+" + separator + "+")

        table = PrettyTable()
        table.field_names = data[0]
        for row in data[1:]:
            table.add_row(row)
        print(table)

if __name__ == '__main__':
    command_functions = {
        'create database': create_database,
        'use': use_database,
        'return': return_database,
        'drop database': drop_database,
        'desc': desc,
        'create table': create_table,
        'insert into': insert_into,
        'delete from': delete_from,
        'select': select,
    }

    while True:
        command = get_command()
        if not check_command(command):
            print("Invalid command!")
            continue

        for cmd, func in command_functions.items():
            if re.match(cmd, command):
                func(command)
                break
