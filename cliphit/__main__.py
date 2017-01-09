#!/usr/bin/env python

import argparse
import sys

import numpy as np
import pygame.midi
import pyaudio


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK_SEC = 1/60.
CHUNK_SIZE = int(RATE * CHUNK_SEC)

PERCUSSION_CHANNEL = 9
PERCUSSION_MAP = {
    35: "Bass Drum 2",
    36: "Bass Drum 1",
    37: "Side Stick",
    38: "Snare Drum 1",
    39: "Hand Clap",
    40: "Snare Drum 2",
    41: "Low Tom 2",
    42: "Closed Hi-hat",
    43: "Low Tom 1",
    44: "Pedal Hi-hat",
    45: "Mid Tom 2",
    46: "Open Hi-hat",
    47: "Mid Tom 1",
    48: "High Tom 2",
    49: "Crash Cymbal 1",
    50: "High Tom 1",
    51: "Ride Cymbal 1",
    52: "Chinese Cymbal",
    53: "Ride Bell",
    54: "Tambourine",
    55: "Splash Cymbal",
    56: "Cowbell",
    57: "Crash Cymbal 2",
    58: "Vibra Slap",
    59: "Ride Cymbal 2",
    60: "High Bongo",
    61: "Low Bongo",
    62: "Mute High Conga",
    63: "Open High Conga",
    64: "Low Conga",
    65: "High Timbale",
    66: "Low Timbale",
    67: "High Agogo",
    68: "Low Agogo",
    69: "Cabasa",
    70: "Maracas",
    71: "Short Whistle",
    72: "Long Whistle",
    73: "Short Guiro",
    74: "Long Guiro",
    75: "Claves",
    76: "High Wood Block",
    77: "Low Wood Block",
    78: "Mute Cuica",
    79: "Open Cuica",
    80: "Mute Triangle",
    81: "Open Triangle"
}


def build_argparser():
    parser = argparse.ArgumentParser(description='Make anything into drum!')
    parser.add_argument(
        '-t',
        '--tone',
        type=int,
        default=36,
        help='''Percussion note number. Default to 36, Bass Drum 1.
    See https://ja.wikipedia.org/wiki/General_MIDI#Percussion_notes .
'''
    )
    parser.add_argument(
        '-o',
        '--output_midi_device_id',
        type=int,
        default=None,
        help='Output MIDI device id.'
    )
    parser.add_argument(
        '-i',
        '--input_device_id',
        type=int,
        default=None,
        help='Input MIC device id.'
    )
    parser.add_argument(
        '-r',
        '--volume_rate',
        type=int,
        default=5,
        help='Volume rate parameter.'
    )
    parser.add_argument(
        '-v',
        '--volume_threshold',
        type=int,
        default=10,
        help='Volume threhold.'
    )
    return parser


def main(argv):
    argparser = build_argparser()
    args = argparser.parse_args(argv[1:])

    audio = pyaudio.PyAudio()
    pygame.midi.init()

    tone = args.tone
    input_device_id = (
        args.input_device_id if args.input_device_id is not None
        else audio.get_default_input_device_info()['index']
    )
    output_midi_device_id = (
        args.output_midi_device_id if args.output_midi_device_id is not None
        else pygame.midi.get_default_output_id()
    )
    volume_rate = args.volume_rate
    volume_threshold = args.volume_threshold

    print("Tone: {} ({})".format(args.tone, PERCUSSION_MAP[args.tone]))
    print("Input Device: {}".format(input_device_id))
    print("Output MIDI Device: {}".format(output_midi_device_id))

    try:
        midi_output = pygame.midi.Output(output_midi_device_id)
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=input_device_id,
            frames_per_buffer=CHUNK_SIZE
        )

        prev_volume = 0
        while True:
            data = np.fromstring(stream.read(CHUNK_SIZE), dtype=np.int16)
            volume = int(np.absolute(data).mean())
            diff = volume - prev_volume
            if diff > volume_threshold:
                velocity = min(127, volume*volume_rate)
                midi_output.note_on(tone, velocity, channel=PERCUSSION_CHANNEL)
            prev_volume = volume

    finally:
        if 'midi_output' in locals():
            midi_output.close()
        pygame.midi.quit()


if __name__ == '__main__':
    exit(main(sys.argv))
