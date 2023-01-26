# Ukulele-Chimes

The primary function of Ukulele Chimes is to replicate the sound of wind chimes using pre-recorded audio from a ukulele. The notes of a given musical scale are played at random intervals. The familiar-sounding major scale is used by default, although many other scales may be used. Each scale has its own "modes" (the same sequence of notes as the respective scale, although a different note of the scale is used at the tonal center). Aditionally, the tonic may be changed to any one of the twelve notes used in Western music. This allows for thousands of options.

## Requirements
Ukulele Chimes requires the following packages to run:<br />
* numpy<br />
* PyQt5<br />
* pygame<br />

## Controls
   **Play Chime** - The notes of the scale are played at random<br />
   **Play Scale** - The notes of the scale are played as quarter notes in ascending order<br />
   **Reset All** - All settings are returned to their default state<br />
   **Tonic Dial** - Adjusts the tonic note of the scale<br />
   **Scale Combo Box** - Select the scale<br />
   **Mode Slider** - Select the mode of the current scale<br />
   **Drone Volume Sliders** - Adjust the volume of the drone notes (based on the root and the fifth of the scale)<br />
   **Note Volume Sliders** - Adjust the volume of each note. (While the scale is set to "Chromatic", adjusting the volume
        sliders may allow for user-created scales when the "Play Chime" button is active.)<br />

   **Keys 1-8** - For most scales, each note of the current note set may be played manually using these keys.
        If a scale has more than eight notes, keys 9, 0, -, =, and BACKSPACE are incorporated.
