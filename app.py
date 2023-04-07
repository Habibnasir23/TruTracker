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
app = Flask(__name__, template_folder = 'templates', static_folder='static')



def get_directions_response():
    url = "https://route-and-directions.p.rapidapi.com/v1/routing"
    querystring = {"waypoints": "40.185740,-92.579699|40.188218,-92.581422", "mode": "walk"}
    headers = {
        "X-RapidAPI-Key": "e59c5e2a48mshe929e8c6509ac15p188c6cjsnd26c2ced7900",
        "X-RapidAPI-Host": "route-and-directions.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response

@app.route("/")
def login():
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