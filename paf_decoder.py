import os
import io
import sys
import struct
import logging
from PIL import Image

RAW = False

def output_file(data: bytes, output: str, width: int, height: int, bpp: int):
    if bpp == 8:
        Image.frombytes("RGB", (width, height), data).save(output)
    elif bpp == 16:
        Image.frombytes("RGB", (width, height), data, "raw", "BGR;16", 0, 1).save(output)  
    elif bpp == 24:
        Image.frombytes("RGB", (width, height), data, "raw", "BGR").save(output)    
    elif bpp == 32:
        aInvert(Image.frombytes("RGBA", (width, height), data, "raw", "BGRA")).save(output)

def pafDecodeFrame(file_buf: io.BytesIO, width: int, height: int, bpp: int):
    RGB332 = b"\x00\x00\x00\x00\x00\x55\x00\x00\xaa\x00\x00\xff\x00\x24\x00\x00\x24\x55\x00\x24\xaa\x00\x24\xff\x00\x48\x00\x00\x48\x55\x00\x48\xaa\x00\x48\xff\x00\x6c\x00\x00\x6c\x55\x00\x6c\xaa\x00\x6c\xff\x00\x90\x00\x00\x90\x55\x00\x90\xaa\x00\x90\xff\x00\xb4\x00\x00\xb4\x55\x00\xb4\xaa\x00\xb4\xff\x00\xd8\x00\x00\xd8\x55\x00\xd8\xaa\x00\xd8\xff\x00\xfc\x00\x00\xfc\x55\x00\xfc\xaa\x00\xfc\xff\x24\x00\x00\x24\x00\x55\x24\x00\xaa\x24\x00\xff\x24\x24\x00\x24\x24\x55\x24\x24\xaa\x24\x24\xff\x24\x48\x00\x24\x48\x55\x24\x48\xaa\x24\x48\xff\x24\x6c\x00\x24\x6c\x55\x24\x6c\xaa\x24\x6c\xff\x24\x90\x00\x24\x90\x55\x24\x90\xaa\x24\x90\xff\x24\xb4\x00\x24\xb4\x55\x24\xb4\xaa\x24\xb4\xff\x24\xd8\x00\x24\xd8\x55\x24\xd8\xaa\x24\xd8\xff\x24\xfc\x00\x24\xfc\x55\x24\xfc\xaa\x24\xfc\xff\x48\x00\x00\x48\x00\x55\x48\x00\xaa\x48\x00\xff\x48\x24\x00\x48\x24\x55\x48\x24\xaa\x48\x24\xff\x48\x48\x00\x48\x48\x55\x48\x48\xaa\x48\x48\xff\x48\x6c\x00\x48\x6c\x55\x48\x6c\xaa\x48\x6c\xff\x48\x90\x00\x48\x90\x55\x48\x90\xaa\x48\x90\xff\x48\xb4\x00\x48\xb4\x55\x48\xb4\xaa\x48\xb4\xff\x48\xd8\x00\x48\xd8\x55\x48\xd8\xaa\x48\xd8\xff\x48\xfc\x00\x48\xfc\x55\x48\xfc\xaa\x48\xfc\xff\x6c\x00\x00\x6c\x00\x55\x6c\x00\xaa\x6c\x00\xff\x6c\x24\x00\x6c\x24\x55\x6c\x24\xaa\x6c\x24\xff\x6c\x48\x00\x6c\x48\x55\x6c\x48\xaa\x6c\x48\xff\x6c\x6c\x00\x6c\x6c\x55\x6c\x6c\xaa\x6c\x6c\xff\x6c\x90\x00\x6c\x90\x55\x6c\x90\xaa\x6c\x90\xff\x6c\xb4\x00\x6c\xb4\x55\x6c\xb4\xaa\x6c\xb4\xff\x6c\xd8\x00\x6c\xd8\x55\x6c\xd8\xaa\x6c\xd8\xff\x6c\xfc\x00\x6c\xfc\x55\x6c\xfc\xaa\x6c\xfc\xff\x90\x00\x00\x90\x00\x55\x90\x00\xaa\x90\x00\xff\x90\x24\x00\x90\x24\x55\x90\x24\xaa\x90\x24\xff\x90\x48\x00\x90\x48\x55\x90\x48\xaa\x90\x48\xff\x90\x6c\x00\x90\x6c\x55\x90\x6c\xaa\x90\x6c\xff\x90\x90\x00\x90\x90\x55\x90\x90\xaa\x90\x90\xff\x90\xb4\x00\x90\xb4\x55\x90\xb4\xaa\x90\xb4\xff\x90\xd8\x00\x90\xd8\x55\x90\xd8\xaa\x90\xd8\xff\x90\xfc\x00\x90\xfc\x55\x90\xfc\xaa\x90\xfc\xff\xb4\x00\x00\xb4\x00\x55\xb4\x00\xaa\xb4\x00\xff\xb4\x24\x00\xb4\x24\x55\xb4\x24\xaa\xb4\x24\xff\xb4\x48\x00\xb4\x48\x55\xb4\x48\xaa\xb4\x48\xff\xb4\x6c\x00\xb4\x6c\x55\xb4\x6c\xaa\xb4\x6c\xff\xb4\x90\x00\xb4\x90\x55\xb4\x90\xaa\xb4\x90\xff\xb4\xb4\x00\xb4\xb4\x55\xb4\xb4\xaa\xb4\xb4\xff\xb4\xd8\x00\xb4\xd8\x55\xb4\xd8\xaa\xb4\xd8\xff\xb4\xfc\x00\xb4\xfc\x55\xb4\xfc\xaa\xb4\xfc\xff\xd8\x00\x00\xd8\x00\x55\xd8\x00\xaa\xd8\x00\xff\xd8\x24\x00\xd8\x24\x55\xd8\x24\xaa\xd8\x24\xff\xd8\x48\x00\xd8\x48\x55\xd8\x48\xaa\xd8\x48\xff\xd8\x6c\x00\xd8\x6c\x55\xd8\x6c\xaa\xd8\x6c\xff\xd8\x90\x00\xd8\x90\x55\xd8\x90\xaa\xd8\x90\xff\xd8\xb4\x00\xd8\xb4\x55\xd8\xb4\xaa\xd8\xb4\xff\xd8\xd8\x00\xd8\xd8\x55\xd8\xd8\xaa\xd8\xd8\xff\xd8\xfc\x00\xd8\xfc\x55\xd8\xfc\xaa\xd8\xfc\xff\xfc\x00\x00\xfc\x00\x55\xfc\x00\xaa\xfc\x00\xff\xfc\x24\x00\xfc\x24\x55\xfc\x24\xaa\xfc\x24\xff\xfc\x48\x00\xfc\x48\x55\xfc\x48\xaa\xfc\x48\xff\xfc\x6c\x00\xfc\x6c\x55\xfc\x6c\xaa\xfc\x6c\xff\xfc\x90\x00\xfc\x90\x55\xfc\x90\xaa\xfc\x90\xff\xfc\xb4\x00\xfc\xb4\x55\xfc\xb4\xaa\xfc\xb4\xff\xfc\xd8\x00\xfc\xd8\x55\xfc\xd8\xaa\xfc\xd8\xff\xfc\xfc\x00\xfc\xfc\x55\xfc\xfc\xaa\xfc\xfc\xff"
    def rgb332_get(num):
        index = num*3
        return RGB332[index:index+3]
    
    o_buf = bytearray()
    while file_buf.tell() < len(file_buf.getvalue()):       
        length = 1        
        rle_type = struct.unpack(">B", file_buf.read(1))[0]        
        if rle_type >= 193 and rle_type < 224:
            length = rle_type-192
        elif rle_type >= 224 and rle_type < 240:
            file_buf.seek(file_buf.tell()-1)
            length = struct.unpack(">H", file_buf.read(2))[0]-57344            
        elif rle_type >= 240:
            length = struct.unpack(">H", file_buf.read(2))[0]            
        else:
            file_buf.seek(file_buf.tell()-1)

        if bpp == 8:
            o_buf += rgb332_get(file_buf.read(1)[0])*length
        else:
            o_buf += file_buf.read(int(bpp/8))*length

    if len(o_buf) < (width*height)*(int(bpp/8)):
        padding_needed = (width*height)*(int(bpp/8))
        o_buf += b"\0" * (padding_needed-len(o_buf))
        assert len(o_buf) == padding_needed, f"{len(o_buf)} - {padding_needed}"

    return bytes(o_buf)

def pafXORBytes(b1, b2):
    return bytes(bytearray(a ^ b for a, b in zip(b1, b2)))

def aInvert(i1: Image.Image):    
    a_data = b"".join([struct.pack("<B", a^0xff) for a in i1.getdata(3)])
    p = i1.copy()    
    p.putalpha(Image.frombytes("L", i1.size, a_data))
    return p

if __name__ == "__main__":
    file_buf = open(sys.argv[1], "rb")
    assert file_buf.read(3) == b"PAF"
    version = int(file_buf.read(1))
    assert version in [1,2,3], f"PAF{version} images is not supported."
    width_height_mode = ""
    bpp_frames_mode = ""
    width_height_size = 0
    bpp_frames_size = 0
    
    if version == 1:
        width_height_size = 1
        width_height_mode = "<B"
        bpp_frames_size = 1
        bpp_frames_mode = "<B"
    elif version == 2:
        width_height_size = 4
        width_height_mode = "<L"
        bpp_frames_size = 4
        bpp_frames_mode = "<L"
    elif version == 3:
        width_height_size = 4
        width_height_mode = "<L"
        bpp_frames_size = 1
        bpp_frames_mode = "<B"
    
    bpp = struct.unpack(bpp_frames_mode, file_buf.read(bpp_frames_size))[0]
    width = struct.unpack(width_height_mode, file_buf.read(width_height_size))[0]
    height = struct.unpack(width_height_mode, file_buf.read(width_height_size))[0]
    frames = struct.unpack(bpp_frames_mode, file_buf.read(bpp_frames_size))[0]

    assert bpp in [8,16,24,32], f"{bpp}-bit PAF images is not supported."

    frame_offsets = []
    paf_frames = []

    for _ in range(frames+1): 
        frame_offsets.append(struct.unpack(">L", file_buf.read(4))[0])

    file_buf.seek(frame_offsets[frames])
    if (file_buf.read(9) != b"EndOfPAF\0"):
        logging.warning("Missing EOF in PAF image")

    file_buf.seek(frame_offsets[0])

    for i in range(frames):
        paf_frames.append(io.BytesIO(file_buf.read(frame_offsets[i+1]-frame_offsets[i])))

    if RAW:
        outr = open(sys.argv[2], "wb")

    if frames <= 1:
        if RAW:
            outr.write(pafDecodeFrame(paf_frames[0], width, height, bpp))
        else:
            output_file(pafDecodeFrame(paf_frames[0], width, height, bpp), sys.argv[2], width, height, bpp)
    else:
        canvas = pafDecodeFrame(paf_frames[0], width, height, bpp)
        if RAW:
            outr.write(canvas)
        else:
            output_file(canvas, f"{os.path.splitext(sys.argv[2])[0]}_1{os.path.splitext(sys.argv[2])[1]}", width, height, bpp)

        for f in range(frames-1):
            canvas = pafXORBytes(canvas, pafDecodeFrame(paf_frames[f+1], width, height, bpp))
            if RAW:
                outr.write(canvas)
            else:
                output_file(canvas, f"{os.path.splitext(sys.argv[2])[0]}_{f+2}{os.path.splitext(sys.argv[2])[1]}", width, height, bpp)
