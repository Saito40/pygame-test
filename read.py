import tkinter as tk
import random
from paho.mqtt import client as mqtt_client

broker = '192.168.11.8'
port = -1

client_press_id = f'python-mqtt-{random.randint(0, 1000)}'
client_release_id = f'python-mqtt-{random.randint(0, 1000)}'
pressed = set()


def connect_mqtt(client_id):
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(
        client_id=client_id,
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client, topic, func):
    def on_message(client, userdata, msg):
        decoded = msg.payload.decode()
        print(f"Received `{decoded}` from `{msg.topic}` topic")
        func(decoded)

    client.subscribe(topic)
    client.on_message = on_message


class KeyDisplayApp:
    def __init__(self, root, client_press, client_release):
        self.root = root
        self.root.title("Pressed Keys Display")
        self.label = tk.Label(root, text="Pressed: None", font=("Helvetica", 20), bg="#1e1e1e", fg="white")
        self.label.pack(padx=20, pady=60, fill='both', expand=True)

        def press(msg):
            print("press", pressed, msg)
            pressed.add(msg)
            self.update_label()
            print("press", pressed, msg)

        def release(msg):
            print("release", pressed, msg)
            pressed.discard(msg)
            self.update_label()
            print("release", pressed, msg)

        subscribe(client_press, "test/pressed", func=press)
        subscribe(client_release, "test/released", func=release)

        self.update_label()

    def update_label(self):
        if pressed:
            sorted_keys = sorted(pressed)
            join_keys = ", ".join(sorted_keys)
            text = "Pressed: " + join_keys
        else:
            text = "Pressed: None"
        self.label.config(text=text)


if __name__ == '__main__':
    client_press = connect_mqtt(client_press_id)
    client_release = connect_mqtt(client_release_id)
    client_press.loop_start()
    client_release.loop_start()

    root = tk.Tk()
    root.geometry("640x480")
    app = KeyDisplayApp(root, client_press, client_release)
    root.mainloop()
