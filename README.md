VLAN Configuration Exporter
A Python tool that connects to Cisco and Aruba AOS-CX switches via SSH, extracts all VLAN SVI (Layer 3) interface data, displays it in a clean terminal table, and exports it to a timestamped Excel file.

Supported Vendors
VendorOptionPlatformCisco IOS / IOS-XEciscoAny Cisco Layer 3 switchAruba AOS-CXaruba_cx8xxx / 6xxx / 4xxx series

Features

SSH connection using Netmiko
Extracts VLAN, IP Address, Subnet Mask, Virtual IP, Priority, Preempt, Status
Detects HSRP (Cisco) and Active-Gateway / VRRP (Aruba CX) virtual IPs
Clean terminal table output with Active / Shutdown summary
Auto-named Excel export: vlan_export_<IP>_<timestamp>.xlsx
Graceful error handling for failed connections and empty results
132 lines of code


Requirements
bashpip install netmiko pandas openpyxl

Usage
bashpython vlan_exporter.py
