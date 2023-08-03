import matplotlib.pyplot as plt

# Simulation parameters
solar_panel_capacity = 8000  # in watts
water_heater_capacity = 1500  # in watts
simulation_duration_hours = 24
time_step_minutes = 15

# Generate solar energy data (fixed pattern for demonstration)


def generate_solar_energy():
    solar_energy_data = [1000] * 6 + [3000] * 6 + [1000] * 6 + [0] * 6
    return solar_energy_data

# Eddi power diverter logic


def eddi_diverter(solar_energy, water_heater_demand):
    surplus_energy = solar_energy - water_heater_demand
    if surplus_energy > 0:
        return water_heater_demand
    else:
        return solar_energy

# Simulation loop


def simulate():
    solar_energy_data = generate_solar_energy()
    water_heater_demand_data = [
        water_heater_capacity] * simulation_duration_hours
    diverted_energy_data = []

    for i in range(simulation_duration_hours):
        solar_energy = solar_energy_data[i]
        water_heater_demand = water_heater_demand_data[i]
        diverted_energy = eddi_diverter(solar_energy, water_heater_demand)
        diverted_energy_data.append(diverted_energy)

    return solar_energy_data, water_heater_demand_data, diverted_energy_data

# Plot the results


def plot_simulation(solar_energy_data, water_heater_demand_data, diverted_energy_data):
    hours = list(range(1, simulation_duration_hours + 1))

    plt.figure(figsize=(10, 6))
    plt.plot(hours, solar_energy_data, label='Solar Energy Generation')
    plt.plot(hours, water_heater_demand_data, label='Water Heater Demand')
    plt.plot(hours, diverted_energy_data, label='Diverted Energy')
    plt.xlabel('Hour')
    plt.ylabel('Energy (Watts)')
    plt.title('Eddi Power Diverter Simulation')
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    solar_energy_data, water_heater_demand_data, diverted_energy_data = simulate()
    plot_simulation(solar_energy_data, water_heater_demand_data,
                    diverted_energy_data)
