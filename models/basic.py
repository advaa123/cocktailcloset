import requests
import json
from lxml import html
import sqlite3
from sqlite3 import Error


def get_popular_drinks():
    url = 'https://www.esquire.com/food-drink/drinks/a30246954/best-alcohol-bottles-2019/'
    page = requests.get(url)
    tree = html.fromstring(page.content)
    alcohol = tree.xpath('//h3[@class="body-h3"]/text()')
    images = tree.xpath('//img[@class="lazyimage lazyload"]/@data-src')

    #alcohol_dict = {'scotch': [], 'tequila': [], 'gin': [], 'rum': [], 'cognac': []}
    alcohol_list = []
    index = 0
    j = 0
    while index < len(alcohol) and j < len(images):
        bottle_dict = {"name": alcohol[index].strip(),
                        "price": alcohol[index + 1].strip(),
                        "img": images[j].replace("?resize=480:*", "")
                        }

        if index < 34:
            bottle_dict['brand'] = 'scotch'
        elif index > 33 and index < 40:
            bottle_dict['brand'] = 'tequila'
        elif index >= 40 and index < 45:
            bottle_dict['brand'] = 'gin'
        elif index >= 46 and index < 52:
            bottle_dict['brand'] = 'rum'
        else:
            bottle_dict['brand'] = 'cognac'
        
        alcohol_list.append(bottle_dict)

        j += 1
        index += 2
    
    return alcohol_list


def get_cocktails(brand):
    reponse = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/filter.php?i={brand}')
    return reponse.json()['drinks']


def get_cocktail_ingredients(api_id):
    response = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={api_id}')
    return response.json()['drinks'][0]


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def run_sql_files(db_file, sql_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    sql_file = open(sql_file)
    sql_as_string = sql_file.read()
    cursor.executescript(sql_as_string)
    for row in cursor.execute("SELECT * FROM users"):
        print(row)
    
    sql_file.close()
    conn.close()


def show_tables(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())
    conn.close()


def add_user(db_file, username, password, name, email):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute(f"INSERT INTO users (username, password, name, email) VALUES ('{username}', '{password}', '{name}', '{email}');")
    except Error as e:
        print(e)
    else:
        conn.commit()
        print("Success")
    
    conn.close()


def delete_user(db_file, username):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM users WHERE username = '{username}';")
    conn.commit()
    conn.close()


def select_all(db_file, table):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table};")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    
    conn.close()

    return rows


# def add_popular_drinks(db_file):
#     alcohol_dict = get_popular_drinks()
#     conn = sqlite3.connect(db_file)
#     cursor = conn.cursor()
#     drinks_tuple_list = []
#     for k, v in alcohol_dict.items():
#         drinks_tuple_list.append((k, v['price']))
    
#     print(drinks_tuple_list)

#     cursor.executemany(f"INSERT INTO popular_drinks (name, price) VALUES (?, ?);", drinks_tuple_list)
#     conn.commit()
#     conn.close()


# if __name__ == '__main__':
#     print(get_popular_drinks())
#     print(get_cocktails())
#     print(get_cocktail_ingredients('11007'))
#     print(get_cocktails('scotch'))
#     create_connection("mydb.db")
#     run_sql_files("mydb.db", "second_step.sql")
#     show_tables("mydb.db")
#     add_user('mydb.db', 'Admin23', '1234', 'Addie', 'yes112@yo.com')
#     delete_user('mydb.db', 'Admin')
#     add_popular_drinks('mydb.db')
#     select_all('mydb.db', 'popular_drinks')