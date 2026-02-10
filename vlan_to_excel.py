from netmiko import ConnectHandler
import pandas as pd
import re
import getpass

def connect_switch(ip, user, pwd):
    device = {
        'device_type': 'cisco_ios',
        'host': ip,
        'username': user,
        'password': pwd,
        'timeout': 60,
        'session_timeout': 60,
    }
    return ConnectHandler(**device)

def get_vlan_data(connection):
    
    try:
        output = connection.send_command(
            'show running-config | section interface Vlan',
            read_timeout=120,
            expect_string=r'#'
        )
    except Exception as e:
        print(f"Error getting config: {e}")
        print("Trying alternative command...")
        output = connection.send_command('show running-config', read_timeout=120)
    
    vlan_list = []
    interfaces = re.split(r'\ninterface ', output)
    
    for interface in interfaces:
        if interface.startswith('Vlan'):
            vlan = {}
            
            
            vlan_num = re.search(r'Vlan(\d+)', interface)
            if vlan_num:
                vlan['VLAN'] = f"Vlan{vlan_num.group(1)}"
            
            
            ip = re.search(r'ip address (\S+) (\S+)', interface)
            if ip:
                vlan['IP_Address'] = ip.group(1)
                vlan['Subnet_Mask'] = ip.group(2)
            
            
            standby_ip = re.search(r'standby \d+ ip (\S+)', interface)
            if standby_ip:
                vlan['Standby_IP'] = standby_ip.group(1)
            
            
            priority = re.search(r'standby \d+ priority (\d+)', interface)
            if priority:
                vlan['Priority'] = priority.group(1)
            
            
            vlan['Preempt'] = 'Yes' if 'preempt' in interface else 'No'
            
            
            vlan['Status'] = 'Shutdown' if 'shutdown' in interface else 'Active'
            
            vlan_list.append(vlan)
    
    return vlan_list

def export_to_excel(data, filename='vlan_data.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Data exported to {filename}")


print("=" * 50)
print("Cisco VLAN to Excel Exporter")
print("=" * 50)


SWITCH_IP = input("Enter switch IP address: ")
USERNAME = input("Enter username: ")
PASSWORD = getpass.getpass("Enter password: ")

print("\nConnecting to switch...")
conn = connect_switch(SWITCH_IP, USERNAME, PASSWORD)

print("Getting VLAN data...")
vlans = get_vlan_data(conn)

print(f"Found {len(vlans)} VLAN interfaces")
for v in vlans:
    print(f"{v.get('VLAN')}: {v.get('IP_Address')} - {v.get('Status')}")

export_to_excel(vlans)

conn.disconnect()
print("Done!")
