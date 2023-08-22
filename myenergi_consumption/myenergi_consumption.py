import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPDigestAuth
from datetime import datetime, timedelta


def get_device_data(device_serial, api_key):
    url = f"https://s18.myenergi.net/cgi-jstatus-*"
    response = requests.get(url, auth=HTTPDigestAuth(device_serial, api_key))
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_consumption_data(device, device_serial, gateway_serial, api_key, selected_date):
    formatted_date = selected_date.strftime("%Y-%m-%d")
    url = f"https://s18.myenergi.net/cgi-jday-{device}{device_serial}-{formatted_date}"
    print(url)
    response = requests.get(url, auth=HTTPDigestAuth(gateway_serial, api_key))
    if response.status_code == 200:
        print(response.json())
        return response.json().get(f"U{device_serial}", [])
    else:
        print("API Failed")
        return None


def find_device(device_data, user_serial):
    user_serial = int(user_serial)
    all_devices = {}
    matched_device = None

    for data_dict in device_data:
        if isinstance(data_dict, dict):
            for device_name in ['zappi', 'eddi', 'harvi', 'libbi']:
                if data_dict.get(device_name):
                    all_devices[device_name] = data_dict[device_name][0].get(
                        'sno')
                    if all_devices[device_name] == user_serial:
                        matched_device = device_name

    return matched_device, all_devices


def joules_to_wh(joules):
    return joules / 3600


def main():
    st.title("Myenergi Data")
    st.info('In order to get your consumption you will need to enter the Gateway Device Serial & API Key to find devices.', icon="ℹ️")
    with st.expander("How on earth do i find my Gateway Device Serial & API Key? Click here for explanation"):
        st.write("""
        First you will need to navigate to https://myaccount.myenergi.com/location#products
        if you haven't already you will need to sign up to myenergi myaccount
        in the code.
        """)
        st.image("https://static.streamlit.io/examples/dice.jpg")

    device_serial = st.text_input("Gateway Device Serial:")
    api_key = st.text_input("Gateway API Key:")

    if 'devices' not in st.session_state:
        st.session_state.devices = []

    if 'device_to_serial_map' not in st.session_state:
        st.session_state.device_to_serial_map = {}

    if 'device_messages' not in st.session_state:
        st.session_state.device_messages = []

    if st.button("Find Devices"):
        if device_serial and api_key:
            device_data = get_device_data(device_serial, api_key)
            matched_device, all_device_serials = find_device(
                device_data, device_serial)

            for device, serial in all_device_serials.items():
                message = ""
                if device not in st.session_state.devices:
                    message = f"Found device: {device} with serial: {serial}"
                    st.session_state.device_messages.append(message)
                    st.session_state.devices.append(device)
                    st.session_state.device_to_serial_map[device] = serial
                else:
                    message = f"Device {device} with serial: {serial} is already in the list."
                    st.session_state.device_messages.append(message)

            if matched_device:
                st.write(
                    f"Matching device for provided serial {device_serial} is {matched_device}")
            else:
                st.write("No matching devices found for the provided serial.")
        else:
            st.warning("Please enter both Device Serial and API Key.")

    for message in st.session_state.device_messages:
        st.write(message)

    selected_device = st.selectbox(
        "Select a device:", st.session_state.devices)
    if selected_device:
        selected_device_first_char_capitalized = selected_device[0].upper()
    else:
        selected_device_first_char_capitalized = None

    st.write("Select the date to fetch the total minute data consumption.")
    selected_date = st.date_input("Select Date", datetime.now())

    if st.button("Fetch Consumption Data"):
        if selected_device and device_serial and api_key:
            selected_device_serial = st.session_state.device_to_serial_map.get(
                selected_device)
            if selected_device_serial:
                consumption_data = get_consumption_data(
                    selected_device_first_char_capitalized, selected_device_serial, device_serial, api_key, selected_date)

                imported_energy_sum = 0
                house_consumption_sum = 0
                voltage_sum = 0
                frequency_sum = 0
                tank_temp1_sum = 0
                tank_temp2_sum = 0
                num_entries = 0
                num_valid_temps = 0

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

                    if tank_temp1 is not None and tank_temp1 != 127:
                        tank_temp1_sum += tank_temp1
                        num_valid_temps += 1

                    if tank_temp2 is not None and tank_temp2 != 127:
                        tank_temp2_sum += tank_temp2

                    num_entries += 1

                avg_voltage = voltage_sum / num_entries if num_entries > 0 else 0
                avg_frequency = frequency_sum / num_entries if num_entries > 0 else 0

                if num_valid_temps > 0:
                    avg_tank_temp1 = tank_temp1_sum / num_valid_temps
                    avg_tank_temp2 = tank_temp2_sum / num_valid_temps
                else:
                    avg_tank_temp1 = 0
                    avg_tank_temp2 = 0

                total_house_consumption_wh = house_consumption_sum / 60
                calculated_self_consumption = total_house_consumption_wh - imported_energy_sum

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

                # Create a DataFrame to hold the data for the bar chart
                data = {
                    'Metrics': ['Total Imported Energy (Wh)', 'Total House Consumption (Wh)', 'Self Consumption (Wh)'],
                    'Values': [imported_energy_sum / 1000 , total_house_consumption_wh / 1000, calculated_self_consumption / 1000]
                }

                df = pd.DataFrame(data)

                # Display the data as a bar chart
                st.subheader("Summary Bar Chart:")
                st.bar_chart(df.set_index('Metrics'))

                st.subheader("Breakdown:")

            else:
                st.warning(
                    "Could not find a serial number for the selected device.")
        else:
            st.warning(
                "Please select a device, and ensure Device Serial and API Key are provided.")


if __name__ == "__main__":
    main()
