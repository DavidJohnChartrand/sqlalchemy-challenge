import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine('sqlite:///Resources/hawaii.sqlite')

Base = automap_base()

Base.prepare(autoload_with=engine)

# Create Classes
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create an app
app = Flask(__name__)


# Define static routes
@app.route("/")
def Home():
    """List of all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs"
    )


@app.route("/station")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a list of the Stations"""

    # Query the DB for all the distinct station
    results = session.query(Measurement.station).distinct().all()


    session.close()

    # Fromat the list for JSON
    all_stations = list(np.ravel(results))

    # Return the result and JSONIFY them
    return jsonify(all_stations)


@app.route("/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB

    session = Session(engine)

    rain= session.query(Measurement.date, func.avg(Measurement.prcp)).\
        filter(Measurement.date >'2016-08-23').\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    session.close()

    # Create a dictionary with the date as a key and precipitaion as the value
    all_precipitation = []
    # Input the results of the query into the dictionary
    for  date, prcp in rain:
        precipitation_dict = {}
        precipitation_dict [date] = prcp
        all_precipitation.append(precipitation_dict)
    

    return jsonify(all_precipitation)

@app.route("/tobs")
def tobs():
    session = Session(engine)

    # Query the temperature mesurments from the single station
    temperature = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >'2016-08-23').all()

    session.close()

    # prep the list
    all_stations = list(np.ravel(temperature))

    return jsonify(all_stations)

@app.route("/<start>")
def temp(start):
    """Fetch the date and reply back with Min, Avg and Max Temp
       the path variable supplied by the user."""

    session = Session(engine)


    date_check = session.query(Measurement.date).\
    filter(Measurement.date == start).distinct().all()

    # Create the list of values I want to extract fromt the queries
    sel =[
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
        ]
    # Query and filter by dates larger then start
    temperature = session.query(*sel).\
    filter(Measurement.date >= start).all()

    result = list(np.ravel(temperature))
        
    try:
        
        return jsonify(result)
    except: jsonify({"error": f" Date {start} not found."}), 404

@app.route("/<start>/<end>")
def temp2(start, end):
    """Fetch the date and reply back with Min, Avg and Max Temp
       the path variable supplied by the user"""

    session = Session(engine)

    sel =[
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
        ]
    temperature = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    result = list(np.ravel(temperature))
        
    try:
        
        return jsonify(result)
    except: jsonify({"error": f" Date {start} not found."}), 404

# Define main behavior
if __name__ == "__main__":
    app.run()
