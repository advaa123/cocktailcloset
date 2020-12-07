from flask import Flask, render_template, request, redirect
from flask_login import current_user, login_required, login_user, logout_user, LoginManager, AnonymousUserMixin, confirm_login
import jinja2
from models.models import User, Brand, Drink, Cart, Cocktail, CocktailByBrand, UserSystem
import requests
# from models.basic import get_popular_drinks, select_all


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = 'strong'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# app.debug = True
# app.config['DEBUG'] = True
user_system = UserSystem()
badge_colors = ['default', 'primary', 'secondary', 'warning', 'info']


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/", methods=['GET', 'POST'])
def main():
    if current_user.is_authenticated:
        return render_template('index.html',
                                drinks=user_system.select_drinks(),
                                brands=user_system.select_brands(),
                                cart=len(current_user.cart),
                                colors=badge_colors)
    
    return render_template('index.html',
                            drinks=user_system.select_drinks(),
                            brands=user_system.select_brands(),
                            colors=badge_colors)


@app.route("/about")
def about():
    if current_user.is_authenticated:
        return render_template('about.html', cart=len(current_user.cart))
    return render_template('about.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
   if not current_user.is_authenticated:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get_or_none(username=username)
        
        if user is not None and user.check_password(password):
            login_user(user)
            return render_template('index.html',
                                drinks=user_system.select_drinks(),
                                brands=user_system.select_brands(),
                                cart=len(current_user.cart),
                                colors=badge_colors)
                                
        return render_template('index.html',
                            drinks=user_system.select_drinks(),
                            brands=user_system.select_brands(),
                            colors=badge_colors,
                            error="Incorrect username or password"
                            )

        return render_template('index.html', drinks=user_system.select_drinks(), brands=user_system.select_brands(), colors=badge_colors)


@app.route("/cart", methods=['GET', 'POST'])
@login_required
def go_to_cart():
    if request.method == "POST":
        if request.form.getlist('drink_item'):
            checked_items = list(map(int, request.form.getlist('drink_item')))
            for item in checked_items:
                cart = Cart.get_or_none(Cart.id == item)
                if cart is not None:
                    cart.delete_instance()

    items = user_system.select_user_cart(current_user)
    total = 0
    split_price = []

    for item in items:
        price = item.drink.price[1:]
        if price.isdecimal():
            total += int(price)
        else:
            split_price = price.split('-$')
    
    if len(split_price) > 0:
        total_str = f'${total + int(split_price[0])}-${total + int(split_price[1])}'
    else:
        total_str = f'${total}'

    return render_template('cart.html',
                            cart=len(current_user.cart),
                            items=items,
                            total=total_str
    )


@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html',
                            user=current_user,
                            cart=len(current_user.cart))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        errors = []

        username = request.form.get('username')
        user = User.get_or_none(User.username == username)

        if len(username) == 0:
            errors.append("Please enter a valid username.")

        if user is not None:
            errors.append(f"'{username}' already exists, please choose a different username.")

        full_name = request.form.get('full_name')
        if len(full_name) == 0:
            errors.append('Please enter a valid full name.')
        password = request.form.get('password')
        if len(password) == 0:
            errors.append('Please enter a longer password.')
        email = request.form.get('email')
        if len(email) == 0 or not '@' in email:
            errors.append('Please enter a valid email address.')

        if len(errors) > 0:
            return render_template('register.html', errors=errors)

        user_system.add_user(username, full_name, password, email)

        login_user(User.get(User.username == username), force=True)
        return redirect('/')
    return render_template('register.html')


@app.route("/add/<drink>", methods=['GET', 'POST'])
# @login_required
def add_to_cart(drink):
    if current_user.is_authenticated:
        drink = Drink.get_or_none(Drink.id == int(drink))
        if drink is not None:
            user_system.add_to_cart(current_user, drink)
            Cart.create(user=current_user.id, drink=drink)
        return redirect('/')

    return render_template('index.html',
                        drinks=user_system.select_drinks(),
                        brands=user_system.select_brands(),
                        colors=badge_colors,
                        error="You need to sign in to perform this action"
                        )


def get_brands(cocktail):
    return CocktailByBrand.select(CocktailByBrand.brand).where(CocktailByBrand.cocktail == cocktail)


def get_cocktails(brand):
    return CocktailByBrand.select(CocktailByBrand.cocktail).where(CocktailByBrand.brand == brand)


@app.route("/cocktails/<brand>", methods=['GET', 'POST'])
def cocktails(brand):
    brand = Brand.get_or_none(Brand.id == int(brand))
    if brand is not None:
        if current_user.is_authenticated:
            return render_template('cocktails.html',
                            cart=len(current_user.cart),
                            cocktails=get_cocktails,
                            func=get_brands,
                            current_brand=brand,
                            brands=user_system.select_brands(),
                            colors=badge_colors
            )
        return render_template('cocktails.html',
                            cocktails=get_cocktails,
                            func=get_brands,
                            current_brand=brand,
                            brands=user_system.select_brands(),
                            colors=badge_colors
            )
    return redirect("/")


@app.route("/cocktails")
def cocktails_main():
    return redirect("/cocktails/1")


@app.route("/cocktail/<cocktail_id>", methods=['GET', 'POST'])
def cocktail_details(cocktail_id):
    cocktail = Cocktail.get_or_none(Cocktail.id == int(cocktail_id))
    if cocktail is not None:
        full_dict = user_system.cocktail_ingredients(cocktail.api_id)
        ingredients_list = []
        measures_list = []
        for k, v in full_dict.items():
            if k.startswith('strIngredient'):
                ingredients_list.append(v)
            elif k.startswith('strMeasure'):
                measures_list.append(v)

        if current_user.is_authenticated:
            return render_template('cocktail.html',
                            cart=len(current_user.cart),
                            cocktail=full_dict,
                            ingredients=list(zip(ingredients_list, measures_list)),
                            colors=badge_colors
            )
        return render_template('cocktail.html',
                            cocktail=full_dict,
                            ingredients=list(zip(ingredients_list, measures_list)),
                            colors=badge_colors
        )
    return redirect("/")


@app.route("/logout")
@login_required
def logout_of_system():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(threaded=True, port=5000)