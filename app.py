from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement_ref = Base.classes.measurement
station_ref = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """All available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value."""
    # Query
    results = session.query(measurement_ref.date, measurement_ref.prcp).all()
    session.close()

    # Create a dictionary from the row data and append to a list
    precipitation = []
    for date, prcp in results:
        prec_dict = {}
        prec_dict["date"] = date
        prec_dict["prcp"] = prcp
        precipitation.append(prec_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query
    results = session.query(station_ref.name, measurement_ref.station).\
                filter(station_ref.station == measurement_ref.station).\
                group_by(measurement_ref.station).\
                all()

    session.close()

    # Convert list of tuples into normal list
    stations = list(np.ravel(results))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations of the most active station for the last year of data."""
    # Query
    last_date = session.query(measurement_ref.date).order_by(measurement_ref.date.desc()).first()
    last_date = last_date[0]
    year = int(last_date[:4])
    month = int(last_date[5:7])
    day = int(last_date[8:10])
    start_date = dt.date(year, month, day) - dt.timedelta(days=365)
    results = session.query(measurement_ref.date, measurement_ref.tobs).\
                filter(measurement_ref.date >= start_date).\
                filter(measurement_ref.date <= last_date).\
                filter(measurement_ref.station == 'USC00519281').\
                order_by(measurement_ref.date).all()

    session.close()

    # Convert list of tuples into normal list
    tobs = list(np.ravel(results))

    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def Start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    """When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    # Query
    results = session.query(
                            func.min(measurement_ref.tobs),
                            func.avg(measurement_ref.tobs),
                            func.max(measurement_ref.tobs)
                            ).\
                            filter(measurement_ref.date >= start).all()

    session.close()

    # Convert list of tuples into normal list
    start_stats = list(np.ravel(results))

    return jsonify(start_stats)

@app.route("/api/v1.0/<start>/<end>")
def Start_End(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    # Query
    results = session.query(
                            func.min(measurement_ref.tobs),
                            func.avg(measurement_ref.tobs),
                            func.max(measurement_ref.tobs)
                            ).\
                            filter(measurement_ref.date >= start).\
                            filter(measurement_ref.date <= end).all()

    session.close()

    # Convert list of tuples into normal list
    start_end_stats = list(np.ravel(results))

    return jsonify(start_end_stats)


if __name__ == "__main__":
    app.run(debug=True)