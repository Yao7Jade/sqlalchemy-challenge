# Import the dependencies.
from flask import Flask,jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import desc
import pandas as pd
import datetime as dt




#################################################
# Database Setup
# ################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
# ################################################
app = Flask(__name__)


#################################################
# Flask Routes
# ################################################
@app.route("/")
def home():
    return """
    /api/v1.0/precipitation <br>
    /api/v1.0/stations <br>
    /api/v1.0/tobs <br>
    /api/v1.0/start <br>
    /api/v1.0/start/end
    """


@app.route("/api/v1.0/precipitation")
def precipitation():
    end_date = session.query(func.max(Measurement.date)).all()[0][0]
    end_datetime = dt.datetime.strptime(end_date, '%Y-%m-%d')
    start_datetime = end_datetime - dt.timedelta(days=365)

    results = session.query(Measurement).filter(Measurement.date >= start_datetime).all()

    data =  {  measurement.date:measurement.prcp  for measurement in  results }

    return jsonify(data)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    stations = []
    for station,name,latitude,longitude,elevation in results:
        station_info = {}
        station_info['station'] = station
        station_info['name'] = name
        station_info['latitude'] = latitude
        station_info['longitude'] = longitude
        station_info['elevation'] = elevation
        stations.append(station_info)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(Measurement.station, func.count(Measurement.station)).group_by(
        Measurement.station).order_by(desc(func.count(Measurement.station))).all()

    active_id = results[0][0]

    end_date = session.query(func.max(Measurement.date)).all()[0][0]
    end_datetime = dt.datetime.strptime(end_date, '%Y-%m-%d')
    start_datetime = end_datetime - dt.timedelta(days=365)

    results = session.query(Measurement).filter(Measurement.date >= start_datetime).filter(
        Measurement.station == active_id).all()
    date_tobses = [  measurement.tobs for measurement in results]

    return jsonify(date_tobses)

@app.route("/api/v1.0/<start>")
def get_min_avg_max_tempature(start):
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date>=start).all()
    result = results[0]
    tempatures = list(result)
    return jsonify(tempatures)

@app.route("/api/v1.0/<start>/<end>")
def get_min_avg_max_tempature2(start,end):
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date>=start)\
        .filter(Measurement.date<=end)\
        .all()
    result = results[0]
    tempatures = list(result)
    return jsonify(tempatures)

if __name__ == "__main__":
    app.run(debug=True)
