""" flask_example.py
    Required packages:
    - flask
    - folium
    Usage:
    Start the flask server by running:
        $ python flask_example.py
    And then head to http://127.0.0.1:5000/ in your browser to see the map displayed
"""

from flask import Flask, render_template, jsonify

import folium
import requests
import pandas as pd
version = 1

from flask import Flask, request, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta


db = SQLAlchemy()


def transfer_data_from_file_to_database():
    with open("Entrances.txt", 'r') as file:
        for line in file:
            data_list = line.strip().split(',')
            Building_name = data_list[0]
            Building_door = data_list[1]
            Building_door = Building_door.lstrip()
            Latitude = float(data_list[2])
            Longitude = float(data_list[3])
            this_location = Locations(Building_name, Building_door, Latitude, Longitude)
            db.session.add(this_location)
            db.session.commit()


def populate_drop_down_menu(buidling_dict):
    with open("Entrances.txt") as file:
        for line in file:
            data_list = line.strip().split(',')
            if data_list[0] in buidling_dict.keys():
                buidling_dict[data_list[0]].append(data_list[1].lstrip())
            else:
                buidling_dict[data_list[0]] = [data_list[1].lstrip()]


def create_app():
    app1 = Flask(__name__, template_folder='templates', static_folder='static')
    app1.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Trutracker.sqlite3'
    app1.config['SECRET_KEY'] = "random string"
    db.init_app(app1)
    # after 5 minutes of inactivity, user's session will expire. They will need to log in again
    app1.permanent_session_lifetime = timedelta(minutes=5)
    return app1


class User(db.Model):
    user_name = db.Column(db.String(100))
    user_email = db.Column(db.String(100), primary_key=True)
    user_pswd = db.Column(db.String(100))

    def __init__(self, name, email, pswd):
        self.user_name = name
        self.user_email = email
        self.user_pswd = pswd


class Locations(db.Model):
    building_name = db.Column(db.String(100))
    building_door = db.Column(db.String(100))
    building_latitude = db.Column(db.Float, primary_key=True)
    building_longitude = db.Column(db.Float)

    def __init__(self, name, build_door, lat, long):
        self.building_name = name
        self.building_door = build_door
        self.building_latitude = lat
        self.building_longitude = long


class Saved_Locations(db.Model):
    user_email = db.Column(db.String(100), primary_key=True) # a combination of primary keys
    saved_name = db.Column(db.String(100), primary_key=True)
    building_name = db.Column(db.String(100))
    door_name = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    #__table_args__ = (db.UniqueConstraint('user_email', 'saved_name', name='unique_saved_location'),)

    def __init__(self, useremail, savedname, buildname, doorname, lat, long):
        self.user_email = useremail
        self.saved_name = savedname
        self.building_name = buildname
        self.door_name = doorname
        self.latitude = lat
        self.longitude = long


class Ryle_Hall(db.Model):
    building_name = db.Column(db.String(100), primary_key=True)
    distance_from_building = db.Column(db.Integer)
    time_from_building = db.Column(db.Integer)

    def __init__(self, name, dist, time):
        self.building_name = name
        self.distance_from_building = dist
        self.time_from_building = time


def add_buildings():
    loc_1 = Locations("West Campus Suites", "North", 1211, 1222)
    db.session.add(loc_1)
    db.session.commit()
    loc_2 = Locations("Recreation Center", "South", 1311, 1333)
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
    user1 = User("habib", "habib@gmail.com", "tru123")
    db.session.add(user1)
    db.session.commit()
    user2 = User("mhmd123", "mhmd@gmail.com", "prince123")
    db.session.add(user2)
    db.session.commit()


def add_user2(u_name, u_email, u_password):
    user = User(u_name, u_email, u_password)
    db.session.add(user)
    db.session.commit()


def add_saved_location(email, buildname, buildoor, savedname):
    this_lat = get_lat(buildname, buildoor)
    this_long = get_long(buildname, buildoor)
    saveLoc = Saved_Locations(email, savedname, buildname, buildoor, this_lat, this_long)
    db.session.add(saveLoc)
    db.session.commit()


def get_saved_locations(email, savedname):
    loc_details = {}
    loc = Saved_Locations.query.filter_by(user_email=email, saved_name=savedname).first()
    if loc is not None:
        loc_details[loc.building_name] = loc.door_name
    else:
        loc_details = None
    return loc_details


def get_all_saved_locations(email):
    loc_details = {}
    locs = Saved_Locations.query.filter_by(user_email=email).all()
    for loc in locs:
        loc_details[loc.saved_name] = {'building_name': loc.building_name, 'door_name':loc.door_name}
    return loc_details

def get_lat(name, door):
    loc = Locations.query.filter_by(building_name=name, building_door=door).first()
    if loc:
        return loc.building_latitude
    else:
        return None


def get_long(name, door):
    loc = Locations.query.filter_by(building_name=name, building_door=door).first()
    if loc:
        return loc.building_longitude
    else:
        return None


def verify_user(useremail, userpswd):
    email_exists = db.session.query(db.exists().where(User.user_email == useremail)).scalar()
    if email_exists:
        print("this email is valid")
        user = User.query.filter_by(user_email=useremail).first()
        pswd = user.user_pswd
        if pswd != userpswd:
            print("the password does not match the username")
            return False
        print("the password matches the username")
        return True
    else:
        print("this email is not valid")
        return False


def verify_pswd(password):
    exists = db.session.query(db.exists().where(User.user_pswd == password)).scalar()
    if exists:
        print("this password is valid")
        return True
    else:
        print("this password is not valid")
        return False


def get_directions_response(lat_src,long_src,lat_dist,long_dist):
    url = "https://route-and-directions.p.rapidapi.com/v1/routing"
    querystring = {"waypoints":f"{str(lat_src)},{str(long_src)}|{str(lat_dist)},{str(long_dist)}","mode":"walk"}
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
transfer_data_from_file_to_database()
add_buildings()
add_ryle_data()
add_user()
# verify_email("habibnasir23@gmail.com")
verify_pswd("tru123")
# verify_email("hvhb@gmail.com")
verify_pswd("sadwa")

this_lat = (get_lat("Ryle Hall", "Southwest"))
print(this_lat)
this_long = (get_long("West Campus Suites", "Southeast"))
print(this_long)
add_saved_location("habibnasir23@gmail.com", "Ryle Hall", "Southwest", "Home")
add_saved_location("habibnasir23@gmail.com", "Ryle Hall", "West", "Work")
this_loc = get_saved_locations("habibnasir23@gmail.com", "Home")
print(this_loc)
all_saved_locs = get_all_saved_locations("habibnasir23@gmail.com")
print(all_saved_locs)

@app.route("/")
def index():
    if not session.get("name"):
       return redirect("/login")
    return render_template('loginScreen.html')


@app.route("/home", methods=["POST","GET"])
def home():
    building_dict = {}
    populate_drop_down_menu(building_dict)
    if request.method == "POST":
        building_name_src = request.form.get("building_name_src")
        door_name_src = request.form.get("door_name_src")

        building_name_dist = request.form.get("building_name_dist")
        door_name_dist = request.form.get("door_name_dist")
        lat_src = (get_lat(building_name_src, door_name_src))
        long_src = (get_long(building_name_src, door_name_src))
        lat_dist = (get_lat(building_name_dist, door_name_dist))
        long_dist = (get_long(building_name_dist, door_name_dist))
        return redirect(url_for("homeMap",lat_src = lat_src,long_src=long_src,lat_dist=lat_dist,long_dist=long_dist))

    return render_template('homeScreen.html', building_name=building_dict.keys(), building_dict=building_dict)

@app.route("/process_saved_data", methods=["POST"])
def process_saved_data():
    fav_building_name = request.form.get("fav_buidling_name")
    fav_door_name = request.form.get("fav_door_name")
    fav_email = session['email']
    add_saved_location(fav_email,fav_building_name,fav_door_name,"Yourmom")
    return jsonify({"Favorite Location has been Submitted": "Data received!"})

@app.route('/api/dictionary')
def get_dictionary():
    fav_email = session['email']
    dictionary = get_all_saved_locations(fav_email)
    return jsonify(dictionary)

@app.route("/login", methods=["POST", "GET"])
def login():
    session.permanent = True
    if request.method == "POST":
        email = request.form.get("email")
        session["email"] = email
        password = request.form.get("password")
        session['password'] = password
        if verify_user(email, password):
            return redirect("/home")
        else:
            return render_template("loginScreen.html")
    return render_template("loginScreen.html")


@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")

@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/signup", methods=["GET", "POST"])
def signUp():
    session.permanent = True
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")
        session['name'] = name
        session['email'] = email
        session['password'] = password
        add_user2(name, email, password)
        return redirect("/login")
    return render_template("signUpScreen.html")


@app.route("/map/<lat_src>/<long_src>/<lat_dist>/<long_dist>")
def homeMap(lat_src,long_src,lat_dist,long_dist):
    """Simple example of a fullscreen map."""

    response = get_directions_response(lat_src,long_src,lat_dist,long_dist)
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
    m.get_root().width = "800px"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    m.get_root().html.add_child(folium.Element("""
    <div style="position: fixed; 
     top: 50px; left: 70px; width: 163px; height: 100px;
     background-color:white; border-radius: 5px; border:2px solid grey;z-index: 900;">
    <h5>Route new destination<h5>
    <button class="button-9" onclick="goBack()" role="button">Back</button>

    <script>
    function goBack(){
        window.location.href = "/home"
    }
    </script>

<style>
.button-9 {
  appearance: button;
  backface-visibility: hidden;
  background-color: #405cf5;
  border-radius: 6px;
  border-width: 0;
  box-shadow: rgba(50, 50, 93, .1) 0 0 0 1px inset,rgba(50, 50, 93, .1) 0 2px 5px 0,rgba(0, 0, 0, .07) 0 1px 1px 0;
  box-sizing: border-box;
  color: #fff;
  cursor: pointer;
  font-family: -apple-system,system-ui,"Segoe UI",Roboto,"Helvetica Neue",Ubuntu,sans-serif;
  font-size: 100%;
  height: 44px;
  line-height: 1.15;
  outline: none;
  overflow: hidden;
  padding: 0 25px;
  position: absolute;
  text-align: center;
  text-transform: none;
  transform: translateZ(0);
  transition: all .2s,box-shadow .08s ease-in;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  width: 50%;
  margin-left: 10px;
}

.button-9:hover{
  background: #2c52ed;
}

.button-9:disabled {
  cursor: default;
}

.button-9:focus {
  box-shadow: rgba(50, 50, 93, .1) 0 0 0 1px inset, rgba(50, 50, 93, .2) 0 6px 15px 0, rgba(0, 0, 0, .1) 0 2px 2px 0, rgba(50, 151, 211, .3) 0 0 0 4px;
}
5{
margin-left: 5px;
text-align: center;
}
</style>
    </div>
    """))

    global version
    version += 1

    m.save('templates/map' + str(version) +'.html')
    return render_template('map' + str(version) +'.html', iframe=iframe)


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
