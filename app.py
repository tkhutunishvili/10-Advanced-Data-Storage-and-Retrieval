import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/end (Example: /api/v1.0/2016-06-20/2016-07-12) <br/>"
    )

#Query for last date
last_date_q = session.query(Measurement).order_by(Measurement.date.desc()).limit(1)
    
for date in last_date_q:
    last_date_r = date.date
last_date_r = dt.datetime.strptime(last_date_r, "%Y-%m-%d")

#One year ago from last date
last_date_year_ago = last_date_r - dt.timedelta(days=365)

@app.route("/api/v1.0/precipitation")
def prcp():
    """Convert the query results to a Dictionary using date as the key and prcp as the value"""
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_date_year_ago, Measurement.date <= last_date_r).\
        order_by(Measurement.date).all()
    # Create a dictionary from the row data and append to a list of all_prcps

    all_prcps ={record.date: record.prcp  for record in  prcp_data}

    return jsonify(all_prcps)

@app.route("/api/v1.0/stations")
def station():
    """Return a list of all Stations"""
    # Query all Stations
    stations_list = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(stations_list))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of Tobs"""
    # Query date and tobs

    tobs_data = session.query(Measurement.tobs).\
        filter(Measurement.date >= last_date_year_ago, Measurement.date <= last_date_r).\
        order_by(Measurement.date).all()

    all_tobs = list(np.ravel(tobs_data))

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature(start, end = None):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    if end == None:
        end = last_date_r
    temp_tobs = [Measurement.station,
         Station.name,
         func.min(Measurement.tobs),
         func.max(Measurement.tobs),
         func.avg(Measurement.tobs)]

    temp_data = session.query(*temp_tobs).filter(Measurement.station==Station.station).\
    filter(Measurement.date >= start).\
    group_by(Measurement.station).all()
    
    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)
