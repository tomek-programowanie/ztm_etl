import sqlite3
import requests
import pandas as pd
import sqlalchemy
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_if_valid_data(df: pd.DataFrame) -> bool:
    # Check if there is data
    if df.empty:
        print('Something goes wrong, there is no ZTM vehicle on the road??? | Empty dataset')
        return False

    # Check if there are duplicates (by checking vehicle number mixed with type)
    if df.duplicated(subset=['vehicle_number', 'type']).sum() > 0:
        raise Exception('It seems like there is one vehicle in two places... | Duplicated values')

    # Check for nulls
    if df.isnull().values.any():
        raise Exception('Null value(s)')

    return True


def run_ztm_vehicles_etl():
    URL = 'https://api.um.warszawa.pl/api/action/busestrams_get/'
    DATABASE_LOCATION = "sqlite:///ztm_vehicles.sqlite"
    API_TOKEN = 'a544a187-62b3-4d70-b8e6-3f29f69a7241'
    RESOURCE_ID = 'f2e5503e927d-4ad3-9500-4ab9e55deb59'

    bus_params = {
        'apikey': API_TOKEN,
        'type': 1,
        'resource_id': RESOURCE_ID
    }

    tram_params = {
        'apikey': API_TOKEN,
        'type': 2,
        'resource_id': RESOURCE_ID
    }

    vehicle_types = ['bus', 'tram']

    vehicle_types_dict = {
        'bus': bus_params,
        'tram': tram_params
    }

    line_numbers = []
    longitudes = []
    latitudes = []
    vehicle_numbers = []
    times = []
    brigades = []
    types = []


    # Extract
    for vehicle_type in vehicle_types:
        r = requests.get(URL, vehicle_types_dict[vehicle_type], verify=False)
        data = r.json()

        for result in data['result']:
            line_numbers.append(result['Lines'])
            longitudes.append(result['Lon'])
            latitudes.append(result['Lat'])
            vehicle_numbers.append(result['VehicleNumber'])
            times.append(result['Time'])
            brigades.append(result['Brigade'])
            types.append(vehicle_type)

    vehicles_dict = {
        'line_number': line_numbers,
        'longitude': longitudes,
        'latitude': latitudes,
        'vehicle_number': vehicle_numbers,
        'time': times,
        'brigade': brigades,
        'type': types
    }

    vehicles_df = pd.DataFrame(vehicles_dict, columns=['line_number', 'longitude', 'latitude', 'vehicle_number', 'time',
                                                       'brigade', 'type'])

    # Validate
    if check_if_valid_data(vehicles_df):
        print("Data valid, please proceed.")

    # Load
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    connection = sqlite3.connect('ztm_vehicles.sqlite')
    crsr = connection.cursor()

    sql_command = """
        CREATE TABLE IF NOT EXISTS ztm_vehicles(
            line_number VARCHAR(200),
            longitude VARCHAR(200),
            latitude VARCHAR(200),
            vehicle_number VARCHAR(200),
            time VARCHAR(200),
            brigade VARCHAR(200),
            type VARCHAR(200)
        )    
        """

    crsr.execute(sql_command)

    try:
        vehicles_df.to_sql("ztm_vehicles", engine, index=False, if_exists='append')
        print('Data has been loaded properly')
    except:
        print("Data has not been loaded properly")

    connection.close()
