#!/usr/bin/python3
import time
import sys
import paho.mqtt.client as mqtt
from flask import Flask, render_template, request

broker = "10.0.0.5"
to_write = open("/home/pi/scripts/nodeMCU/file.txt", "w")
def on_connect(client, userdata, flags, rc): 
    if (rc == 0):
        print("Connected with result code " + str(rc)) 
        client.subscribe("lights/desk/state") 
        client.subscribe("lights/D7/state") 
    else:
        print("Could not connect; code " + str(rc))

def on_publish(client, userdata, result):
   print("Published message")

def on_message(client, userdata, msg): 
   stuff = msg.topic.split("/")
   myLoad = str(msg.payload.decode("utf-8"))
   print("got message " + myLoad)
   
   print("Topic " + stuff[1])
   
   pins[stuff[1]][state] = myLoad
   templateData = {
      'pins' : pins
   }
   return render_template('index.html', **templateData)
   
   
   


client = mqtt.Client()


client.on_connect = on_connect 
client.on_message = on_message 
client.on_publish = on_publish
client.username_pw_set(username="Bo3lwa98", password="AneechkIhne!")

if (client.connect(broker, 1883)):
    print ("did not connect")


client.loop_start()

"""
ret = client.publish("lights/pin2", "on")

ret = client.publish("lights/D7", "on")

ret = client.publish("lights/pin2", "reqState")

if (ret[0]):
    print("could not send message")
"""

app = Flask(__name__)

pins = {
   "desk" : {'name' : 'desk', 'state' : 1, "topic": "lights/desk"},
   "D7": {'name' : 'Node D7', 'state' : 1, 'topic': "lights/D7"},
   }


@app.route("/")
def main():
   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      ret = client.publish("lights/"+pin, "reqState")
   # Put the pin dictionary into the template data dictionary:
   templateData = {
      'pins' : pins
      }
   # Pass the template data into the template main.html and return it to the user
   return render_template('index.html', **templateData)


@app.route("/<changePin>/<action>")
def action(changePin, action):
   # Convert the pin from the URL into an integer:
   # Get the device name for the pin being changed:
   deviceName = pins[changePin]['name']
   topicName = pins[changePin]['topic']
   # If the action part of the URL is "on," execute the code indented below:
   if action == "on":
      # Set the pin high:
      ret_val = client.publish(topicName, "on")
      print("Got " + str(ret_val))
      pins[changePin]["state"] = 1
      # Save the status message to be passed into the template:
      message = "Turned " + topicName + " on."
   if action == "off":
      client.publish(topicName, "off")
      pins[changePin]["state"] = 0
      message = "Turned " + topicName + " off."
   print(message)

   # For each pin, read the pin state and store it in the pins dictionary:
   # Along with the pin dictionary, put the message into the template data dictionary:
   templateData = {
      'pins' : pins
   }

   return render_template('index.html', **templateData)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=42069, debug=True)
