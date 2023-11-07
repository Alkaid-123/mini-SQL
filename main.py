import re
import os
import datetime
import json
import csv
from prettytable import PrettyTable, from_csv

database='test2'

def get_command():
    command = ''
    while not command.strip():
        command = input("sql> ").lower().strip() + ';'
    command=re.sub(r'\s+',' ',command)
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
        re.compile(r'select (\w+(,\s*\w+)*|\*) from (\w+,\s*)*\w+(\s+where ([\w\.]+\s*(=|>|<|>=|<=|!=)\s*(\'[\w\u4e00-\u9fa5\-]+\'|\d+|[\w\.]+)\s*and\s*)*\s*[\w\.]+\s*(=|>|<|>=|<=|!=)\s*(\'[\w\u4e00-\u9fa5\-]+\'|\d+|[\w\.]+)\s*)?;'),
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


def print_table(data):
    table = PrettyTable()
    table.field_names = data[0]
    for row in data[1:]:
        table.add_row(row)
    print(table)

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
    print_table(data)
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


def cartesian_product(tables):
    if len(tables) == 1:
        return tables[0]
    result = []
    rest_product = cartesian_product(tables[1:])
    for item in tables[0]:
        for product_item in rest_product:
            result.append(item + product_item)
    
    return result


def find_index(tables,name,table_name_list,header):
    result=re.search(r'([\w]+)\.([\w]+)',name)
    if result:
        table_name=result.group(1)
        column_name=result.group(2)
        table_index=table_name_list.index(table_name)
        column_index=header[table_index].index(column_name)
    else:
        for i,table in enumerate(tables):
            if name in table[0]:
                table_index=i
                column_index=table[0].index(name)
                break
    return [table_index,column_index]




def select(command):
    global database
    if(database==''):
        print("No database in use!")
        return
    table_name = re.search(r'from ([\w,\s]+)(where|;)',command).group(1)
    table_name=table_name.replace(' ','')
    table_name_list = table_name.split(',')
    print(table_name_list)

    with open(database+'/system_table.json','r') as f:
        table_dict=json.load(f)

    tables=[]
    header=[]
    # datas=[]
    for table_name in table_name_list:
        if os.path.exists(database+'/'+table_name+'.csv')==False:
            print("Table '"+ table_name +"' not exists!")
            return
        with open(database+'/'+table_name+'.csv','r') as f:
            reader = csv.reader(f)
            table_data = [row for row in reader]

        # 将type为int的列转换为int
        for item in table_dict[table_name]:
            if item['type'] == 'int':
                table_data = [[int(item) if item.isdigit() else item for item in row] for row in table_data]

        header.append(table_data[0])
        # datas.append(table_data[1:])
        tables.append(table_data)
    
    print(tables)
    


    # join and select操作
    is_where = re.search(r'where (.*);',command)
    select_list = []
    join_list = []
    if is_where:
        where=is_where.group(1)
        # 将操作数和操作符提取出来
        where_list=re.findall(r'([\w\.]+)\s*(=|>|<|>=|<=|!=)\s*(\'[\w\u4e00-\u9fa5\-]+\'|\d+|[\w\.]+)',where)

        where_list=[list(item) for item in where_list]

        
        for item in where_list:
            if item[2].startswith('\''):
                item[2] = item[2].strip('\'')
                select_list.append(item)
            elif item[2].isdigit():
                item[2] = int(item[2])
                select_list.append(item)
            else:
                join_list.append(item)
        print(where_list)
        print(select_list)
        print(join_list)
        
        # select操作
        # TODO 得去自己里面找 不能用笛卡尔积 不然所有人都会满足条件 也就是更新tables
        for item in select_list:
            item[0]=find_index(tables,item[0],table_name_list,header)
        print(select_list)
        for item in join_list:
            item[0]=find_index(tables,item[0],table_name_list,header)
            item[2]=find_index(tables,item[2],table_name_list,header)
        print(join_list)

        for item in select_list:
            table=tables[item[0][0]]
            if item[1]=='=':
                table=[table[0]]+[row for row in table[1:] if row[item[0][1]]==item[2]]
            elif item[1]=='>':
                table=[table[0]]+[row for row in table[1:] if row[item[0][1]]>item[2]]
            elif item[1]=='<':
                table=[table[0]]+[row for row in table[1:] if row[item[0][1]]<item[2]]
            elif item[1]=='>=':
                table=[table[0]]+[row for row in table[1:] if row[item[0][1]]>=item[2]]
            elif item[1]=='<=':
                table=[table[0]]+[row for row in table[1:] if row[item[0][1]]<=item[2]]
            elif item[1]=='!=':
                table=[table[0]]+[row for row in table[1:] if row[item[0][1]]!=item[2]]
            tables[item[0][0]]=table
        print('selected tables',tables)

        # join操作
        # TODO 这只是两表合并 还有多表合并
        if len(join_list)==len(table_name_list)-1 and len(join_list)!=0:
            merge_table=[]
            for item in join_list:
                table1=tables[item[0][0]]
                table2=tables[item[2][0]]
                # 如果table1中某一行当中item[0][1]列的值和table2中某一行item[2][1]列的值相等 则将这两行合并
                merge_table.append(table1[0]+table2[0])
                for row1 in table1[1:]:
                    for row2 in table2[1:]:
                        if row1[item[0][1]]==row2[item[2][1]]:
                            merge_table.append(row1+row2)
                tables[item[0][0]]=merge_table
                tables[item[2][0]]=merge_table 
                print('tables\n',tables)
            tables=merge_table

            

    # TODO 封装函数
    # 笛卡尔积
    if len(join_list)==len(table_name_list)-1 and len(join_list)!=0:
        pass
    elif len(join_list)!=len(table_name_list)-1:
        datas=[]
        for table in tables:
            datas.append(table[1:])
        header=[item for sublist in header for item in sublist]
        tables=[header]+cartesian_product(datas)
    else:
        tables=tables[0]

    # project操作
    project=re.search(r'select (.*) from',command).group(1)
    project_list=project.split(',')
    print(project_list)
    if project_list[0]=='*':
        pass
    else:
        project_list=[item.strip() for item in project_list]
        project_list=[tables[0].index(item) for item in project_list]
        header=[tables[0][i] for i in project_list]
        tables=[header]+[[item[i] for i in project_list] for item in tables[1:]]
    # print(tables)
    # TODO tables[0???
    print_table(tables)
    print('共有'+str(len(tables)-1)+'条记录')

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


# TODO 各种异常处理 不要退出程序