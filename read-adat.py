#!/usr/bin/python3

import zlib
import struct

import sys
import os
from dataclasses import dataclass

TOC_ENTRY_LEN = 128 + 4*4

@dataclass
class Entry:
    name: str
    offset: int
    length: int
    compressed_length: int
    u0: int

def read_content(fh):
    # read header
    magic = fh.read(4)
    if magic != b"ADAT":
        raise RuntimeError(f"Not an ADAT file? Found magic: {magic}")
    
    toc_offset, toc_length, version = struct.unpack("<LLL", fh.read(4*3))

    if version != 9:
        raise RuntimeError(f"Unsupported version: {version}, expected 9")
    
    entry_count = toc_length // TOC_ENTRY_LEN
    if entry_count == 0:
        raise RuntimeError("Empty index")

    # read toc
    entries = []
    fh.seek(toc_offset)
    for _ in range(entry_count):
        name = fh.read(128).decode("utf8").rstrip("\0")
        offset, length, compressed_length, u0 = struct.unpack("<LLLL", fh.read(16))
        entries.append(Entry(name, offset, length, compressed_length, u0))

    return entries

def list_files(filename):
    entries = None
    with open(filename, "rb") as file:
        entries = read_content(file)
    for entry in entries:
        print(entry.name)

def extract_file(filename, path):
    content = None
    with open(filename, "rb") as file:
        entries = dict([ (f.name, f) for f in read_content(file)])
        if not path in entries:
            raise RuntimeError(f"path {path} for found")
        
        entry = entries[path]
        file.seek(entry.offset)
        buffer = file.read(entry.compressed_length)

        content = zlib.decompress(buffer, bufsize=entry.length)

    ospath = "data/" + path.replace("\\", "/")
    os.makedirs( os.path.dirname(ospath), exist_ok=True )
    with open(ospath, "wb") as file:
        file.write(content)
    print(f"extracted: {ospath}")

def main(self, action, filename, path = ""):
    if action == "ls" or action == "list":
        list_files(filename)
    elif action == "extract" or action == "x":
        extract_file(filename, path)
    else:
        raise RuntimeError(f"unknown action {action}, known: list, extract")

main(*sys.argv)