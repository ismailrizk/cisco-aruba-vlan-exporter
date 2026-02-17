from netmiko import ConnectHandler
import pandas as pd
import re, getpass, sys
from datetime import datetime

VENDORS = {'cisco': 'cisco_ios', 'aruba_cx': 'aruba_aoscx'}


def connect(ip, user, pwd, vendor):
    return ConnectHandler(
        device_type=VENDORS[vendor], host=ip,
        username=user, password=pwd,
        timeout=60, session_timeout=60,
    )


def prefix_to_mask(prefix):
    if prefix == 0: return '0.0.0.0'
    bits = (0xFFFFFFFF >> (32 - prefix)) << (32 - prefix)
    return '.'.join(str((bits >> (8 * i)) & 0xFF) for i in reversed(range(4)))


def parse_cisco(conn):
    try:
        raw = conn.send_command('show running-config | section interface Vlan', read_timeout=120, expect_string=r'#')
    except Exception:
        raw = conn.send_command('show running-config', read_timeout=120)

    vlans = []
    for block in re.split(r'\ninterface ', raw):
        if not block.startswith('Vlan'): continue
        v = {}
        m = re.search(r'Vlan(\d+)', block)
        if m: v['VLAN'] = f"Vlan{m.group(1)}"
        m = re.search(r'ip address (\S+) (\S+)', block)
        if m: v['IP Address'], v['Subnet Mask'] = m.group(1), m.group(2)
        m = re.search(r'standby \d+ ip (\S+)', block)
        if m: v['Virtual IP'] = m.group(1)
        m = re.search(r'standby \d+ priority (\d+)', block)
        if m: v['Priority'] = m.group(1)
        v['Preempt'] = 'Yes' if 'preempt' in block else 'No'
        v['Status']  = 'Shutdown' if 'shutdown' in block else 'Active'
        vlans.append(v)
    return vlans


def parse_aruba_cx(conn):
    raw = conn.send_command('show running-config', read_timeout=120)

    vlans = []
    for block in re.split(r'(?=^interface vlan\d)', raw, flags=re.MULTILINE):
        if not re.match(r'interface vlan\d', block, re.IGNORECASE): continue
        v = {}
        m = re.match(r'interface vlan(\d+)', block, re.IGNORECASE)
        if m: v['VLAN'] = f"Vlan{m.group(1)}"
        m = re.search(r'ip address (\d+\.\d+\.\d+\.\d+)/(\d+)', block)
        if m: v['IP Address'], v['Subnet Mask'] = m.group(1), prefix_to_mask(int(m.group(2)))
        m = re.search(r'active-gateway ip\s+(\d+\.\d+\.\d+\.\d+)\b', block)
        if m: v['Virtual IP'] = m.group(1)
        m = re.search(r'^\s+address\s+(\d+\.\d+\.\d+\.\d+)', block, re.MULTILINE)
        if m: v['Virtual IP'] = m.group(1)
        m = re.search(r'^\s+priority\s+(\d+)', block, re.MULTILINE)
        if m: v['Priority'] = m.group(1)
        v['Preempt'] = 'Yes' if re.search(r'^\s+preempt\b', block, re.MULTILINE) else 'No'
        v['Status']  = 'Shutdown' if re.search(r'(?<!no )shutdown', block) else 'Active'
        vlans.append(v)
    return vlans


PARSERS = {'cisco': parse_cisco, 'aruba_cx': parse_aruba_cx}
COLS    = ['VLAN', 'IP Address', 'Subnet Mask', 'Virtual IP', 'Priority', 'Preempt', 'Status']


def export(data, filename):
    pd.DataFrame(data, columns=COLS).to_excel(filename, index=False)


def print_table(vlans):
    widths = {c: max(len(c), max((len(str(v.get(c, ''))) for v in vlans), default=0)) for c in COLS}
    sep    = "+" + "+".join("-" * (widths[c] + 2) for c in COLS) + "+"
    header = "|" + "|".join(f" {c:<{widths[c]}} " for c in COLS) + "|"
    print(sep); print(header); print(sep)
    for v in vlans:
        print("|" + "|".join(f" {str(v.get(c, '')):<{widths[c]}} " for c in COLS) + "|")
    print(sep)


if __name__ == '__main__':
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║        VLAN Configuration Exporter           ║")
    print("║           Cisco  |  Aruba AOS-CX             ║")
    print("╚══════════════════════════════════════════════╝")
    print()

    SWITCH_IP = input("  Switch IP Address : ").strip()
    print("  Vendor options    : cisco | aruba_cx")
    VENDOR    = input("  Vendor            : ").strip().lower()

    if VENDOR not in VENDORS:
        print(f"\n  [ERROR] Unknown vendor '{VENDOR}'. Choose: cisco | aruba_cx")
        sys.exit(1)

    USERNAME = input("  Username          : ").strip()
    PASSWORD = getpass.getpass("  Password          : ")

    print(f"\n  Connecting to {SWITCH_IP} ...")
    try:
        conn = connect(SWITCH_IP, USERNAME, PASSWORD, VENDOR)
    except Exception as e:
        print(f"\n  [ERROR] Connection failed: {e}")
        sys.exit(1)

    print("  Connected successfully.")
    print("  Retrieving VLAN data ...")

    vlans = PARSERS[VENDOR](conn)
    conn.disconnect()

    if not vlans:
        print("\n  No VLAN interfaces found on this device.")
        sys.exit(0)

    active   = sum(1 for v in vlans if v.get('Status') == 'Active')
    shutdown = len(vlans) - active
    print(f"\n  Found {len(vlans)} VLAN(s)  —  {active} Active  /  {shutdown} Shutdown\n")
    print_table(vlans)

    filename = f"vlan_export_{SWITCH_IP}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    export(vlans, filename)
    print(f"\n  Export saved to: {filename}")
    print("  Done.\n")
