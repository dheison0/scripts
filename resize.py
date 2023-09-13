#!/usr/bin/env python
# Description: Resize image files keeping the aspect ratio
# Needs: ffmpeg installed

from argparse import ArgumentParser
from dataclasses import dataclass
from logging import INFO, basicConfig, error, info
from math import ceil
from os import path, popen
from re import findall
from tempfile import mktemp as mktempfile
from time import time

basicConfig(format="[%(levelname)s] %(message)s", level=INFO)


@dataclass
class Size:
    width: int
    height: int

    def __repr__(self) -> str:
        return f"{self.width}x{self.height}"


class AspectBasedSizeCalculator:
    aspect: float

    def __init__(self, original_size: Size):
        self.aspect = original_size.width / original_size.height

    def best_fit(self, target_size: Size) -> Size:
        size = self.height_based(target_size.height)
        if size.width < target_size.width or size.height < target_size.height:
            size = self.width_based(target_size.width)
        return size

    def width_based(self, width: int) -> Size:
        height = width / self.aspect
        size = Size(ceil(width), ceil(height))
        return size

    def height_based(self, height: int) -> Size:
        width = height * self.aspect
        size = Size(ceil(width), ceil(height))
        return size


def parse_size(size: str) -> Size:
    width, height = size.split("x")
    size = Size(int(width), int(height))
    return size


def get_original_size(file: str) -> Size:
    proc = popen(f"file '{file}'")
    if proc._proc.wait() != 0:
        raise Exception("'file' program run into errors")
    output = proc._proc.stdout.read()
    sizes = findall(r"([0-9]*[ ]?x[ ]?[0-9]*)", output)
    if not sizes:
        raise Exception("'file' program don't showed any size")
    return parse_size(sizes[-1])


def convert(input_file: str, output_file: str, target_size: Size):
    logfile = mktempfile()
    proc = popen(
        " ".join(
            [
                "ffmpeg -y",
                f"-i '{input_file}'",
                f"-s {target_size}",
                f"'{output_file}'",
                f"1>{logfile} 2>{logfile}",
            ]
        )
    )
    if proc._proc.wait() != 0:
        error(f"Failed to convert, ffmpeg log {logfile}")
        exit(4)


def parse_arguments():
    args = ArgumentParser(
        description="Resize images keeping the original aspect ratio",
    )
    args.add_argument("size", help="wanted output size(i.e: 1080x720)")
    args.add_argument("input", help="input image")
    args.add_argument(
        "-o", "--output", help="output file [default: resized-{filename}]"
    )
    return args.parse_args()


def main():
    arg = parse_arguments()
    try:
        target_size = parse_size(arg.size)
    except ValueError:
        error("Invalid target size")
        exit(1)
    if not path.isfile(arg.input):
        error("Input file not found")
        exit(2)
    try:
        original_size = get_original_size(arg.input)
    except Exception as e:
        error(f"Failed to get original size: {e}")
        exit(3)
    output_size = AspectBasedSizeCalculator(original_size).best_fit(target_size)
    output_file = arg.output or ("resized-" + arg.input.split("/")[-1])
    info(f"Converting {arg.input} [{original_size} → {output_size}]...")
    started_at = time()
    convert(arg.input, output_file, output_size)
    finished_at = time()
    info(f"Converted with success in {finished_at-started_at:.2f} seconds.")


if __name__ == "__main__":
    main()
