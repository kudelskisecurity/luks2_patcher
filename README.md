# LUKS2 header patcher tool

Tool to dump and patch LUKS2 JSON area. The header checksum are recomputed with the new JSON when patched. Only the first header is patched, the second rescue header is not.

# Example

To change a value in the JSON area, here is the way to proceed. First dump the json area:
```bash
$ ./luks2_patcher.py -d disk.img
Found LUKS2 header of size 0x4000 bytes.
Current checksum: 0b80c36ddd2cabae5611e321a66ed584afd348dd10e4edbda830ec4c49c22555
JSON Area saved in header.json.
```

Suppose we want to change the field `"fido2-clientPin-required"` of a token to false. We edit the file header.json accordingly: 
```bash
$ python
>>> import json
>>> f = open("header.json", "r+")
>>> d = json.load(f)
>>> d["tokens"]["0"]["fido2-clientPin-required"] = False
>>> json.dump(d,f)
>>> f.close()
```

Then we patch the LUKS2 header with the header file:
```bash
$ ./luks2_patcher.py -d disk.img
Found LUKS2 header of size 0x4000 bytes.
Current checksum: 0b80c36ddd2cabae5611e321a66ed584afd348dd10e4edbda830ec4c49c22555
JSON Area loaded from header.json.
Patched checksum: 109abd6c12b025c70cbf65910aae29eef43a3906ae939b22e62c209f4b797021
```