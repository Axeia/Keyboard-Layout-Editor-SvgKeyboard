# Keyboard-Layout-Editor-SvgKeyboard
A python port of github.com/ijprest/keyboard-layout-editor capable of generating an SVG

## What is this? 
This is a port of [keyboard-layout-editor](https://github.com/ijprest/keyboard-layout-editor) to pure python that generates a SVG image.
* [pysjon5 by dpranke](https://github.com/dpranke/pyjson5) is used for reading in KLE's json files which are in JSON5. If you're trying to read data right from "Raw Data" tab on the keyboard-layout-editor site be warned that it is not valid JSON5 but can be made into it by putting some square brackets around it[].
* [pykle_serial by hajimen](https://github.com/hajimen/pykle_serial/) is used for parsing the KLE data

Everything else was written by myself, heavily based on the [TypeScript version](https://github.com/ijprest/keyboard-layout-editor) of keyboard-layout-editor. 

## What can it do?
* It can take input from keyboard-layout-editor.com and turn it into an SVG 
* It can do Matrix manipulations which are used to position the keys - including rotated layouts (Python has no native Matrix support out of the box)
* It can do somewhat advanced color manipulation - basically the only thing it does is calculate a lighter version of a given color but this is achieved by taking a hexcode and converting it back and forth between 5 colorspaces with some advanced maths. 

## What can't it do?
The code for rendering fonts on top of keycaps is rudimentary at best. I have not really looked up how it is done in the Typescript version that creates static images (not SVGs) and their SVG version foregoes font legends entirely.
The keycaps might differ in appearance compared to what you see on the website.

## How to get started?
Download the entire thing and just run the test.py file and it should create a keyboard.svg file in the same directory.

## Why was this made?
I'm in the process of writing a FreeCAD macro and this was an excercise to learn Python (which is new to me) and to have a fancy UI that previews the keyboard code as an SVG. 
Initially I wrote my own code but as I got confused by the unusual choices made in the KLE syntax and trying to find documentation on it I found [pykle_serial](https://github.com/hajimen/pykle_serial/) instead. Why re-invent the wheel right?

## Why am I not using all of it myself?
I wanted this to be a straight forward port of keyboard-layout-editor's TypeScript so I can confirm the results are the same. Now that I know it works as expected and I have tested this with various keyboard layouts I can start deviating from it for my Macro.
Having learned some Python whilst porting this over and having a better idea of how it works and what I from it I have a good starting point to start deviating from.

## Disclaimer
This is my first experience with Python so the code might not be cleanest code ever written. 
The Typescript for the color calculations was hard to understand as I wasn't familiar with some of the Typescript syntax used. It does however seem to work perfectly fine.
render.py compared to the original render.js has been simplified somewhat as I didn't see the need to calculate everything in pixels and milimeters as milimeters work fine for a SVG and can just be scaled to whatever is needed from there. The SVG might not look exactly like the SVGs you can create on keyboard-layout-editor.com but the positioning and keycap outlines (the important bits) should be the exact same.

## License
As the project uses pyjson5 (Apache 2.0 license) and pykle_serial(MIT License) you may consider this project Apache 2.0 licensed as well as it seems to be more restrictive license of the two. 
The KLE Typescript that I have more or less ported over is originally MIT licensed.

