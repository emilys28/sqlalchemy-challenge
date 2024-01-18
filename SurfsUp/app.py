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

# /
# Start at the homepage.
#List all the available routes.

@app.route("/")
def welcome():
    return (
        f"Welcome to the .. API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )

# /api/v1.0/precipitation
# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
# to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    precipt_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago)
    precipitation_dict = {date: prcp for date, prcp in precipt_data}
    return jsonify(precipitation_dict)

# /api/v1.0/stations
# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    stations_list = session.query(Station.station).distinct().all()
    stations_list = [station[0] for station in stations_list]
    return jsonify(stations_list)

# /api/v1.0/tobs
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
      tobs = session.query(Measurement.date,  Measurement.tobs,Measurement.prcp).\
                filter(Measurement.date >= one_year_ago).\
                filter(Measurement.station == most_active_station).\
                order_by(Measurement.date).all()
      # Convert the list to Dictionary
      all_tobs = []
      for prcp, date,tobs in tobs:
            tobs_dict = {}
            tobs_dict["prcp"] = prcp
            tobs_dict["date"] = date
            tobs_dict["tobs"] = tobs
            
            all_tobs.append(tobs_dict)
            return jsonify(all_tobs)
      
# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
def start_date_summary(start):
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