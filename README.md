# Cisco VLAN to Excel Exporter

Simple Python script to extract VLAN interface data from Cisco switches via SSH and export to Excel.

## Features

- Connect to Cisco switches via SSH
- Extract VLAN interface configurations
- Parse HSRP/VRRP standby information
- Export data to Excel spreadsheet
- Simple command-line interface

## Prerequisites

- Python 3.7 or higher
- SSH access to Cisco switch
- User credentials with privilege to view running-config

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ismailrizk/cisco-vlan-to-excel.git
cd cisco-vlan-to-excel
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python simple_vlan_to_excel.py
```

The script will prompt you for:
- Switch IP address
- Username
- Password (hidden input)

Output file: `vlan_data.xlsx`

## Example Output

The Excel file will contain columns:
- VLAN (e.g., Vlan5, Vlan6)
- IP_Address
- Subnet_Mask
- Standby_IP (HSRP virtual IP)
- Priority (HSRP priority)
- Preempt (Yes/No)
- Status (Active/Shutdown)

## Supported Devices

- Cisco IOS switches
- Cisco IOS-XE switches
- Any Cisco device supporting SSH and standard show commands

## Troubleshooting

### Connection Timeout
- Increase timeout values in the script
- Check network connectivity
- Verify SSH is enabled on switch

### Authentication Failed
- Verify username and password
- Check user privilege level
- Ensure SSH is configured correctly

### Command Not Found
- Script will fallback to full `show running-config`
- Some older IOS versions may not support `section` command

