from flask import Flask, jsonify, render_template, redirect
from flask_pymongo import PyMongo

#Import Python functions from the scrape_mars.py file
from .scrape_mars import scrape


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
#Pymongo Setup
#################################################

mongo = PyMongo(app, uri="mongodb://stefanie:mart4ino@ds249233.mlab.com:49233/mars_app")

#################################################
# Flask Routes
#################################################

@app.route("/")
def index():

    # Query the mars database
    mars = mongo.db.mars.find_one()

    # Return template and database
    return render_template("index.html", mars=mars)
   
@app.route("/scrape")
def scrape():
    mars = mongo.db.mars
    data = scrape_mars.scrape()

    mars.update(
    {},
    data,
    upsert=True
    )
    return redirect('/', code=302)

       
if __name__ == "__main__":
    app.run(debug=True)
