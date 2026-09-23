#!/usr/bin/env python3
"""
Scan for SunSpec Map provided by SolarEdge inverters.

usage: scanner.py 
"""

import argparse
import pymodbus.client as ModbusClient
from pymodbus import ModbusException
from pymodbus.pdu import ModbusPDU


def read_string_register(client: ModbusClient.ModbusTcpClient, address: int, device_id: int, count: int) -> tuple[int, str]:

    try:
        rr: ModbusPDU = client.read_holding_registers(address=address, count=count, device_id=device_id)
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        return -1,""
    if rr.isError():
        print(f"Received exception from device ({rr})")
        return -1,""

    try:
        converted_value = client.convert_from_registers(registers=rr.registers, data_type=client.DATATYPE.STRING)
    except Exception as exc:
        print(f"Received Exception({exc}) while convert_from_registers")
        return address+count,""

    if isinstance(converted_value, str):
        return address+count, converted_value
    else:
        return -1,""


def read_int_register(client: ModbusClient.ModbusTcpClient, address: int, device_id: int) -> tuple[int, int]:

    try:
        rr: ModbusPDU = client.read_holding_registers(address=address, count=1, device_id=device_id)
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        client.close()
        return -1,-1
    if rr.isError():
        print(f"Received exception from device ({rr})")
        client.close()
        return -1,-1

    converted_value = client.convert_from_registers(registers=rr.registers, data_type=client.DATATYPE.INT16)

    if isinstance(converted_value, int):
        return address+1, int(converted_value)
    else:
        return -1,-1


def process_common_block(client: ModbusClient.ModbusTcpClient, start_address: int, device_id: int) -> None:

    next_address, manufacturer = read_string_register(client=client, address=start_address, device_id=device_id, count=16)
    next_address, model = read_string_register(client=client, address=next_address, device_id=device_id, count=16)
    next_address, options = read_string_register(client=client, address=next_address, device_id=device_id, count=8)
    next_address, version = read_string_register(client=client, address=next_address, device_id=device_id, count=8)
    next_address, serial_number = read_string_register(client=client, address=next_address, device_id=device_id, count=16)
    next_address, device_address = read_int_register(client=client, address=next_address, device_id=device_id)
    
    print(f"     Manufacturer:   [{manufacturer}]")
    print(f"     Model:          [{model}]")
    print(f"     Options:        [{options}]")
    print(f"     Version:        [{version}]")
#    print(f"     Serial Number:  [{serial_number}]")
    print( "     Serial Number:  [hidden]")
    print(f"     Device Address: [{device_address}]")


def read_block(client: ModbusClient.ModbusTcpClient, block_address: int, device_id: int) -> int:

    print()
    print(f"   Reading Block at address [{block_address} ({hex(block_address)})] for device [{device_id}]")

    next_address, block_id = read_int_register(client=client, address=block_address, device_id=device_id)
    next_address, block_length = read_int_register(client=client, address=next_address, device_id=device_id)

    print(f"    Block id     = [{block_id}]")
    print(f"    Block length = [{block_length}]")

    match block_id:
        case -1:
            print("    Block type   = [The End of the block list has been reached]")
            next_address = -1
        case 1:
            print("    Block type   = [Common - All SunSpec compliant devices must include this as the first model]")
            process_common_block(client=client, start_address=next_address, device_id=device_id)
        case 2:
            print("    Block type   = [Basic Aggregator - Aggregates a collection of models for a given model id]")
        case 3:
            print("    Block type   = [Secure Dataset Read Request - Request a digital signature over a specified set of data registers]")
        case 4:
            print("    Block type   = [Secure Dataset Read Response - Compute a digital signature over a specified set of data registers]")
        case 5:
            print("    Block type   = [Secure Write Request - Include a digital signature along with the control data]")
        case 6:
            print("    Block type   = [Secure Write Sequential Request - Include a digital signature along with the control data]")
        case 7:
            print("    Block type   = [Secure Write Response Model (DRAFT 1) - Include a digital signature over the response]")
        case 8:
            print("    Block type   = [Get Device Security Certificate - Security model for PKI]")
        case 9:
            print("    Block type   = [Set Operator Security Certificate - Security model for PKI]")
        case 10:
            print("    Block type   = [Communication Interface Header - To be included first for a complete interface description]")
        case 11:
            print("    Block type   = [Ethernet Link Layer - Include to support a wired ethernet port]")
        case 12:
            print("    Block type   = [IPv4 - Include to support an IPv4 protocol stack on this interface]")
        case 13:
            print("    Block type   = [IPv6 - Include to support an IPv6 protocol stack on this interface]")
        case 14:
            print("    Block type   = [Proxy Server - Include this block to allow for a proxy server]")
        case 15:
            print("    Block type   = [Interface Counters Model - Interface counters]")
        case 16:
            print("    Block type   = [Simple IP Network - Include this model for a simple IPv4 network stack]")
        case 17:
            print("    Block type   = [Serial Interface - Include this model for serial interface configuration support]")
        case 18:
            print("    Block type   = [Cellular Link - Include this model to support a cellular interface link]")
        case 19:
            print("    Block type   = [PPP Link - Include this model to configure a Point-to-Point Protocol link]")
        case 101:
            print("    Block type   = [Inverter (Single Phase) - Include this model for single phase inverter monitoring]")
        case 102:
            print("    Block type   = [Inverter (Split-Phase) - Include this model for split phase inverter monitoring]")
        case 103:
            print("    Block type   = [Inverter (Three Phase) - Include this model for three phase inverter monitoring]")
        case 111:
            print("    Block type   = [Inverter (Single Phase) FLOAT - Include this model for single phase inverter monitoring using float values]")
        case 112:
            print("    Block type   = [Inverter (Split Phase) FLOAT - Include this model for split phase inverter monitoring using float values]")
        case 113:
            print("    Block type   = [Inverter (Three Phase) FLOAT - Include this model for three phase inverter monitoring using float values]")
        case 120:
            print("    Block type   = [Nameplate - Inverter Controls Nameplate Ratings ]")
        case 121:
            print("    Block type   = [Basic Settings - Inverter Controls Basic Settings ]")
        case 122:
            print("    Block type   = [Measurements_Status - Inverter Controls Extended Measurements and Status ]")
        case 123:
            print("    Block type   = [Immediate Controls - Immediate Inverter Controls ]")
        case 124:
            print("    Block type   = [Storage - Basic Storage Controls ]")
        case 125:
            print("    Block type   = [Pricing - Pricing Signal  ]")
        case 126:
            print("    Block type   = [Static Volt-VAR - Static Volt-VAR Arrays ]")
        case 127:
            print("    Block type   = [Freq-Watt Param - Parameterized Frequency-Watt ]")
        case 128:
            print("    Block type   = [Dynamic Reactive Current - Dynamic Reactive Current ]")
        case 129:
            print("    Block type   = [LVRTD - LVRT Must Disconnect]")
        case 130:
            print("    Block type   = [HVRTD - HVRT Must Disconnect]")
        case 131:
            print("    Block type   = [Watt-PF - Watt-Power Factor ]")
        case 132:
            print("    Block type   = [Volt-Watt - Volt-Watt ]")
        case 133:
            print("    Block type   = [Basic Scheduling - Basic Scheduling ]")
        case 134:
            print("    Block type   = [Freq-Watt Crv - Curve-Based Frequency-Watt ]")
        case 135:
            print("    Block type   = [LFRT - Low Frequency Ride-through]")
        case 136:
            print("    Block type   = [HFRT - High Frequency Ride-through]")
        case 137:
            print("    Block type   = [LVRTC - LVRT must remain connected]")
        case 138:
            print("    Block type   = [HVRTC - HVRT must remain connected]")
        case 139:
            print("    Block type   = [LVRTX - LVRT extended curve]")
        case 140:
            print("    Block type   = [HVRTX - HVRT extended curve]")
        case 141:
            print("    Block type   = [LFRTC - LFRT must remain connected]")
        case 142:
            print("    Block type   = [HFRTC - HFRT must remain connected]")
        case 143:
            print("    Block type   = [LFRTX - LFRT extended curve]")
        case 144:
            print("    Block type   = [HFRTX - HFRT extended curve]")
        case 145:
            print("    Block type   = [Extended Settings - Inverter controls extended settings ]")
        case 160:
            print("    Block type   = [Multiple MPPT Inverter Extension Model]")
        case 201:
            print("    Block type   = [Meter (Single Phase) single phase (AN or AB) meter - Include this model for single phase (AN or AB) metering]")
        case 202:
            print("    Block type   = [split single phase (ABN) meter]")
        case 203:
            print("    Block type   = [wye-connect three phase (abcn) meter]")
        case 204:
            print("    Block type   = [delta-connect three phase (abc) meter]")
        case 211:
            print("    Block type   = [single phase (AN or AB) meter]")
        case 212:
            print("    Block type   = [split single phase (ABN) meter]")
        case 213:
            print("    Block type   = [wye-connect three phase (abcn) meter]")
        case 214:
            print("    Block type   = [delta-connect three phase (abc) meter]")
        case 220:
            print("    Block type   = [Secure AC Meter Selected Readings - Include this model for secure metering]")
        case 302:
            print("    Block type   = [Irradiance Model - Include to support various irradiance measurements]")
        case 303:
            print("    Block type   = [Back of Module Temperature Model - Include to support variable number of  back of module temperature measurements]")
        case 304:
            print("    Block type   = [Inclinometer Model - Include to support orientation measurements]")
        case 305:
            print("    Block type   = [GPS - Include to support location measurements]")
        case 306:
            print("    Block type   = [Reference Point Model - Include to support a standard reference point]")
        case 307:
            print("    Block type   = [Base Met - Base Meteorological Model]")
        case 308:
            print("    Block type   = [Mini Met Model - Include to support a few basic measurements]")
        case 401:
            print("    Block type   = [String Combiner (Current) - A basic string combiner]")
        case 402:
            print("    Block type   = [String Combiner (Advanced) - An advanced string combiner]")
        case 403:
            print("    Block type   = [String Combiner (Current) - A basic string combiner model]")
        case 404:
            print("    Block type   = [String Combiner (Advanced) - An advanced string combiner including voltage and energy measurements]")
        case 501:
            print("    Block type   = [Solar Module - A solar module model supporting DC-DC converter]")
        case 502:
            print("    Block type   = [Solar Module - A solar module model supporting DC-DC converter]")
        case 601:
            print("    Block type   = [Tracker Controller DRAFT 2 - Monitors and controls multiple trackers]")
        case 701:
            print("    Block type   = [DER AC Measurement - DER AC measurement model.]")
        case 702:
            print("    Block type   = [DER Capacity - DER capacity model.]")
        case 703:
            print("    Block type   = [Enter Service - Enter service model.]")
        case 704:
            print("    Block type   = [DER AC Controls - DER AC controls model.]")
        case 705:
            print("    Block type   = [DER Volt-Var - DER Volt-Var model.]")
        case 706:
            print("    Block type   = [DER Volt-Watt - DER Volt-Watt model.]")
        case 707:
            print("    Block type   = [DER Trip LV - DER low voltage trip model.]")
        case 708:
            print("    Block type   = [DER Trip HV - DER high voltage trip model.]")
        case 709:
            print("    Block type   = [DER Trip LF - DER low frequency trip model.]")
        case 710:
            print("    Block type   = [DER Trip HF - DER high frequency trip model.]")
        case 711:
            print("    Block type   = [DER Frequency Droop - DER Frequency Droop model.]")
        case 712:
            print("    Block type   = [DER Watt-Var - DER Watt-Var model.]")
        case 713:
            print("    Block type   = [DER Storage Capacity - DER storage capacity.]")
        case 714:
            print("    Block type   = [DER DC Measurement - DER DC measurement.]")
        case 715:
            print("    Block type   = [DERCtl - DER Control]")
        case 801:
            print("    Block type   = [Energy Storage Base Model (DEPRECATED) - This model has been deprecated.]")
        case 802:
            print("    Block type   = [Battery Base Model]")
        case 803:
            print("    Block type   = [Lithium-Ion Battery Bank Model]")
        case 804:
            print("    Block type   = [Lithium-Ion String Model]")
        case 805:
            print("    Block type   = [Lithium-Ion Module Model]")
        case 806:
            print("    Block type   = [Flow Battery Model]")
        case 807:
            print("    Block type   = [Flow Battery String Model]")
        case 808:
            print("    Block type   = [Flow Battery Module Model]")
        case 809:
            print("    Block type   = [Flow Battery Stack Model]")
        case _:
            print("    Block type   = [Unknown]")

    if next_address >= 0 and block_length > 0:
        return next_address + block_length
    else:
        return -1



def read_battery(client: ModbusClient.ModbusTcpClient, address: int, device_id: int) -> None:

    print()
    print(f"   Reading Battery at address [{address} ({hex(address)})] for device [{device_id}]")

    next_address, manufacturer = read_string_register(client=client, address=address, device_id=device_id, count=16)
    next_address, model = read_string_register(client=client, address=next_address, device_id=device_id, count=16)
    next_address, firmware_version = read_string_register(client=client, address=next_address, device_id=device_id, count=16)
    next_address, serial_number = read_string_register(client=client, address=next_address, device_id=device_id, count=16)
    next_address, battery_device_id = read_int_register(client=client, address=next_address, device_id=device_id)
    next_address, battery_reserved = read_int_register(client=client, address=next_address, device_id=device_id)

    print(f"     Manufacturer:     [{manufacturer}]")
    print(f"     Model:            [{model}]")
    print(f"     Firmware Version: [{firmware_version}]")
    print(f"     Serial Number:    [{serial_number}]")
#    print( "     Serial Number:    [hidden]")
    print(f"     Device id:        [{battery_device_id}]")
    print(f"     Reserved:         [{battery_reserved}]")
    print(f"     Next Address:     [{next_address} ({hex(next_address)})]")


if __name__ == "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument("host", type=str, help="modbus TCP address")
    argparser.add_argument("port", type=int, help="modbus TCP port")
    argparser.add_argument("--device-id", type=int, choices=range(1, 256), default=1, metavar="[1-255]", help="modbus device address (default: 1)")
    args: argparse.Namespace = argparser.parse_args()

    client = ModbusClient.ModbusTcpClient(host=args.host, port=args.port)

    print("Connecting to server")
    client.connect()
    if client.connected:
        print(" Connected to server")
        print()

        block_address, sunspecs = read_string_register(client=client, address=40000, device_id=args.device_id, count=2)
        if sunspecs == "SunS":
            print("  The inverter is providing a SunSpec Map")

            while block_address > 0 and client.connected:
                block_address = read_block(client=client, block_address=block_address, device_id=args.device_id)

            print()
            print("  End of Sunspec MAP")
        else:
            print("  The inverter is NOT providing a SunSpec Map")

        print()
        print("  Trying to probe for batteries")
        read_battery(client=client, address=57600, device_id=args.device_id)
        read_battery(client=client, address=57856, device_id=args.device_id)

    print()
    if client.connected:
        client.close()
        print("Disconnected from server")
    else:
        print("Already disconnected from server")
