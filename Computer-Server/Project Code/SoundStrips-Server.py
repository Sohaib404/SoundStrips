"""
SoundStrips-Server.py: GUI python application that communicates with the arduino through serialport COM3

Author: Sohaib Khadri
Copyright: GPLv3 2020, Sohaib Khadri

"""

import pyaudio
import serial
import audioop
from tkinter import *
from tkinter import colorchooser, messagebox, ttk
from ttkthemes import themed_tk as tk
import time
import pickle
import os
import webbrowser

# initialize serial and global variables
ser = serial.Serial('COM3', 9600)
rms = 4500
preset_dict = {  # Name: minVol, maxVol, fade, r, g, b
        "Red": "30,100,100,25,255,0,0",
        "Green": "30,100,100,25,0,255,0",
        "Blue": "30,100,100,25,0,0,255"
    }
saved_settings = []
device = 0
color = ((255.99609375, 0.0, 0.0), '#ff0000')
power_on = False
feed_on = False


# function used for handling popup messages
def popup(string):
    if string == "undefined color":
        messagebox.showwarning("Undefined Color", "Please choose a color.")
    elif string == "preset exists":
        messagebox.showwarning("Preset Exists", "Please choose a different preset name or delete the old preset.")
    elif string == "reset":
        response = messagebox.askyesno("Reset Settings", "Reset all settings? (Presets & Default Device)")
        if response:
            reset()
    elif string == "preset saved":
        messagebox.showinfo("Preset Saved", "Preset has been saved.")


# saves all settings to pickle file
def save_settings():
    global saved_settings
    saved_settings = [device, preset_dict]
    if os.path.isfile("saved_settings.pickle"):
        os.remove("saved_settings.pickle")
    pickle_make = open("saved_settings.pickle", "wb")
    pickle.dump(saved_settings, pickle_make)
    pickle_make.close()


# resets all presets
def reset():
    global preset_dict
    preset_dict = {  # Name: minVol, maxVol, fade, r, g, b
        "Red": "30,100,100,25,255,0,0",
        "Green": "30,100,100,25,0,255,0",
        "Blue": "30,100,100,25,0,0,255"
    }

    preset_dropdown_menu.delete(0, END)
    for string in list(preset_dict.keys()):
        preset_dropdown_menu.add_command(label=string,
                                         command=lambda value=string: chosen_preset.set(value))
    select_device()


# load in settings
try:
    pickle_in = open("saved_settings.pickle", "rb")
    saved_settings = pickle.load(pickle_in)
    pickle_in.close()
    device = saved_settings[0]
    preset_dict = saved_settings[1]
except (OSError, IOError):
    save_settings()


# converts RGB color to HEX color
def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


# GUI system
root = tk.ThemedTk()
root.get_themes()
root.set_theme("equilux")
root.title("SoundStrips")
root.iconbitmap('images/icon.ico')
root.resizable(False, False)
root.configure(bg='grey20')

notebook_style = ttk.Style()
notebook_style.configure('Custom.TNotebook.Tab', padding=[46, 0])

menu_image = PhotoImage(file='images/menu.png').subsample(2, 2)
gear_image = PhotoImage(file='images/gear.png').subsample(2, 2)
power_off_image = PhotoImage(file='images/poweroff.png').subsample(2, 2)
power_on_image = PhotoImage(file='images/poweron.png').subsample(2, 2)
color_image = PhotoImage(file='images/color.png').subsample(2, 2)
download_image = PhotoImage(file='images/download.png').subsample(3, 3)
trash_image = PhotoImage(file='images/trashcan.png').subsample(3, 3)
save_image = PhotoImage(file='images/save.png').subsample(3, 3)
upload_image = PhotoImage(file='images/upload.png').subsample(3, 3)
play_image = PhotoImage(file='images/play.png').subsample(3, 3)
pause_image = PhotoImage(file='images/pause.png').subsample(3, 3)
stop_image = PhotoImage(file='images/stop.png').subsample(3, 3)
check_image = PhotoImage(file='images/check.png').subsample(3, 3)
cross_image = PhotoImage(file='images/cross.png').subsample(3, 3)
warning_image = PhotoImage(file='images/warning.png').subsample(2, 2)
shaboi_image = PhotoImage(file='images/shaboi.png').subsample(4, 4)
select_image = PhotoImage(file='images/select.png').subsample(2, 2)
refresh_image = PhotoImage(file='images/refresh.png').subsample(2, 2)

notebook = ttk.Notebook(root, style='Custom.TNotebook')
notebook.grid(row=1, column=0, padx=15, pady=15)

menu_tab = LabelFrame(notebook, padx=10, pady=5, bg='grey20')
settings_tab = LabelFrame(notebook, padx=10, pady=5, bg='grey20')
menu_tab.pack()
settings_tab.pack()

notebook.add(menu_tab, image=menu_image, sticky=E+W)
notebook.add(settings_tab, image=gear_image, sticky=E+W)


# Power Button GUI
def power_switch():
    global power_on
    global power_button

    if power_on:
        power_button = ttk.Button(root, image=power_off_image, command=power_switch).grid(row=0, column=0, ipadx=107,
                                                                                          pady=(15, 0), padx=10)
        power_on = False
    else:
        power_button = ttk.Button(root, image=power_on_image, command=power_switch).grid(row=0, column=0, ipadx=107,
                                                                                         pady=(15, 0), padx=10)
        power_on = True
        process_audio()


power_button = ttk.Button(root, image=power_off_image, command=power_switch).grid(row=0, column=0, ipadx=107,
                                                                                  pady=(15, 0), padx=10)

# Presets GUI
preset_frame = LabelFrame(menu_tab, text=" Presets ", font=('Malgun Gothic', 15), fg='White', padx=5, pady=5,
                          bg='grey20')
preset_frame.grid(row=1, column=0, sticky=W+E, padx=5, pady=2)

chosen_preset = StringVar(root)
chosen_preset.set(list(preset_dict.keys())[0])
preset_dropdown = OptionMenu(preset_frame, chosen_preset, *list(preset_dict.keys()))
preset_dropdown.config(indicatoron=0, bg='grey15', font=('Malgun Gothic', 10), fg='White', width=15, bd=0)
preset_dropdown_menu = preset_dropdown["menu"]
preset_dropdown.grid(row=0, column=0, padx=3)


# loads selected preset
def load_preset():
    settings_string = preset_dict.get(chosen_preset.get())
    settings_list = settings_string.split(',')
    min_volume_slider.set(settings_list[0])
    max_volume_slider.set(settings_list[1])
    brightness_slider.set(settings_list[2])
    fade_slider.set(settings_list[3])

    global color
    color = ((settings_list[4], settings_list[5], settings_list[6]),
             rgb_to_hex((int(settings_list[4]), int(settings_list[5]), int(settings_list[6]))))
    global color_button
    color_button = Button(customize_frame, image=color_image, width=75, height=75, bg=color[1],
                          command=color_set).grid(row=0, column=0, columnspan=2, rowspan=4)


# deletes selected preset
def delete_preset():
    del preset_dict[chosen_preset.get()]

    preset_dropdown_menu.delete(0, END)
    for string in list(preset_dict.keys()):
        preset_dropdown_menu.add_command(label=string,
                                         command=lambda value=string: chosen_preset.set(value))
    chosen_preset.set(list(preset_dict.keys())[0])


load_preset_button = Button(preset_frame, command=load_preset, bg='grey15', image=download_image, bd=0,
                            activebackground='grey10').grid(row=0, column=1, padx=20)
delete_preset_button = Button(preset_frame, command=delete_preset, bg='grey15', image=trash_image, bd=0,
                              activebackground='grey10').grid(row=0, column=2, padx=(2, 0))


# asks for color using color chooser
def color_set():
    global color
    color = colorchooser.askcolor()
    global color_button
    color_button = Button(customize_frame, image=color_image, width=75, height=75, bg=color[1],
                          command=color_set).grid(row=0, column=0, columnspan=2, rowspan=4)


# Customize GUI
customize_frame = LabelFrame(menu_tab, text=" Customize ", font=('Malgun Gothic', 15), fg='White', padx=5, pady=5,
                             bg='grey20')
customize_frame.grid(row=2, column=0, sticky=W+E, padx=5, pady=2)


color_button = Button(customize_frame, image=color_image, width=75, height=75, bd=0, bg='grey15',
                      activebackground='grey10', command=color_set).grid(row=0, column=0, columnspan=2, rowspan=4,
                                                                         padx=5)

min_volume_slider = Scale(customize_frame, label="Min Volume Threshold", from_=1, to=100, orient=HORIZONTAL, length=150,
                          bg='grey20', fg='White', troughcolor='Grey15', highlightthickness=0, bd=0)
min_volume_slider.set(30)
min_volume_slider.grid(row=0, column=2, columnspan=2, padx=(5, 0))

max_volume_slider = Scale(customize_frame, label="Max Volume Threshold", from_=1, to=100, orient=HORIZONTAL, length=150,
                          bg='grey20', fg='White', troughcolor='Grey15', highlightthickness=0, bd=0)
max_volume_slider.set(100)
max_volume_slider.grid(row=1, column=2, columnspan=2, padx=(5, 0))


brightness_slider = Scale(customize_frame, label="Brightness", from_=0, to=100, orient=HORIZONTAL, length=150,
                          bg='grey20', fg='White', troughcolor='Grey15', highlightthickness=0, bd=0)
brightness_slider.set(100)
brightness_slider.grid(row=2, column=2, columnspan=2, padx=(5, 0), pady=5)

fade_slider = Scale(customize_frame, label="Fade Speed", from_=1, to=100, orient=HORIZONTAL, length=150, bg='grey20',
                    fg='White', troughcolor='Grey15', highlightthickness=0, bd=0)
fade_slider.set(25)
fade_slider.grid(row=3, column=2, columnspan=2, padx=(5, 0), pady=5)


# send new settings to client
def send_settings():

    try:
        color[0][0]
    except (NameError, TypeError):
        popup("undefined color")
        return

    ser.write(b'9')

    settings_string = str(fade_slider.get())

    for i in range(3):
        settings_string += "," + str(int(int(color[0][i])*(brightness_slider.get()/100)))
    settings_string += "."
    for c in settings_string:
        ser.write(c.encode())
        time.sleep(0.1)


# reads customizable values and saves to a preset
def add_preset(name):
    if name in preset_dict:
        popup("preset exists")
    else:

        preset_dict[name] = str(min_volume_slider.get()) + "," + str(max_volume_slider.get()) + "," +\
                            str(brightness_slider.get()) + "," + str(fade_slider.get())
        for i in range(3):
            preset_dict[name] += "," + str(int(color[0][i]))

        preset_dropdown_menu.delete(0, END)
        for string in list(preset_dict.keys()):
            preset_dropdown_menu.add_command(label=string,
                                             command=lambda value=string: chosen_preset.set(value))

        save_settings()
        popup("preset saved")


# opens new window asking for new preset name
def save_window():

    try:
        color[0][0]
    except (NameError, TypeError):
        popup("undefined color")
        return

    name_window = Toplevel()
    name_window.title("Enter Preset Name")
    name_window.config(bg='grey20')

    text = Label(name_window, text="Enter Preset Name:", bg='grey18', font=('Malgun Gothic', 9), fg='White',
                 padx=5, pady=5).grid(padx=10, pady=10, row=0, column=0)

    name_entry = Entry(name_window, width=15)
    name_entry.grid(padx=10, pady=10, row=1, column=0)

    save_button = Button(name_window, image=save_image,
                         command=lambda: [add_preset(name_entry.get()), name_window.destroy()], bg='grey15',
                         fg='White', padx=5, pady=5, bd=0, activebackground='grey10').grid(row=2, column=0,
                                                                                           padx=5, pady=5)


save_preset_button = Button(customize_frame, command=save_window, bg='grey15', image=save_image, bd=0,
                            activebackground='grey10').grid(row=4, column=0, padx=5, pady=5)
apply_button = Button(customize_frame, command=send_settings, bg='grey15', image=upload_image, bd=0,
                      activebackground='grey10').grid(row=4, column=3, padx=5, pady=5)


# Live Feed GUI
feed_frame = LabelFrame(menu_tab, text=" Live Feed ", font=('Malgun Gothic', 15), fg='White', padx=5, pady=5,
                        bg='grey20')
feed_frame.grid(row=3, column=0, sticky=W+E, padx=5, pady=2)


# switches live feed on/off
def feed_switch():
    global feed_on
    global play_pause_button
    if feed_on:
        play_pause_button = Button(feed_frame, command=feed_switch,  bg='grey15', image=play_image, bd=0,
                                   activebackground='grey10').grid(row=0, column=0, padx=5, pady=5)

        feed_on = False
    else:

        play_pause_button = Button(feed_frame, command=feed_switch,  bg='grey15', image=pause_image, bd=0,
                                   activebackground='grey10').grid(row=0, column=0, padx=5, pady=5)

        feed_on = True


play_pause_button = Button(feed_frame, command=feed_switch, bg='grey15', image=play_image, bd=0,
                           activebackground='grey10').grid(row=0, column=0, padx=5, pady=5)
feed_text = Label(feed_frame, text="Current Volume Output:", bg='grey18', font=('Malgun Gothic', 10), fg='White',
                  padx=5, pady=5).grid(row=0, column=1, padx=(0, 0), pady=5)

feed_val_text = Label(feed_frame, text="0", bg='grey18', font=('Malgun Gothic', 10), fg='White', padx=5, pady=5)
feed_val_text.grid(row=0, column=2, pady=5)


# displays live feed
def feed():
    feed_val_text.config(text=int(rms * (100 / 15000)))


# Settings GUI
settings_frame = LabelFrame(settings_tab, text=" Settings ", font=('Malgun Gothic', 15), fg='White', padx=5, pady=5,
                            bg='grey20')
settings_frame.grid(row=0, column=0, sticky=W+E, padx=5, pady=2)


# returns device name from device index
def get_device(chosen_device):
    p = pyaudio.PyAudio()
    dev = p.get_device_info_by_index(chosen_device)
    return dev['name']


device_text = Label(settings_frame, text="Selected Device: \n" + get_device(device)[:25], font=('Malgun Gothic', 10),
                    fg='White', padx=5, pady=5, bg='grey20').grid(row=0, column=0, columnspan=2, sticky=W+E)
device_scrollbar = Scrollbar(settings_frame, orient=VERTICAL)
device_listbox = Listbox(settings_frame, width=37, height=5, yscrollcommand=device_scrollbar.set,
                         bg='grey18', fg='White')
device_scrollbar.config(command=device_listbox.yview)
device_scrollbar.grid(row=1, column=2, sticky=N+S)
device_listbox.grid(row=1, column=0, columnspan=2, sticky=W+E)


# lists all audio input devices
def list_devices():
    device_listbox.delete(0, END)

    p = pyaudio.PyAudio()
    i = 0
    n = p.get_device_count()
    while i < n:
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            device_listbox.insert(i, dev['name'])
        i += 1


# changes current audio device
def select_device():
    global device_text
    device_text = Label(settings_frame, text="Selected Device: \n" + device_listbox.get(ANCHOR)[:25],
                        font=('Malgun Gothic', 10), fg='White', padx=5, pady=5,
                        bg='grey20').grid(row=0, column=0, columnspan=2, sticky=W + E)
    global device
    print(device_listbox.curselection())
    if device_listbox.curselection() == ():
        device = 0
    else:
        device = int(str(device_listbox.curselection())[1])
    if power_on:
        power_switch()
    save_settings()


refresh_device_button = Button(settings_frame, bg='grey15', image=refresh_image, command=list_devices, fg='White', bd=0,
                               activebackground='grey10', height=30).grid(row=2, column=0, padx=5, pady=5)
select_device_button = Button(settings_frame, bg='grey15', image=select_image, command=select_device, fg='White', bd=0,
                              activebackground='grey10', height=30).grid(row=2, column=1, padx=5, pady=5)
reset_button = Button(settings_frame, bg='grey15', text="Reset all Settings", command=lambda: popup("reset"),
                      font=('Malgun Gothic', 11), fg='White', padx=5, pady=5, bd=0, activebackground='grey10').grid(
    row=4, column=0, columnspan=2, padx=5, pady=5)


# About GUI
about_frame = LabelFrame(settings_tab, text=" About ", font=('Malgun Gothic', 15), fg='White', padx=5, pady=5,
                         bg='grey20')
about_frame.grid(row=1, column=0, sticky=W+E, padx=5, pady=2)


# opens links
def open_link(string):
    if string == "rm":
        os.startfile("README.md")
    elif string == "gpl":
        os.startfile("LICENSE.txt")
    elif string == "git":
        webbrowser.open('https://github.com/Sohaib404/SoundStrips')


text1 = Label(about_frame, text="This open source application\n was made by Sohaib Khadri", bg='grey18',
              font=('Malgun Gothic', 9), fg='White', padx=5, pady=5).grid(row=0, column=0, columnspan=2)
text2 = Label(about_frame, text="Licensed under GNU GPLv3", bg='grey18', font=('Malgun Gothic', 9), fg='White',
              padx=5, pady=5).grid(row=1, column=0, columnspan=2)

image = Label(about_frame, image=shaboi_image, bg='grey20').grid(row=0, column=2, rowspan=2)
github_button = Button(about_frame, text="Github Link", command=lambda: open_link("git"), font=('Malgun Gothic', 10),
                       bg='grey15', fg='White', padx=5, pady=5, bd=0, activebackground='grey10').grid(row=2, column=0)
readme_button = Button(about_frame, text="README", command=lambda: open_link("rm"), font=('Malgun Gothic', 10),
                       bg='grey15', fg='White', padx=5, pady=5, bd=0, activebackground='grey10').grid(row=2, column=1)
license_button = Button(about_frame, text="LICENSE", command=lambda: open_link("gpl"), font=('Malgun Gothic', 10),
                        bg='grey15', fg='White', padx=5, pady=5, bd=0, activebackground='grey10').grid(row=2, column=2)


# audio processing using pyaudio
def process_audio():

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=2048,
                    input_device_index=device)

    while power_on:
        root.update_idletasks()
        root.update()
        if feed_on:
            feed()
        data = stream.read(2048)
        global rms
        rms = audioop.rms(data, 2)

        min_volume_level = min_volume_slider.get() * (15000/100)
        max_volume_level = max_volume_slider.get() * (15000/100)
        if max_volume_level >= rms >= min_volume_level:
            ser.write(1)


if __name__ == '__main__':
    # GUI loop
    root.mainloop()
