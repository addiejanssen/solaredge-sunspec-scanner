# SolarEdge SunSpec Scanner

The current version of the [Domoticz SolarEdge_ModbusTCP plugin](https://github.com/addiejanssen/domoticz-solaredge-modbustcp-plugin)
uses the [solaredge_modbus library](https://github.com/nmakel/solaredge_modbus) which has been archived by its author.

The solaredge_modbus library uses static addresses to find meters and batteries.
Unfortunately, some inverters return values for non-existing meters or batteries.

Since SolarEdge inverters support monitoring data directly from the inverter using the SunSpec open protocol,
they should also provide an option to return a map showing the devices connected to the inverter.

This scanner tries to find the SunSpec Map and display the entries in it.

We are asking owners of SolarEdge inverters to run the scanner and share the output in the
[Domoticz forum](https://forum.domoticz.com/viewtopic.php?t=34039) helping us to replace the solaredge_modbus library.

## How to use

- Download the `scanner.py` file to your computer.
- Install `pymodbus` version `3.15.0` by running `pip install pymodbus==3.15.0`.
- Run the scanner: `python scanner.py <IP address or the DNS name of the inverter> <Modbus port number>`
  - Optionally add `--device-id <number>` when the inverter setup for anything else than `1`.
- Share the output in the [Domoticz forum](https://forum.domoticz.com/viewtopic.php?t=34039)
