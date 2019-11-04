from matplotlib import style
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from  flask import Flask, jsonify

# Set up query engine. 'echo=True is the default - will keep a log of activities'
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
#session = Session(engine)

# Create our Flask app

app = Flask(__name__)




@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return(f"Welcome to Johnny Giang's 'Home' page! </br>"
            f"/api/v1.0/precipitation </br>"
            f"/api/v1.0/stations </br>"
            f"/api/v1.0/tobs </br>"
            f"/api/v1.0/<start> </br>"
            f"/api/v1.0/<start>/<end> </br>"
    )




@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date_measurement = dt.date(2017, 8 ,23)
    one_year_ago = last_date_measurement - dt.timedelta(days=365)
    date = dt.date(2016, 8, 23)

    #### ASK: Convert the query results to a Dictionary using date as the key and prcp as the value. ####
    #### QUESTION!: VERIFY THIS IS RIGHT.

    #FOR REFERENCE:
    #result = session.query(Measurement.date, Measurement.station, Measurement.prcp, Measurement.tobs).filter(Measurement.date >= date).all()

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date).all()


    new_results = {}

    for dateprcp in results:
    
        new_results[dateprcp.date] = dateprcp.prcp

    return jsonify(new_results)




@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Return a JSON list of stations from the dataset.
    stations_result = session.query(Measurement.station).group_by(Measurement.station).order_by(Measurement.station).all()
    #results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date).all()
    all_stations = []

    for indv_station in stations_result:
        stations_dict = {}
        stations_dict['station'] = indv_station.station
        all_stations.append(stations_dict)
    
    return jsonify(all_stations)




@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date_measurement = dt.date(2017, 8 ,23)
    one_year_ago = last_date_measurement - dt.timedelta(days=365)
    date = dt.date(2016, 8, 23)

    #### ASK: Convert the query results to a Dictionary using date as the key and prcp as the value. ####
    #### QUESTION!: VERIFY THIS IS RIGHT.

    #FOR REFERENCE:
    #result = session.query(Measurement.date, Measurement.station, Measurement.prcp, Measurement.tobs).filter(Measurement.date >= date).all()

    results = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date >= date).all()
    tobs_results = []

    for tob in results:
        tobs_dict = {}
        tobs_dict['date'] = tob.date
        tobs_dict['station'] = tob.station
        tobs_dict['tobs'] = tob.tobs

        tobs_results.append(tobs_dict)
    
    return jsonify(tobs_results)




@app.route("/api/v1.0/<start_date>")
@app.route("/api/v1.0/<start_date>/<end_date>")

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

def calc_temps(start_date, end_date=None):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVE, and TMAX
    """

    #start_date = str(start_date + " 23:95:95")
    
    session = Session(engine)
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs), Measurement.date]

    if end_date == None:
        # result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date = start_date).all()
        result = session.query(*sel).group_by(Measurement.date).filter(Measurement.date >= start_date).filter(Measurement.date <= start_date).all()

    else:
        result = session.query(*sel).filter(Measurement.date >= start_date).group_by(Measurement.date).filter(Measurement.date <= end_date).all()

    result_list = []
    for x in result:
        result_dict = {
            "date" : x[3],
            "TMIN" : x[0],
            "TAVG" : x[1],
            "TMAX" : x[2]
        }
        result_list.append(result_dict)
    
    return jsonify(result_list)


if __name__ == "__main__":
    app.run(debug=True)