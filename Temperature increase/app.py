import streamlit as st


def calculate_temperature_increase(energy_kwh, water_volume_liters):
    # Convert energy to Joules
    energy_joules = energy_kwh * 3.6e6
    # Since 1 liter of water is 1 kg, mass in kg is the same as volume in liters
    mass_kg = water_volume_liters
    # Specific heat capacity of water in J/kg°C
    specific_heat_capacity = 4186
    # Calculating temperature increase
    delta_temp = energy_joules / (mass_kg * specific_heat_capacity)
    return delta_temp


# Streamlit UI
st.title('eddi |Temperature Increase Calculator')

# User input
water_volume_liters = st.slider(
    'Select the size of the hot water tank (L):', 50, 500, 200)
energy_kwh = st.number_input(
    'Enter the diverted energy (kWh):', value=4.2, step=0.1)

# Calculations
temperature_increase = calculate_temperature_increase(
    energy_kwh, water_volume_liters)

# Display result
st.metric(label='Temperature Increase (°C)',
          value=f'{temperature_increase:.2f}', delta=None)

# Check if temperature increase is above 100°C and display warning with animated GIF
if temperature_increase > 100:
    st.warning('The water is boiling!')
    st.markdown(
        '![Boiling Water](https://gifdb.com/images/high/boiling-water-bubbles-cartoon-65zw0jns86htivzc.gif)', unsafe_allow_html=True)
