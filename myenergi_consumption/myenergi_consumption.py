import streamlit as st
import requests
from requests.auth import HTTPDigestAuth
from datetime import datetime, timedelta

# Function to fetch data from Myenergi API


def get_consumption_data(eddi_serial, api_key, selected_date):
    formatted_date = selected_date.strftime("%Y-%m-%d")
    url = f"https://s18.myenergi.net/cgi-jday-E{eddi_serial}-{formatted_date}"
    response = requests.get(url, auth=HTTPDigestAuth(eddi_serial, api_key))
    if response.status_code == 200:
        return response.json().get(f"U{eddi_serial}", [])
    else:
        return None

# Convert joules to watt-hours


def joules_to_wh(joules):
    return joules / 3600

# Function to convert temperature from Fahrenheit to Celsius


def fahrenheit_to_celsius(fahrenheit_temp):
    return (fahrenheit_temp - 32) * 5 / 9

# Streamlit app


def main():
    st.title("Myenergi Consumption Data")
    st.write(
        "Enter the Eddi Serial, API Key, and select the date to fetch the total minute data consumption.")

    # Input fields for user
    eddi_serial = st.text_input("Eddi Serial:")
    api_key = st.text_input("API Key:")
    selected_date = st.date_input("Select Date", datetime.now())

    if st.button("Fetch Data"):
        if eddi_serial and api_key:
            consumption_data = get_consumption_data(
                eddi_serial, api_key, selected_date)
            if consumption_data:
                imported_energy_sum = 0
                house_consumption_sum = 0
                voltage_sum = 0
                frequency_sum = 0
                tank_temp1_sum = 0
                tank_temp2_sum = 0
                num_entries = 0
                num_valid_temps = 0  # Counter for valid temperature values

                for data in consumption_data:
                    imported_energy_wh = joules_to_wh(data.get('imp', 0))
                    house_consumption_w = data.get('hsk', 0)
                    voltage_v1 = data.get('v1', None) / 10
                    frequency = data.get('frq', None) / 100
                    tank_temp1 = data.get('pt1', None)
                    tank_temp2 = data.get('pt2', None)

                    imported_energy_sum += imported_energy_wh
                    house_consumption_sum += house_consumption_w
                    voltage_sum += voltage_v1 if voltage_v1 is not None else 0
                    frequency_sum += frequency if frequency is not None else 0

                    # Calculate valid tank temperatures
                    if tank_temp1 is not None and tank_temp1 != 127:
                        tank_temp1_sum += tank_temp1
                        num_valid_temps += 1

                    if tank_temp2 is not None and tank_temp2 != 127:
                        tank_temp2_sum += tank_temp2

                    num_entries += 1

                avg_voltage = voltage_sum / num_entries if num_entries > 0 else 0
                avg_frequency = frequency_sum / num_entries if num_entries > 0 else 0

                # Calculate average tank temperatures only when there are valid temperature values
                if num_valid_temps > 0:
                    avg_tank_temp1 = tank_temp1_sum / num_valid_temps
                    avg_tank_temp2 = tank_temp2_sum / num_valid_temps
                else:
                    avg_tank_temp1 = 0
                    avg_tank_temp2 = 0

                # Calculate total house consumption in watt-hours (Wh)
                total_house_consumption_wh = house_consumption_sum / \
                    60  # Convert to watt-hours (Wh)

                # Calculate self consumption in watt-hours
                calculated_self_consumption = total_house_consumption_wh - imported_energy_sum

                # Callout cards for total imported energy, total house consumption, and averages
                st.subheader("Summary:")
                st.write("Total Imported Energy: {:.2f} Wh".format(
                    imported_energy_sum))
                st.write("Total House Consumption: {:.2f} Wh".format(
                    total_house_consumption_wh))
                st.write("Self Consumption: {:.2f} Wh".format(
                    calculated_self_consumption))
                st.write("Average Voltage: {:.2f} V".format(avg_voltage))
                st.write("Average Frequency: {:.2f} Hz".format(avg_frequency))
                st.write("Average Tank Temperature Sensor 1: {:.2f} °C".format(
                    avg_tank_temp1))
                st.write("Average Tank Temperature Sensor 2: {:.2f} °C".format(
                    avg_tank_temp2))

            else:
                st.error(
                    "Failed to fetch data. Please check your Eddi Serial, API Key, and selected date.")
        else:
            st.warning("Please enter both Eddi Serial and API Key.")


if __name__ == "__main__":
    main()
