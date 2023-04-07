""" flask_example.py
    Required packages:
    - flask
    - folium
    Usage:
    Start the flask server by running:
        $ python flask_example.py
    And then head to http://127.0.0.1:5000/ in your browser to see the map displayed
"""

from flask import Flask, render_template

import folium
import requests
import pandas as pd

from flask import Flask, request, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

db = SQLAlchemy()


def create_app():
    app1 = Flask(__name__, template_folder = 'templates', static_folder='static')
    app1.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Trutracker.sqlite3'
    app1.config['SECRET_KEY'] = "random string"
    db.init_app(app1)
    # after 5 minutes of inactivity, user's session will expire. They will need to log in again
    app1.permanent_session_lifetime = timedelta(minutes=5)
    return app1



class User(db.Model):
    user_name = db.Column(db.String(100), primary_key=True)
    user_pswd = db.Column(db.String(100))

    def __init__(self, name, pswd):
        self.user_name = name
        self.user_pswd = pswd


class Locations(db.Model):
    building_name = db.Column(db.String(100))
    building_id = db.Column(db.Integer, primary_key=True)
    building_latitude = db.Column(db.Integer)
    building_longitude = db.Column(db.Integer)

    def __init__(self, name, build_id, lat, long):
        self.building_name = name
        self.building_id = build_id
        self.building_latitude = lat
        self.building_longitude = long


class Ryle_Hall(db.Model):
    building_name = db.Column(db.String(100), primary_key=True)
    distance_from_building = db.Column(db.Integer)
    time_from_building = db.Column(db.Integer)

    def __init__(self, name, dist, time):
        self.building_name = name
        self.distance_from_building = dist
        self.time_from_building = time


def add_buildings():
    loc_1 = Locations("West Campus Suites", 1, 1211, 1222)
    db.session.add(loc_1)
    db.session.commit()
    loc_2 = Locations("Recreation Center", 2, 1311, 1333)
    db.session.add(loc_2)
    db.session.commit()


def add_ryle_data():
    build_1 = Ryle_Hall("West Campus", 2, 20)
    db.session.add(build_1)
    db.session.commit()
    build_2 = Ryle_Hall("Recreation Center", 1, 15)
    db.session.add(build_2)
    db.session.commit()


def add_user():
    user1 = User("habib23", "tru123")
    db.session.add(user1)
    db.session.commit()
    user2 = User("mhmd123", "prince123")
    db.session.add(user2)
    db.session.commit()


def get_lat(name):
    this_location = Locations.query.filter_by(building_name=name).first()
    return this_location.building_latitude


def get_long(name):
    this_location = Locations.query.filter_by(building_name=name).first()
    return this_location.building_longitude


def verify_username(username):
    exists = db.session.query(db.exists().where(User.user_name == username)).scalar()
    if exists:
        print("this username is valid")
    else:
        print("this username is not valid")


def verify_pswd(password):
    exists = db.session.query(db.exists().where(User.user_pswd == password)).scalar()
    if exists:
        print("this password is valid")
    else:
        print("this password is not valid")


def get_directions_response():
    url = "https://route-and-directions.p.rapidapi.com/v1/routing"
    querystring = {"waypoints": "40.185740,-92.579699|40.188218,-92.581422", "mode": "walk"}
    headers = {
        "X-RapidAPI-Key": "e59c5e2a48mshe929e8c6509ac15p188c6cjsnd26c2ced7900",
        "X-RapidAPI-Host": "route-and-directions.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response


app = create_app()
app.app_context().push()
db.drop_all()
db.create_all()



@app.route("/")
def login():
    add_buildings()
    add_ryle_data()
    add_user()
    verify_username("habib23")
    verify_pswd("tru123")
    verify_username("hvhb")
    verify_pswd("sadwa")

    this_lat = (get_lat("West Campus Suites"))
    print(this_lat)
    this_long = (get_long("West Campus Suites"))
    print(this_long)
    return render_template('loginScreen.html')


@app.route("/signup")
def signUp():
    return render_template('signUpScreen.html')

@app.route("/map")
def homeMap():
    """Simple example of a fullscreen map."""

    response = get_directions_response()
    mls = response.json()['features'][0]['geometry']['coordinates']
    points = [(i[1], i[0]) for i in mls[0]]

    m = folium.Map()
    for point in [points[0], points[-1]]:
        folium.Marker(point).add_to(m)
        # add the lines
    folium.PolyLine(points, weight=5, opacity=1).add_to(m)
    # create optimal zoom
    df = pd.DataFrame(mls[0]).rename(columns={0: 'Lon', 1: 'Lat'})[['Lat', 'Lon']]
    sw = df[['Lat', 'Lon']].min().values.tolist()
    ne = df[['Lat', 'Lon']].max().values.tolist()
    m.fit_bounds([sw, ne])


    return m.get_root().render()

@app.route("/test")
def test():
    return render_template('homeScreen.html')


@app.route("/iframe")
def iframe():
    """Embed a map as an iframe on a page."""
    m = folium.Map()

    # set the iframe width and height
    m.get_root().width = "800px"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    return render_template(
        iframe=iframe,
    )


@app.route("/components")
def components():
    """Extract map components and put those on a page."""
    m = folium.Map(
        width=800,
        height=600,
    )

    m.get_root().render()
    header = m.get_root().header.render()
    body_html = m.get_root().html.render()
    script = m.get_root().script.render()

    return render_template(
        header=header,
        body_html=body_html,
        script=script,
    )


if __name__ == "__main__":
    app.run(debug=True)