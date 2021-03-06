import urllib3
http = urllib3.PoolManager()
# from urllib.parse import urlencode
import urllib
import uuid
def get_mac():
        mac_num = hex(uuid.getnode()).replace('0x', '').upper()
        mac = ':'.join(mac_num[i : i + 2] for i in range(0, 11, 2))
        return str(mac)
macAddress=get_mac()
fields1={'MAC':macAddress}
encoded_args = urllib.urlencode(fields1)
url = 'http://52.170.42.16:5557/get?' + encoded_args
r = http.request('GET', url)
print('HTTP Send Status: ',r.status)
#print(fields1)
print(r.data)
#config_data=r.data
config_data=eval(r.data)
#config_data=[{'Machine': 'Machine2', 'MAC': 'B8:27:EB:45:7D:92', 'SignalType': 'EndOfCycle', 'PIN': '12', 'Facility': 'IZM'},{'Machine': 'Machine1', 'MAC': 'B8:27:EB:45:7D:92', 'SignalType': 'EndOfCycle', 'PIN': '13', 'Facility': 'IZM'}, {'Machine': 'Machine1', 'MAC': 'B8:27:EB:45:7D:92', 'SignalType': 'Quality', 'PIN': '19', 'Facility': 'IZM'}]
#print config_data
#as output of r.data you should get something like: config_data=[{"MAC": "AA:AA:AA:AA:AA:AA", "PIN": "1", "Machine":
#"machine01", "Facility": "IZM", "SignalType": "EndOfCycle"},{"MAC": "AA:AA:AA:AA:AA:AA", "PIN": "2", "Machine":
#"machine01", "Facility": "IZM", "SignalType": "Quality"},{"MAC": "AA:AA:AA:AA:AA:AA", "PIN": "3", "Machine": "machine02",
#"Facility": "IZM", "SignalType": "EndOfCycle"},{"MAC": "AA:AA:AA:AA:AA:AA", "PIN": "4", "Machine": "machine02",
#"Facility": "IZM", "SignalType": "Quality"}] import itertools im

machine_data=[]
#machine_name=['Machine1','Machine2','Machine3','machine4']

for machine in config_data:
        machine_data.append(machine['Machine'])
#print (machine_data)
machineCount = list(set(machine_data))
print machineCount
#print("total machine connected:"+str(len(machineCount)))

with open("machineConfig.txt", "w+") as myfile:
        myfile.write("[machine-config]\n")
        if any("Facility" in d for d in config_data):
                data ="Facility              = "+ config_data[0]['Facility']+"\n"
                myfile.write(data)
        data ="TotalMachines        = " +str(len(machineCount))+"\n"
        myfile.write(data)
        for x in range(int(len(machineCount))):
                data="MACHINE"+str(x+1)+"_NAME         = "+machineCount[x]+"\n"
                myfile.write(data)
                goodbadPresent=0
                for machine in config_data:
                        if machine['Machine']==machineCount[x]:
                                if machine['SignalType']=='EndOfCycle':
                                        data= machineCount[x]+"_CYCLE        = "+machine['PIN']+"\n"
                                        myfile.write(data)
                                if machine['SignalType']=='Quality':
                                        data= machineCount[x]+"_Quality      = "+machine['PIN']+"\n"
                                        myfile.write(data)
                                        goodbadPresent=1
                if goodbadPresent==0:
                        data= machineCount[x]+"_Quality      = not connected\n"
                        myfile.write(data)
