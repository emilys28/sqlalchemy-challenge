# Import the dependencies.
from flask import Flask, jsonify

import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
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
def welcome():
    return (
        f"Welcome to the .. API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    precipt_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= "2016-08-24")
    precipitation_dict = {date: prcp for date, prcp in precipt_data}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    stations_list = session.query(Station.station).distinct().all()
    stations_list = [station[0] for station in stations_list]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
     active_station_tobs = session.query(Measurement.date,  Measurement.tobs,Measurement.prcp).\
                filter(Measurement.date >= '2016-08-23').\
                filter(Measurement.station=='USC00519281').\
                order_by(Measurement.date).all()
     tobs_list = [{"Date": date, "Temperature": tobs} for date, tobs in active_station_tobs]
     return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_date_summary(start):
    # Query to calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    # Modify this query according to your database structure
    temperature_summary = session.query(func.min(Measurement.tobs).label('min_temp'),
                                       func.avg(Measurement.tobs).label('avg_temp'),
                                       func.max(Measurement.tobs).label('max_temp'))\
        .filter(Measurement.date >= start)\
        .all()
    summary_dict = {
        "Min Temperature": temperature_summary[0].min_temp,
        "Average Temperature": temperature_summary[0].avg_temp,
        "Max Temperature": temperature_summary[0].max_temp
    }
    return jsonify(summary_dict)

#/api/v1.0/<start> and /api/v1.0/<start>/<end>
#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>/<end>")
def start_end_date_summary(start, end):
    # Query to calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive
    # Modify this query according to your database structure
    temperature_summary = session.query(func.min(Measurement.tobs).label('min_temp'),
                                       func.avg(Measurement.tobs).label('avg_temp'),
                                       func.max(Measurement.tobs).label('max_temp'))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end)\
        .all()

    # Convert the query results to a dictionary
    summary_dict = {
        "Min Temperature": temperature_summary[0].min_temp,
        "Average Temperature": temperature_summary[0].avg_temp,
        "Max Temperature": temperature_summary[0].max_temp
    }

    return jsonify(summary_dict)


if __name__ == "__main__":
    app.run(debug=True)