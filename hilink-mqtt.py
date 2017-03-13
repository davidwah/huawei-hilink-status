#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import xmltodict
import requests
import time
import math
from ConfigParser import SafeConfigParser
import paho.mqtt.client as mqtt
from datetime import datetime
import logging
import os
import schedule

# global
mqtt_connection_status = 0

# In %
mqtt_signal_strength  = 0

# In Bars
mqtt_signal_level  = 0

# eg. Number 1- 41
mqtt_network_type  = 0

# In min elapsed
mqtt_current_connection_time = 0

# In Mb
mqtt_total_upload = 0
mqtt_total_download = 0
mqtt_total_data = 0
mqtt_current_upload = 0
mqtt_current_download = 0

mqtt_sms =0



config_file = 'config.ini'

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.info("Startup Huawei HiLink Status: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
config_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), config_file)

# Get login details from 'config.ini'
parser = SafeConfigParser()
if os.path.exists(config_file_path):
  logging.info("Loaded config file " + config_file_path)
  #candidates = [ 'config.ini', 'my_config.ini' ]
  candidates = config_file_path
  found = parser.read(candidates)
  device_ip = parser.get('hilink-status', 'hilink_ip')
  mqtt_host = parser.get('hilink-status', 'mqtt_host')
  mqtt_port = parser.get('hilink-status', 'mqtt_port')
  mqtt_username = parser.get('hilink-status', 'mqtt_username')
  mqtt_password = parser.get('hilink-status', 'mqtt_password')
  mqtt_topic = parser.get('hilink-status', 'mqtt_topic')
  GET_UPDATE_INTERVAL = parser.get('hilink-status', 'update_interval_min')
  logging.info("updating data every " + GET_UPDATE_INTERVAL +"min")
else:
  logging.error("ERROR: Config file not found " + config_file_path)
  quit()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  logging.info("Connected to MQTT host " + mqtt_host + " with result code "+str(rc))
  logging.info("Publishing to topic: " + mqtt_topic)
  client.publish(mqtt_topic, "MQTT connected");
  
client = mqtt.Client()
# Callback when MQTT is connected
client.on_connect = on_connect
# Connect to MQTT
client.username_pw_set(mqtt_username, mqtt_password);
client.connect(mqtt_host, mqtt_port, 60)
client.publish(mqtt_topic, "Connecting to MQTT host " + mqtt_host);
# Non-blocking MQTT subscription loop
client.loop_start()
  
def to_size(size):
   if (size == 0):
       return '0 Bytes'
   size_name = ('Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
   i = int(math.floor(math.log(size,1024)))
   p = math.pow(1024,i)
   s = round(size/p,2)
   return '%s %s' % (s,size_name[i])


def is_hilink(device_ip):
    try:
        r = requests.get(url='http://' + device_ip + '/api/device/information', timeout=(int(2),int(2)))
    except requests.exceptions.RequestException as e:
        logging.error("Error: "+str(e))
        return False;
        
    if r.status_code != 200:
        return False
    d = xmltodict.parse(r.text, xml_attribs=True)
    if 'error' in d:
        return False;
    return True

def call_api(device_ip, resource, xml_attribs=True):
    try:
        r = requests.get(url='http://' + device_ip + resource, timeout=(2.0,2.0))
    except requests.exceptions.RequestException as e:
        logging.error("Error: "+str(e))
        return False;
    if r.status_code == 200:
    	d = xmltodict.parse(r.text, xml_attribs=xml_attribs)
        if 'error' in d:
            raise Exception('Received error code ' + d['error']['code'] + ' for URL ' + r.url)
        return d
    else:
      raise Exception('Received status code ' + str(r.status_code) + ' for URL ' + r.url)

def get_connection_status(status):
    result = 'n/a'
    if status == '2' or status == '3' or status == '5' or status == '8' or status == '20' or status == '21' or status == '23' or status == '27' or status == '28' or status == '29' or status == '30' or status == '31' or status == '32' or status == '33':
        result = 'Connection failed, the profile is invalid'
    elif status == '7' or status == '11' or status == '14' or status == '37':
        result = 'Network access not allowed'
    elif status == '12' or status == '13':
        result = 'Connection failed, roaming not allowed'
    elif status == '201':
        result = 'Connection failed, bandwidth exceeded'
    elif status == '900':
        result = 'Connecting'
    elif status == '901':
        result = 'Connected'
    elif status == '902':
        result = 'Disconnected'
    elif status == '903':
        result = 'Disconnecting'
    return result

def get_network_type(type):
    result = 'n/a'
    if type == '0':
        result = 'No Service'
    elif type == '1':
        result = 'GSM'
    elif type == '2':
        result = 'GPRS (2.5G)'
    elif type == '3':
        result = 'EDGE (2.75G)'
    elif type == '4':
        result = 'WCDMA (3G)'
    elif type == '5':
        result = 'HSDPA (3G)'
    elif type == '6':
        result = 'HSUPA (3G)'
    elif type == '7':
        result = 'HSPA (3G)'
    elif type == '8':
        result = 'TD-SCDMA (3G)'
    elif type == '9':
        result = 'HSPA+ (4G)'
    elif type == '10':
        result = 'EV-DO rev. 0'
    elif type == '11':
        result = 'EV-DO rev. A'
    elif type == '12':
        result = 'EV-DO rev. B'
    elif type == '13':
        result = '1xRTT'
    elif type == '14':
        result = 'UMB'
    elif type == '15':
        result = '1xEVDV'
    elif type == '16':
        result = '3xRTT'
    elif type == '17':
        result = 'HSPA+ 64QAM'
    elif type == '18':
        result = 'HSPA+ MIMO'
    elif type == '19':
        result = 'LTE (4G)'
    elif type == '41':
        result = '3G'
    return result

def get_roaming_status(status):
    result = 'n/a'
    if status == '0':
        result = 'Disabled'
    elif status == '1':
        result = 'Enabled'
    return result

def get_signal_level(level):
    result = '-'
    if level == '1':
        result = '*'
    if level == '2':
        result = '**'
    if level == '3':
        result = '***'
    if level == '4':
        result = '****'
    if level == '5':
        result = '*****'
    return result

def traffic_statistics(device_ip, connection_status):
    d = call_api(device_ip, '/api/monitoring/traffic-statistics')
    current_connect_time = d['response']['CurrentConnectTime']
    current_upload = d['response']['CurrentUpload']
    current_download = d['response']['CurrentDownload']
    total_upload = d['response']['TotalUpload']
    total_download = d['response']['TotalDownload']
    global mqtt_current_connection_time, mqtt_total_upload, mqtt_total_download, mqtt_current_upload, mqtt_current_download

    if connection_status == '901':
        formatted_current_connection_time = time.strftime('%H:%M:%S', time.gmtime(float(current_connect_time)))
        mqtt_current_connection_time = round( (float(current_connect_time) * 0.0166667) ,2)
        logging.info('    Connected for: ' + formatted_current_connection_time + ' (hh:mm:ss)')
        
        # in Mb
        mqtt_current_download = round(float(current_download) / 1024.0 / 1024.0 ,2)
        size_current_download = to_size(float(current_download))
        logging.info('    Downloaded: ' + size_current_download)
        
        mqtt_current_upload = round(float(current_upload) / 1024.0 / 1024.0 ,2)
        size_current_upload = to_size(float(current_upload))
        logging.info('    Uploaded: ' + size_current_upload)
        
    mqtt_total_download = round(float(total_download) / 1024.0 / 1024.0 ,2)
    size_total_download = to_size(float(total_download))
    logging.info('  Total downloaded: ' + size_total_download)
    
    mqtt_total_upload = round(float(total_download) / 1024.0 / 1024.0 ,2)
    size_total_upload = to_size(float(total_upload))
    logging.info('  Total uploaded: ' + size_total_upload)
    
    mqtt_total_data = round( (mqtt_total_upload + mqtt_total_download) , 2)

def connection_status(device_ip):
    global mqtt_connection_status, mqtt_signal_strength, mqtt_signal_level, mqtt_network_type
    d = call_api(device_ip, '/api/monitoring/status')
    connection_status = d['response']['ConnectionStatus']
    signal_strength = d['response']['SignalStrength']
    signal_level = d['response']['SignalIcon']
    network_type = d['response']['CurrentNetworkType']
    roaming_status = d['response']['RoamingStatus']
    wan_ip = d['response']['WanIPAddress']
    primary_dns_ip = d['response']['PrimaryDns']
    secondary_dns_ip = d['response']['SecondaryDns']
    wifi_status = d['response']['WifiStatus']
    wifi_users_current = d['response']['CurrentWifiUser']
    wifi_users_max = d['response']['TotalWifiUser']

    # r = requests.get('http://ip.o11.net')
    # public_ip = None
    # if r.status_code == 200:
        # public_ip = r.text.rstrip()

    mqtt_connection_status = get_connection_status(connection_status)
    logging.info('  Connection status: ' + mqtt_connection_status)
    if connection_status == '901':
      
        formatted_network_type = get_network_type(network_type)
        mqtt_network_type = network_type
        mqtt_signal_level = get_signal_level(signal_level)
        mqtt_signal_strength = signal_strength
        logging.info('    Network type: ' + formatted_network_type)
        logging.info('    Signal level: ' + mqtt_signal_level + ' (' + mqtt_signal_strength + '%)')
        logging.info('    Roaming: ' + get_roaming_status(roaming_status))
    if wan_ip is not None:
        logging.info('    Modem WAN IP address: ' +  wan_ip)
    # logging.info('    Public IP address: ' + public_ip)
    # logging.info('    DNS IP addresses: ' + primary_dns_ip + ', ' + secondary_dns_ip)
    if wifi_status == '1':
        logging.info('    WIFI users\t\t' + wifi_users_current + ' (of ' + wifi_users_max + ')')

    return connection_status

def device_info(device_ip):
    d = call_api(device_ip, '/api/device/information')
    device_name = d['response']['DeviceName']
    serial_number = d['response']['SerialNumber']
    imei = d['response']['Imei']
    hardware_version = d['response']['HardwareVersion']
    software_version = d['response']['SoftwareVersion']
    mac_address1 = d['response']['MacAddress1']
    mac_address2 = d['response']['MacAddress2']
    product_family = d['response']['ProductFamily']

    logging.info('Huawei ' + device_name + ' ' + product_family + ' Modem (IMEI: ' + imei + ')')
    logging.info('  Hardware version: ' + hardware_version)
    logging.info('  Software version: ' + software_version)
    logging.info('  Serial: ' + serial_number)
    # print('  MAC address (modem): ' + mac_address1, end='')
    # if mac_address2 is not None:
    #     print('\tMAC address (WiFi): ' + mac_address2)
    # else:
    #     print('')

def provider(device_ip, connection_status):
    d = call_api(device_ip, '/api/net/current-plmn')
    state = d['response']['State']
    provider_name = d['response']['FullName']
    if connection_status == '901':
        logging.info('    Network operator: ' + provider_name)

def unread(device_ip):
    d = call_api(device_ip, '/api/monitoring/check-notifications')
    global mqtt_sms
    unread_messages = d['response']['UnreadMessage']
    if unread_messages is not None and int(unread_messages) > 0:
        logging.info('  Unread SMS: ' + unread_messages)
        mqtt_sms = unread_messages

if len(sys.argv) == 2:
    device_ip = sys.argv[1]

def mqtt_publish():
  if is_hilink(device_ip):
      logging.info("Publish to MQTT")
      client.publish(mqtt_topic + "/connection_status", mqtt_connection_status)
      client.publish(mqtt_topic + "/signal_strength", mqtt_signal_strength)
      client.publish(mqtt_topic + "/signal_level", mqtt_signal_level)
      client.publish(mqtt_topic + "/network_type", mqtt_network_type)
      client.publish(mqtt_topic + "/current_connection_time", mqtt_current_connection_time)
      client.publish(mqtt_topic + "/current_upload", mqtt_current_upload)
      client.publish(mqtt_topic + "/current_download", mqtt_current_download)
      client.publish(mqtt_topic + "/total_upload", mqtt_total_upload)
      client.publish(mqtt_topic + "/total_download", mqtt_total_download)
      client.publish(mqtt_topic + "/total_data", mqtt_total_data)
      # client.publish(mqtt_topic + "/sms", mqtt_sms)


# Run once
if is_hilink(device_ip):
  device_info(device_ip)
  connection_status = connection_status(device_ip)
  provider(device_ip, connection_status)
  traffic_statistics(device_ip, connection_status)
  unread(device_ip)
  logging.info('')
  mqtt_publish()
else:
  logging.error("Can't find a Huawei HiLink device on " + device_ip)


# Then schedule
logging.info("Schedule update every " + GET_UPDATE_INTERVAL + "min")
schedule.every(int(GET_UPDATE_INTERVAL)).minutes.do(mqtt_publish)

while True:
    schedule.run_pending()
    time.sleep(1)

