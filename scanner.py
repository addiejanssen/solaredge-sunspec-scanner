#!/usr/bin/env python3
"""
Scan for SunSpec Map provided by SolarEdge inverters.

usage: scanner.py <host> <port> --device-id <number>

The --device-id is optional. It defaults to '1'.
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
        client.close()
        return -1,""
    if rr.isError():
        print(f"Received exception from device ({rr})")
        client.close()
        return -1,""

    converted_value = client.convert_from_registers(registers=rr.registers, data_type=client.DATATYPE.STRING)

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
        return address +1, int(converted_value)
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
    print(f"     Serial Number:  [{serial_number}]")
    print(f"     Device Address: [{device_address}]")


def read_block(client: ModbusClient.ModbusTcpClient, block_address: int, device_id: int) -> int:

    print()
    print(f"   Reading Block at address [{block_address}] for device [{device_id}]")

    next_address, block_id = read_int_register(client=client, address=block_address, device_id=device_id)
    next_address, block_length = read_int_register(client=client, address=next_address, device_id=device_id)

    match block_id:
        case -1:
            print("    Block id = -1: The End of the block list has been reached")
            next_address = -1
        case 1:
            print("    Block id = 1: Common")
            process_common_block(client=client, start_address=next_address, device_id=device_id)
        case 2:
            print("    Block id = 2: Basic Aggregator")
        case 3:
            print("    Block id = 3: Secure Dataset Read Request")
        case 4:
            print("    Block id = 4: Secure Dataset Read Response")
        case 5:
            print("    Block id = 5: Secure Write Request")
        case 6:
            print("    Block id = 6: Secure Write Sequential Request")
        case 7:
            print("    Block id = 7: Secure Write Response Model (DRAFT 1)")
        case 8:
            print("    Block id = 8: Get Device Security Certificate")
        case 9:
            print("    Block id = 9: Set Operator Security Certificate")
        case 10:
            print("    Block id = 10: Communication Interface Header")
        case 11:
            print("    Block id = 11: Ethernet Link Layer")
        case 12:
            print("    Block id = 12: IPv4")
        case 13:
            print("    Block id = 13: IPv6")
        case 14:
            print("    Block id = 14: Proxy Server")
        case 15:
            print("    Block id = 15: Interface Counters Model")
        case 16:
            print("    Block id = 16: Simple IP Network")
        case 17:
            print("    Block id = 17: Serial Interface")
        case 18:
            print("    Block id = 18: Cellular Link")
        case 19:
            print("    Block id = 19: PPP Link")
        case 101:
            print("    Block id = 101: Inverter (Single Phase)")
        case 102:
            print("    Block id = 102: Inverter (Split-Phase)")
        case 103:
            print("    Block id = 103: Inverter (Three Phase)")
        case 111:
            print("    Block id = 111: Inverter (Single Phase) FLOAT")
        case 112:
            print("    Block id = 112: Inverter (Split Phase) FLOAT")
        case 113:
            print("    Block id = 113: Inverter (Three Phase) FLOAT")
        case 120:
            print("    Block id = 120: Nameplate")
        case 121:
            print("    Block id = 121: Basic Settings")
        case 122:
            print("    Block id = 122: Measurements_Status")
        case 123:
            print("    Block id = 123: Immediate Controls")
        case 124:
            print("    Block id = 124: Storage")
        case 125:
            print("    Block id = 125: Pricing")
        case 126:
            print("    Block id = 126: Static Volt-VAR")
        case 127:
            print("    Block id = 127: Freq-Watt Param")
        case 128:
            print("    Block id = 128: Dynamic Reactive Current")
        case 129:
            print("    Block id = 129: LVRTD")
        case 130:
            print("    Block id = 130: HVRTD")
        case 131:
            print("    Block id = 131: Watt-PF")
        case 132:
            print("    Block id = 132: Volt-Watt")
        case 133:
            print("    Block id = 133: Basic Scheduling")
        case 134:
            print("    Block id = 134: Freq-Watt Crv")
        case 135:
            print("    Block id = 135: LFRT")
        case 136:
            print("    Block id = 136: HFRT")
        case 137:
            print("    Block id = 137: LVRTC")
        case 138:
            print("    Block id = 138: HVRTC")
        case 139:
            print("    Block id = 139: LVRTX")
        case 140:
            print("    Block id = 140: HVRTX")
        case 141:
            print("    Block id = 141: LFRTC")
        case 142:
            print("    Block id = 142: HFRTC")
        case 143:
            print("    Block id = 143: LFRTX")
        case 144:
            print("    Block id = 144: HFRTX")
        case 145:
            print("    Block id = 145: Extended Settings")
        case 160:
            print("    Block id = 160: Multiple MPPT Inverter Extension Model")
        case 201:
            print("    Block id = 201: Meter (Single Phase)single phase (AN or AB) meter")
        case 202:
            print("    Block id = 202: split single phase (ABN) meter")
        case 203:
            print("    Block id = 203: wye-connect three phase (abcn) meter")
        case 204:
            print("    Block id = 204: delta-connect three phase (abc) meter")
        case 211:
            print("    Block id = 211: single phase (AN or AB) meter")
        case 212:
            print("    Block id = 212: split single phase (ABN) meter")
        case 213:
            print("    Block id = 213: wye-connect three phase (abcn) meter")
        case 214:
            print("    Block id = 214: delta-connect three phase (abc) meter")
        case 220:
            print("    Block id = 220: Secure AC Meter Selected Readings")
        case 302:
            print("    Block id = 302: Irradiance Model")
        case 303:
            print("    Block id = 303: Back of Module Temperature Model")
        case 304:
            print("    Block id = 304: Inclinometer Model")
        case 305:
            print("    Block id = 305: GPS")
        case 306:
            print("    Block id = 306: Reference Point Model")
        case 307:
            print("    Block id = 307: Base Met")
        case 308:
            print("    Block id = 308: Mini Met Model")
        case 401:
            print("    Block id = 401: String Combiner (Current)")
        case 402:
            print("    Block id = 402: String Combiner (Advanced)")
        case 403:
            print("    Block id = 403: String Combiner (Current)")
        case 404:
            print("    Block id = 404: String Combiner (Advanced)")
        case 501:
            print("    Block id = 501: Solar Module")
        case 502:
            print("    Block id = 502: Solar Module")
        case 601:
            print("    Block id = 601: Tracker Controller DRAFT 2")
        case 801:
            print("    Block id = 801: Energy Storage Base Model (DEPRECATED)")
        case 802:
            print("    Block id = 802: Battery Base Model")
        case 803:
            print("    Block id = 803: Lithium-Ion Battery Bank Model")
        case 804:
            print("    Block id = 804: Lithium-Ion String Model")
        case 805:
            print("    Block id = 805: Lithium-Ion Module Model")
        case 806:
            print("    Block id = 806: Flow Battery Model")
        case 807:
            print("    Block id = 807: Flow Battery String Model")
        case 808:
            print("    Block id = 808: Flow Battery Module Model")
        case 809:
            print("    Block id = 809: Flow Battery Stack Model")
        case _:
            print(f"    Block id = {block_id}: Unknown block")
            next_address = -1

    if next_address > 0:
        return next_address + block_length
    else:
        return -1

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
        else:
            print("  The inverter is NOT providing a SunSpec Map")

    if client.connected:
        client.close()
        print()
        print("Closed connection to server")
