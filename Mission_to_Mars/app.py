from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import pymongo
import scrape_mars

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_db"
mongo = PyMongo(app)

# Create connection variable
#conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
#client = pymongo.MongoClient(conn)

# Connect to a database. Will create one if not already available.
# db = mongo.mars_db

@app.route("/")
def index():
    mars = mongo.db.planet.find_one()
    # Find one record of data from the mongo database
    # mars_dict = mongo.db.mars_dict.find_one()
    # Return template and data
    return render_template("index.html", mars=mars)

@app.route("/index2.html")
def index2():
    planet_data = {}
    planet_data = mongo.db.planet.find({})

    return (planet_data)   
    

@app.route("/scrape.html")
def scrapeData():
    scrape_mars.scrape()
    mars = mongo.db.planet.find()
    # return render_template("scrape.html", mars=mars_dict)
    return redirect("/")
    # mars_dict = mongo.db.mars_dict
    # mars_data = scrape_mars.scrape()
    # Update the Mongo database using update and upsert=True
    # mars_dict.update({}, mars_data, upsert=True)
    

if __name__ == "__main__":
    app.run(debug=True)