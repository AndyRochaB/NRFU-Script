from Device import Device

T111 = { 'name' : 'Test 1.1.1', 'commands' : [ 'show version', ] }
T112 = { 'name' : 'Test 1.1.2', 'commands' : [ 'show ip interface brief | exclude unassigned', 'show running-config | section ssh', ] }
T113 = { 'name' : 'Test 1.1.3', 'commands' : [ 'show ip ospf neighbors', 'show ip route ospf', ] }
T114 = { 'name' : 'Test 1.1.4', 'commands' : [ 'show ip route', ] }

aggWan = Device('Agg-WAN', '10.255.255.1', [ T111, T112, ])
cpe = Device('INT', '10.255.255.2', [ T111, T112, T113, T114, ])
core = Device('Core', '10.255.255.3', [ T111, T112, T113, ])
div = Device('Div', '10.255.255.4', [ T111, T112, T113, ])
mz = Device('MZ', '10.255.255.5', [ T111, T112, T113, ])
idf1 = Device('IDF-1', '10.255.255.6', [ T111, T112, T113, ])
server = Device('Server', '10.255.255.7', [ T111, T112, T114, ])

labDevices = [ aggWan, cpe, core, div, mz, idf1, server, ]

# ping -o 10.255.255.1 | grep packet
# ping -o 10.255.255.2 | grep packet
# ping -o 10.255.255.3 | grep packet
# ping -o 10.255.255.4 | grep packet
# ping -o 10.255.255.5 | grep packet
# ping -o 10.255.255.6 | grep packet
# ping -o 10.255.255.7 | grep packet
