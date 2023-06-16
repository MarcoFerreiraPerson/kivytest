import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.spinner import Spinner

import random
from paho.mqtt import client as mqtt_client

kivy.require('1.0.9')

broker = "12.1.52.180"
port = 5000
sub_topic = "Marco"

client_id = f'publish-{random.randint(0, 1000)}'

topics = {
    "GPT": "CHAT_GPT",
    "Bill": "bill",
    "Angela": "ANGELINA",
    "Annie": "Annie"
}


class MyApp(App):
    def build(self):
        self.width = Window.width
        self.height = Window.height
        Window.size = (self.width, self.height)
        Window.clearcolor = (65 / 255.0, 76 / 255.0, 80 / 255.0, 1)
        self.my_box = BoxLayout(orientation='vertical', spacing=10)

        self.name_spinner = Spinner(
            values=['GPT', 'Angela', 'Bill', 'Annie', 'Add Topic'],
            text='GPT',
            size_hint=(1, 0.09),
            font_size=38,
            background_color=(65 / 255, 76 / 255, 80 / 255, 0.5)
        )

        self.my_box.add_widget(self.name_spinner)

        self.scrollview = ScrollView(size_hint=(1, 0.7), do_scroll_x=False, bar_width=10)
        self.msg_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.msg_box.bind(minimum_height=self.msg_box.setter('height'))
        self.scrollview.add_widget(self.msg_box)
        self.my_box.add_widget(self.scrollview)

        self.spacer = Label(height=80, size_hint_y=None)
        self.msg_box.add_widget(self.spacer)

        self.lbl = Label(text='', halign='center', font_size=25, size_hint_y=None, height=50,
                         text_size=(self.width, None), valign='top')
        self.msg_box.add_widget(self.lbl, index=0)

        input_button_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))

        self.my_input = TextInput(hint_text='Enter your message...', multiline=True, size_hint=(0.8, 1.2), font_size=40,
                                  background_color=(65 / 255, 76 / 255, 80 / 255))
        input_button_box.add_widget(self.my_input)

        self.send_button = Button(text='Send', size_hint=(0.2, 1.2), background_color=(57 / 255, 172 / 255, 231 / 255))
        self.send_button.bind(on_release=self.publish)
        input_button_box.add_widget(self.send_button)

        self.my_box.add_widget(input_button_box)

        self.client = self.connect_mqtt()
        self.subscribe(self.client)

        self.client.loop_start()

        return self.my_box

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to server!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(client_id)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    def on_message(self, client, userdata, msg):
        Clock.schedule_once(lambda dt: self.add_message(f"\n{msg.payload.decode()}"))

    def subscribe(self, client: mqtt_client):
        client.subscribe(sub_topic)
        client.on_message = self.on_message

    def add_message(self, txt):
        self.spacer.height += 10
        self.lbl.text += "\n" + txt

    def publish(self, instance):
        global topic
        topic = self.name_spinner.text

        topic = topics.get(topic)

        msg = self.my_input.text

        if topic == "":
            return

        if topic == None:
            topics[msg] = msg
            self.name_spinner.values.insert(len(self.name_spinner.values) - 1, msg)
            self.my_input.text = ''
            return

        result = self.client.publish(topic, f'From {sub_topic}: {msg}')
        status = result[0]
        if status == 0:
            print(f"Send {msg} to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        self.add_message(f'\nMe: {msg}')
        self.my_input.text = ''


if __name__ == '__main__':
    MyApp().run()
