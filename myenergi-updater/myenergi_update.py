# Importing necessary libraries
import streamlit as st
import requests
from requests.auth import HTTPDigestAuth
import threading

# Constants
BASE_URL = "https://s18.myenergi.net"
DEVICES = ['zappi', 'eddi', 'harvi', 'libbi']

# Function to get device data


def get_device_data(device_serial, api_key):
    url = f"{BASE_URL}/cgi-jstatus-*"
    response = requests.get(url, auth=HTTPDigestAuth(device_serial, api_key))
    return response.json() if response.status_code == 200 else None

# Function to handle the update requests


def execute_request(endpoint, device_serial, api_key):
    response = requests.get(
        endpoint, auth=HTTPDigestAuth(device_serial, api_key))
    return response.status_code

# Function to find device


# Function to find device
def find_device(device_data, user_serial):
    user_serial = int(user_serial)
    all_devices = {
        device: data[device][0].get('sno')
        for data in device_data
        if isinstance(data, dict)
        for device in DEVICES
        if device in data and data[device]
    }
    matched_device = next(
        (device for device, serial in all_devices.items() if serial == user_serial), None)
    return matched_device, all_devices

# Main function


def main():
    st.title("Myenergi Device Updater")
    st.info('In order to update your devices remotely you will need to enter the Gateway Device Serial & API Key to find devices.', icon="ℹ️")
    with st.expander("How on earth do i find my Gateway Device Serial & API Key? Click here for explanation"):
        st.write("""
        1. First you will need to navigate to https://myaccount.myenergi.com/location#products if you haven't already you will need to sign up to myenergi myaccount
        2. Once logged in use the menu and navigate to "locations" and then "myenergi products"
        3. Once on the "myenergi Product" page you will be presented with your "Gateway product" take a note of the serial number "sn"
        4. press "Advance"
        5. Press "Generate new API Key" - take a note 
        6. pop them both in below and you are off!
        """)
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
            device_info_list = next(
                (item[device] for item in device_data if device in item), None)
            device_info = device_info_list[0] if device_info_list else None

            message = f"Found device: {device} with serial: {serial}" if device not in st.session_state.devices else f"Device {device} with serial: {serial} is already in the list."
            st.session_state.device_messages.append(message)
            if device not in st.session_state.devices:
                st.session_state.devices.append(device)
                st.session_state.device_to_serial_map[device] = serial

                if device_info:
                    new_app_available = device_info.get('newAppAvailable')
                    new_bootloader_available = device_info.get(
                        'newBootloaderAvailable')

                    if new_app_available or new_bootloader_available:
                        st.metric(
                            label=f"{device} Update Available", value="TRUE")
                        if new_bootloader_available:
                            bootloader_endpoint = f"{BASE_URL}/cgi-force-install-bootloader-{device[0].upper()}{serial}"
                            if st.button(f"Update Bootloader for {device}"):
                                update_thread = threading.Thread(target=execute_request, args=(
                                    bootloader_endpoint, device_serial, api_key))
                                update_thread.start()

                        if new_app_available:
                            app_endpoint = f"{BASE_URL}/cgi-force-install-app-{device[0].upper()}{serial}"
                            if st.button(f"Update App for {device}"):
                                update_thread = threading.Thread(
                                    target=execute_request, args=(app_endpoint, device_serial, api_key))
                                update_thread.start()

                    else:
                        st.write(f"No updates available for {device}")

    elif not device_serial or not api_key:
        st.warning("Please enter both Device Serial and API Key.")

    for message in st.session_state.device_messages:
        st.write(message)


if __name__ == "__main__":
    main()
