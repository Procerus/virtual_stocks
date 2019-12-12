import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CSrun50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # owned has id stockid userid and amount, stocks has stocks and stock id, users has id username hash and cash
    stock = []
    # get the amount of money user has
    cash = db.execute("SELECT cash FROM  users WHERE id = "+str(session["user_id"]))
    cash = cash[0]['cash']
    all = cash
    # get the info of the stocks the user owns
    usersid = db.execute("SELECT * FROM owned WHERE userid = "+str(session["user_id"]))
    # iterate through the list of lists in the for loop and get the stock names from each owned stock
    for i in usersid:
        symbol = db.execute("SELECT stocks FROM stocks WHERE stockid =" + str(i['stockid']))

        symbol = symbol[0]['stocks']
        stockname = lookup(symbol)
        # create the list of each stock info the user owns
        stock.append([symbol, stockname['name'], str(i['amount']), stockname['price'],
            i['amount'] * stockname['price']])
        all = all + i['amount'] * stockname['price']
    # submit the data to index where jninja will put it in table format and enters users cash at the end
    return render_template("index.html", stock=stock, total=cash , all=all)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # checks to make sure there is a submission and returns apology if not
    if request.method == "POST":
        # Get the post request for name and amount of stocks they want
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("Please enter a stock symbol", 400)
        # convert the amount to an integer form
        try:
            int(request.form.get("shares"))
        except ValueError:
            return apology("Use whole Number for shares", 400)
        amounts = int(request.form.get("shares"))
        if amounts < 0:
            return apology("Enter Positive share amount", 400)
        # get price of stock at cureent time using symbol and API for exchange
        price = lookup(request.form.get("symbol"))
        # if no price then either server down or user typed in wrong Symbol
        if price == None:
            return apology("Enter Valid Stock", 400)
        # get name of stock and convert it to uppercase
        stocks = db.execute("SELECT * FROM stocks WHERE stocks = :name",
                            name=request.form.get("symbol").upper())
        if len(stocks) != 1:
            # inserts into stocks the name if it isnt in the list yet
            db.execute("INSERT INTO stocks (stockid, stocks) VALUES(NULL, '" + request.form.get("symbol").upper() + "')")
        money = db.execute("SELECT cash FROM users WHERE id= " + str(session["user_id"]))
        stocks = db.execute("SELECT * FROM stocks WHERE stocks = :name",
                            name=request.form.get("symbol").upper())
        # subtract the price from the amount the stock costs as long as the user has the amount
        if money[0]['cash'] > price["price"] * amounts:
            money = money[0]['cash'] - price["price"] * amounts
        else:
            return apology("You cannot afford that")
        # gets the owned information so that it can update the owned info with the new amounts listed
        usersid = db.execute("SELECT * FROM owned WHERE userid = " +
                             str(session["user_id"])+" AND stockid =" + str(stocks[0]['stockid']))
        if len(usersid) != 1:
            db.execute("INSERT INTO owned (id,userid,stockid,amount) VALUES(NULL,:user,:stock, :amount)",
                       user=str(session["user_id"]), stock=str(stocks[0]['stockid']), amount=str(amounts))
        else:
            db.execute("UPDATE owned SET amount =:amount WHERE id=:id",
                       amount=str(usersid[0]['amount'] + amounts), id=str(usersid[0]['id']))
        db.execute("UPDATE users SET cash=:cash WHERE id=:id",
                   cash=money, id=str(session["user_id"]))
        db.execute("INSERT INTO history (id,userid,stockid,buy,cost,amount,date) VALUES(NULL,:userid,:stockid,:buy,:cost,:amount,datetime('now'))",
                   userid=str(session["user_id"]), stockid=str(stocks[0]['stockid']), buy=True, cost=price['price'], amount=str(amounts))
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    if request.method == "GET":
        name = request.args.get("username")
        """Return true if username available, else false, in JSON format"""
        user = db.execute("SELECT * FROM users WHERE username=:name", name=name)
        if not user:
            return jsonify(True)
        else:
            return jsonify(False)
    else:
        return render_template("register.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # owned has id stockid userid and amount, stocks has stocks and stock id, users has id username hash and cash
    stock = []
    # get the amount of money user has
    history = db.execute("SELECT cash FROM  users WHERE id = "+str(session["user_id"]))
    # get the info of the stocks the user owns
    usersid = db.execute("SELECT * FROM history WHERE userid = "+str(session["user_id"]))
    # iterate through the list of lists in the for loop and get the stock names from each owned stock
    for i in usersid:
        symbol = db.execute("SELECT stocks FROM stocks WHERE stockid =" + str(i['stockid']))

        symbol = symbol[0]['stocks']
        stockname = lookup(symbol)
        # create the list of each stock info the user owns
        # symbol shares price transacted
        stock.append([symbol, str(i['amount']), i['amount'] * i['cost'], i['date']])

    # submit the data to index where jninja will put it in table format and enters users cash at the end
    return render_template("history.html", stock=stock)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Please enter a stock symbol")
        name=lookup(request.form.get("symbol"))
        if not name:
            return apology("Stock not found")
        return render_template("quoted.html", name=name)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # make sure the user enters in username and passwords
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Please enter username and password")
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords did not match")
        user = db.execute("SELECT * FROM users WHERE username=:name", name=request.form.get("username"))
        if not user:
            db.execute("INSERT INTO users (id,username, hash) VALUES(NULL,'" + request.form.get("username") +
                   "','"+generate_password_hash(request.form.get("password"))+"')")
        else:
            return apology("Username Taken",400)
        return render_template("login.html")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # same as buy function however if there is no stock left it will delete from the database
    stocklist = db.execute(
        "SELECT stocks FROM owned INNER JOIN stocks ON stocks.stockid = owned.stockid WHERE userid = "+str(session["user_id"]))
    if request.method == "POST":
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("Please enter a stock symbol and shares you wish to sell")
        price = lookup(request.form.get("symbol"))
        amounts = int(request.form.get("shares"))
        if price == None:
            return render_template("sell.html")
        stocks = db.execute("SELECT * FROM stocks WHERE stocks = :name",
                            name=request.form.get("symbol").upper())
        if len(stocks) != 1:
            db.execute("INSERT INTO stocks (stockid, stocks) VALUES(NULL, '" + request.form.get("symbol").upper() + "')")
        money = db.execute("SELECT cash FROM users WHERE id= "+str(session["user_id"]))
        money = money[0]['cash'] + price["price"]
        usersid = db.execute("SELECT * FROM owned WHERE userid = " +
                             str(session["user_id"])+" AND stockid =" + str(stocks[0]['stockid']))
        if len(usersid) != 1 or usersid[0]['amount'] < amounts:
            return apology("You do not own that stock")
        else:
            db.execute("UPDATE owned SET amount =:amount WHERE id=:id",
                       amount=str(usersid[0]['amount'] - amounts), id=str(usersid[0]['id']))
        if usersid[0]['amount'] == amounts:
            # deletes from the database when empty
            db.execute("DELETE FROM owned WHERE id=:id", id=str(usersid[0]['id']))
        db.execute("UPDATE users SET cash=:cash WHERE id=:id",
                   cash=money, id=str(session["user_id"]))
        db.execute("INSERT INTO history (id,userid,stockid,buy,cost,amount,date) VALUES(NULL,:userid,:stockid,:buy,:cost,:amount,datetime('now'))",
                   userid=str(session["user_id"]), stockid=str(stocks[0]['stockid']), buy=False, cost=price['price'], amount=-1 * amounts)
        return redirect("/")
    else:
        return render_template("sell.html", stock=stocklist)

    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
