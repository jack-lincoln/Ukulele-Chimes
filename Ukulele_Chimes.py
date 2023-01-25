#! python3
# Ukulele_Chimes.py - A program that uses pre-recorded musical notes played on a ukulele
# to replicate the randomness of wind chimes.

"""

    •Play Chime - The notes of the current note set are played at random
    •Play Scale - The notes of the current note set are played as quarter notes in ascending order
    •Reset All - All settings are returned to their default state
    •Root Dial - Adjusts the root note of the current note set
    •Scale Combo Box - Select the scale used for the current note set
    •Mode Slider - Select the mode of the current scale
    •Drone Volume Sliders - Adjust the volume of the drone notes (based on the root and the fifth of the current note set)
    •Note Volume Sliders - Adjust the volume of each note. (While the scale is set to "Chromatic", adjusting the volume
        sliders may allow for user-created note sets when the "Play Chime" button is active.)

    •Keys 1-8 - For most scales, each note of the current note set may be played manually using these keys.
        If a scale has more than eight notes, keys 9, 0, -, =, and BACKSPACE are incorporated.

"""

import sys
import json
import random
import time
import math
import numpy
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import pygame


class UkuleleChimes(QWidget):
    """Overall class to create the program."""

    def __init__(self, parent=None):
        """A method to control settings, as well as to run all class methods."""

        super(UkuleleChimes, self).__init__(parent)

        # Load GUI layout
        uic.loadUi("Ukulele_Chimes_Layout.ui", self)

        # Load json file containing music scales
        filename = 'music_scales.json'
        with open(filename, encoding='utf-8') as f:
            self.all_scale_data = json.load(f)
        self.scales = self.all_scale_data["Scales"]

        # Load json file containing musical key roots
        filename = 'roots.json'
        with open(filename, encoding='utf-8') as f:
            self.all_root_data = json.load(f)
        self.roots = self.all_root_data["Roots"]

        # Initialize pygame.mixer
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)

        # Create a list of all scale names
        self.scale_names = []
        self.mode_degrees = []
        for key, value in self.scales.items():
            self.scale_names.append(value["name"])

        self.playing_chimes_list = []

        self.allow_play = True

        # Window setup
        self.title = "Ukulele Chimes"
        self.setWindowTitle(self.title)
        self.window_width = 820
        self.window_height = 520
        self.setFixedWidth(self.window_width)
        self.setFixedHeight(self.window_height)

        self.root_list = ['G', 'G♯/A♭', 'A', 'A♯/B♭', 'B', 'C', 'C♯/D♭', 'D', 'D♯/E♭', 'E', 'F', 'F♯/G♭']

        # Connect the root dial
        self.root_label_display = self.findChild(QLabel, 'root_label_display')
        self.root = (int(self.root_dial.value()))
        self.root_label_display.setText(self.root_list[self.root])
        self.root_dial = self.findChild(QDial, 'root_dial')
        self.root_dial.valueChanged.connect(self.root_dial_changed)

        # Load and assign the audio files
        self.notes = []
        for i in range(0, 24):
            si = '%02d' % i
            self.notes.append({i: f'AudioFiles/note_{si}.wav'})

        # Create the drone note list
        self.drones = []
        d = 196
        for i in range(0, 24):
            self.drones.append(d)
            d *= 1.059463

        # Connect the drone volume sliders
        self.drone_volume_slider_00 = self.findChild(QSlider, "drone_slider_00")
        self.drone_volume_slider_01 = self.findChild(QSlider, "drone_slider_01")

        # Create the current note set with default settings
        self.current_note_set = []
        for i in range(5, 18):
            self.current_note_set.append({'note': self.notes[i], 'volume': 5, 'tempo': 5, 'drone': self.drones[i]})

        # Connect the current scale label
        self.current_scale_label = self.findChild(QLabel, "current_scale_label")

        # Add the scale names to the scale_combo_box
        self.scale_combo_box = self.findChild(QComboBox, "scale_combo_box")
        for scale in self.scale_names:
            self.scale_combo_box.addItem(scale)

        self.current_display_notes = []

        self.start_time = time.time()

        self.drone_root = self.current_note_set[0]['drone']

        # Connect the mode slider
        self.mode_slider = self.findChild(QSlider, "mode_slider")
        self.current_mode = self.mode_slider.value()
        self.previous_mode = self.current_mode
        self.mode_slider.valueChanged.connect(self.mode_slider_changed)

        # Establish the current scale and current mode degrees
        self.current_scale = self.scales["major"]
        for scale_degree in self.current_scale["degrees"]:
            self.mode_degrees.append(scale_degree)

        # Create the mode_intervals list, which is used for the scale degree labels.
        # Lists the notes used in the given note set.
        self.mode_intervals = ['1', '', '2', '', '3', '4', '', '5', '', '6', '', '7', '8']

        # Connect the play chime buttons
        self.play_chime_button.clicked.connect(self.chime_on_off)

        self.play_chime_notes = False

        self.drone_root_label = self.current_scale["degrees"][0]
        self.drone_5th_label = self.current_scale["degrees"][4]

        # Connect the play scale button
        self.play_scale_button.clicked.connect(self.play_scale)

        # Connect the Reset All button
        self.reset_all_button.clicked.connect(self.reset_all)

        self.scale_note_finder()

        self.update_note_labels()

        self.drone_note()

        self.update_current_note_set()

    def mode_finder(self):
        """A method to create a list of scale degrees based on the current mode of the current scale."""

        self.mode_degrees.clear()
        temp_mode_degrees = []
        temp2_mode_degrees = []

        scale_degrees = self.current_scale["degrees"]  # List of degrees
        current_mode_degree = scale_degrees[self.current_mode - 1]  # Mode 1 = 0

        if self.current_scale["name"] == "Chromatic":
            self.mode_degrees = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        else:
            for degree in scale_degrees:
                if degree < current_mode_degree:
                    degree += 12
                    temp_mode_degrees.append(degree)
                else:
                    temp_mode_degrees.append(degree)
            temp_mode_degrees.append(current_mode_degree + 12)
            for i in temp_mode_degrees:
                if i not in temp2_mode_degrees:
                    temp2_mode_degrees.append(i)
            for item in temp2_mode_degrees:
                item -= current_mode_degree
                self.mode_degrees.append(item)

        self.mode_degrees.sort()

    def update_current_scale(self):
        """A method to update the self.current_scale variable."""
        new_scale = self.scale_combo_box.currentText()
        for key in self.scales:
            if new_scale == self.scales[key]["name"]:
                if new_scale != self.current_scale["name"]:
                    self.scale_changed(key)
                else:
                    pass
            else:
                pass

    def update_current_scale_label(self):
        """A method to update the self.current_scale_label with the root, scale, and mode"""

        one_mode = ["Whole Tone", "Chromatic"]
        two_modes = ["Augmented", "Diminished"]

        mode_index = self.current_mode - 1
        current_scale_label_0a = self.current_display_notes[0]
        current_scale_label_0b = str(self.current_scale["name"])
        current_scale_label_0c = " Scale"

        if self.current_scale["name"] in one_mode:
            current_scale_label_0d = ''
        elif self.current_scale["name"] in two_modes:
            current_scale_label_0d = ", " + self.current_scale["modes"][mode_index]
        else:
            current_scale_label_0d = ", Mode " + str(self.current_mode)

        current_scale_label_0 = current_scale_label_0a + " " \
                                + current_scale_label_0b \
                                + current_scale_label_0c \
                                + current_scale_label_0d

        current_scale_label_1 = self.current_scale["modes"][mode_index]

        if self.current_scale["name"] == self.current_scale["modes"][mode_index] or "Mode" in current_scale_label_1:
            self.label = current_scale_label_0
        else:
            self.label = current_scale_label_0 \
                         + " (" + current_scale_label_1 \
                         + ")"
        self.current_scale_label.setText(self.label)

    def mode_interval_finder(self):
        """A method to name the intervals (i.e. 1, 2, ♭3, etc.) for the current mode"""

        temp_ints = []
        temp_ints.clear()
        for interval in self.mode_intervals:
            temp_ints.append(interval)
        self.mode_intervals.clear()

        if len(self.mode_degrees) == 13:
            chromatic_scale = ['1', '♭2', '2', '♭3', '3', '4', '♭5',
                               '5', '♭6', '6', '♭7', '7', '8']
            for interval in chromatic_scale:
                self.mode_intervals.append(interval)

        elif len(self.mode_degrees) < 13:
            if 0 in self.mode_degrees:
                self.mode_intervals.append('1')

            if 1 in self.mode_degrees:
                self.mode_intervals.append('♭2')
            else:
                self.mode_intervals.append('')

            if 2 in self.mode_degrees:
                if 1 in self.mode_degrees and len(self.current_scale["degrees"]) == 9:
                    self.mode_intervals.append('2')
                elif 1 in self.mode_degrees:
                    self.mode_intervals.append('𝄫3')
                else:
                    self.mode_intervals.append('2')
            else:
                self.mode_intervals.append('')

            if 3 in self.mode_degrees:
                if len(self.current_scale["degrees"]) > 7:
                    if 1 not in self.mode_degrees and 2 not in self.mode_degrees:
                        self.mode_intervals.append('♯2')
                    elif '𝄫3' in self.mode_intervals:
                        self.mode_intervals.append('𝄫4')
                    else:
                        self.mode_intervals.append('♭3')
                elif len(self.current_scale["degrees"]) == 7:
                    if self.current_scale["name"] == 'Augmented' and self.current_mode % 2 != 0:
                        self.mode_intervals.append('♯2')
                    elif self.current_scale["name"] == 'Pelog' and self.current_mode == 4:
                        self.mode_intervals.append('♯2')
                    else:
                        self.mode_intervals.append('♭3')
                else:
                    self.mode_intervals.append('♭3')
            else:
                self.mode_intervals.append('')

            if 4 in self.mode_degrees:
                if len(self.current_scale["degrees"]) == 8:
                    if '♭3' in self.mode_intervals:
                        self.mode_intervals.append('♭4')
                    elif '𝄫3' in self.mode_intervals:
                        self.mode_intervals.append('♭4')
                    else:
                        self.mode_intervals.append('3')
                elif len(self.current_scale["degrees"]) == 6:
                    self.mode_intervals.append('3')
                elif len(self.current_scale["degrees"]) == 7:
                    if self.current_scale["name"] == 'Pelog' and self.current_mode == 1:
                        self.mode_intervals.append('♭4')
                    else:
                        self.mode_intervals.append('3')
                elif len(self.current_scale["degrees"]) == 9:
                    self.mode_intervals.append('3')
            else:
                self.mode_intervals.append('')

            if 5 in self.mode_degrees:
                if len(self.current_scale["degrees"]) == 8:
                    if self.current_scale["name"] == 'Enigmatic' and self.current_mode == 5:
                        self.mode_intervals.append('𝄫5')
                    elif '𝄫4' in self.mode_intervals:
                        self.mode_intervals.append('𝄫5')
                    elif '♭4' in self.mode_intervals:
                        self.mode_intervals.append('𝄫5')
                    elif '𝄫3' in self.mode_intervals:
                        self.mode_intervals.append('4')
                    elif '♭3' in self.mode_intervals:
                        self.mode_intervals.append('4')
                    elif '3' in self.mode_intervals:
                        self.mode_intervals.append('4')
                    else:
                        self.mode_intervals.append('♯3')
                else:
                    self.mode_intervals.append('4')
            else:
                self.mode_intervals.append('')

            if 6 in self.mode_degrees:
                if len(self.current_scale["degrees"]) == 8:
                    if '4' in self.mode_intervals:
                        self.mode_intervals.append('♭5')
                    elif '♭4' in self.mode_intervals:
                        self.mode_intervals.append('♭5')
                    elif '𝄫4' in self.mode_intervals:
                        self.mode_intervals.append('♭5')
                    else:
                        self.mode_intervals.append('♯4')
                elif len(self.current_scale["degrees"]) == 6:
                    if self.current_scale["name"] == 'Hirajōshi' and self.current_mode == 5:
                        self.mode_intervals.append('♯4')
                    else:
                        self.mode_intervals.append('♭5')
                elif len(self.current_scale["degrees"]) == 7:
                    if self.current_scale["name"] == 'Pelog' and self.current_mode == 2:
                        self.mode_intervals.append('♯4')
                    elif self.current_scale["name"] == 'Whole Tone':
                        self.mode_intervals.append('♯4')
                    else:
                        self.mode_intervals.append('♭5')
                elif len(self.current_scale["degrees"]) == 9:
                    if '4' in self.mode_intervals:
                        self.mode_intervals.append('♭5')
                    else:
                        self.mode_intervals.append('♯4')
            else:
                self.mode_intervals.append('')

            if 7 in self.mode_degrees:
                if len(self.current_scale["degrees"]) == 8:
                    if self.current_scale["name"] == 'Enigmatic Minor' and self.current_mode == 3:
                        self.mode_intervals.append('𝄪4')
                    elif self.current_scale["name"] == 'Enigmatic Minor' and self.current_mode == 4:
                        self.mode_intervals.append('𝄫6')
                    elif self.current_scale["name"] == 'Enigmatic Major' and self.current_mode == 2:
                        self.mode_intervals.append('𝄪4')
                    elif self.current_scale["name"] == 'Enigmatic Major' and self.current_mode == 4:
                        self.mode_intervals.append('𝄫6')
                    elif self.current_scale["name"] == 'Hungarian Major' and self.current_mode == 2:
                        self.mode_intervals.append('𝄫6')
                    elif self.current_scale["name"] == 'Composite II' and self.current_mode == 4:
                        self.mode_intervals.append('𝄫6')
                    elif self.current_scale["name"] == 'Ionian ♭5' and self.current_mode == 7:
                        self.mode_intervals.append('𝄫6')
                    elif self.current_scale["name"] == 'Locrian ♮7' and self.current_mode == 7:
                        self.mode_intervals.append('𝄫6')
                    elif self.current_scale["name"] == 'Persian' and self.current_mode == 7:
                        self.mode_intervals.append('𝄫6')
                    else:
                        self.mode_intervals.append('5')
                else:
                    self.mode_intervals.append('5')
            else:
                self.mode_intervals.append('')

            if 8 in self.mode_degrees:
                if len(self.current_scale["degrees"]) == 8:
                    if '5' in self.mode_intervals:
                        self.mode_intervals.append('♭6')
                    elif '♭5' in self.mode_intervals:
                        self.mode_intervals.append('♭6')
                    elif '𝄫5' in self.mode_intervals:
                        self.mode_intervals.append('♭6')
                    else:
                        self.mode_intervals.append('♯5')
                elif len(self.current_scale["degrees"]) == 6:
                    if self.current_scale["name"] == 'Major Pentatonic' and self.current_mode == 3:
                        self.mode_intervals.append('♯5')
                    elif self.current_scale["name"] == 'Minor Pentatonic' and self.current_mode == 4:
                        self.mode_intervals.append('♯5')
                    else:
                        self.mode_intervals.append('♭6')
                elif len(self.current_scale["degrees"]) == 7:
                    if self.current_scale["name"] == 'Whole Tone':
                        self.mode_intervals.append('♯5')
                    elif self.current_scale["name"] == 'Augmented' and self.current_mode % 2 == 0:
                        self.mode_intervals.append('♯5')
                    elif self.current_scale["name"] == 'Pelog' and self.current_mode == 4:
                        self.mode_intervals.append('♯5')
                    else:
                        self.mode_intervals.append('♭6')
                elif len(self.current_scale["degrees"]) == 9:
                    if self.current_scale["name"] == 'Bebop Dorian' and self.current_mode == 3:
                        self.mode_intervals.append('♭6')
                    elif '♯4' in self.mode_intervals:
                        self.mode_intervals.append('♯5')
                    else:
                        self.mode_intervals.append('♭6')
            else:
                self.mode_intervals.append('')

            if 9 in self.mode_degrees:
                if len(self.current_scale["degrees"]) == 8:
                    if self.current_scale["name"] == 'Enigmatic Minor' and self.current_mode == 2:
                        self.mode_intervals.append('𝄪5')
                    elif self.current_scale["name"] == 'Enigmatic Major' and self.current_mode == 2:
                        self.mode_intervals.append('𝄪5')
                    elif '♭6' in self.mode_intervals:
                        self.mode_intervals.append('𝄫7')
                    elif '𝄫6' in self.mode_intervals:
                        self.mode_intervals.append('𝄫7')
                    else:
                        self.mode_intervals.append('6')
                elif len(self.current_scale["degrees"]) == 6:
                    self.mode_intervals.append('6')
                elif len(self.current_scale["degrees"]) == 7:
                    if '♭6' in self.mode_intervals:
                        self.mode_intervals.append('𝄫7')
                    else:
                        self.mode_intervals.append('6')
                elif len(self.current_scale["degrees"]) == 9:
                    self.mode_intervals.append('6')
            else:
                self.mode_intervals.append('')

            if 10 in self.mode_degrees:
                if len(self.current_scale["degrees"]) == 8:
                    if '𝄫6' in self.mode_intervals:
                        self.mode_intervals.append('♭7')
                    elif '♭6' in self.mode_intervals:
                        self.mode_intervals.append('♭7')
                    elif '6' in self.mode_intervals:
                        self.mode_intervals.append('♭7')
                    elif self.mode_degrees[-2] == 10:
                        self.mode_intervals.append('♭7')
                    else:
                        self.mode_intervals.append('♯6')
                elif len(self.current_scale["degrees"]) == 6:
                    self.mode_intervals.append('♭7')
                elif len(self.current_scale["degrees"]) == 7:
                    self.mode_intervals.append('♭7')
                elif len(self.current_scale["degrees"]) == 9:
                    if self.current_scale["name"] == 'Bebop Dorian' and self.current_mode == 8:
                        self.mode_intervals.append('♯6')
                    else:
                        self.mode_intervals.append('♭7')
            else:
                self.mode_intervals.append('')

            if 11 in self.mode_degrees:
                self.mode_intervals.append('7')
            else:
                self.mode_intervals.append('')

            if 12 in self.mode_degrees:
                self.mode_intervals.append('8')

    def scale_note_finder(self):
        """A method to determine the correct note names for the current scale/mode"""

        if len(self.current_display_notes) < len(self.mode_degrees):
            pass
        else:
            self.current_display_notes.clear()

        temp_ints = []
        temp_ints.clear()

        temp_degrees = []

        for degree in self.mode_degrees:
            temp_degrees.append(degree)

        for interval in self.mode_intervals:
            temp_ints.append(interval)

        root_note = self.current_scale["roots"][str(self.current_mode)][self.root]  # 'C'

        current_key = self.roots[root_note]

        for key, value in current_key.items():
            if key in temp_ints:
                self.current_display_notes.append(value)

        if self.current_scale["name"] == "Chromatic" and self.root == 11 and self.current_mode == 11:
            self.current_display_notes[11] = '♫'

    def paintEvent(self, event):
        """A method to draw and update the graphicsView."""
        self._check_events()

    def _check_events(self):
        self.update_current_scale_label()
        self.update_current_scale()
        self.update_note_labels()
        self.update_current_note_set()
        self.mode_slider_changed()
        self.update_current_drones()
        self.check_chime_button()

    def check_chime_button(self):

        if self.play_chime_notes and not self.playing_chimes():
            self.play_chime_button.setText("Stop Chime")
            for degree in self.mode_degrees:
                self.do_in_background_as_well(self.play_chime, [degree])
        elif not self.play_chime_notes:
            self.play_chime_button.setText("Play Chime")

    def scale_changed(self, key):
        self.mode_slider.setValue(1)
        self.current_mode = self.mode_slider.value()
        self.current_scale = self.scales[key]
        self.scale_note_finder()
        self.mode_slider.setMaximum(len(self.current_scale["degrees"]) - 1)
        self.mode_interval_finder()
        self.mute_unused_notes()
        self.mode_finder()

        self.drone_first.stop()
        self.drone_second.stop()
        self.update_current_note_set()
        self.drone_note()

    def root_dial_changed(self):
        """A method to respond to the root dial being altered."""
        self.root = (int(self.root_dial.value()))
        self.root_label_display.setText(self.root_list[self.root])
        self.scale_note_finder()
        self.mute_unused_notes()
        self.mode_finder()

        self.drone_first.stop()
        self.drone_second.stop()
        self.update_current_note_set()
        self.drone_note()

    def mode_slider_changed(self):
        """A method to respond to the mode slider being moved."""
        self.current_mode = self.mode_slider.value()
        self.update_current_scale()
        self.scale_note_finder()
        self.update_note_labels()
        self.mute_unused_notes()
        self.mode_interval_finder()
        self.mode_finder()
        self.update_scale_degree_labels()

        count = 1
        if self.current_mode != self.previous_mode:
            self.root_dial_changed()
            count += 1
            if count > 1:
                self.previous_mode = self.current_mode
                count = 0

    def update_current_note_set(self):
        """A method to determine which audio samples to use, based on the current scale, root, and mode"""

        # Update the notes used based on the root dial setting
        for i in range(0, 13):
            si = "%02d" % i
            si = int(si) + self.root
            if int(si) < 10:
                si = "0" + str(si)
            else:
                pass

            self.current_note_set[i]['note'] = self.notes[int(si)]

            self.current_note_set[i]['drone'] = self.drones[int(si)]

        # Update each notes' volume based on the current value of the volume sliders
        for i in range(0, 13):
            si = "%02d" % i
            slider_name = "volume_slider_" + si
            slider = getattr(self, slider_name)

            self.current_note_set[i]['volume'] = slider.value() / 10

        self.drone_first.set_volume(self.drone_volume_slider_00.value() / 10)
        self.drone_second.set_volume(self.drone_volume_slider_01.value() / 10)

    def mute_unused_notes(self):
        """A method to mute notes not used in the current scale."""

        # Style sheet for lighter label
        light = "font: 10pt 'Malgun Gothic'; background-color: rgb(100, 125, 100)"

        # Style sheet for darkened label
        dark = "font: 10pt 'Malgun Gothic'; background-color: rgb(50, 50, 50)"

        self.unmuted_notes = []
        self.unmuted_notes.clear()

        for i in range(0, 13):
            if i in self.mode_degrees:
                self.unmuted_notes.append(i)
            else:
                pass

        for i in range(0, 13):
            si = "%02d" % i

            # Find the note labels
            label_name = "note_" + si + "_label"
            note_label = getattr(self, label_name)

            # Find the scale degree labels
            degree_label_name = "scale_degree_" + si + "_label"
            degree_label = getattr(self, degree_label_name)

            if i in self.mode_degrees:
                note_label.setStyleSheet(light)
                degree_label.setStyleSheet(light)
            else:
                note_label.setStyleSheet(dark)
                degree_label.setStyleSheet(dark)

    def update_scale_degree_labels(self):
        """A method to update the scale degree labels when a new scale and/or mode is selected"""

        for i in range(0, 12):
            si = "%02d" % i

            # Find the scale degree label
            scale_degree_label_name = "scale_degree_" + si + "_label"
            scale_degree_label_widget = getattr(self, scale_degree_label_name)

            if i in self.unmuted_notes:
                scale_degree_label_widget.setText(self.mode_intervals[i])
            else:
                scale_degree_label_widget.setText('')

    def update_note_labels(self):
        """A method to update the note labels."""

        if len(self.current_display_notes) < len(self.mode_degrees):
            dif = len(self.mode_degrees) - len(self.current_display_notes)
            for i in range(dif):
                self.current_display_notes.append('')
        else:
            pass

        index = 0

        for i in range(0, 13):
            si = "%02d" % i  # String Index
            label_name = "note_" + si + "_label"
            label_widget = getattr(self, label_name)

            if i in self.mode_degrees:
                label = self.current_display_notes[index]
                index += 1
            else:
                label = ''

            previous_label = label_widget.text()

            label_widget.setText(label)

    def update_current_drones(self):
        """A method to update the drone notes displayed and played"""

        self.drone_root_label = self.note_00_label.text()
        self.drone_root = self.current_note_set[0]['drone']

        if len(self.mode_degrees) != 6:
            if "5" in self.mode_intervals:
                self.drone_5th_label = self.note_07_label.text()
                self.drone_5th = self.current_note_set[7]['drone']
            elif "♭5" in self.mode_intervals:
                self.drone_5th_label = self.note_06_label.text()
                self.drone_5th = self.current_note_set[6]['drone']
            elif "♯5" in self.mode_intervals:
                self.drone_5th_label = self.note_08_label.text()
                self.drone_5th = self.current_note_set[8]['drone']
            elif "𝄫5" in self.mode_intervals:
                self.drone_5th_label = self.note_05_label.text()
                self.drone_5th = self.current_note_set[5]['drone']
            elif "𝄪5" in self.mode_intervals:
                self.drone_5th_label = self.note_09_label.text()
                self.drone_5th = self.current_note_set[9]['drone']
            else:
                self.drone_5th_label = self.note_05_label.text()
                self.drone_5th = self.current_note_set[5]['drone']
        else:
            if "5" in self.mode_intervals:
                self.drone_5th_label = self.note_07_label.text()
                self.drone_5th = self.current_note_set[7]['drone']
            elif "♭5" in self.mode_intervals:
                self.drone_5th_label = self.note_06_label.text()
                self.drone_5th = self.current_note_set[6]['drone']
            elif "♯5" in self.mode_intervals:
                self.drone_5th_label = self.note_08_label.text()
                self.drone_5th = self.current_note_set[8]['drone']
            elif "𝄫5" in self.mode_intervals:
                self.drone_5th_label = self.note_05_label.text()
                self.drone_5th = self.current_note_set[5]['drone']
            else:
                self.drone_5th_label = self.note_05_label.text()
                self.drone_5th = self.current_note_set[5]['drone']

        self.drone_label_00.setText(self.drone_root_label)
        self.drone_label_01.setText(self.drone_5th_label)

    def keyPressEvent(self, QKeyEvent):
        """A method to play notes when keys are pressed."""

        if len(self.mode_degrees) > 5:
            if QKeyEvent.key() == Qt.Key_1:
                self.play_note(0, self.current_note_set[self.mode_degrees[0]]['note'][self.root + self.mode_degrees[0]],
                               self.current_note_set[self.mode_degrees[0]]['volume'])
            elif QKeyEvent.key() == Qt.Key_2:
                self.play_note(1, self.current_note_set[self.mode_degrees[1]]['note'][self.root + self.mode_degrees[1]],
                               self.current_note_set[self.mode_degrees[1]]['volume'])
            elif QKeyEvent.key() == Qt.Key_3:
                self.play_note(2, self.current_note_set[self.mode_degrees[2]]['note'][self.root + self.mode_degrees[2]],
                               self.current_note_set[self.mode_degrees[2]]['volume'])
            elif QKeyEvent.key() == Qt.Key_4:
                self.play_note(3, self.current_note_set[self.mode_degrees[3]]['note'][self.root + self.mode_degrees[3]],
                               self.current_note_set[self.mode_degrees[3]]['volume'])
            elif QKeyEvent.key() == Qt.Key_5:
                self.play_note(4, self.current_note_set[self.mode_degrees[4]]['note'][self.root + self.mode_degrees[4]],
                               self.current_note_set[self.mode_degrees[4]]['volume'])
            elif QKeyEvent.key() == Qt.Key_6:
                self.play_note(5, self.current_note_set[self.mode_degrees[5]]['note'][self.root + self.mode_degrees[5]],
                               self.current_note_set[self.mode_degrees[5]]['volume'])
        if len(self.mode_degrees) > 6:
            if QKeyEvent.key() == Qt.Key_7:
                self.play_note(6, self.current_note_set[self.mode_degrees[6]]['note'][self.root + self.mode_degrees[6]],
                               self.current_note_set[self.mode_degrees[6]]['volume'])
        if len(self.mode_degrees) > 7:
            if QKeyEvent.key() == Qt.Key_8:
                self.play_note(7, self.current_note_set[self.mode_degrees[7]]['note'][self.root + self.mode_degrees[7]],
                               self.current_note_set[self.mode_degrees[7]]['volume'])
        if len(self.mode_degrees) > 8:
            if QKeyEvent.key() == Qt.Key_9:
                self.play_note(8, self.current_note_set[self.mode_degrees[8]]['note'][self.root + self.mode_degrees[8]],
                               self.current_note_set[self.mode_degrees[8]]['volume'])
        if len(self.mode_degrees) > 9:
            if QKeyEvent.key() == Qt.Key_0:
                self.play_note(9, self.current_note_set[self.mode_degrees[9]]['note'][self.root + self.mode_degrees[9]],
                               self.current_note_set[self.mode_degrees[9]]['volume'])
        if len(self.mode_degrees) > 10:
            if QKeyEvent.key() == Qt.Key_Minus:
                self.play_note(10, self.current_note_set[self.mode_degrees[10]]['note'][self.root + self.mode_degrees[10]],
                               self.current_note_set[self.mode_degrees[10]]['volume'])
            elif QKeyEvent.key() == Qt.Key_Equal:
                self.play_note(11, self.current_note_set[self.mode_degrees[11]]['note'][self.root + self.mode_degrees[11]],
                               self.current_note_set[self.mode_degrees[11]]['volume'])
            elif QKeyEvent.key() == Qt.Key_Backspace:
                self.play_note(12, self.current_note_set[self.mode_degrees[12]]['note'][self.root + self.mode_degrees[12]],
                               self.current_note_set[self.mode_degrees[12]]['volume'])

        if QKeyEvent.key() == Qt.Key_Delete:
            self.allow_play = False

    def chime_on_off(self):
        """A method to respond to the Play Chime button. Turns the chime function on or off"""

        if self.play_chime_notes:
            self.play_chime_notes = False
        elif not self.play_chime_notes:
            self.play_chime_notes = True

        # self.check_chime_button()

    def do_in_background(self, fcn, ts, kwargs):

        self.start_time = time.time()

        # Sleep for the amount of time left over from the start time to the current time stamp
        sleep_time = self.start_time + 1 - time.time()
        time.sleep(sleep_time)

        thread_object = threading.Thread(target=fcn, args=kwargs)
        thread_object.start()

    def do_in_background_also(self, fcn):

        thread_object = threading.Thread(target=fcn)
        thread_object.start()

    def do_in_background_as_well(self, fcn, kwargs):

        thread_object = threading.Thread(target=fcn, args=kwargs)
        thread_object.start()

    def play_chime(self, degree):
        """A method to randomly play notes from the current scale (a la wind chimes). Responds to Play Chime button."""

        current_note_dict = self.current_note_set[degree]

        self.playing_chimes_list.append(True)

        rand_time = random.randint(0, 25) / 5

        time.sleep(float(rand_time))

        # rand = random.choice(self.mode_degrees)
        current_note = current_note_dict['note'][self.root + degree]
        current_volume = current_note_dict['volume']
        self.play_note(13, current_note, current_volume)

        self.playing_chimes_list.pop()

    def playing_chimes(self):

        for value in self.playing_chimes_list:
            if value:
                return True
        return False

    def play_scale(self):
        """A method to play the current scale/mode in ascending order. Responds to Play Scale button."""

        mixer = pygame.mixer
        mixer.Channel(14)

        self.start_time = time.time()

        for ts, i in enumerate(self.mode_degrees):
            self.do_in_background(self.play_note, ts, (14, self.current_note_set[i]['note'][self.root + i],
                                                       self.current_note_set[i]['volume']))

    def sleep(self, value):

        time.sleep(value)

    def play_note(self, channel, note, volume):
        """A method to play the musical notes."""

        mixer = pygame.mixer
        mixer.Channel(channel)
        sound = mixer.Sound(note)
        sound.set_volume(volume)
        sound.play()

    def drone_note(self):

        bits = 16

        self.update_current_drones()

        pygame.mixer.pre_init(44100, -bits, 2)
        mixer = pygame.mixer
        mixer2 = pygame.mixer
        mixer.Channel(14)
        mixer2.Channel(15)

        duration = 1.0  # in seconds
        # freqency for the left speaker
        frequency_l = float(self.drone_root)
        # frequency for the right speaker
        frequency_r = float(self.drone_5th)

        sample_rate = 44100

        n_samples = int(round(duration * sample_rate))

        # setup our numpy array to handle 16 bit ints, which is what we set our mixer to expect with "bits" up above
        buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
        buf2 = numpy.zeros((n_samples, 2), dtype=numpy.int16)
        max_sample = 2 ** (bits - 1) - 1

        for s in range(n_samples):
            t = float(s) / sample_rate  # time in seconds

            # grab the x-coordinate of the sine wave at a given time,
            # while constraining the sample to what our mixer is set to with "bits"
            buf[s][0] = int(round(max_sample * math.sin(2 * math.pi * frequency_l * t)))  # left
            buf[s][1] = int(round(max_sample * math.sin(2 * math.pi * frequency_l * t)))  # right

        for s in range(n_samples):
            t = float(s) / sample_rate  # time in seconds

            # grab the x-coordinate of the sine wave at a given time,
            # while constraining the sample to what our mixer is set to with "bits"
            buf2[s][0] = int(round(max_sample * math.sin(2 * math.pi * frequency_r * t)))  # left
            buf2[s][1] = int(round(max_sample * math.sin(2 * math.pi * frequency_r * t)))  # right

        sound = pygame.sndarray.make_sound(buf)
        sound2 = pygame.sndarray.make_sound(buf2)
        # play once, then loop forever
        self.drone_first = mixer.Sound(sound)
        self.drone_second = mixer2.Sound(sound2)
        self.drone_first.play(loops=-1)
        self.drone_second.play(loops=-1)
        self.drone_first.set_volume(self.drone_volume_slider_00.value() / 20)
        self.drone_second.set_volume(self.drone_volume_slider_01.value() / 20)

    def reset_all(self):
        """A method to reset all settings to their default state"""

        # Reset the root
        self.root = 5
        self.root_dial.setValue(self.root)
        self.root_label_display.setText(self.root_list[self.root])

        # Reset the mode slider
        self.mode_slider.setValue(1)

        # Reset the drones
        self.drone_slider_00.setValue(0)
        self.drone_slider_01.setValue(0)

        # Reset the current scale
        self.scale_combo_box.setCurrentText("Major")

        # Reset the volume sliders
        for i in range(0, 13):
            si = "%02d" % i
            slider_name = "volume_slider_" + si
            slider = getattr(self, slider_name)

            slider.setValue(5)


class MyApplication(QApplication):
    def __init__(self, *args):
        super().__init__(*args)

    def set_program(self, ukulele_chimes):
        self.ukulele_chimes = ukulele_chimes


if __name__ == '__main__':
    app = MyApplication(sys.argv)
    ukulele_chimes = UkuleleChimes()
    app.set_program(ukulele_chimes)
    ukulele_chimes.show()

    sys.exit(app.exec())
