import RPi.GPIO as GPIO
import pytz
import time
from time import gmtime, strftime, sleep
import datetime
import urllib3
http = urllib3.PoolManager()
import logging
import sys
import ConfigParser
import uuid
#for python 2
import urllib
import threading
#for python 3
#from urllib.parse import urlencode
import buffer
config = ConfigParser.ConfigParser()
config.readfp(open(r'machineConfig.txt'))
LOCATION= config.get('machine-config','Facility')
TOTAL_MACHINE_CONNECTED = int(config.get('machine-config', 'TOTAL_MACHINES'))
MACHINE1_CYCLE  = int(config.get('machine-config', 'MACHINE1_CYCLE'))
MACHINE1_GOOD_BAD =int(config.get('machine-config','MACHINE1_Quality'))
MACHINE2_CYCLE  = int(config.get('machine-config', 'MACHINE2_CYCLE'))
MACHINE2_GOOD_BAD =int(config.get('machine-config','MACHINE2_Quality'))
MACHINE1_NAME =config.get('machine-config','MACHINE1_NAME')
MACHINE2_NAME =config.get('machine-config','MACHINE2_NAME')


log_config = ConfigParser.ConfigParser()
log_config.readfp(open(r'logConfig.txt'))


LOG= log_config.get('log-config', 'LOG_ENABLE')
#if MACHINE1_GOOD_BAD=="NOT CONNECTED":

#lock=threading.Lock()
root = logging.getLogger()
root.setLevel(logging.DEBUG)
if LOG == 'True':
        root.disabled = False
else :
        root.disabled=True
log_message =logging.StreamHandler(sys.stdout)
log_message.setLevel(logging.DEBUG)
#use %(lineno)d for printnig line  no
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s',"%Y-%m-%d %H:%M:%S")
log_message.setFormatter(formatter)
root.addHandler(log_message)


machine1_good_badpart_pinvalue=0
machine1_cycle_risingEdge_detected=0
machine2_good_badpart_pinvalue=0
machine2_cycle_risingEdge_detected=0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#GPIO.setmode(GPIO.BOARD)
#MACHINE_CYCLE  = 23
#MACHINE_CYCLE2 = 24
#GPIO.setup(MACHINE_CYCLE,GPIO.IN)
#GPIO.setup(MACHINE_CYCLE2,GPIO.IN)

GPIO.setup(MACHINE1_CYCLE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MACHINE1_GOOD_BAD, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MACHINE2_CYCLE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MACHINE2_GOOD_BAD, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(STATUS1,GPIO.OUT)
#GPIO.setup(STATUS2,GPIO.OUT)

#INITALIZE = 1
## PIN NUBERS   BCM  PHYCICAL
#               27    13
#               18   12
#GPIO.setup(0, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO.setup(18, GPIO.OUT, pull_up_down = GPIO.PUD_UP)



class Machine:
        'Common base class for all machines'
        MachineCount = 0
        def __init__(self, machine_cycle_rising_edge, machine_cycle_falling_edge, machine_cycle_pulse_time):
                self.machine_cycle_rising_edge = machine_cycle_rising_edge
                self.machine_cycle_falling_edge = machine_cycle_falling_edge
                self.machine_cycle_pulse_time = machine_cycle_pulse_time

                #Machine.machineCount += 1
        def machine_cycle_starttime(self):

                self.machine_cycle_rising_edge=time.time()
                logging.debug(self.machine_cycle_rising_edge)
        def machine_cycle_stoptime(self):
                self.machine_cycle_falling_edge=time.time()
                logging.debug(self.machine_cycle_falling_edge)
        def machine_cycle_cleartime(self):
                self.machine_cycle_rising_edge=0
                self.machine_cycle_falling_edge=0
        def machine_cycle_pulseTime(self,machineno):
                self.machineno=machineno
                self.machine_cycle_pulse_time=self.machine_cycle_falling_edge-self.machine_cycle_rising_edge
                logging.debug ("Total Duration of MACHINE CYCLE SIGNAL%s is :%s ",str(machineno),str(self.machine_cycle_pulse_time))
                if self.machine_cycle_pulse_time >=2 and self.machine_cycle_pulse_time <= 4 :
                        return 1
                else:
                        return 0
        def partCount(self):
                self.MachineCount+=1
                return self.MachineCount

def plcMachine1(channel):
        time.sleep(0.1)
        global machine1_cycle_risingEdge_detected
        global machine1_good_badpart_pinvalue
        data_send_from_machine1_status=0
        machine1_cycle_pinvalue=0
        if (GPIO.input(MACHINE1_CYCLE)==0): # dry contact closed on machine cycle pin
                machine1_cycle_risingEdge_detected = 1
                #m1.machine_cycle_starttime()
                logging.debug ("Rising edge : MACHINE1 CYCLE SIGNAL ")
                m1.machine_cycle_starttime()
                if (GPIO.input(MACHINE1_GOOD_BAD)==0): # check value of good_badpart_signal and set it to 1 if ok
                        machine1_good_badpart_pinvalue=1
                else:   #good_badpart is not ok
                        machine1_good_badpart_pinvalue=0
        else: # dry contact opend falling edge detected for machine_cycle pin
                if machine1_cycle_risingEdge_detected == 1:
                        logging.debug ("Falling edge: MACHINE1 CYCLE SIGNAL ")
                        m1.machine_cycle_stoptime()
                        machine1_cycle_risingEdge_detected=0
                        #utc_datetime = datetime.datetime.utcnow()
                        machine_cycle_timestamp=datetime.datetime.now(tz=pytz.UTC).replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+"+00:00"
                        #machine_cycle_timestamp=utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
                        #machine_cycle_timestamp  = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                        #logging.info(machine_cycle_timestamp)
                        #logging.debug ("Falling edge: MACHINE1 CYCLE SIGNAL ")
                        machine1_cycle_pinvalue=m1.machine_cycle_pulseTime(1)
                        if machine1_cycle_pinvalue==1:                          #//if this is valid pulse
                                if(GPIO.input(MACHINE1_GOOD_BAD)==0):
                                        machine1_good_badpart_pinvalue=1
                                else:
                                        machine1_good_badpart_pinvalue=0
                                count=m1.partCount()
#                       m1.machine_cycle_cleartime()
                        #try:
                        #        lock.acquire()
                                finalmessage="Quality"+":"+str(machine1_good_badpart_pinvalue)
                                logging.debug(finalmessage)
                                fields={'ts':machine_cycle_timestamp,'loc':LOCATION,'mach':MACHINE1_NAME,'data':finalmessage}
                                encoded_args = urllib.urlencode(fields)
                                url = 'http://52.170.42.16:5555/get?' + encoded_args
                                try:
                                        r = http.request('GET', url,timeout=1.0)
                                        data_send_from_machine1_status=r.status
                                        #logging.debug('HTTP Send Status: ',r.status)
                                except urllib3.exceptions.MaxRetryError as e:
                                        data_send_from_machine1_status=0
                                #print('connection error: ')
                                if data_send_from_machine1_status==0 or data_send_from_machine1_status != 200 :
                                        if data_send_from_machine1_status==0:
                                                logging.debug("not able to send data :Connection Error")
                                        else:
                                                data=1
#                                               logging.debug("HTTP send status : %d",data_send_from_machine1_status)
                                        buffer.push(machine_cycle_timestamp+" "+LOCATION+ " " + MACHINE1_NAME +" "+finalmessage)
                                else:
                                        logging.debug("HTTP send status : %d",data_send_from_machine1_status)
                        else:
                                logging.debug("Machine 1 cycle pulse width is invalid")
                m1.machine_cycle_cleartime()
                        #machine_cycle_risingEdge_detected = 0


def plcMachine2(channel):
        time.sleep(0.1)
        global machine2_cycle_risingEdge_detected
        global machine2_good_badpart_pinvalue
        data_send_from_machine2_status=0
        machine2_cycle_pinvalue=0
        if (GPIO.input(MACHINE2_CYCLE)==0): # dry contact closed on machine cycle pin
                machine2_cycle_risingEdge_detected = 1
                logging.debug ("Rising edge : MACHINE2 CYCLE SIGNAL ")
                m2.machine_cycle_starttime()
                #logging.debug ("Rising edge : MACHINE2 CYCLE SIGNAL ")
                if (GPIO.input(MACHINE2_GOOD_BAD)==0): # check value of good_badpart_signal and set it to 1 if ok
                        machine2_good_badpart_pinvalue=1
                else:   #good_badpart is not ok
                        machine2_good_badpart_pinvalue=0
        else: # dry contact opend falling edge detected for machine_cycle pin
                if machine2_cycle_risingEdge_detected == 1:
                        logging.debug ("Falling edge: MACHINE2 CYCLE SIGNAL ")
                        m2.machine_cycle_stoptime()
                        machine2_cycle_risingEdge_detected=0
                        #utc_datetime = datetime.datetime.utcnow()
                        machine_cycle_timestamp=datetime.datetime.now(tz=pytz.UTC).replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+"+00:00"
                        #machine_cycle_timestamp=utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
                        #machine_cycle_timestamp  = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                        #logging.info(machine_cycle_timestamp)
                 #       logging.debug ("Falling edge: MACHINE2 CYCLE SIGNAL ")
                        machine2_cycle_pinvalue=m2.machine_cycle_pulseTime(2)
                        if machine2_cycle_pinvalue==1:
                                if(GPIO.input(MACHINE2_GOOD_BAD)==0): # valid pulse
                                        machine2_good_badpart_pinvalue=1
                                else:
                                        machine1_good_badpart_pinvalue=0

                                #try:
                                #        lock.acquire()
                                count=m2.partCount()
                                finalmessage="Quality"+":"+str(machine2_good_badpart_pinvalue)
                                logging.debug(finalmessage)
                                fields={'ts':machine_cycle_timestamp,'loc':LOCATION,'mac':MACHINE2_NAME,'data':finalmessage}
                                encoded_args = urllib.urlencode(fields)
                                url = 'http://52.170.42.16:5555/get?' + encoded_args
                                try:
                                        r = http.request('GET', url,timeout=1.0)
                                        data_send_from_machine2_status=r.status
                                        #logging.debug('HTTP Send Status: ',r.status)
                                except urllib3.exceptions.MaxRetryError as e:
                                        data_send_from_machine2_status=0
                                        #print('connection error: ')
                                if data_send_from_machine2_status==0 or data_send_from_machine2_status != 200 :
                                        if data_send_from_machine2_status==0:
                                                logging.debug("Not able to send data :Connection Error")
                                        else:
                                                data=1
                                        #       logging.debug("HTTP send status : %d",data_send_from_machine2_status)
                                        buffer.push(machine_cycle_timestamp+" "+LOCATION+" "+MACHINE2_NAME+finalmessage)
                                else:
                                        logging.debug("HTTP send status : %d",data_send_from_machine2_status)
                        else:
                                logging.debug("Machine2 cycle pulse width is invalid")
                m2.machine_cycle_cleartime()





def get_mac():
        mac_num = hex(uuid.getnode()).replace('0x', '').upper()
        mac = ':'.join(mac_num[i : i + 2] for i in range(0, 11, 2))
        return mac

mac=str(get_mac())


GPIO.add_event_detect(MACHINE1_CYCLE, GPIO.BOTH, callback=plcMachine1,bouncetime=200)
GPIO.add_event_detect(MACHINE2_CYCLE, GPIO.BOTH, callback=plcMachine2,bouncetime=200)
m1 = Machine(0, 0, 0)
m2 = Machine(0, 0, 0)
#print ("Total machines  %d" % Machine.machineCount)
logging.debug("data collection started")
try:
        while True:
                time.sleep(10)
                logging.debug("--")
except KeyboardInterrupt:
        logging.debug("Quit")
        GPIO.cleanup()
