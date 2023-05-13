from textual import on
from textual.app import App, ComposeResult
from textual.color import Color
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Input, Static, Label, TabbedContent, TabPane, Footer, Button, OptionList, Switch, Markdown
from textual.containers import Grid
from textual.screen import ModalScreen
import random
import re
import os
import json
import appdirs
import math

def animation_time(n_items: int) -> float:
    base_time = 1.0  # base time for 10 items
    max_time = 2.0  # maximum time allowed

    if n_items <= 10:
        return base_time
    else:
        # Use a logarithmic scale to calculate additional time
        additional_time = math.log(n_items / 10)
        total_time = base_time + additional_time

        # Ensure the total time does not exceed the maximum
        return min(total_time, max_time)

ABOUT_MARKDOWN = """\
# Rich Color Picker

This is a simple color picker app made to work on linux and windows terminals.
- Author: *PlusPlusMan*
- Version: *0.1*
- License: *MIT*

___

## Tips
- Loose focus from the color inputs by pressing `Enter`
- Switch between tabs by pressing `Tab` or `Shift+Tab`
- Switch between color inputs by pressing `Right Arrow` or `Left Arrow`
- Save a color by pressing `s` or clicking the `Save color` button
- Randomize the color by pressing `r` or clicking the `Randomize` button
- Quit the app by pressing `q` or clicking the `Quit` button


## Contact

You can contact me via:
- Discord: *PlusPlusMan#3822*
- Email: *contact@plusplusman.com*
- My [Github](https://github.com/PlusPlusMan) page

___

Shout out to [Textual](https://github.com/Textualize/textual/tree/main) discord community. Big thanks to *@davep* for helping me with this first Textual project of mine.
"""

COLORS = [
'black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 
'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange', 
'aliceblue', 'antiquewhite', 'aquamarine', 'azure', 'beige', 'bisque', 
'blanchedalmond', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 
'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 
'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 
'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 
'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 
'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 
'deepskyblue', 'dimgray', 'dimgrey',
]

userdata_dir = appdirs.user_data_dir("RichColorPicker", "PlusPlusMan", "0.1")

os.makedirs(userdata_dir, exist_ok=True)

data_file = os.path.join(userdata_dir, 'data.json')

if not os.path.exists(data_file):
    with open(data_file, 'w') as f:
        json.dump(
            {
                'dark_mode': True,
                'sounds': True,
                'sliders': False,
                'auto_tab_switch': True,
                'saved_colors': []
                }, f, indent=4)
        

class SavedColor(Static):
    def __init__(self, label_content):
        super().__init__(classes="saved-color")
        self.content = label_content
    
    def compose(self) -> ComposeResult:
        with Vertical(classes="content-container") as h:
            with Horizontal(classes="content-container-top"):         
                with Static(id="content-container-color") as s:
                    s.styles.background = Color(self.content['rgb'][0], self.content['rgb'][1], self.content['rgb'][2])
            with Horizontal(classes="content-container-bottom"):
                yield Label(f"RGB: [b]{self.content['rgb'][0]} {self.content['rgb'][1]} {self.content['rgb'][2]}[/b]\nHSL: [b]{self.content['hsl'][0]:0.2f} {self.content['hsl'][1]:0.2f} {self.content['hsl'][2]:0.2f}[/b]\nHEX: [b]{self.content['hex']}[/b]", classes="color-values")
                yield Button("Remove", classes="remove", variant="error")
                
        
class QuitScreen(ModalScreen):
    """Screen with a dialog to quit."""
    
    BINDINGS = [
        ("enter", "quit", "Quit"),
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            Button("Quit [Enter]", variant="error", id="quit", classes="quit-buttons"),
            Button("Cancel [ESC]", variant="primary", id="cancel", classes="quit-buttons"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        elif event.button.id == "cancel":
            self.app.pop_screen()
            
    def action_quit(self):
        self.app.exit()
        
    def action_cancel(self):
        self.app.pop_screen()

class ComputedApp(App):
    global data_file
    
    DEFAULT_CSS = """
Screen {
    layout: horizontal;
    height: 100%;
    overflow: auto auto;
}

#main {
    dock: top;
    height: 100%;
    overflow: auto auto;
}

#title {
    margin: 1 0 0 0;
    align: center top;
}

.title-label {
    background: $boost;
    text-align: center;
    color: $secondary-lighten-2;
    border: vkey $secondary;
}

.color { /* Color panel representing current color for hsl and rgb panels*/
    height: 15fr;
    border: hkey $secondary;
    margin: 2 0;
    text-align: center;
    align: center middle;
    border-title-color: $secondary-lighten-2;
    border-title-style: bold italic;
    border-title-align: center;
}

.color-label { /* Label inside color panel */
    dock: bottom;
    color: black;
    text-align: center;
    width: auto;
    height: 7;
    align-horizontal: right;
    border: wide $secondary;
}

#color-inputs { /* Container of all color inputs */
    height: 5fr;
    width: 100%;
    align: center middle;
    margin: 0 0 0 0;
    border: vkey transparent;
    border-subtitle-color: $primary;
    border-subtitle-style: bold italic;
    border-subtitle-align: right;
}

.color-input { /* All by one color inputs */
    width: 100%;
    height: auto;
    margin: 0 1;
    border: panel $accent;
    border-title-style: bold italic;
    border-title-color: $accent-darken-3;
    border-title-align: center;
}

.color-input:hover{ /* Hovered color input */
    border: panel $accent-lighten-1;
}

.color-input:focus { /* Focused color input */
    border: panel $accent-lighten-2;
}

#red { /* Red color input */
    color: red;
}

#green { /* Green color input */
    color: green;
}

#blue { /* Blue color input */
    color: blue;
}

.color-input-hsl{ /* Hsl color input */
    color: gold;
}

#hex { /* Hex color input */
    margin: 0 10;
    border-subtitle-align: left;
    color: silver;
}

/* Quit Screen */
QuitScreen {
    align: center middle;
}

#dialog { /* Quit screen dialog */
    grid-size: 2;
    grid-gutter: 1 2;
    grid-rows: 1fr 3;
    padding: 1 11;
    width: 60;
    height: 11;
    border: thick $background 80%;
    background: $surface;
}

#question { /* Quit screen question */
    column-span: 2;
    height: 1fr;
    width: 1fr;
    content-align: center middle;
}

.saved-color {
    offset: 2 0;
    margin: 1 0;
    align: center top;
    border: wide $accent;
    height: 10;
    width: 90%;
}

#saved-colors-container {
    border: round $accent;
    color: red;
    margin: 1 2;
    height: auto;
    background: $primary-background-darken-1;

}

.content-container {
    align: center bottom;
    background: $boost;
}

.content-container-top {
    margin: 1 1;
}

#content-container-color {
    height: 100%;
}

.content-container-bottom {
    height: auto;
    margin: 0 0 1 0;
    align: center middle;
}

.color-values {
    margin: 0 4 0 2;
    color: $secondary;
}

.remove {
    margin: 0 2 0 4;
}

#settings-main-container {
    margin: 1 1;
    height: 30fr;
    border: round $boost;

}

Switch {
    height: 3;
    width: 10;
}

.settings-container {
    align: center middle;

}

.settings-label {
    offset: 0 1;
    color: $secondary;
}

#auto-tab-switch-container {
    offset: -3 0;
}

#remove-all-label {
    color: $error;
}

#remove-all-button {
    background: $error;
}

#remove-all-button:hover {
    background: $error-darken-1;
}

#remove-all-button:focus {
    background: $error-darken-3;
}

#color-name-input {
    margin: 2 10;
    height: auto;
}

#colors-main-container {
    margin: 1 1;
    height: 30fr;
    width: 100%;
    border: round $boost;
}

#color-option-list {
    margin: 0 2 0 2;
    background: $panel;
    border: round $panel;
    color: $secondary;
}

#colors-right-container {
    background: $boost;
    margin: 0 2 0 2;
    border: round $boost;
}
#color-preview {
    dock: top;
    background: black;
    height: 75%;
}

#color-preview-label {
    dock: bottom;
    height: 15%;
    width: 100%;
    color: $secondary;
    border: round $secondary;
    text-align: center;
}

#markdown-container {
    overflow: hidden hidden;
    height: auto;
    border: round $boost-lighten-3;
    margin: 0 2 2 0;
}

#about-markdown {
    margin: 0 2;
}
    """
    BINDINGS = [
        ("s", "save_color", "Save color"),
        ("r", "randomize", "Randomize"),
        ("q", "quit", "Quit")
    ]

    
    red = reactive(0)
    green = reactive(0)
    blue = reactive(0)
    
    hue = reactive(0, always_update=True)
    saturation = reactive(0, always_update=True)
    lightness = reactive(0, always_update=True)
    
    color_rgb = reactive(Color.parse("black"))
    color_hsl = reactive(Color.parse("black"), always_update=True)
    color_hex = reactive(Color.parse("black"))
    
    settings = json.load(open(data_file))
    dark_mode = reactive(settings['dark_mode'])
    sounds = reactive(settings['sounds'])
    sliders = reactive(settings['sliders'])
    auto_tab_switch = reactive(settings['auto_tab_switch'])

    def compose(self) -> ComposeResult:
        with TabbedContent(id="main") as tabs:
            with TabPane("RGB", id="rgb_tab"):
                with Static(id="title"):
                    yield Label("RGB Color Picker", classes="title-label")
                with Static(id="rgb-color", classes="color") as s:
                    s.border_title = "Color"
                    yield Label(id="rgb-color-label", classes="color-label")
                with Horizontal(id="color-inputs") as h:
                    h.border_subtitle = "Whole value between 0 and 255"
                    with Vertical() as v:
                        _input = Input(placeholder="Enter red", id="red", classes="color-input")
                        _input.border_title = "Red:"
                        yield _input
                    with Vertical() as v:
                        _input = Input(placeholder="Enter green", id="green", classes="color-input")
                        _input.border_title = "Green:"
                        yield _input
                    with Vertical() as v:
                        _input = Input(placeholder="Enter blue", id="blue", classes="color-input")
                        _input.border_title = "Blue:"
                        yield _input
                
            with TabPane("HSL", id="hsl_tab"):
                with Static(id="title"):
                    yield Label("HSL Color Picker", classes="title-label")
                with Static(id="hsl-color", classes="color") as s:
                    s.border_title = "Color"
                    yield Label(id="hsl-color-label", classes="color-label")
                with Horizontal(id="color-inputs") as h:
                    h.border_subtitle = "Float values between 0.0 and 0.999"
                    with Vertical() as v:
                        _input = Input(placeholder="Enter hue", id="hue", classes="color-input color-input-hsl")
                        _input.border_title = "Hue:"
                        yield _input
                    with Vertical() as v:
                        _input = Input(placeholder="Enter saturation", id="saturation", classes="color-input color-input-hsl")
                        _input.border_title = "Saturation:"
                        yield _input
                    with Vertical() as v:
                        _input = Input(placeholder="Enter lightness", id="lightness", classes="color-input color-input-hsl")
                        _input.border_title = "Lightness:"
                        yield _input
                        
            with TabPane("HEX", id="hex_tab"):
                with Static(id="title"):
                    yield Label("HEX Color Picker", classes="title-label")
                with Static(id="hex-color", classes="color") as s:
                    s.border_title = "Color"
                    yield Label(id="hex-color-label", classes="color-label")
                with Horizontal(id="color-inputs") as h:
                    h.border_subtitle = "Hexadecimal value"
                    with Vertical() as v:
                        _input = Input(placeholder="Enter hex", id="hex", classes="color-input")
                        _input.border_title = "Hex:"
                        yield _input
            
            with TabPane("Saved", id="saved_tab"):
                saved_colors = json.load(open(data_file))['saved_colors']
                with Static(id="title"):
                    yield Label("List of Saved Colors", classes="title-label")
                yield ScrollableContainer(*(SavedColor(color) for color in saved_colors), id='saved-colors-container')             
                
            with TabPane("Colors", id="colors_tab"):
                with Static(id="title"):
                    yield Label("List of Colors", classes="title-label")
                with Horizontal(id="colors-main-container"):
                    with Vertical(id="colors-left-container"):
                        yield OptionList(
                                *COLORS,
                            name="colors",
                            id="color-option-list"
                        )
                    with Vertical(id="colors-right-container"):
                        yield Static(id="color-preview")
                        _rgb = Color.parse('black').rgb
                        _hsl = Color.parse('black').hsl
                        _hex = Color.parse('black').hex 
                        yield Label(f"RGB: {_rgb[0]} {_rgb[1]} {_rgb[2]}\nHSL: {_hsl.h} {_hsl.s} {_hsl.l}\nHEX: {_hex}",id="color-preview-label")
          
            with TabPane("Settings", id="settings_tab"):
                with Static(id="title"):
                    yield Label("Settings", classes="title-label")
                      
                with Vertical(id="settings-main-container"):
                    with Horizontal(classes="settings-container"):
                        yield Label("Dark Mode: ", classes="settings-label")
                        yield Switch(self.dark_mode, id="dark-mode-switch", classes="settings-switch")
                    with Horizontal(classes="settings-container"):
                        yield Label("Sounds:    ", classes="settings-label")
                        yield Switch(self.sounds, id="sounds-switch", classes="settings-switch")
                    with Horizontal(classes="settings-container", id="auto-tab-switch-container"):
                        yield Label("Auto Tab Switch:", classes="settings-label")
                        yield Switch(self.auto_tab_switch, id="auto-tab-switch", classes="settings-switch")
                    with Horizontal(classes="settings-container"):
                        yield Label("Sliders:  ", classes="settings-label")
                        yield Switch(id="sliders-switch", classes="settings-switch", disabled=True)
                    with Horizontal(classes="settings-container"):
                        yield Label("Remove All Data:    ", id="remove-all-label", classes="settings-label remove-all")
                        yield Button("Remove", id="remove-all-button", classes="remove-all")
                                           
            with TabPane("About", id="about_tab"):
                with ScrollableContainer(id="markdown-container"):
                    yield Markdown(ABOUT_MARKDOWN, id="about-markdown")
                
        yield Footer()
        
    def on_mount(self) -> None:
        self.dark = self.dark_mode
        
    def action_save_color(self) -> None:
        if self.query_one(TabbedContent).active in ["rgb_tab", "hsl_tab", "hex_tab"]:
            data = dict()
            if self.query_one(TabbedContent).active == "rgb_tab":
                data = {
                    'rgb': self.color_rgb,
                    'hsl': [self.color_rgb.hsl.h, self.color_rgb.hsl.s, self.color_rgb.hsl.l],
                    'hex': self.color_rgb.hex
                }
            elif self.query_one(TabbedContent).active == "hsl_tab":
                data = {
                    'rgb': self.color_hsl.rgb,
                    'hsl': [self.color_hsl.hsl.h, self.color_hsl.hsl.s, self.color_hsl.hsl.l],
                    'hex': self.color_hsl.hex
                }
            elif self.query_one(TabbedContent).active == "hex_tab":
                data = {
                    'rgb': self.color_hex.rgb,
                    'hsl': [self.color_hex.hsl.h, self.color_hex.hsl.s, self.color_hex.hsl.l],
                    'hex': self.color_hex
                }

            settings_data = json.load(open(data_file, "r"))
            settings_data["saved_colors"].append(data)
            json.dump(settings_data, open(data_file, "w"), indent=4)
            new_color = SavedColor(label_content=data)
            self.query_one("#saved-colors-container").mount(new_color)
            
            if self.auto_tab_switch:
                self.query_one(TabbedContent).active = "saved_tab"
                self.query_one("#saved-colors-container").scroll_end(easing='in_out_quad', duration=animation_time(len(self.query_one("#saved-colors-container").children)))
        
    @on(OptionList.OptionSelected, "#color-option-list")
    def update_color(self, event: OptionList.OptionSelected) -> None:
        self.query_one("#color-preview").styles.animate("background", value=Color.parse(event.option.prompt), duration=0.5)
        _rgb = Color.parse(event.option.prompt).rgb
        _hsl = Color.parse(event.option.prompt).hsl
        _hex = Color.parse(event.option.prompt).hex
        self.query_one("#color-preview-label").update(f"RGB: {_rgb[0]} {_rgb[1]} {_rgb[2]}\nHSL: {_hsl.h:0.2f} {_hsl.s:0.2f} {_hsl.l:0.2f}\nHEX: {_hex}")
          
    @on(Switch.Changed, "#dark-mode-switch")
    async def toggle_dark_mode(self, event: Switch.Changed) -> None:
        self.dark = not self.dark
        self.dark_mode = self.dark
        
    @on(Switch.Changed, "#sounds-switch")
    async def toggle_sounds(self, event: Switch.Changed) -> None:
        self.sounds = not self.sounds
        
    @on(Switch.Changed, "#auto-tab-switch")
    async def toggle_auto_tab_switch(self, event: Switch.Changed) -> None:
        self.auto_tab_switch = not self.auto_tab_switch
        
    @on(Switch.Changed, ".settings-switch") 
    def update_settings(self, event: Switch.Changed) -> None:
        settings_data = json.load(open(data_file, "r"))
        settings_data["dark_mode"] = self.dark
        settings_data["sounds"] = self.sounds
        settings_data["sliders"] = self.sliders
        settings_data["auto_tab_switch"] = self.auto_tab_switch
        json.dump(settings_data, open(data_file, "w"), indent=4)
    
    @on(Button.Pressed, ".remove")
    async def remove_color(self, event: Button.Pressed) -> None:
        container_to_remove = event.button.parent.parent.parent
        event.button.parent.parent.parent.styles.animate("opacity", 0.1, duration=0.5, on_complete=container_to_remove.remove)

    @on(Button.Pressed, "#remove-all-button")
    async def remove_all(self, event: Button.Pressed) -> None:
        for color in self.query_one("#saved-colors-container").children:
            color.remove
        
        settings_data = json.load(open(data_file, "r"))
        settings_data["saved_colors"] = []
        json.dump(settings_data, open(data_file, "w"), indent=4)

    def action_quit(self):
        self.push_screen(QuitScreen())
        
    def action_randomize(self):
        if self.query_one(TabbedContent).active == "rgb_tab":
            self.red = random.randint(0, 255)
            self.green = random.randint(0, 255)
            self.blue = random.randint(0, 255)
        elif self.query_one(TabbedContent).active == "hsl_tab":
            self.hue = float(f"0.{random.randint(0, 999)}")
            self.saturation = float(f"0.{random.randint(0, 999)}")
            self.lightness = float(f"0.{random.randint(0, 999)}")
        elif self.query_one(TabbedContent).active == "hex_tab":
            hex_digits = "0123456789abcdef"
            random_hex = "".join(random.choice(hex_digits) for _ in range(6))
            self.color_hex = Color.parse(f"#{random_hex}")
        elif self.query_one(TabbedContent).active == "colors_tab":
            random_color = random.choice(COLORS)
            self.query_one("#color-preview").styles.animate("background", value=Color.parse(random_color), duration=0.5)
            self.query_one("#color-option-list").highlighted = COLORS.index(random_color)
            self.query_one("#color-preview-label").update(f"RGB: {Color.parse(random_color).rgb[0]} {Color.parse(random_color).rgb[1]} {Color.parse(random_color).rgb[2]}\nHSL: {Color.parse(random_color).hsl.h:0.2f} {Color.parse(random_color).hsl.s:0.2f} {Color.parse(random_color).hsl.l:0.2f}\nHEX: {Color.parse(random_color).hex}")
        elif self.query_one(TabbedContent).active == "saved_tab":
            self.query_one("#saved-colors-container").scroll_to_widget(random.choice(self.query_one("#saved-colors-container").children), easing='in_out_back', duration=animation_time(len(self.query_one("#saved-colors-container").children)))

    def compute_color_rgb(self) -> Color:
        return Color(self.red, self.green, self.blue).clamped

    def watch_color_rgb(self, color_rgb: Color) -> None:  # 
        rgb_to_hsl = color_rgb.hsl
        rgb_to_hex = color_rgb.hex
        self.query_one("#rgb-color-label").update(f"\n[uu]RGB: [b]{self.red} {self.green} {self.blue}[/b][/uu]\nHSL: [b]{rgb_to_hsl.h:0.2f} {rgb_to_hsl.s:0.2f} {rgb_to_hsl.l:0.2f}[/b]\nHEX: [b]{rgb_to_hex}[/b]")
        self.query_one("#rgb-color").styles.background = color_rgb
        self.query_one("#rgb-color-label").styles.background = Color.with_alpha(color_rgb.inverse, 0.25)
        self.query_one("#rgb-color-label").styles.border = ("wide", Color.with_alpha(color_rgb.inverse, 0.8))
        self.query_one("#rgb-color").styles.border = ("hkey", Color.with_alpha(color_rgb.inverse, 0.8))
        self.query_one("#rgb-color").styles.border_title_color = Color.with_alpha(color_rgb.inverse, 0.8)
    
    def compute_color_hsl(self) -> Color:
        color = Color.from_hsl(h=self.hue, s=self.saturation, l=self.lightness).clamped
        return color
        
    def watch_color_hsl(self, color_hsl: Color) -> None:
        hsl_to_rgb = color_hsl.rgb
        hsl_to_hex = color_hsl.hex
        self.query_one("#hsl-color").styles.background = color_hsl
        self.query_one("#hsl-color-label").update(f"\n[uu]HSL: [b]{self.hue:0.2f} {self.saturation:0.2f} {self.lightness:0.2f}[/b][/uu]\nRGB: [b]{hsl_to_rgb[0]} {hsl_to_rgb[1]} {hsl_to_rgb[2]}[/b]\nHEX: [b]{hsl_to_hex}[/b]")
        self.query_one("#hsl-color-label").styles.background = Color.with_alpha(color_hsl.inverse, 0.25)
        self.query_one("#hsl-color-label").styles.border = ("wide", Color.with_alpha(color_hsl.inverse, 0.8))
        self.query_one("#hsl-color").styles.border = ("hkey", Color.with_alpha(color_hsl.inverse, 0.8))
        self.query_one("#hsl-color").styles.border_title_color = Color.with_alpha(color_hsl.inverse, 0.8)
    
    def watch_color_hex(self, color_hex: Color) -> None:
        hex_to_rgb = color_hex.rgb
        hex_to_hsl = color_hex.hsl
        self.query_one("#hex-color").styles.background = color_hex
        self.query_one("#hex-color-label").update(f"\n[uu]HEX: [b]{self.color_hex.hex}[/b][/uu]\nRGB: [b]{hex_to_rgb[0]} {hex_to_rgb[1]} {hex_to_rgb[2]}[/b]\nHSL: [b]{hex_to_hsl.h:0.2f} {hex_to_hsl.s:0.2f} {hex_to_hsl.l:0.2f}[/b]")
        self.query_one("#hex-color-label").styles.background = Color.with_alpha(color_hex.inverse, 0.25)
        self.query_one("#hex-color-label").styles.border = ("wide", Color.with_alpha(color_hex.inverse, 0.8))
        self.query_one("#hex-color").styles.border = ("hkey", Color.with_alpha(color_hex.inverse, 0.8))
        self.query_one("#hex-color").styles.border_title_color = Color.with_alpha(color_hex.inverse, 0.8)
        
    def on_input_changed(self, event: Input.Changed) -> None:
        
        if self.query_one(TabbedContent).active == "rgb_tab":
            try:
                component = event.value
                if component == "":
                    component = 0
                elif len(event.input.value) > 3:
                    raise IndexError
                elif int(event.input.value) > 255:
                    event.input.value = "255"
                elif len(event.input.value) > 1 and event.input.value[0] == "0":
                    event.input.value = event.input.value[1:]
                component = int(component)
            except ValueError:
                event.input.value = event.value[0:-1]
                if self.sounds:
                    self.bell()
            except IndexError:
                event.input.value = event.value[0:-1]
            else:
                if event.input.id == "red":
                    self.red = component
                elif event.input.id == "green":
                    self.green = component
                else:
                    self.blue = component
                    
        elif self.query_one(TabbedContent).active == "hsl_tab":
            try:
                component = event.value
                if component == "":
                    component = 0
                component = float(component)
            except ValueError:
                event.input.value = event.value[0:-1]
                if self.sounds():
                    self.bell()
            except IndexError:
                event.input.value = event.value[0:-1]
            else:
                if event.input.id == "hue":
                    self.hue = component
                elif event.input.id == "saturation":
                    self.saturation = component
                else:
                    self.lightness = component
                    
        elif self.query_one(TabbedContent).active == "hex_tab":
            pattern = "^#([A-Fa-f0-9]{1,8})$"
            component = f"#{event.value}" if not event.value.startswith("#") else event.value
            component = str(component)

            if not re.match(pattern, component) and component != "#":
                event.input.value = event.value[0:-1]
                if self.sounds:
                    self.bell()
                return

            if event.input.id == "hex":
                try:
                    self.color_hex = Color.parse(component)
                except Exception:
                    self.color_hex = Color.parse("transparent")

    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.set_focus(None)
        print(f"{self.query_one('#hex').value}")

def main():
    app = ComputedApp()
    app.run()
    
if __name__ == "__main__":
    app = ComputedApp()
    app.run()
