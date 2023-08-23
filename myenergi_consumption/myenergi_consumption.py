# Importing necessary libraries
import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPDigestAuth
from datetime import datetime
import base64
import csv
import io

# Constants
BASE_URL = "https://s18.myenergi.net"
DEVICES = ['zappi', 'eddi', 'harvi', 'libbi']

# Function to get device data


def get_device_data(device_serial, api_key):
    url = f"{BASE_URL}/cgi-jstatus-*"
    response = requests.get(url, auth=HTTPDigestAuth(device_serial, api_key))
    return response.json() if response.status_code == 200 else None

# Function to get consumption data


def get_consumption_data(device, device_serial, gateway_serial, api_key, start_date, end_date):
    data = []
    date_range = pd.date_range(start_date, end_date)
    for date in date_range:
        formatted_date = date.strftime("%Y-%m-%d")
        url = f"{BASE_URL}/cgi-jday-{device}{device_serial}-{formatted_date}"
        response = requests.get(
            url, auth=HTTPDigestAuth(gateway_serial, api_key))
        if response.status_code == 200:
            data.extend(response.json().get(f"U{device_serial}", []))
    return data

# Function to find device


def find_device(device_data, user_serial):
    user_serial = int(user_serial)
    all_devices = {device_name: data_dict[device_name][0].get('sno') for data_dict in device_data if isinstance(
        data_dict, dict) for device_name in DEVICES if data_dict.get(device_name)}
    matched_device = next(
        (device for device, serial in all_devices.items() if serial == user_serial), None)
    return matched_device, all_devices

# Main function


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

    st.session_state.setdefault('devices', [])
    st.session_state.setdefault('device_to_serial_map', {})
    st.session_state.setdefault('device_messages', [])

    if st.button("Find Devices") and device_serial and api_key:
        with st.spinner('Fetching device data...'):
            device_data = get_device_data(device_serial, api_key)
        matched_device, all_device_serials = find_device(
            device_data, device_serial)

        for device, serial in all_device_serials.items():
            message = f"Found device: {device} with serial: {serial}" if device not in st.session_state.devices else f"Device {device} with serial: {serial} is already in the list."
            st.session_state.device_messages.append(message)
            if device not in st.session_state.devices:
                st.session_state.devices.append(device)
                st.session_state.device_to_serial_map[device] = serial

        st.write(
            f"Matching device for provided serial {device_serial} is {matched_device}" if matched_device else "No matching devices found for the provided serial.")
    elif not device_serial or not api_key:
        st.warning("Please enter both Device Serial and API Key.")

    for message in st.session_state.device_messages:
        st.write(message)

    selected_device = st.selectbox(
        "Select a device:", st.session_state.devices)
    selected_device_first_char_capitalized = selected_device[0].upper(
    ) if selected_device else None

    st.write("Select the date range to fetch the total minute data consumption.")
    start_date = st.date_input("Start Date", datetime.now())
    end_date = st.date_input("End Date", datetime.now())

    if st.button("Fetch Consumption Data") and selected_device and device_serial and api_key:
        selected_device_serial = st.session_state.device_to_serial_map.get(
            selected_device)
        if selected_device_serial:
            with st.spinner('Fetching consumption data...'):
                consumption_data = get_consumption_data(
                    selected_device_first_char_capitalized, selected_device_serial, device_serial, api_key, start_date, end_date)
            df = pd.DataFrame(consumption_data)
            df['v1'] = df['v1'] / 10
            df['frq'] = df['frq'] / 100
            df['pt1'] = df['pt1'] / 10
            df['pt2'] = df['pt2'] / 10

            # Columns for metrics in kWh (these values are the energy consumed in each minute)
            df['imp_kWh_metric'] = df['imp'] / (60 * 1000)
            df['exp_kWh_metric'] = df['exp'] / (60 * 1000)
            df['gep_kWh_metric'] = df['gep'] / (60 * 1000)
            if 'gen' in df.columns:
                df['gen_kWh_metric'] = df['gen'] / (60 * 1000)
            else:
                df['gen_kWh_metric'] = 0

            # Convert joules per minute to kW for display in the line chart
            df['imp_kW'] = df['imp'] / 60000
            df['exp_kW'] = df['exp'] / 60000
            df['gep_kW'] = df['gep'] / 60000
            if 'gen' in df.columns:
                df['gen_kW'] = df['gen'] / 60000
            else:
                df['gen_kW'] = 0

            # Sum the joules for each minute and then convert them to kWh for metrics
            df['imp_total_joules'] = df['imp'].sum()
            df['exp_total_joules'] = df['exp'].sum()
            df['gep_total_joules'] = df['gep'].sum()
            if 'gen' in df.columns:
                df['gen_total_joules'] = df['gen'].sum()
            else:
                df['gen_total_joules'] = 0

            df['imp_kWh_metric'] = df['imp_total_joules'] / 3600000
            df['exp_kWh_metric'] = df['exp_total_joules'] / 3600000
            df['gep_kWh_metric'] = df['gep_total_joules'] / 3600000
            df['gen_kWh_metric'] = df['gen_total_joules'] / 3600000

            # df['imp'] = df['imp'] / 60000  # Convert to kW
            # df['exp'] = df['exp'] / 60000  # Convert to kW
            # df['gep'] = df['gep'] / 60000  # Convert to kW
            # df['gen'] = df['gen'] / 60000  # Convert to kW

            df['hr'].fillna(0, inplace=True)
            df['min'].fillna(0, inplace=True)
            df['time'] = pd.to_datetime(df['yr'].astype(str) + '-' + df['mon'].astype(str) + '-' + df['dom'].astype(str) + ' ' +
                                        df['hr'].astype(int).astype(str).str.zfill(2) + ':' +
                                        df['min'].astype(int).astype(str).str.zfill(2), format='%Y-%m-%d %H:%M')
            st.subheader("Summary:")
            col1, col2 = st.columns(2)

            st.subheader("Breakdown:")
            st.line_chart(df.set_index('time')[['v1', 'frq']].rename(
                columns={'v1': 'Voltage', 'frq': 'Frequency Hz'}))

            st.subheader("Tank Temperatures:")
            st.line_chart(df.set_index('time')[['pt1', 'pt2']].rename(
                columns={'pt1': 'Tank 1 Temperature C', 'pt2': 'Tank 2 Temperature C'}))

            st.subheader("Energy Graph:")
            st.line_chart(df.set_index('time')[['imp_kW', 'exp_kW', 'gep_kW', 'gen_kW']].rename(columns={
                'imp_kW': 'Imported Energy kW', 'exp_kW': 'Exported Energy kW',
                'gep_kW': 'Positive generation energy kW', 'gen_kW': 'Negative generation energy kW'}))

            # CSV Export
            csv = df.to_csv(index=False)
            # Convert CSV to base64
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="myenergi_data.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)

            # Display metrics using either st.write() or col1.metric()
            # using iloc[0] to just get the single value from the dataframe
            col1.metric("Total Imported Energy", "{:.2f} kWh".format(
                df['imp_kWh_metric'].iloc[0]))
            col1.metric("Total Exported Energy", "{:.2f} kWh".format(
                df['exp_kWh_metric'].iloc[0]))
            col1.metric("Total Generated Energy", "{:.2f} kWh".format(
                df['gep_kWh_metric'].iloc[0]))
            col1.metric("Total Consumed Energy", "{:.2f} kWh".format(
                df['gen_kWh_metric'].iloc[0]))

            col2.metric("Average Voltage", "{:.2f} V".format(df['v1'].mean()))
            col2.metric("Average Frequency",
                        "{:.2f} Hz".format(df['frq'].mean()))
            col2.metric("Average Tank Temperature Sensor 1",
                        "{:.2f} °C".format(df['pt1'].mean()))
            col2.metric("Average Tank Temperature Sensor 2",
                        "{:.2f} °C".format(df['pt2'].mean()))

        else:
            st.warning(
                "Could not find a serial number for the selected device.")
    else:
        st.warning(
            "Please select a device, and ensure Device Serial and API Key are provided.")


if __name__ == "__main__":
    main()
