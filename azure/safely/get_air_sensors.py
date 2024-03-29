from datetime import datetime
import sqlite3

def get_mq_data(number_of_rows):
    try:
        conn = sqlite3.connect('database/sensor_data.db')
        cur = conn.cursor()
        mq_data = {
            "mq2": {"datetimes": [], "values": []},
            "mq7": {"datetimes": [], "values": []},
            "mq135": {"datetimes": [], "values": []},
        }

        for sensor in mq_data:
            cur.execute(f"SELECT datetime, {sensor} FROM {sensor}_data ORDER BY datetime DESC LIMIT {number_of_rows};")
            rows = cur.fetchall()
            for row in rows:
                timestamp = datetime.strptime(row[0], '%d/%m/%Y %H:%M:%S')
                formatted_timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
                mq_data[sensor]["datetimes"].append(formatted_timestamp)
                mq_data[sensor]["values"].append(row[1])

        for sensor_data in mq_data.values():
            sensor_data["datetimes"] = sensor_data["datetimes"][::-1]
            sensor_data["values"] = sensor_data["values"][::-1]

        return mq_data
    except sqlite3.Error as sql_e:
        print(f"SQLite error occurred: {sql_e}")
    finally:
        if conn:
            conn.close()

def get_room_data(number_of_rows):
    room_query = """SELECT * FROM dht11_data ORDER BY datetime DESC;"""
    room_datetimes = []
    room_temperatures = []
    room_humidities = []
        
    try:
        conn = sqlite3.connect('database/sensor_data.db')
        cur = conn.cursor()
        cur.execute(room_query)
        room_rows = cur.fetchmany(number_of_rows)
        
        for room_row in room_rows:
            timestamp_str = room_row[0]
            timestamp = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M:%S')
            formatted_timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
            room_datetimes.append(formatted_timestamp)
            room_temperatures.append(room_row[1])
            room_humidities.append(room_row[2])
        
        return room_datetimes[::-1], room_temperatures[::-1], room_humidities[::-1]
    except sqlite3.Error as sql_e:
        print(f"SQLite error occurred: {sql_e}")
    finally:
        if conn:
            conn.close()

def get_battery_data(number_of_rows):
    battery_query = """SELECT datetime, BAT FROM bat_data ORDER BY datetime DESC;"""
    battery_datetimes = []
    battery_values = []

    try:
        conn = sqlite3.connect('database/sensor_data.db')
        cur = conn.cursor()
        cur.execute(battery_query)
        battery_rows = cur.fetchmany(number_of_rows)

        for battery_row in battery_rows:
            timestamp_str = battery_row[0]
            timestamp = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M:%S')
            formatted_timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
            battery_datetimes.append(formatted_timestamp)
            battery_values.append(battery_row[1])

        return battery_datetimes[::-1], battery_values[::-1]
    except sqlite3.Error as sql_e:
        print(f"SQLite error occurred: {sql_e}")
    finally:
        if conn:
            conn.close()

def get_shelly_state():
    conn = sqlite3.connect('database/sensor_data.db')
    c = conn.cursor()
    c.execute("SELECT state FROM shelly1_state ORDER BY datetime DESC LIMIT 1")
    state = c.fetchone()
    conn.close()
    return state[0] if state else None

if __name__ == "__main__":
    mq_number_of_rows = 10
    room_number_of_rows = 10
    
    mq_data = get_mq_data(mq_number_of_rows)
    for sensor, data in mq_data.items():
        print(f"{sensor} Data:")
        print("Datetimes:", data["datetimes"])
        print("Values:", data["values"])

    room_datetimes, room_temperatures, room_humidities = get_room_data(room_number_of_rows)
    print("\nRoom Data:")
    print("Datetimes:", room_datetimes)
    print("Temperatures:", room_temperatures)
    print("Humidities:", room_humidities)
