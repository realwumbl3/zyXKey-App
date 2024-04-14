import os
import sys

"""
This (pure!) python script streams a YUV4MPEG format video to stout. It easily
runs at 1080p60fps on my machine.
Pipe it into a media player like this:
python3 swar_life.py | mpv -
The implementation works by storing each cell as a 4-bit value, all packed into
a single python bigint. Operations are performed on every cell in parallel, using
SWAR techniques ("SIMD With A Register", where "register" is a bigint. SWAB?).
4-bits-per-cell allows us to count the number of neighbors without overflow.
It's also convenient, because we can abuse python's int-to-hex formatter to expand
the data into 8-bits-per-cell, for video output.
# native res on 14" M1 MBP (minus notch)
WIDTH  = 3024
HEIGHT = 1890
FPS = 20
"""
WIDTH = 1920
HEIGHT = 1080
FPS = 60

STATE_BYTE_LENGTH = (WIDTH * HEIGHT) // 2
COLSHIFT = WIDTH * 4
WRAPSHIFT = WIDTH * HEIGHT * 4
BIAS = (WIDTH + 1) * 4

MASK_1 = int.from_bytes(b"\x11" * STATE_BYTE_LENGTH, "little") << BIAS
MASK_NOT_3 = MASK_1 * (15 ^ 3)
MASK_NOT_4 = MASK_1 * (15 ^ 4)
WRAP_MASK = int.from_bytes(b"\x11" * (BIAS//2), "little") << BIAS
BLIT_MASK_1 = int.from_bytes(b"\x01" * WIDTH * HEIGHT, "little")

sys.stdout.buffer.write(f"YUV4MPEG2 W{WIDTH} H{HEIGHT} F{FPS}:1 Cmono\n".encode())
state = int.from_bytes(os.urandom(STATE_BYTE_LENGTH), "little") & MASK_1

while True:
	"""
	if we include ourself as a neighbor:
	alive = (exactly 3 neighbors) or (alive and 4 neighbors)
	"""

	# implement wraparound
	state |= (state >> WRAPSHIFT) + ((state & WRAP_MASK) << WRAPSHIFT)

	# count neighbors
	summed = state
	summed += (state >> 4) + (state << 4)
	summed += (summed >> COLSHIFT) + (summed << COLSHIFT)

	# check if there are exactly 3 neighbors
	has_3_neighbors = summed ^ MASK_NOT_3 # at this point, a value of all 1s means it was initially 3
	has_3_neighbors &= has_3_neighbors >> 2 # fold in half
	has_3_neighbors &= has_3_neighbors >> 1 # fold in half again
	
	# check if there are exactly 4 neighbors
	has_4_neighbors = summed ^ MASK_NOT_4 # at this point, a value of all 1s means it was initially 4
	has_4_neighbors &= has_4_neighbors >> 2  # fold in half
	has_4_neighbors &= has_4_neighbors >> 1  # fold in half again

	# apply game-of-life rules
	state &= has_4_neighbors
	state |= has_3_neighbors
	state &= MASK_1

	# Hack to expand from 4bpp to 8bpp
	hexed = f"{state>>BIAS:0{WIDTH*HEIGHT}x}"
	blitted = int.from_bytes(hexed.encode(), "little")
	blitted &= BLIT_MASK_1  # convert ascii 0s and 1s to actual 0x00 and 0x01
	blitted <<= 7 # turn 0x01 into 0x80 so it's more visibile (ideally we'd generate 0xff but that's expensive)

	# output a YUV4MPEG frame
	sys.stdout.buffer.write(b"FRAME\n")
	sys.stdout.buffer.write(blitted.to_bytes(WIDTH*HEIGHT, "little"))