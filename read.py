# python 3.6 https://qiita.com/emqx_japan/items/b63c918fe137a6db4b37

import random
import pygame

from paho.mqtt import client as mqtt_client

broker = '192.168.11.8'
port = -1
test_topic = "python/mqtt"
# generate client ID with pub prefix randomly
client_press_id = f'python-mqtt-{random.randint(0, 1000)}'
client_release_id = f'python-mqtt-{random.randint(0, 1000)}'
# username = 'user'
# password = 'pass'
pressed = set()
WIDTH, HEIGHT = 640, 480
# 初期化
pygame.init()
font = pygame.font.Font(None, 36)


def connect_mqtt(client_id):
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(
        client_id=client_id,
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client, topic, func) -> None:
    def on_message(client, userdata, msg):
        decoded = msg.payload.decode()
        print(f"Received `{decoded}` from `{msg.topic}` topic")
        func(decoded)

    client.subscribe(topic)
    client.on_message = on_message


def subscribe_test(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(test_topic)
    client.on_message = on_message


def flip_pygame(screen):
    screen.fill((30, 30, 30))
    if pressed:
        sorted_key = sorted(pressed)
        join_key = ", ".join(sorted_key)
        text = "Pressed: " + join_key
    else:
        text = "Pressed: None"
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (20, HEIGHT // 2 - 20))
    pygame.display.flip()


def create_screen(client_press, client_release):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pressed Keys Display")

    def press(msg):
        print("press", pressed, msg)
        pressed.add(msg)
        flip_pygame(screen)
        print("press", pressed, msg)

    def release(msg):
        print("release", pressed, msg)
        pressed.discard(msg)
        flip_pygame(screen)
        print("release", pressed, msg)
    subscribe(client_press, "test/pressed", func=press)
    subscribe(client_release, "test/released", func=release)
    flip_pygame(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()


if __name__ == '__main__':
    client_press = connect_mqtt(client_press_id)
    client_release = connect_mqtt(client_release_id)
    client_press.loop_start()
    client_release.loop_start()
    # subscribe_test(client)
    create_screen(client_press, client_release)
