# python 3.6 https://qiita.com/emqx_japan/items/b63c918fe137a6db4b37

import random
import pygame

from paho.mqtt import client as mqtt_client

broker = '192.168.11.8'
port = -1
test_topic = "python/mqtt"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
# username = 'user'
# password = 'pass'
pressed = []
WIDTH, HEIGHT = 640, 480
font = pygame.font.Font(None, 36)


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client, topic, func) -> None:
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        func(msg)

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


def create_screen():
    # 初期化
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pressed Keys Display")

    def press(msg):
        pressed.add(msg)
        flip_pygame(screen)

    def release(msg):
        pressed.discard(msg)
        flip_pygame(screen)
    subscribe(client, "test/pressed", func=press)
    subscribe(client, "test/released", func=release)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()


if __name__ == '__main__':
    client = connect_mqtt()
    client.loop_start()
    # subscribe_test(client)
    create_screen()
