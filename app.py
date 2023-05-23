# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, render_template, jsonify


#################################################
# Database Setup
#################################################

# Create engine to connect to the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
connect = engine.connect()

# reflect an existing database into a new model
# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Define the app route
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    #querying all data
    prcp_data = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    #adding the data to alist 
    precipitation_ls = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = precipitation_ls.append(prcp_dict)

    # Return the data as JSON
    return jsonify(precipitation_data)

# Define the app route
@app.route("/api/v1.0/stations")
def stations():

    #querying all data
    station_data = session.query(Station.station).all()

    session.close()

    station_list = [station[0] for station in station_data]

    # Return the list of stations as JSON
    return jsonify(station_list)

# Define the app route
@app.route("/api/v1.0/tobs")
def tobs():
   
    # first i query the data from stations and hten I make it in descending prder in order 
    # to get the data in order from starting from the beginning
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first()

    # in this calucaltion I went back a year 
    recent_date_query = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active_station[0]).first()
    max_date = recent_date_query[0]
    starting_date = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # in this line of code i applied filters to the most active stations as well as from the starting 
    # date from the year previous
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station[0]).\
        filter(Measurement.date >= starting_date).all()

    # I created a for loop for the both the date and temperature into a list from the stations
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    # Return the list of temperature observations as JSON
    return jsonify(tobs_list)


# Define the app routes
@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    #in this code I queried the min, avg and max using func. and applied to a filter in order to 
    # gain data from the beginning of the year
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Here I created a list to store the results
    temp_stats = {}
    temp_stats["TMIN"] = results[0][0]
    temp_stats["TAVG"] = results[0][1]
    temp_stats["TMAX"] = results[0][2]

    # Return the temperature statistics as JSON
    return jsonify(temp_stats)


@app.route("/api/v1.0/<start>/<end>")
def temp_stats_range(start, end):
    # #in this code I queried the min, avg and max using func. and applied to a filter in order to 
    # gain data from the beginning of the year but this time also added an end date
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # Here I created a list to store the results
    temp_stats = {}
    temp_stats["TMIN"] = results[0][0]
    temp_stats["TAVG"] = results[0][1]
    temp_stats["TMAX"] = results[0][2]

    # Return the temperature statistics as JSON
    return jsonify(temp_stats)


if __name__ == '__main__':
    app.run(debug=True)
