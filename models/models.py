from flask_login import UserMixin
from peewee import *
from .basic import get_popular_drinks, get_cocktails, get_cocktail_ingredients
from werkzeug.security import generate_password_hash, check_password_hash


db = SqliteDatabase('mydb7.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(UserMixin, BaseModel):
    username = CharField(unique=True)
    full_name = CharField()
    password = CharField()
    email = CharField()
    
    def set_password(self, password):
        self.password = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password, password)
    

    def is_authenticated(self):
        return True
    

    def get_id(self):
        return self.id


    def is_active(self):
        return True

    
    def is_anonymous(self):
        return False


    def __str__(self):
        return f'@{self.username} - {self.full_name}'


class Brand(BaseModel):
    name = CharField(unique=True)


class Drink(BaseModel):
    name = CharField(unique=True)
    price = CharField()
    img = CharField()
    brand = ForeignKeyField(Brand, backref='drinks')


class Cocktail(BaseModel):
    name = CharField(unique=True)
    img = CharField()
    api_id = IntegerField()


class CocktailByBrand(BaseModel):
    brand = ForeignKeyField(Brand, backref='cocktails')
    cocktail = ForeignKeyField(Cocktail, backref='cocktails')


class Cart(BaseModel):
    user = ForeignKeyField(User, backref='cart')
    drink = ForeignKeyField(Drink, backref='cart')


class UserSystem:
    def add_user(self, username, full_name, password, email):
        try:
            User.create(
                username=username,
                full_name=full_name,
                password=generate_password_hash(password),
                email=email
            )
        except Exception as e:
            print(e)
            return False
        else:
            return True


    def remove_user(self, username):
        try:
            user = User.get(User.username == username)
            user.delete_instance()
        except Exception:
            print(f"Couldn't delete '{username}'.")
        else:
            print(f"User {username} has been deleted.")


    def select_users(self):
        for user in User.select():
            print(user.username, user.full_name, user.password)


    def select_drinks(self):
        return Drink.select()

    
    def select_brands(self):
        return Brand.select()
    

    def add_drink(self, name, price, img, brand):
        try:
            Drink.create(
                name=name,
                price=price,
                img=img,
                brand=brand
            )
        except Exception as e:
            print(e)
            return False
        else:
            return True


    def remove_drink(self, drink):
        name = drink.name
        try:
            drink.delete_instance()
        except Exception as e:
            print(e)
        else:
            print(f"The drink '{name}' has been deleted.")


    # def add_cocktail(self, name, price, img):
    #     try:
    #         Cocktail.create(
    #             name=name
    #         )
    #     except Exception as e:
    #         print(e)
    #         return False
    #     else:
    #         return True


    def remove_cocktail(self, name):
        cocktail = Cocktail.get(Cocktail.name == name)
        try:
            cocktail.delete_instance()
        except Exception as e:
            print(e)
        else:
            print(f"Cocktail '{name}' has been deleted.")


    def add_to_cart(self, user, drink):
        try:
            Cart.create(user=user, drink=drink)
        except Exception as e:
            return e
        else:
            return f"{drink.name} has been added to {user.username}'s cart."


    def remove_from_cart(self, cart, drink):
        cart = Cart.get(Cart.drink == drink)
        try:
            cart.delete_instance()
        except Exception as e:
            print(e)
        else:
            print(f"{drink.name} has been removed from {cart.user.username}'s cart.")


    def select_user_cart(self, user):
        try:
            return user.cart
        except Exception as e:
            return e


    def select_all_carts(self):
        for c in Cart.select():
            print(c.id, c.user.id, c.drink.id)


    def login(self, username, password):
        try:
            user = User.get(User.username == username)
        except Exception:
            print(f"User '{username}' does not exist.")
        else:
            if user.check_password(password):
                print("Logged in successfully.")
            else:
                print("Wrong password, try again.")


    def create_brands(self):
        for brand in ['scotch', 'tequila', 'gin', 'rum', 'cognac']:
            Brand.create(name=brand)
    

    def add_popular_drinks(self):
        fields = [Drink.name, Drink.price, Drink.img, Drink.brand]
        drinks = get_popular_drinks()
        
        for drink in drinks:
            drink['brand'] = Brand.get(Brand.name == drink['brand'])
        
        Drink.insert_many(drinks, fields=fields).execute()
    

    def add_cocktails(self):
        fields = [Cocktail.name, Cocktail.img, Cocktail.api_id]
        
        for brand in Brand.select():
            fitted_list = []
            cocktails = get_cocktails(brand.name)
            for cocktail in cocktails:
                fitted_list.append({'name': cocktail['strDrink'], 'img': cocktail['strDrinkThumb'], 'api_id': cocktail['idDrink']})

            Cocktail.insert_many(fitted_list, fields=fields).on_conflict_replace().execute()


    def get_cocktails_list(self):
        return Cocktail.select()
    

    def cocktails_by_brand(self):
        fields = [CocktailByBrand.brand, CocktailByBrand.cocktail]
        cbb_list = []
        for brand in Brand.select():
            cocktails = get_cocktails(brand.name)
            for cocktail in cocktails:
                cbb_list.append((brand, Cocktail.get(Cocktail.name == cocktail['strDrink'])))
        
        CocktailByBrand.insert_many(cbb_list, fields=fields).execute()
    

    def get_cocktails_by_brand(self):
        return CocktailByBrand.select()


    def cocktail_ingredients(self, api_id):
        ingredients_dict = get_cocktail_ingredients(api_id)
        updated_dict = {}
        for k, v in ingredients_dict.items():
            if v is not None:
                updated_dict[k] = v
        
        return updated_dict

# https://www.thecocktaildb.com/api/json/v1/1/filter.php?i=Gin
# https://www.thecocktaildb.com/api/json/v1/1/filter.php?i=vodka
# https://www.thecocktaildb.com/api/json/v1/1/filter.php?i=rum
# https://www.thecocktaildb.com/api/json/v1/1/filter.php?i=Tequila
# https://www.thecocktaildb.com/api/json/v1/1/filter.php?i=Scotch


    # name = CharField(unique=True)
    # price = CharField()
    # img = CharField()
    # brand = ForeignKeyField(Brand, backref='drinks')

# if __name__ == '__main__':
#     db.connect()
#     us = UserSystem()
#     db.create_tables([User, Brand, Drink, Cocktail, CocktailByBrand, Cart])
    # us.add_user('Admin2', 'Addie', '1234', 'a@b.c')
    # us.add_user('Admin', 'Addie', '1234', 'a@b.c')
    # us.add_user('Damn1', 'Addie', '1234', 'a@b.c')
    # us.add_user('User', 'Didi', '1234', 'a@b.c')
    # us.add_drink('Glenfidich','$20', 'asdas.png', 'scotch')
    # us.select_users()
    # us.select_drinks()
    # us.add_to_cart()
    # us.remove_user('')
    # us.create_brands()
    # us.add_popular_drinks()
    # us.add_cocktails()
    # for cocktail in us.get_cocktails_list():
    #      print(cocktail.id, cocktail.name, cocktail.api_id)
    
    # us.cocktails_by_brand()
    # for c in us.get_cocktails_by_brand():
    #     print(c.brand.name, c.cocktail.name)

    # us.select_drinks()
    # drink = Drink.get_or_none(Drink.id == 1)
    # print(drink.brand.name)
    # drink = Drink.select().where(Drink.id == 1)
    # us.remove_drink(drink)
    # user = User.get(User.username == 'Damn')
    # #user2 = User.get(User.username == 'User')
    # us.add_to_cart(user, drink)
    # add_to_cart(User.get(User.username == 'User'), drink)
    # us.select_user_cart(user)
    # remove_from_cart(Cart.get(Cart.user == user), drink)
    # select_user_cart(User.get(User.username == 'User'))
    # select_all_carts()
    # user = User()
    # user.set_password('lol2')

    # add_user('Damn1', 'Roy', user.password, 'ab@c.d')
    # select_drinks()
    # us.select_users()
    # us.login('Damn1', 'lol2')
    # db.close()