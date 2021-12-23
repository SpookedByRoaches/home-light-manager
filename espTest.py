#!/usr/bin/python3
import time
import sys
import paho.mqtt.client as mqtt
from flask import Flask, render_template, request

broker = "localhost"

rooms = {'Desk':4, 'Kitchen':3, 'Living':4, 'Bedroom':4, 'BedroomBathroom':3}
def on_connect(client, userdata, flags, rc): 
    if (rc == 0):
        print("Connected with result code " + str(rc)) 
        client.subscribe("lights/Desk/state") 
        client.subscribe("lights/Kitchen/state") 
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
client.username_pw_set(username="REDACTED", password="REDACTED")

if (client.connect(broker, 1883)):
    print ("did not connect")


client.loop_start()

app = Flask(__name__)

pins = {}

for room, numPins in rooms.items():
    pins[room] = []
    for i in range(numPins):
        pins[room].append({'name' : room + ' ' + str(i) , 'state' : 0, 'topic': 'lights/' + room + '/' + str(i)})

print(pins)

@app.route("/")
def main():
   # For each pin, read the pin state and store it in the pins dictionary:
   for room in pins:
       for pin in room:
          ret = client.publish('lights/' + room + '/' + pin, "reqState")
   # Put the pin dictionary into the template data dictionary:
   templateData = {
      'pins' : pins
      }
   # Pass the template data into the template main.html and return it to the user
   return render_template('index.html', **templateData)


@app.route("/<room>/<pin>/<action>")
def action(room, pin, action):
   # Convert the pin from the URL into an integer:
   # Get the device name for the pin being changed:
   deviceName = pins[room][pin]['name']
   topicName = pins[room][pin]['topic']
   # If the action part of the URL is "on," execute the code indented below:
   if action == "on":
      # Set the pin high:
      ret_val = client.publish(topicName, "on")
      print("Got " + str(ret_val))
      pins[room][pin]["state"] = 1
      # Save the status message to be passed into the template:
      message = "Turned " + topicName + " on."
   if action == "off":
      client.publish(topicName, "off")
      pins[room][pin]["state"] = 0
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
