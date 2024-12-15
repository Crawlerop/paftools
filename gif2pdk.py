from itertools import repeat, compress, groupby
import argparse
from PIL import Image, GifImagePlugin
import struct

def ilen(iterable):
    """
    Return the number of items in iterable.

    >>> ilen(x for x in range(1000000) if x % 3 == 0)
    333334
    """
    # using zip() to wrap the input with 1-tuples which compress() reads as true values.
    return sum(compress(repeat(1), zip(iterable)))

def rle_encode(iterable):
    """
    >>> "".join(rle_encode("AAAABBBCCDAA"))
    '4A3B2C1D2A'
    >>> "".join(rle_encode("AAAABBBCCDAA", length_first=False))
    'A4B3C2D1A2'
    """
    return (
        (k, ilen(g))
        for k, g in groupby(iterable)
    )
    
def rgb24to565(pixel):
    return (pixel[2] >> 3) | ((pixel[1] >> 2) << 5) | ((pixel[0] >> 3) << 11)
    
if __name__ == "__main__":
    ap = argparse.ArgumentParser("gif2pdk")
    
    ap.add_argument("--version", "-v", help="PAF version to use", default=1, type=int, choices=[1, 2, 3])
    ap.add_argument("in_file")
    ap.add_argument("out_file")

    args = ap.parse_args()
    src_img: GifImagePlugin.GifImageFile = Image.open(args.in_file)
    dest_ani = open(args.out_file, "wb")

    if args.version == 1:
        dest_ani.write(b"PAF1" + struct.pack("<BBBB", 16, src_img.width, src_img.height, src_img.n_frames))
        
    elif args.version == 2:
        dest_ani.write(b"PAF2" + struct.pack("<LLLL", 16, src_img.width, src_img.height, src_img.n_frames))
        
    elif args.version == 3:
        dest_ani.write(b"PAF3" + struct.pack("<BLLB", 16, src_img.width, src_img.height, src_img.n_frames))
        
    paf_frame_table_offset = dest_ani.tell()
    paf_frame_ani_tables = []
    paf_xor_last_frame = [0] * (src_img.width * src_img.height)

    dest_ani.write((0).to_bytes(4) * (src_img.n_frames + 1))

    while True:
        try:
            paf_frame_ani_tables.append(dest_ani.tell())
            pixels_base = [rgb24to565(x) for x in src_img.convert("RGB").getdata()]
            pixels_conv = []

            for i, p in enumerate(pixels_base):
                pixels_conv.append((p ^ paf_xor_last_frame[i]).to_bytes(2, "little"))
                paf_xor_last_frame[i] = p
            
            for pix, count in rle_encode(pixels_conv):
                if pix[0] >= 0xc0 and count == 1:
                    dest_ani.write(b"\xc1" + pix)

                elif count > 1:
                    if count < 32:
                        dest_ani.write((0xc0 + count).to_bytes(1) + pix)

                    elif count < 4096:
                        dest_ani.write(struct.pack(">BB", 0xe0 | count >> 8, count & 0xff) + pix)

                    else:
                        dest_ani.write(struct.pack(">BH", 0xf0 | count >> 16, count & 0xffff) + pix)

                else:
                    dest_ani.write(pix)

            src_img.seek(src_img.tell() + 1)

        except EOFError:
            break

    paf_frame_ani_tables.append(dest_ani.tell())
    dest_ani.write(b"EndOfPAF\0")

    dest_ani.seek(paf_frame_table_offset)
    for t in paf_frame_ani_tables:
        dest_ani.write(t.to_bytes(4, "big"))

    dest_ani.close()
        