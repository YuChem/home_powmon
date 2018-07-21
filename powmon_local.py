#!/usr/bin/python3

# based on https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/iot/api-client/mqtt_example

"""
Power monitor module connecting to the local MQTT broker over non-encrypted connection
based on the google's MQTT secure code
"""

import argparse
from datetime import datetime as dt, timezone, timedelta
import os
import random
import time

import paho.mqtt.client as mqtt

from sensors.pzem import Pzem_004

JSON_TEMPLATE = '{{"phase":"L","V":{V},"A":{A}, "W":{W}, "KWh":{Wh},"collected":"{ts}"}}'

# The initial backoff time after a disconnection occurs, in seconds.
minimum_backoff_time = 1

# The maximum backoff time before giving up, in seconds.
MAXIMUM_BACKOFF_TIME = 32

# Whether to wait with exponential backoff before publishing.
should_backoff = False

# [START iot_mqtt_config]
def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_connect(unused_client, unused_userdata, unused_flags, rc):
    print(dt.now(), ': on_connect', mqtt.connack_string(rc))

    # After a successful connect, reset backoff time and stop backing off.
    global should_backoff
    global minimum_backoff_time
    should_backoff = False
    minimum_backoff_time = 1

def on_disconnect(unused_client, unused_userdata, rc):
    print(dt.now(), ': on_disconnect', error_str(rc))

    global should_backoff
    should_backoff = True


def on_publish(unused_client, unused_userdata, unused_mid):
    print(dt.now(), ': ack')


def on_message(unused_client, unused_userdata, message):
    payload = str(message.payload)
    print(dt.now(), ': Received message \'{}\' on topic \'{}\' with Qos {}'.format(payload, message.topic, str(message.qos)))


def get_client(device_id, 
               mqtt_bridge_hostname, 
               mqtt_bridge_port):
    """Create our MQTT client. The client_id is a unique string that identifies
    this device. For Google Cloud IoT Core, it must be in the format below."""
    client = mqtt.Client(client_id=(device_id))

    #client.username_pw_set(username='', password='')

    # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
    # describes additional callbacks that Paho supports. In this example, the
    # callbacks just print to standard out.
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Connect to the Google MQTT bridge.
    print("connecting to MQTT broker: %s:%s" % (mqtt_bridge_hostname, mqtt_bridge_port))
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    # This is the topic that the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(device_id)

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)

    return client

def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=('Power monitor MQTT basic client.'))
    parser.add_argument('--device_id', required=True, help='Cloud IoT Core device id')
    parser.add_argument('--num_messages',type=int,default=100,help='Number of messages to publish.')
    parser.add_argument('--mqtt_bridge_hostname',default='localhost',help='MQTT bridge hostname.')
    parser.add_argument('--mqtt_bridge_port',choices=(1883, 8883),default=1883,type=int,help='MQTT bridge port.')

    return parser.parse_args()

# [START iot_mqtt_run]
def main():
    global minimum_backoff_time

    args = parse_command_line_args()

    mqtt_topic = '/devices/{}/state'.format(args.device_id)
    print("publishing topic: %s" % mqtt_topic)

    client = get_client(args.device_id, args.mqtt_bridge_hostname, args.mqtt_bridge_port)

    p = Pzem_004()
    p.open()

    # Publish num_messages mesages to the MQTT bridge once per second.
    for i in range(1, args.num_messages + 1):
        # Process network events.
        client.loop()

        # Wait if backoff is required.
        if should_backoff:
            # If backoff time is too large, give up.
            if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
                print('Exceeded maximum backoff time. Giving up.')
                break

            # Otherwise, wait and connect again.
            delay = minimum_backoff_time + random.randint(0, 1000) / 1000.0
            print('Waiting for {} before reconnecting.'.format(delay))
            time.sleep(delay)
            minimum_backoff_time *= 2
            client.connect(args.mqtt_bridge_hostname, args.mqtt_bridge_port)

        data = p.read_all()
        data['ts'] = dt.now(timezone.utc).replace(microsecond=0).isoformat()[:-6] + 'Z'
        payload = JSON_TEMPLATE.format(**data)

        print(dt.now(), ': ', payload)

        # Publish "payload" to the MQTT topic. qos=1 means at least once
        # delivery. Cloud IoT Core also supports qos=0 for at most once
        # delivery.
        client.publish(mqtt_topic, payload, qos=0)

        # Send events every second. State should not be updated as often
        time.sleep(10)

    print('Finished.')

if __name__ == '__main__':
    main()
