import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

import flask
from flask import Flask, jsonify

import datetime as dt
import numpy as np
import pandas as pd

#setup database
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask setup
app = Flask(__name__)

#Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"This query returns precipitation data between 08/24/16 and 08/23/17 inclusive in Hawaii.<br/>"
        f"/api/v1.0/stations<br/>"
        f"This query returns the list of stations where the precipitation data was gathered from.<br/>"
        f"/api/v1.0/tobs<br/>"
        f"This query returns the dates and temperature observations of the most active station, station USC00519281, during the tracked time period.<br/>"
        f"/api/v1.0/<start><br/>"
        f"The query above provides the minimum temperature, maximum temperature, and average temperature given the dates you provide.  If only the start date is provided, the calculations taken will include data from your selected start date until the end of observation, 08/23/17.<br/>"
        f"Please enter a date after the first slash using the following format Month/Day/Year.  Include zeroes with day/month and write the whole year please."
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = list(np.ravel(last_date))[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    last_year = last_date - dt.timedelta(days=365)
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > last_year).all()

    session.close()

    # Create a dictionary from the row data
    rain_data=[]
    for date,prcp in data:
        data_dict = {}
        data_dict["date"] = date
        data_dict["precipitation in inches"] = prcp
        rain_data.append(data_dict)
    #return data
    return jsonify(rain_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    station_list = list(np.ravel(results))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    station_count=func.count(Measurement.station)
    station_activity = session.query(Measurement.station, station_count).group_by(Measurement.station).order_by(station_count.desc()).all()
    most_active_station = station_activity[0][0]
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = list(np.ravel(last_date))[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    last_year = last_date - dt.timedelta(days=365)
    temps = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > last_year).filter(Measurement.station==most_active_station).all()
   
    session.close()

    temp_data=[]
    for date,tobs in temps:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temperature"] = tobs
        temp_data.append(temp_dict)
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")
def startdate(start):
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = list(np.ravel(last_date))[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    last_year = last_date - dt.timedelta(days=365)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date > last_year).all()

    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def startandenddates(start,end):
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = list(np.ravel(last_date))[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    last_year = last_date - dt.timedelta(days=365)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date<=end).filter(Measurement.date > last_year).all()

    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)




