#!/usr/bin/env python
# Resize image files keeping the aspect ratio

import os
import re
import tempfile
from argparse import ArgumentParser
from dataclasses import dataclass
from math import ceil
from time import time


@dataclass
class Size:
    width: int
    height: int

    def __repr__(self) -> str:
        return f"{self.width}x{self.height}"


class CalculateSize:
    def __init__(self, original: Size):
        self.original = original

    def calculate(self, target: Size) -> Size:
        size = self.based_on_height(target.height)
        if size.width < target.width:
            size = self.based_on_width(target.width)
        return size

    def based_on_width(self, width: int) -> Size:
        aspect = self.original.height / self.original.width
        height = aspect * width
        size = Size(ceil(width), ceil(height))
        return size

    def based_on_height(self, height: int) -> Size:
        aspect = self.original.width / self.original.height
        width = aspect * height
        size = Size(ceil(width), ceil(height))
        return size


def parse_size(size: str) -> Size:
    width, height = size.split('x')
    size = Size(int(width), int(height))
    return size


def get_original_size(file: str) -> Size:
    proc = os.popen(f"file '{file}'")
    if proc._proc.wait() != 0:
        raise Exception("'file' program run into errors")
    output = proc._proc.stdout.read()
    sizes = re.findall(r'([0-9]*[ ]?x[ ]?[0-9]*)', output)
    if not sizes:
        raise Exception("'file' program don't showed any size")
    return parse_size(sizes[-1])


def convert(inputFile: str, output: str, size: Size):
    logfile = tempfile.mktemp()
    print(f"Converting {input} [→ {size}]...")
    proc = os.popen(
        " ".join([
            "ffmpeg -y",
            f"-i '{inputFile}'",
            f"-s {size}",
            f"'{output}'",
            f"1>{logfile} 2>{logfile}"
        ])
    )
    if proc._proc.wait() != 0:
        print(f"Failed to convert, ffmpeg log {logfile}")
        exit(4)


def parse_arguments():
    args = ArgumentParser(
        description="Resize images keeping the original aspect ratio",
        epilog="if output is omitted the original file will be replaced by the resized one"
    )
    args.add_argument("target", help="output target size(i.e: 1080x720)")
    args.add_argument("input", help="input image")
    args.add_argument("-o", "--output", help="output file")
    return args.parse_args()


def main():
    started_at = time()
    arg = parse_arguments()
    original_size: Size
    target_size: Size
    try:
        target_size = parse_size(arg.target)
    except:
        print("invalid target size")
        exit(1)
    if not os.path.isfile(arg.input):
        print("Input file not found")
        exit(2)
    try:
        original_size = get_original_size(arg.input)
    except Exception as e:
        print(f"Failed to get original size: {e}")
        exit(3)
    output_size = CalculateSize(original_size).calculate(target_size)
    output = arg.output or arg.input
    convert(arg.input, output, output_size)
    finished_at = time()
    print(f"Converted with success in {finished_at-started_at:.2f} seconds.")


if __name__ == "__main__":
    main()
