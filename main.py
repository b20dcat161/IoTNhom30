import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
from kivy.uix.widget import Widget
import paho.mqtt.client as mqtt
import speech_recognition as sr

    
class LightApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        layout.background_color = (1,1,1, 0)
        layout.size = (10000, 10000)
        with layout.canvas.before:
            Color(0.2, 0.4, 0.6, 1) 
            self.rect = Rectangle(size=layout.size, pos=layout.pos)

        self.titleLabel=Label(text='Well come!', font_size = '24sp')
        self.titleLabel.color = (0,0,1,1)
        self.titleLabel.size_hint = (0.3,0.45)
        self.titleLabel.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        self.button1 = Button(text='Toggle Light')
        self.button1.background_color = (0,0,1,1)
        self.button1.size_hint=(0.2,0.1)
        self.button1.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.button1.bind(on_press=self.toggle_light)

        self.button2 = Button(text='Speach')
        self.button2.size_hint=(0.2,0.1)
        self.button2.background_color = (0,0,1,1)
        self.button2.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.button2.bind(on_release=self.start_listening)


        self.button3 = Button(text='Exit')
        self.button3.size_hint=(0.2,0.1)
        self.button3.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.button3.background_color = (0,0,1,1)
        self.button3.bind(on_press=self.exit_app)
        
        self.commandLabel = Label(text="Notification")
        self.commandLabel.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.commandLabel.background_color = (0,0,1,1)
        self.commandLabel.size_hint = (0.3,0.45)

        self.timeLabel = Label(text=f"")
        self.timeLabel.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.timeLabel.background_color = (0,0,1,1)
        self.timeLabel.size_hint = (0.3,0.45)

        layout.add_widget(self.titleLabel)
        layout.add_widget(self.button1)
        layout.add_widget(self.button2)
        layout.add_widget(self.button3)
        layout.add_widget(self.commandLabel)
        layout.add_widget(self.timeLabel)
        return layout

    def toggle_light(self, instance):
        if self.button1.text == 'Toggle Light':
            self.button1.text = 'Light is on'
            self.turn_on_light()
        else:
            self.button1.text = 'Toggle Light'
            self.turn_off_light()

    def turn_on_light(self):
        client = mqtt.Client()
        def on_connect(client, userdata, flags, rc):
            print("Connected to MQTT Broker")
            self.commandLabel.text= "Connected to MQTT Broker"
            client.subscribe("/PTIT_Test/at161/mqtt") 

        def on_message(client, userdata, msg):
            if msg.payload.decode() == "N":
                self.commandLabel.text= "Message: ON"
                print("Light is on")

        client.on_connect = on_connect
        client.on_message = on_message

        client.connect("broker.hivemq.com", 1883, 60)  # Kết nối đến MQTT Broker

        # Gửi yêu cầu bật đèn
        client.publish("/PTIT_Test/at161/mqtt", "N")

        client.loop_start()  # Bắt đầu vòng lặp để nhận thông điệp MQTT

    def turn_off_light(self):
        client = mqtt.Client()
        def on_connect(client, userdata, flags, rc):
            print("Connected to MQTT Broker")
            self.commandLabel.text= "Connected to MQTT Broker"
            client.subscribe("/PTIT_Test/at161/mqtt")
              # Đăng ký chủ đề để nhận trạng thái đèn

        def on_message(client, userdata, msg):
            if msg.payload.decode() == "F":
                self.commandLabel.text= f"Message: OFF"
                print("Light is off")

        client.on_connect = on_connect
        client.on_message = on_message

        client.connect("broker.hivemq.com", 1883, 60)  # Kết nối đến MQTT Broker

        # Gửi yêu cầu tắt đèn
        client.publish("/PTIT_Test/at161/mqtt", "F")

        client.loop_start()  # Bắt đầu vòng lặp để nhận thông điệp MQTT

    def start_listening(self, button):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("start")
            # engine = pyttsx3.init()
            # engine.say("I am listerning") 
            # engine.runAndWait()
            self.commandLabel.text = "Đang lắng nghe..."

            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            self.commandLabel.text = recognizer.recognize_google(audio,language='vi-VN')
            if self.commandLabel.text.lower() == "bật đèn":
                self.turn_on_light()
            if self.commandLabel.text.lower() == "tắt đèn":
                self.turn_off_light()
        except sr.UnknownValueError:
            self.commandLabel.text = "Không nhận dạng được giọng nói"
        except sr.RequestError as e:
            self.commandLabel.text = f"Lỗi trong quá trình nhận dạng giọng nói: {str(e)}"
      
    def exit_app(self, instance):
        self.stop()


if __name__ == '__main__':
    LightApp().run()

