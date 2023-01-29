# Ukulele-Chimes

![GUI_screenshot_01](https://user-images.githubusercontent.com/65179426/214991660-c28c5ab2-bce6-442e-869c-910f149b2655.jpg)

The primary function of Ukulele Chimes is to replicate the sound of wind chimes using pre-recorded audio from a ukulele. The notes of a given musical scale are played at random intervals. The user also has the option to hear the selected scale in a mid-tempo, ascending order. The familiar-sounding major scale is used by default, although many other scales may be used. Each scale has its own modes, which can be selected with a slider. Additionally, the tonic may be changed to any one of the twelve notes used in Western music. This allows for thousands of options. The current tonic, scale, mode, and name of the mode (when applicable) is shown in the center of the user interface window.

Each of the twelve possible notes in the octave also has its own volume slider. Setting a note's volume to "0" in any given scale may result in even more possibilities when using the chime function.

If you find yourself getting lost in an exotic scale, not knowing where the tonal center is, there are drone notes that may be played in the background. There is a drone for the tonic note, as well as the current scale's dominant note (in many cases, the fifth note in the scale).

Ukulele Chimes may certainly be used if you want to have some relaxing, ambient music playing. It also may be used as an educational tool. The display labels corresponding to the twelve notes of the octave change color when available in the current scale. This is a great way to visualize the intervals between notes of different scales.

## Requirements
Ukulele Chimes requires the following packages to run:<br />
* numpy<br />
* PyQt5<br />
* pygame<br />

## Scale Options
<b>Heptatonic:</b><br />
* Major<br />
* Minor<br />
* Melodic Minor<br />
* Harmonic Minor<br />
* Harmonic Major<br />
* Hungarian Minor<br />
* Hungarian Major<br />
* Neapolitan Minor<br />
* Neapolitan Major<br />
* Enigmatic Minor<br />
* Enigmatic Major<br />
* Composite II<br />
* Ionian ♭5<br />
* Locrian ♮7<br />
* Persian<br />

<b>Pentatonic:</b><br />
* Major Pentatonic<br />
* Minor Pentatonic<br />
* Kumoi<br />
* Hirajōshi<br />

<b>Hexatonic:</b><br />
* Whole Tone<br />
* Blues<br />
* Augmented<br />
* Pelog<br />
* Dominant Suspended<br />

<b>Octatonic:</b><br />
* Diminished<br />
* Eight Tone Spanish<br />
* Bebop Locrian ♮2<br />
* Bebop Dominant<br />
* Bebop Dorian<br />
* Bebop Major<br />

<b>Other:</b><br />
* Chromatic

## Controls
   **Play/Stop Chime** - The notes of the scale are played at random<br />
   **Play Scale** - The notes of the scale are played as quarter notes in ascending order<br />
   **Reset All** - All settings are returned to their default state<br />
   **Tonic Dial** - Adjusts the tonic note of the scale<br />
   **Scale Combo Box** - Select the scale<br />
   **Mode Slider** - Select the mode of the current scale<br />
   **Drone Volume Sliders** - Adjust the volume of the drone notes (based on the root and the fifth of the scale)<br />
   **Note Volume Sliders** - Adjust the volume of each note. (While the scale is set to "Chromatic",<br />
        &emsp;adjusting the volume sliders may allow for user-created scales when the "Play Chime" button is active.)<br />

   **Keys 1-8** - For most scales, each note of the current note set may be played manually using these keys.<br />
        &emsp;If a scale has more than eight notes, keys 9, 0, -, =, and BACKSPACE are incorporated.
        
  ![GUI_screenshot_02](https://user-images.githubusercontent.com/65179426/214991695-10e759ae-c33e-4165-b86b-e9b53634094d.jpg)

