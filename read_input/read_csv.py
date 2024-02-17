# -*- coding: ISO-8859-1 -*-
import os
import csv
import numpy as np

def read_reserves(filename, params, network, thermals) -> None:
    """
        Read reserve requirements from csv file
    """

    f = open(filename, 'r', encoding='utf-8')
    reader = csv.reader(f, delimiter=';')
    row = next(reader)  # <BEGIN>
    row = next(reader)  # Header
    row = next(reader)  # either the first reserve or end
    while row[0].strip() != '</END>':
        if row[0] not in network.RESERVES.keys():
            network.RESERVES[row[0]] = {t: 0 for t in range(params.T)}

        assert int(row[1]) in network.RESERVES[row[0]].keys(), \
            f"I dont recognize period {row[1]} in the reserve file {filename}"
        network.RESERVES[row[0]][int(row[1])] = float(row[2]) / params.POWER_BASE

        row = next(reader)  # next reserve

    f.close()
    del f


def gross_load_and_renewable_gen(filename_gross_load,
                                filename_renewable_gen,
                                params, network):
    """Read gross load and renewable generation. compute the net load and print it"""

    network.NET_LOAD = np.zeros((len(network.BUS_ID), params.T), dtype='d')
    renewable_gen = np.zeros((len(network.BUS_ID), params.T), dtype='d')

    f = open(filename_gross_load, 'r', encoding='utf-8')
    found_bus = {bus: False for bus in network.BUS_ID}
    reader = csv.reader(f, delimiter=';')
    row = next(reader)  # <BEGIN>
    row = next(reader)  # Header
    row = next(reader)  # either the first bus or end
    while row[0].strip() != '</END>':
        try:
            bus = [bus for bus in network.BUS_ID if network.BUS_NAME[bus] == row[0].strip()][0]
        except IndexError:
            raise ValueError(f'Bus {row[0].strip()} is not in the system')

        b = network.BUS_ID.index(bus)

        for t in range(params.T):
            network.NET_LOAD[b, t] = float(row[1 + t].strip())

        found_bus[bus] = True
        row = next(reader)  # next bus or end

    if not (all(found_bus.values())):
        raise ValueError('No load has been found for buses ' +
                         [bus for bus in network.BUS_ID if not (found_bus[bus])])

    if os.path.isfile(filename_renewable_gen):
        f = open(filename_renewable_gen, 'r', encoding='utf-8')
        found_bus = {bus: False for bus in network.BUS_ID}
        reader = csv.reader(f, delimiter=';')
        row = next(reader)  # <BEGIN>
        row = next(reader)  # Header
        row = next(reader)  # either the first bus or end
        while row[0].strip() != '</END>':
            try:
                bus = [bus for bus in network.BUS_ID if network.BUS_NAME[bus] == row[0].strip()][0]
            except IndexError:
                raise ValueError(f'Bus {row[0].strip()} is not in the system')

            b = network.BUS_ID.index(bus)

            for t in range(params.T):
                renewable_gen[b, t] = float(row[1 + t].strip())

            found_bus[network.BUS_ID[b]] = True
            row = next(reader)  # next bus or end

        if not (all(found_bus.values())):
            raise ValueError('No load has been found for buses ' +
                             [bus for bus in network.BUS_ID if not (found_bus[bus])])
    else:
        print("No file of renewable generation found. Assuming no renewable generation", flush=True)

    network.NET_LOAD = np.multiply(np.subtract(network.NET_LOAD, renewable_gen),
                                   1 / params.POWER_BASE)

    f = open(params.OUT_DIR + 'net load - ' + params.PS
             + ' - case ' + str(params.CASE) + '.csv', 'w',
             encoding='utf-8')
    f.write('<BEGIN>\nBus/Hour;')

    for t in range(params.T):
        f.write(str(t) + ';')
    f.write('\n')
    for b, bus in enumerate(network.BUS_ID):
        f.write(network.BUS_NAME[bus] + ';')
        for t in range(params.T):
            f.write(str(network.NET_LOAD[b][t] * params.POWER_BASE) + ';')
        f.write('\n')

    f.write('</END>')
    f.close()
    del f


def reset_gen_costs_of_thermals(filename, params, thermals):
    """Reset the unitary generation costs for the thermal units"""

    f = open(filename, 'r', encoding='ISO-8859-1')
    reader = csv.reader(f, delimiter=';')
    row = next(reader)  # <BEGIN>
    row = next(reader)  # Header
    row = next(reader)  # Either the first hydro or end

    while row[0].strip() != '</END>':
        try:
            g = [g for g in thermals.ID if thermals.UNIT_NAME[g] == row[1].strip()][0]
        except IndexError:
            raise ValueError(f'Thermal unit {row[1].strip()} is not in the system')

        thermals.GEN_COST[g] = (params.DISCRETIZATION *
                                params.POWER_BASE * float(row[2].strip()) * params.SCAL_OBJ_F)

        row = next(reader)  # next thermal unit or end

    f.close()
    del f

def read_ini_state_thermal(filename, params, thermals):
    """Read the initial state of the thermal units"""

    f = open(filename, 'r', encoding='ISO-8859-1')
    reader = csv.reader(f, delimiter=';')

    row = next(reader)  # '<BEGIN>'
    row = next(reader)  # <Thermal plants>
    row = next(reader)  # header

    header = {}
    header['ID'] = row.index('ID')
    header['Name'] = row.index('Name')
    header['iniGen'] = row.index('Generation in time t = -1 in MW')
    header['iniState'] = row.index('State in t = -1. Either 1, if up, or 0, if down')
    header['nHoursInIniState'] = row.index('Number of hours (> 0) in the state of t = -1')
    header['inStartupTraj'] = row.index('Start-up trajectory (TRUE or FALSE)')
    header['inShutDownTraj'] = row.index('Shut-down trajectory (TRUE or FALSE)')

    row = next(reader)  # either first thermal or </Thermal plants>
    while not (row[0] == '</Thermal plants>'):
        plant_name = row[header['Name']].strip()
        ini_gen = float(row[header['iniGen']])
        ini_state = int(row[header['iniState']])
        n_hours_in_ini_state = int(row[header['nHoursInIniState']])

        inStartUp = True if row[header['inStartupTraj']].strip() in ('TRUE', 'True') else False
        inShutDown = True if row[header['inShutDownTraj']].strip() in ('TRUE', 'True') else False

        try:
            g = [g for g in thermals.ID if thermals.UNIT_NAME[g] == row[header['Name']]][0]
        except IndexError:
            raise ValueError(f'Thermal unit {plant_name} is not in the system')

        if (not (inStartUp) and not (inShutDown) and
                (ini_state == 1 and (ini_gen < (thermals.MIN_P[g] * params.POWER_BASE - 1e-4)))):
            raise ValueError(f'Thermal plant {plant_name} is not in a start-up or shut-down ' +
                             'trajectory and yet its initial generation is less than its minimum')

        thermals.STATE_0[g] = (ini_state
                               if ((thermals.MIN_P[g] + thermals.CONST_COST[g]) > 0
                                   and (thermals.GEN_COST[g] + thermals.CONST_COST[g]) > 0)
                               else 1
                               )
        thermals.N_HOURS_IN_PREVIOUS_STATE[g] = n_hours_in_ini_state

        if ini_state == 1:
            if ((thermals.MIN_P[g] + 1e-4) <= (ini_gen / params.POWER_BASE)
                    <= (thermals.MAX_P[g] - 1e-4)):
                thermals.T_G_0[g] = ini_gen / params.POWER_BASE
            elif ini_gen / params.POWER_BASE > (thermals.MAX_P[g] - 1e-4):
                thermals.T_G_0[g] = thermals.MAX_P[g]
            else:
                thermals.T_G_0[g] = thermals.MIN_P[g]
        else:
            thermals.T_G_0[g] = 0

        row = next(reader)
    f.close()


def read_generators(filename, params, thermals):
    """Read data of hydro, thermal and wind generators"""

    def read_thermals(row, reader, params, thermals):
        """Read data of thermal generators"""

        row = next(reader)  # header
        header = {}
        header['ID'] = row.index('ID')
        header['Name'] = row.index('Name')
        header['minP'] = row.index('Minimum power output (MW)')
        header['maxP'] = row.index('Maximum power output (MW)')
        header['genCost'] = row.index('Unitary linear cost ($/MW)')
        header['rampUp'] = row.index('Ramp-up limit (MW/h)')
        header['rampDown'] = row.index('Ramp-down limit (MW/h)')
        header['minUp'] = row.index('Minimum up-time (h)')
        header['minDown'] = row.index('Minimum down-time (h)')
        header['bus'] = row.index('Bus id')
        header['constCost'] = row.index('Constant cost ($)')
        header['stUpCost'] = row.index('Start-up cost ($)')
        header['stDwCost'] = row.index('Shut-down cost ($)')
        try:
            header['Reserve eligibility'] = row.index('Reserve eligibility')
        except ValueError:
            header['Reserve eligibility'] = None

        row = next(reader)  # either the first thermal plant or </Thermal plants>
        while not (row[0] == '</Thermal plants>'):
            thermals.add_new_thermal(params, row, header)
            row = next(reader)  # next thermal plant or </Thermal plants>

    f = open(filename, 'r', encoding='ISO-8859-1')
    reader = csv.reader(f, delimiter=';')

    row = next(reader)  # '<BEGIN>'
    row = next(reader)  # either </END>, or <Hydro plants>, or <Thermal plants>

    while not (row[0] == '</END>'):
        if (row[0] == '<Thermal plants>'):
            read_thermals(row, reader, params, thermals)

        elif (row[0] == '<Deficit cost>'):
            row = next(reader)  # Header of the deficit cost
            row = next(reader)  # Deficit cost
            params.DEFICIT_COST = (float(row[0].strip()) * params.POWER_BASE * params.SCAL_OBJ_F *
                                   params.DISCRETIZATION)
            row = next(reader)  # </Deficit cost>

        row = next(reader)
    f.close()

def read_network(filename, params, network):
    """Read all network components of the system: buses and lines"""

    def read_buses(row, reader, network):
        """read bus data"""
        row = next(reader)  # header
        header = {}
        header['ID'] = row.index('ID')
        header['Name'] = row.index('Name')
        header['Reference bus'] = row.index('Reference bus')
        header['baseVoltage'] = row.index('Base voltage (kV)')
        header['area'] = row.index('Area')
        header['submName'] = row.index('Subsystem market - Name')
        header['submID'] = row.index('Subsystem market - ID')

        row = next(reader)  # either the first bus or </Buses>
        while not (row[0] == '</Buses>'):
            network.add_new_bus(row, header)
            row = next(reader)  # next bus or </Buses>

    def read_lines(row, reader, params, network):
        """read transmission line data"""

        row = next(reader)  # header
        header = {}
        header['From (ID)'] = row.index('From (ID)')
        header['From (Name)'] = row.index('From (Name)')
        header['To (ID)'] = row.index('To (ID)')
        header['To (Name)'] = row.index('To (Name)')
        header['Cap'] = row.index('Line rating (MW)')
        header['Reac'] = row.index('Reactance (p.u.) - 100-MVA base')

        row = next(reader)  # either the line or </AC Transmission lines>
        while not (row[0] == '</AC Transmission lines>'):
            network.add_new_line(params, row, header)
            row = next(reader)  # next line or </AC Transmission lines>

    def read_DC_links(row, reader, params, network):
        """read DC Link data"""

        row = next(reader)  # header
        header = {}
        header['From (ID)'] = row.index('From (ID)')
        header['To (ID)'] = row.index('To (ID)')
        header['Cap'] = row.index('Rating (MW)')
        row = next(reader)  # either the first DC link or </DC Links>
        while not (row[0] == '</DC Links>'):
            network.add_new_DC_link(params, row, header)
            row = next(reader)  # next DC link or </DC Links>

    f = open(filename, 'r', encoding='ISO-8859-1')
    reader = csv.reader(f, delimiter=';')

    row = next(reader)  # '<BEGIN>'
    row = next(reader)  # either </END>, or <Hydro plants>, or <Thermal plants>

    while not (row[0] == '</END>'):
        if (row[0] == '<Buses>'):
            read_buses(row, reader, network)
        elif (row[0] == '<AC Transmission lines>'):
            read_lines(row, reader, params, network)
        elif (row[0] == '<DC Links>'):
            read_DC_links(row, reader, params, network)
        row = next(reader)
    f.close()
