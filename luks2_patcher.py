#!/usr/bin/env python
import argparse
import hashlib
import json

LUKS2_BINARY_HEADER_SIZE = 0x1000
LUKS2_CSUM_OFFSET = 0x1c0
LUKS2_CSUM_LENGTH = 32

def patch_client_pin(json_area):
    d = json.loads(json_area)
    d["tokens"]["0"]["fido2-clientPin-required"] = False
    return json.dumps(d).encode()

def dump_json(json_area):
    d = json.loads(json_area)
    with open("header.json", "w") as json_header:
        json.dump(d, json_header) 
    print("JSON Area saved in header.json.")

def patch_header(filename):
    with open("header.json", "r") as json_header:
        d = json.load(json_header) 
    print("JSON Area loaded from header.json.")
    json_area = json.dumps(d).encode()
    
    with open(filename, "r+b") as bin:
        header = bin.read(LUKS2_CSUM_OFFSET)
        header_size = int.from_bytes(header[8:16])
        header += b"\x00" * LUKS2_CSUM_LENGTH
        bin.seek(LUKS2_CSUM_OFFSET + LUKS2_CSUM_LENGTH)
        header += bin.read(LUKS2_BINARY_HEADER_SIZE-LUKS2_CSUM_OFFSET-LUKS2_CSUM_LENGTH)
        # Patch JSON area
        bin.write(json_area)
        header += json_area + b"\x00" * (header_size-LUKS2_BINARY_HEADER_SIZE-len(json_area))
        
        # Compute hash
        h = hashlib.sha256()
        h.update(header)
        new_csum = h.digest()
        
        bin.seek(LUKS2_CSUM_OFFSET)
        bin.write(new_csum)
    
    print(f"Patched checksum: {new_csum.hex()}")
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LUKS2 JSON manipulation tool')
    parser.add_argument('filename')
    parser.add_argument('-d', '--dump', action='store_true', help="dump the JSON area")
    parser.add_argument('-p', '--patch', action='store_true', help="patch the JSON area")
    args = parser.parse_args()
    
    with open(args.filename, "rb") as bin:
        # Reader binary header
        binary_header = bin.read(LUKS2_BINARY_HEADER_SIZE)
        if binary_header[0:8] != b"LUKS\xba\xbe\x00\x02":
            print(f"Not a valid LUKS2 header: {binary_header[0:8]}")
            exit()
        else:
            header_size = int.from_bytes(binary_header[8:16])
            print(f"Found LUKS2 header of size {hex(header_size)} bytes.")

        # Read current hash value
        csum = binary_header[LUKS2_CSUM_OFFSET:LUKS2_CSUM_OFFSET+LUKS2_CSUM_LENGTH]
        print(f"Current checksum: {csum.hex()}")

        # Read first json area
        json_area = bin.read(header_size-LUKS2_BINARY_HEADER_SIZE).split(b"\x00")[0]
        
    if args.dump:
        dump_json(json_area)
    elif args.patch:
        patch_header(args.filename)
