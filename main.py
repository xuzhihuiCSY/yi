from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'system')
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.audio import SoundLoader
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
import datetime
from kivy.uix.label import Label
from cnlunar import Lunar
import random
import os
from kivy.metrics import dp
import sys
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, PushMatrix, PopMatrix, Rotate, Rectangle
from kivy.core.text import Label as CoreLabel
from math import pi, sin, cos
from kivy.graphics import Triangle
from kivymd.uix.button import MDIconButton
from kivy.utils import platform
from kivy.uix.textinput import TextInput

class SpinningWheel(Widget):
    def __init__(self, items, **kwargs):
        super().__init__(**kwargs)
        self.items = items
        self.angle = 0
        self.is_spinning = False
        self.speed = 0

        self.colors = [
            (0.7, 0.9, 1, 1),
            (1, 0.7, 0.7, 1), 
            (0.7, 1, 0.7, 1),
            (1, 1, 0.7, 1),
            (0.9, 0.7, 1, 1),  
            (0.7, 1, 1, 1), 
            (0.8, 0.8, 1, 1),  
            (1, 0.8, 0.8, 1), 
            (0.8, 1, 0.8, 1), 
            (1, 1, 0.8, 1), 
            (0.85, 0.7, 1, 1),  
            (0.7, 0.85, 1, 1), 
            (0.95, 0.75, 0.75, 1), 
            (0.75, 0.95, 0.75, 1), 
            (0.75, 0.75, 0.95, 1), 
        ]
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()

        size = min(self.width, self.height)
        pos = (self.center_x - size / 2, self.center_y - size / 2)
        cx, cy = self.center

        with self.canvas:
            PushMatrix()
            Rotate(angle=self.angle+180, origin=self.center)

            if self.items:
                slice_angle = 360 / len(self.items)
                radius = size / 2
                for i in range(len(self.items)):
                    color = self.colors[i % len(self.colors)]
                    Color(*color)
                    angle_start = i * slice_angle
                    angle_end = (i + 1) * slice_angle
                    Ellipse(pos=pos, size=(size, size), angle_start=angle_start, angle_end=angle_end)

            PopMatrix()

        with self.canvas:
            pointer_size = 30
            cx, cy = self.center
            Color(0.3, 0.3, 0.3, 1)
            Triangle(points=[
                cx, cy + size / 2 - pointer_size,
                cx - pointer_size / 2, cy + size / 2 ,
                cx + pointer_size / 2, cy + size / 2
            ])

            if self.items:
                slice_angle = 360 / len(self.items)
                radius = size / 2

                for i, item in enumerate(self.items):
                    slice_angle = 360 / len(self.items)

                    text_angle = i * slice_angle + self.angle + slice_angle / 2 - 90

                    angle_rad = text_angle * pi / 180
                    x = cx + radius * 0.8 * cos(angle_rad)
                    y = cy + radius * 0.8 * sin(angle_rad)

                    label = CoreLabel(text=item, font_size=20, font_name=FONT_NAME, color=(0.3, 0.3, 0.3, 1))
                    label.refresh()
                    texture = label.texture
                    texture_size = list(texture.size)

                    # Color(1, 1, 1, 1)
                    Rectangle(texture=texture, pos=(x - texture_size[0]/2, y - texture_size[1]/2), size=texture_size)

    def start_spin(self):
        if not self.is_spinning:
            self.is_spinning = True
            self.speed = 80
            Clock.schedule_interval(self.spin_step, 1 / 60)

    def spin_step(self, dt):
        if self.speed > 0.01:
            self.angle += self.speed
            self.angle = self.angle % 360
            self.speed *= 0.98
            self.update_canvas()
        else:
            self.is_spinning = False
            Clock.unschedule(self.spin_step)
            self.angle = self.angle % 360

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

FONT_FILE = 'NotoSansSC-Black.ttf'
FONT_NAME = 'NotoSansSC'
font_path = resource_path(FONT_FILE)

if not os.path.exists(font_path):
    raise FileNotFoundError(f"字体文件 '{FONT_FILE}' 未找到，请确保它与main.py在同一目录")

LabelBase.register(name=FONT_NAME, fn_regular=font_path)

KV = f'''
MDScreen:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(32)
        pos_hint: {{'center_x': 0.5, 'center_y': 0.5}}
        size_hint: 0.8, None
        height: self.minimum_height

        MDLabel:
            text: '[b][size=32sp]易经摇卦[/size][/b]'
            markup: True
            halign: 'center'
            font_style: 'H4'
            font_name: '{FONT_NAME}'
            size_hint_y: None
            height: self.texture_size[1]

        MDRaisedButton:
            text: '今日历法'
            font_name: '{FONT_NAME}'
            pos_hint: {{'center_x': 0.5}}
            size_hint: (1, None)
            height: dp(48)
            on_release: app.show_calendar_info()

        MDRaisedButton:
            text: '开始摇卦'
            font_name: '{FONT_NAME}'
            pos_hint: {{'center_x': 0.5}}
            size_hint: (1, None)
            height: dp(52)
            on_release: app.start_divination()

        MDRaisedButton:
            text: '选择转盘'
            font_name: '{FONT_NAME}'
            pos_hint: {{'center_x': 0.5}}
            size_hint: (1, None)
            height: dp(56)
            on_release: app.show_wheel_popup()

        MDRaisedButton:
            text: '电子木鱼'
            font_name: '{FONT_NAME}'
            pos_hint: {{'center_x': 0.5}}
            size_hint: (1, None)
            height: dp(60)
            on_release: app.show_muyu_popup()
        
'''

class DivinationApp(MDApp):
    def build(self):
        self.icon = "yy.png"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.font_styles.update({
            "H1": [FONT_NAME, 96, False, -1.5],
            "H2": [FONT_NAME, 60, False, -0.5],
            "H3": [FONT_NAME, 48, False, 0],
            "H4": [FONT_NAME, 34, False, 0.25],
            "H5": [FONT_NAME, 24, False, 0],
            "H6": [FONT_NAME, 20, False, 0.15],
            "Subtitle1": [FONT_NAME, 16, False, 0.15],
            "Subtitle2": [FONT_NAME, 14, False, 0.1],
            "Body1": [FONT_NAME, 16, False, 0.5],
            "Body2": [FONT_NAME, 14, False, 0.25],
            "Button": [FONT_NAME, 14, True, 1.25],
            "Caption": [FONT_NAME, 12, False, 0.4],
            "Overline": [FONT_NAME, 10, True, 1.5],
            "Icon": ["Icons", 24, False, 0],
        })
        return Builder.load_string(KV)
    
    def show_wheel_popup(self):
        from kivy.uix.boxlayout import BoxLayout
        wheel = SpinningWheel(items=[], size_hint=(None, None), size=(680, 680))
        self.wheel = wheel

        wheel_outer_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=600,
            padding=(0, 0, 0, 0),
            spacing=0
        )
        wheel_outer_box.add_widget(Widget(size_hint_x=1))
        wheel_outer_box.add_widget(wheel)
        wheel_outer_box.add_widget(Widget(size_hint_x=1))

        input_box = MDBoxLayout(
            orientation="horizontal",
            spacing="8dp",
            size_hint_y=None,
            height="56dp"
        )

        input_wrapper = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height="56dp",
            padding=[0, 4]
        )

        self.item_input = TextInput(
            hint_text="请输入内容(暂不支持中文输入)",
            font_name=FONT_NAME,
            font_size="22sp",
            padding=(10, 14),
            background_normal='',
            background_active='',
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0.1, 0.5, 0.9, 1),
            size_hint=(1, None),
            height="50dp",
            multiline=False
        )

        input_wrapper.add_widget(self.item_input)

        add_button = MDRaisedButton(
            text="添加",
            font_name=FONT_NAME,
            size_hint_y=None,
            height="48dp",
            pos_hint={"center_y": 0.5}
        )

        input_box.add_widget(input_wrapper)
        input_box.add_widget(add_button)

        self.item_list = MDBoxLayout(
            orientation="vertical",
            spacing="8dp",
            size_hint_y=None
        )
        self.item_list.bind(minimum_height=self.item_list.setter('height'))

        scroll = ScrollView(size_hint=(1, None), height="150dp")
        scroll.add_widget(self.item_list)

        content = MDBoxLayout(
            orientation="vertical",
            padding="5dp",
            spacing="5dp",
            size_hint_y=None
        )

        content.add_widget(wheel_outer_box)
        content.add_widget(input_box)
        content.add_widget(scroll)

        spin_button = MDRaisedButton(
            text="开始转盘",
            font_name=FONT_NAME,
            pos_hint={"center_x": 0.5}
        )
        spin_button.bind(on_release=lambda x: wheel.start_spin())
        content.add_widget(spin_button)

        content.bind(minimum_height=content.setter('height'))

        # --- Input logic ---
        def add_item(instance):
            text = self.item_input.text.strip()
            if text:
                item_box = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height="40dp",
                    padding=("8dp", "0dp"),
                    spacing="8dp"
                )

                label = MDLabel(
                    text=f"[font={FONT_NAME}]{text}[/font]",
                    markup=True,
                    font_name=FONT_NAME,
                    size_hint_x=0.7,
                    halign="left",
                    valign="center"
                )

                delete_button = MDIconButton(
                    icon="delete",
                    theme_text_color="Custom",
                    text_color=(1, 0.3, 0.3, 0.8),
                    size_hint_x=None,
                    width="40dp"
                )

                item_box.add_widget(label)
                item_box.add_widget(delete_button)

                self.item_list.add_widget(item_box)

                self.wheel.items.append(text)
                self.wheel.update_canvas()

                self.item_input.text = ""

                def delete_item(btn_instance):
                    if text in self.wheel.items:
                        self.wheel.items.remove(text)
                        self.wheel.update_canvas()

                    self.item_list.remove_widget(item_box)

                delete_button.bind(on_release=delete_item)

        add_button.bind(on_release=add_item)

        self.wheel_dialog = MDDialog(
            title="[font={}]选择转盘[/font]".format(FONT_NAME),
            type="custom",
            content_cls=content,
            auto_dismiss=True,
            size_hint=(0.9, None),
            height="700dp",
            buttons=[
                MDRaisedButton(
                    text="关闭",
                    font_name=FONT_NAME,
                    on_release=lambda x: self.wheel_dialog.dismiss()
                )
            ],
            md_bg_color=self.theme_cls.bg_normal
        )
        self.wheel_dialog.open()


    def show_muyu_popup(self):
        # Load sound once
        if not hasattr(self, 'muyu_sound'):
            self.muyu_sound = SoundLoader.load(resource_path("muyu.mp3"))

        class TappableImage(ButtonBehavior, Image):
            pass

        # Create the image
        image = TappableImage(
            source=resource_path("muyu.png"),
            size_hint=(None, None),
            size=(dp(200), dp(200)),
            pos_hint={"center_x": 0.5}
        )

        def on_tap(*args):
            anim = (
                Animation(size=(dp(220), dp(220)), duration=0.1) +
                Animation(size=(dp(200), dp(200)), duration=0.1)
            )
            anim.start(image)

            if self.muyu_sound:
                self.muyu_sound.stop()
                self.muyu_sound.play()

            pos_choice = random.choice([
                ("left", image.center_x - dp(130)),
                ("center", image.center_x - dp(50)),
                ("right", image.center_x - dp(-30)),
            ])

            alignment, start_x = pos_choice

            popup_label = Label(
                text="功德+1",
                font_name=FONT_NAME,
                font_size="20sp",
                color=(1, 1, 1, 1),
                bold=True,
                size_hint=(None, None),
                size=(dp(100), dp(30)),
                pos=(start_x, image.top - dp(30)),
                opacity=1
            )

            # Just add label directly, no rotation
            image_wrapper.add_widget(popup_label)

            # Animate floating up and fading out
            float_anim = Animation(
                y=popup_label.y + dp(80),
                opacity=0,
                duration=1.5
            )

            def remove_label(*args):
                if popup_label.parent:
                    popup_label.parent.remove_widget(popup_label)

            float_anim.bind(on_complete=remove_label)
            float_anim.start(popup_label)


        image.bind(on_release=on_tap)

        image_wrapper = FloatLayout(
            size_hint=(1, None),
            height=dp(200),
        )
        image.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        image_wrapper.add_widget(image)

        # Outer vertical layout
        content = MDBoxLayout(
            orientation="vertical",
            padding="16dp",
            spacing="16dp",
            size_hint_y=None,
            height="280dp"
        )
        content.add_widget(image_wrapper)

        # Dialog
        self.muyu_dialog = MDDialog(
            title="[font={}][color=FFFFFF][b]电子木鱼[/b][/color][/font]".format(FONT_NAME),
            type="custom",
            content_cls=content,
            auto_dismiss=True,
            buttons=[
                MDRaisedButton(
                    text="关闭",
                    font_name=FONT_NAME,
                    on_release=lambda x: self.muyu_dialog.dismiss()
                )
            ],
            size_hint=(0.8, None),
            height="420dp",
            md_bg_color=[0, 0, 0, 1],
        )
        self.muyu_dialog.open()


    def show_calendar_info(self):
        now = datetime.datetime.now()
        lunar = Lunar(now)

        def safe_text(value):
            if isinstance(value, list):
                value = "、".join(value)
            if isinstance(value, str):
                return value.replace('[', '【').replace(']', '】')
            return str(value)

        # Data preparation
        solar_date = now.strftime("%Y-%m-%d")
        lunar_date = f"{lunar.lunarYear}年{lunar.lunarMonth}月{lunar.lunarDay}日"
        ganzhi = f"{lunar.year8Char}年 {lunar.month8Char}月 {lunar.day8Char}日"
        jieqi = lunar.todaySolarTerms or "无"
        good_god = safe_text(lunar.goodGodName)
        bad_god = safe_text(lunar.badGodName)
        yi = safe_text(lunar.goodThing)
        ji = safe_text(lunar.badThing)
        starZodiac = safe_text(lunar.starZodiac)
        pengzu_full = safe_text(lunar.get_pengTaboo())
        lucky_direction = safe_text(lunar.get_luckyGodsDirection())
        chineseZodiacClash = safe_text(lunar.get_chineseZodiacClash())
        luckyhour = lunar.get_twohourLuckyList()
        CharList = lunar.twohour8CharList

        # Step 1: Make the full text
        text = f"[font={FONT_NAME}][size=18sp][b]今日信息[/b][/size][/font]\n\n"
        text += f"[font={FONT_NAME}][size=16sp]阳历：{solar_date}\n农历：{lunar_date}\n干支：{ganzhi}\n"
        if jieqi != '无':
            text += f"节气：{jieqi}\n"
        text += f"生肖冲煞：{chineseZodiacClash}\n"
        text += f"星座：{starZodiac}[/size][/font]\n\n"

        text += f"[font={FONT_NAME}][size=18sp][b]吉神凶煞[/b][/size][/font]\n\n"
        text += f"[font={FONT_NAME}][size=16sp]吉神：{good_god}\n凶煞：{bad_god}\n吉神方位：{lucky_direction}[/size][/font]\n\n"

        text += f"[font={FONT_NAME}][size=18sp][b]宜忌事项[/b][/size][/font]\n\n"
        text += f"[font={FONT_NAME}][size=16sp]宜：{yi}\n忌：{ji}[/size][/font]\n\n"

        text += f"[font={FONT_NAME}][size=18sp][b]彭祖百忌[/b][/size][/font]\n\n"
        text += f"[font={FONT_NAME}][size=16sp]{pengzu_full}[/size][/font]\n\n"

        # Step 2: Create scrollable layout inside ScrollView
        scroll_content = MDBoxLayout(
            orientation="vertical",
            padding="8dp",
            spacing="8dp",
            size_hint_y=None,
        )

        # Add the main text label
        label = MDLabel(
            text=text,
            markup=True,
            font_name=FONT_NAME,
            halign="left",
            valign="top",
            size_hint_x=1,
            size_hint_y=None,
        )
        label.bind(texture_size=lambda instance, value: setattr(label, 'height', value[1]))
        scroll_content.add_widget(label)

        # 1. Table title
        table_title = MDLabel(
            text=f"[font={FONT_NAME}][size=18sp][b]今日时辰吉凶[/b][/size][/font]",
            markup=True,
            font_name=FONT_NAME,
            halign="center",
            valign="middle",
            size_hint_x=1,
            size_hint_y=None,
            height="40dp"
        )
        scroll_content.add_widget(table_title)

        # 2. Header row (MDBoxLayout with background)
        header_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="36dp",
            md_bg_color=[0.85, 0.85, 0.85, 1],  # Light gray background
        )
        header_box.add_widget(MDLabel(
            text="[b]时辰[/b]",
            markup=True,
            font_name=FONT_NAME,
            halign="center",
            valign="middle",
        ))
        header_box.add_widget(MDLabel(
            text="[b]吉/凶[/b]",
            markup=True,
            font_name=FONT_NAME,
            halign="center",
            valign="middle",
        ))
        scroll_content.add_widget(header_box)

        # 4. Data rows with row striping
        for index, (char, luck) in enumerate(zip(CharList, luckyhour)):
            row_bg_color = [1, 1, 1, 1] if index % 2 == 0 else [0.95, 0.95, 0.95, 1]

            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height="30dp",
                md_bg_color=row_bg_color,
            )
            row.add_widget(MDLabel(
                text=safe_text(char),
                markup=True,
                font_name=FONT_NAME,
                halign="center",
                valign="middle",
            ))
            row.add_widget(MDLabel(
                text=safe_text(luck),
                markup=True,
                font_name=FONT_NAME,
                halign="center",
                valign="middle",
            ))
            scroll_content.add_widget(row)

        # Important: bind scroll_content minimum_height
        scroll_content.bind(minimum_height=scroll_content.setter('height'))

        # Step 3: Wrap into ScrollView
        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False
        )
        scroll.add_widget(scroll_content)
        
        # Step 4: Add scroll into a simple container box
        container = MDBoxLayout(
            orientation="vertical",
            padding="8dp",
            spacing="8dp",
            size_hint=(1, None),
            height=600
        )
        container.add_widget(scroll)

        # Step 5: Create and open Dialog
        self.calendar_dialog = MDDialog(
            title=f"[font={FONT_NAME}]今日历法[/font]",
            type="custom",
            content_cls=container,
            size_hint=(0.9, None),
            height="700dp",
            auto_dismiss=True,
            buttons=[
                MDRaisedButton(
                    text="确定",
                    font_name=FONT_NAME,
                    on_release=lambda x: self.calendar_dialog.dismiss()
                )
            ],
            md_bg_color=self.theme_cls.bg_normal,
        )
        self.calendar_dialog.open()

    def start_divination(self):
        self.reset()
        self.lines = []
        self.current_line = 0

        # Layout
        content = MDBoxLayout(
            orientation="vertical",
            padding="24dp",
            spacing="16dp",
            size_hint_y=None,
        )

        # Static Title
        self.title_label = MDLabel(
            text="[b][size=22sp]正在摇卦，请稍候[/size][/b]",
            markup=True,
            font_name=FONT_NAME,
            halign="center",
            size_hint_y=None,
            height="48dp",
        )
        content.add_widget(self.title_label)

        # Line Label
        self.line_label = MDLabel(
            text="[size=18sp]准备开始...[/size]",
            markup=True,
            font_name=FONT_NAME,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height="150dp",
        )
        content.add_widget(self.line_label)

        # Progress Bar
        from kivymd.uix.progressbar import MDProgressBar
        self.progress_bar = MDProgressBar(
            value=0,
            max=6,
            size_hint_y=None,
            height="6dp",
        )
        content.add_widget(self.progress_bar)

        content.bind(minimum_height=content.setter('height'))

        # Dialog
        self.line_dialog = MDDialog(
            title="[font={}]摇卦中...[/font]".format(FONT_NAME),
            type="custom",
            content_cls=content,
            size_hint=(0.8, None),
            height="480dp",
            auto_dismiss=False,
            md_bg_color=self.theme_cls.bg_normal,
        )
        self.line_dialog.open()

        # Start generating lines
        Clock.schedule_interval(self.generate_line, 0.7)

    def generate_line(self, dt):
        if self.current_line < 6:
            line = self.get_line()
            self.lines.append(line)

            # Directly update without flashing
            self.line_label.text = (
                f'[font={FONT_NAME}][b][size=20sp]正在摇第 {self.current_line + 1} 爻[/size][/b]\n\n'
                f'[size=16sp][b]当前卦象:[/b] {"".join(self.lines)}[/size][/font]'
            )
            self.line_label.markup = True

            # Update progress bar
            self.progress_bar.value = self.current_line + 1

            self.current_line += 1
        else:
            Clock.unschedule(self.generate_line)
            self.line_dialog.dismiss()
            self.show_result()

    @staticmethod
    def get_line():
        coins = [random.choice([2, 3]) for _ in range(3)]
        total = sum(coins)
        if total == 6:
            return 'x'  # 老阴
        elif total == 7:
            return 'o'  # 少阳
        elif total == 8:
            return 'x'  # 少阴
        elif total == 9:
            return 'o'  # 老阳

    def show_result(self):
        gua = ''.join(self.lines)
        explanation, fortune = self.get_explanation(gua)

        if explanation == '暂无解释。':
            text = f'[font={FONT_NAME}][b]卦象:[/b] {gua}\n[b]解释:[/b] 暂无解释。[/font]'
        else:
            text = (
                f'[font={FONT_NAME}][b]卦象:[/b] {gua}\n\n'
                f'[size=20sp][b]运势:[/b] {fortune}\n'
                f'[size=16sp]{explanation}[/size][/font]'
            )

        content = MDBoxLayout(orientation="vertical", padding="18dp", spacing="10dp", size_hint_y=None)
        content_label = MDLabel(
            text=text,
            markup=True,
            font_name=FONT_NAME,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=400
        )
        content.add_widget(content_label)
        content.bind(minimum_height=content.setter('height'))

        self.result_dialog = MDDialog(
            title="[font={}]摇卦结果[/font]".format(FONT_NAME),
            type="custom",
            content_cls=content,
            size_hint=(0.85, None),
            height="520dp",
            auto_dismiss=True,
            buttons=[
                MDRaisedButton(
                    text="确定",
                    font_name=FONT_NAME,
                    on_release=lambda x: self.result_dialog.dismiss()
                )
            ],
            md_bg_color=self.theme_cls.bg_normal
        )
        self.result_dialog.open()

    def get_explanation(self, gua):
        explanations = {
            # 乾宫八卦（属金）
            'xxxxxx': ('乾为天：元亨利贞。\n困龙得水好运交，不由喜气上眉梢。\n一切谋望皆如意，向后时运渐渐高。\n\n词讼和吉，病人痊愈，功名有成，求名大吉。', '大吉'),
            'xxxxxo': ('天风姤：他乡遇友喜气欢，须知运气福重添。\n自今交了顺当运，向从保管不相干。\n\n家宅平安，占病无妨，功名有成，失物得见。', '中吉'),
            'xxxxoo': ('天山遯：浓云蔽日不光明，劝君切莫远出行。\n婚姻求财皆不利，提防口舌到门庭。\n\n讼事见官，占病不安，功名不成，事不遂心。', '凶'),
            'xxxooo': ('天地否：虎落陷坑不堪言，近前容易退后难。\n谋望不遂自己意，疾病口舌有牵连。\n\n占财不成，贵人远行，出行不易，事事晚成。', '半凶'),
            'xxoooo': ('风地观：鹊遇天晚睡林中，不知林中先有鹳。\n虽然同处心生恶，卦若逢之祸非轻。\n\n先难后易，谋事不易，交节过令，忧愁变喜。', '末吉'),
            'xooooo': ('山地剥：花遇甘露旱逢河，生意买卖利息多。\n婚姻自有人来助，出门永不受折磨。\n\n占讼得利，占病即愈，占信得见，谋事即成。', '中吉'),
            'xoxooo': ('火地晋：锄地除去苗里草，谁想财帛将人找。\n谋望求财皆如意，这个运气也算好。\n\n进退两难，不敢强办，拨云见日，该你出现。', '小吉'),
            'xoxxxx': ('火天大有：砍树摸雀做事牢，是非口舌自然消。\n婚姻合伙不费力，若问过失未脱逃。\n\n恍惚不做，拿稳下手，若求名利，到处自有。', '大吉'),

            # 坎宫八卦（属水）
            'oxooxo': ('坎为水：一轮明月照水中，只见影儿不见踪。\n愚人当真下去取，摸来摸去一场空。\n\n婚姻不成，疾病不愈，求名不遂，合伙不利。', '凶'),
            'oxoxox': ('水火既济：金榜之上提姓名，不负当年苦用功。\n人逢此卦多吉庆，一切谋望大享通。\n\n月令吉善，找人寻见，丢失能找，口舌消散。', '大吉'),
            'oxooxx': ('水泽节：时来运转喜气生，灯台封神姜太公。\n到此诸神皆退位，纵然有祸不成凶。\n\n月令高强，声名大扬，走失有信，官事不妨。', '中吉'),
            'oxooox': ('水雷屯：风刮乱丝不见头，颠三倒四犯忧愁。\n慢促款来头有绪，急促反若不自由。\n\n疾病未好，婚姻不巧，口舌琐碎，做事颠倒。', '半凶'),
            'oxxxox': ('泽火革：苗逢旱天渐渐衰，幸得天恩降雨来。\n忧去喜来能变化，求谋诸事遂心怀。\n\n出门大吉，走失能找，行人来信，百般凑巧。', '中吉'),
            'ooxxox': ('雷火丰：古镜昏暗好几年，一朝磨明似月圆。\n君子谋事占此卦，时来运转乐自然。\n\n出行有益，疾病见好，交易得利，求名大吉。', '小吉'),
            'oooxox': ('地火明夷：时乖运拙走不着，急忙过河拆了桥。\n恩人无义反成怨，凡事无功反受劳。\n\n行人未至，头绪不准，口舌紧避，凡事小心。', '末凶'),
            'ooooxo': ('地水师：将军领旨去出征，骑着烈马拉硬弓。\n百步穿杨射的准，箭射金钱喜气生。\n\n疾病大好，走失能找，游子有信，运气真巧。', '吉'),

            'xooxoo': ('艮为山：财帛常打心中走，可惜眼前难倒手。\n不如一时且忍耐，遇到闲事休开口。\n\n好事难成，走失难寻，凡是忍耐，交节安宁。', '末吉'),  # 修正编码为 xooxoo
            'xooxox': ('山火贲：时来运转锐气有，窈窕淑女君子求。\n钟鼓乐声大吉庆，占得此卦喜临头。\n\n出门吉祥，诸事顺当，失物得见，月令高强。', '中吉'),
            'xooxxx': ('山天大畜：忧愁常锁两眉尖，千头万绪挂心间。\n从今以后打开阵，任意而行不相干。\n\n交节换运，出门大吉，好运有信，百事和顺。', '吉'),  # 修正编码为 xooxxx
            'xoooxx': ('山泽损：时运不至费心多，比作推车受折磨。\n山路崎岖掉了耳，左插右安安不着。\n\n时运不遂，不可胡为，交节换月，自然夺魁。', '半吉'),  # 修正编码为 xoooxx
            'xoxoxx': ('火泽睽：路上行人色匆匆，过河无桥遇薄冰。\n小心谨慎过得去，一步错了落水中。\n\n薄冰甚险，行人难禁，若占此卦，凡事小心。', '末凶'),
            'xxxoxx': ('天泽履：俊鸟幸得出笼中，脱离灾难显威风。\n一朝得志凌云去，东西南北任意行。\n\n合伙生意，买卖兴旺，迁移如意，求财十分。', '大吉'),
            'xxooxx': ('风泽中孚：此卦占之运气歹，如同太公做买卖。\n贩猪羊快贩牛迟，牛羊齐贩断了宰。\n\n占名不利，疾病不愈，不利不食，做事更难。', '凶'),  # 修正编码为 xxooxx
            'xxoxoo': ('风山渐：凤凰落在西岐山，长鸣几声出圣贤。\n天降文王开基业，富贵荣华八百年。\n\n出门有益，诸事平安，求财必准，疾病皆除。', '大吉'),

            # 震宫八卦（属木）
            'ooxoox': ('震为雷：占者逢之撞金钟，时来运转响一声。\n谋事求财不费力，交易和伙大享通。\n\n求名遂意，作事遂心，行人失信，自然有音。', '中吉'),
            'ooxooo': ('雷地豫：青龙得意喜气生，谋望求财事有成。\n婚姻出行无阻隔，是非口舌得安宁。\n\n交易既成，行人即归，头绪有准，合伙有利。', '吉'),
            'ooxoxo': ('雷水解：五关脱难运头抬，劝君须当把财求。\n交易出行有人助，疾病口舌不用愁。\n\n疾病大好，行人来早，谋望求全，诸般凑巧。', '小吉'),
            'ooxxxo': ('雷风恒：鱼来撞网乐自然，挂占行人不久还。\n交易婚姻两成就，谋望求财不费难。\n\n出行凑巧，有病就好，虽有口舌，自然消了。', '吉'),
            'oooxxo': ('地风升：指日高升气象新，走失行人有音信。\n功名出行遂心好，疾病口舌皆除根。\n\n求财到手，谋事可成，寻人得见，家宅安宁。', '中吉'),
            'oxoxxo': ('水风井：枯井破了以多年，一朝流泉出水鲜。\n滋生解渴人称羡，时来运转乐自然。\n\n精神渐爽，福禄日增，出入皆吉，百事享通。', '吉'),
            'oxxxxo': ('泽风大过：夜梦金银醒来空，求名求利大不通。\n婚姻难成交易散，走失行人不见踪。\n\n凡是忍耐，好事难谋，休要琢磨，月令不合。', '凶'),
            'oxxoox': ('泽雷随：推车靠崖道路干，谋望求财不费难。\n婚姻出行无阻隔，疾病口舌得平安。\n\n苦极生荣，喜气盈盈，一切做事，大运享通。', '大吉'),

            # 巽宫八卦（属木）
            'xxoxxo': ('巽为风：孤舟得水离滩沙，出外行人早回家。\n是非口舌皆无碍，婚姻合伙更不差。\n\n功名称意，求财得利，交易可成，疾病全去。', '吉'),
            'xxoxxx': ('风天小畜：浓云密排下雨难，盼望行人不见还。\n交易出行空费力，婚姻求谋是枉然。\n\n疾病口舌，交节安宁，忍耐从容，月令中平。', '末吉'),
            'xxoxox': ('风火家人：镜里观花休认真，求望谋财不遂心。\n交易不成婚姻散，走失行人无音信。\n\n找人不遇，疾病不愈，求名不准，官事不利。', '半凶'),
            'xxooox': ('风雷益：时来运转吉气发，多年枯木又开花。\n枝叶重生多茂盛，人人见了人人夸。\n\n交易有成，见官有理，走失得见，出门见喜。', '中吉'),
            'xxxoox': ('天雷无妄：鸟入笼中难出头，占得此卦不自由。\n谋望求财不定准，疾病忧烦口舌愁。\n\n出门不遇，求财不利，婚姻走失，疾病不易宜。', '凶'),
            'xoxoox': ('火雷噬嗑：运拙如同身受饥，幸得送饭又遇食。\n适口充肠心欢喜，忧愁从此渐消移。\n\n出门见喜，见官有理，婚姻成全，诸事如意。', '小吉'),
            'xooxox': ('山雷颐：文王访贤在渭滨，谋望求财事遂心。\n交易出行方如意，疾病口舌可以离去。\n\n出门吉祥，诸事顺当，失物得见，月令高强。', '中吉'),
            'xooxxo': ('山风蛊：卦中爻象如推磨，顺当为福反为祸。\n心中有意事改变，凡事尽从忙里错。\n\n出行无益，行人未回，走失难见，诸事莫为。', '末凶'),

            # 离宫八卦（属火）
            'xoxxox': ('离为火：灾消卦者遇天官，福禄必然降人间。\n一切谋望皆吉庆，愁闲消散主平安。\n\n出门见喜，诸事方便，灾消病散，月令吉善。', '大吉'),
            'xoxxoo': ('火山旅：飞鸟树上垒高巢，小人使计用火烧。\n如占此卦大不利，一切谋望枉徒劳。\n\n求助费力，行人未还，走失无信，找事也难。', '凶'),
            'xoxxxo': ('火风鼎：若占此卦喜自然，求名得利而周全。\n婚姻和伙皆如意，生意兴隆乐自然。\n\n出门有益，诸事安宁，官事无妨，交易可成。', '吉'),
            'xoxoxo': ('火水未济：太岁入运事事愁，婚姻财帛莫强求。\n交易出门未见吉，走失行人未露头。\n\n官讼不利，口舌有灾，目下忍耐，官事无妨。', '半凶'),
            'xoooxo': ('山水蒙：卦中气豪犯小耗，谋望求财枉徒劳。\n钟鼓乐声大吉庆，占得此卦喜临头。\n\n为人仔细，挣钱费力，有心好学，难得开去。', '末吉'),
            'xxooxo': ('风水涣：隔河望见一锭金，想取河宽水又深。\n指望钱财难到手，昼思夜想枉费心。\n\n婚姻不济，合伙不利，交易出行，总不如意。', '半凶'),
            'xxxoxo': ('天水讼：两人争路未肯让，占得此卦费主张。\n交易出行有阻隔，生意合伙也平常。\n\n好事难成，求财费力，光生闲气，月令不济。', '末凶'),
            'xxxxox': ('天火同人：仙人指路遇路通，劝君任意走西东。\n交易求财不费力，生意合伙也相通。\n\n婚姻有成，行人回来，走失得见，做事无差。', '大吉'),

            # 坤宫八卦（属土）
            'oooooo': ('坤为地：饥虑得食甚喜欢，求名应试主高迁。\n出门吉利行人到，是非口舌不相干。\n\n寻人可见，走失有信，疾病见好，凡事皆顺。', '大吉'),
            'ooooox': ('地雷复：若占此卦不相合，忧疑愁闲无定夺。\n恩人无义反成怨，是非平地起风波。\n\n寻人不见，心事不定，交节换月，自然安宁。', '半凶'),
            'ooooxx': ('地泽临：发政施仁志量高，走失行人有信号。\n婚姻交易大有志，出外求财任逍遥。\n\n口舌消散，疾病即愈，家宅平安，求名称意。', '吉'),
            'oooxxx': ('地天泰：喜极三元运气强，谋望求财大吉祥。\n交易出行多得意，是非口舌总无妨。\n\n婚姻有成，行人即至，失物可寻，诸般凑巧。', '大吉'),
            'ooxxxx': ('雷天大壮：卦占工师得大木，眼前该着走上路。\n时来运转多顺当，有事只管放心作。\n\n出门吉利，口舌远避，疾病皆除，行人即至。', '中吉'),
            'oxxxxx': ('泽天夬：游蜂脱网喜无边，添财进口福禄连。\n外则通达内则顺，富贵荣华胜以前。\n\n讼事了解，疾病除根，求财如意，诸事遂心。', '大吉'),
            'oxoxxx': ('水天需：明珠土埋日久深，无光无亮到土中。\n忽然大风吹去土，自然显露又放光。\n\n深谋有成，婚姻撮合，求财如意，随意喜动。', '吉'),
            'oxoooo': ('水地比：顺风行船撒起棚，上天之功一篷风。\n不用费力逍遥去，任意而行大享通。\n\n走失可寻，见官有理，婚姻求名，保管恭喜。', '中吉'),

            # 兑宫八卦（属金）
            'oxxoxx': ('兑为泽：这个卦象真有趣，觉得做事不费力。\n休要错过这机关，事事就觉遂心意。\n\n口舌消散，疾病痊愈，求财到手，谋事遂意。', '大吉'),
            'oxxoxo': ('泽水困：时运不来有人欺，千方百计与商议。\n明明与你说好话，撮上杆去抽了梯。\n\n当交君子，莫近小人，凡是小心，永不受穷。', '半凶'),
            'oxxooo': ('泽地萃：鲤鱼化龙喜气来，口舌疾病永无灾。\n愁疑从此都消散，祸门闭来福门开。\n\n鲤鱼化龙，喜气重重，求财到手，做事有功。', '吉'),
            'oxxxoo': ('泽山咸：脚踏棒槌转悠悠，时运不来莫强求。\n幸喜今日时运转，自有好事在后头。\n\n谋望看成，出门可行，走失来信，疾病安宁。', '小吉'),
            'oxoxoo': ('水山蹇：大雨倾地雪满天，路上行人苦又难。\n拖泥带水费尽力，事不遂心且忍耐。\n\n行人未至，投向无门，好事难成，求名无功。', '末凶'),
            'oooxoo': ('地山谦：天赐贫人一封金，不用争竞二人分。\n彼此分得金到手，一切谋望皆遂心。\n\n婚姻遂意，出外得地，交易合伙，事事顺心。', '中吉'),
            'ooxxoo': ('雷山小过：行人路过独木桥，心内惶恐眼内焦。\n爽利保你过得去，慢行一步不安牢。\n\n求财到手，官事平常，目下不吉，交节自强。', '末吉'),
            'ooxoxx': ('雷泽归妹：求鱼顺当向水中，树上求之不顺情。\n受尽爬揭难遂意，劳而无功事不成。\n\n月令不好，做事颠倒，打算到手，随心的少。', '凶')
        }
        return explanations.get(gua, ('暂无解释。', ''))

    def reset(self):
        self.lines = []
        self.current_line = 0

if __name__ == '__main__':
    DivinationApp().run()