import os
import io
import sys
import struct
import logging
from PIL import Image

# def pafDecodeFrame(file_buf: io.BytesIO, width: int, height: int):
#     o_buf = bytearray()
#     while len(o_buf) < (width*height)*2:
#         #print(len(o_buf), (width*height)*2)        
#         length = 1        
#         try:
#             rle_type = struct.unpack(">B", file_buf.read(1))[0]        
#             if rle_type >= 193 and rle_type < 224:
#                 length = rle_type-192
#             elif rle_type >= 224 and rle_type < 240:
#                 file_buf.seek(file_buf.tell()-1)
#                 length = struct.unpack(">H", file_buf.read(2))[0]-57344            
#             elif rle_type >= 240:
#                 length = struct.unpack(">H", file_buf.read(2))[0]            
#             else:
#                 file_buf.seek(file_buf.tell()-1)
#             o_buf += file_buf.read(2)*length
#         except Exception:
#             print(len(o_buf), (width*height)*2)
#             open("error", "wb").write(o_buf)
#             raise
#     return o_buf

def pafDecodeFrame(file_buf: io.BytesIO, width: int, height: int):
    o_buf = bytearray()
    while len(o_buf) < (width*height)*2:       
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
        o_buf += file_buf.read(2)*length
    return o_buf

def pafDecodeFrameRGBA(file_buf: io.BytesIO, width: int, height: int):
    o_buf = bytearray()
    while len(o_buf) < (width*height)*4:
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
        o_buf += file_buf.read(4)*length
    return o_buf    

def pafDecodeFrameRGB(file_buf: io.BytesIO, width: int, height: int):
    o_buf = bytearray()
    while len(o_buf) < (width*height)*3:
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
        o_buf += file_buf.read(3)*length
    return o_buf     

def pafXORBytes(b1, b2):
    return bytearray(a ^ b for a, b in zip(b1, b2))

def aInvert(i1: Image.Image):
    a_data = b"".join([struct.pack("<H", a^0xff) for a in i1.getdata(3)])
    p = i1.copy()
    p.putalpha(Image.frombytes("L", i1.size, a_data))
    return p

if __name__ == "__main__":
    file_buf = open(sys.argv[1], "rb")
    assert file_buf.read(3) == b"PAF"
    version = int(file_buf.read(1))
    assert version in [1,2,3], f"PAF{version} images is not supported."

    if version == 1:
        bpp = file_buf.read(1)[0]
        width = file_buf.read(1)[0]
        height = file_buf.read(1)[0]
        frames = file_buf.read(1)[0]
        assert bpp in [16], f"{bpp}-bit PAF{version} images is not supported."
        
        frame_offsets = []

        for _ in range(frames): 
            frame_offsets.append(struct.unpack(">L", file_buf.read(4))[0])

        footer_offset = struct.unpack(">L", file_buf.read(4))[0]
        f_tmp = file_buf.tell()
        file_buf.seek(footer_offset)
        if (file_buf.read(9) != b"EndOfPAF\0"):
            logging.warning("Missing EOF in PAF image")
        
        file_buf.seek(f_tmp)
        
        base_frame = pafDecodeFrame(file_buf, width, height)
        
        if frames > 1:
            frame = 1
            Image.frombytes("RGB", (width, height), bytes(base_frame),"raw", "BGR;16", 0, 1).save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
            frame_data = base_frame            
            for _ in range(frames-1):                
                frame += 1                
                frame_data = pafXORBytes(frame_data, pafDecodeFrame(file_buf, width, height))
                Image.frombytes("RGB", (width, height), bytes(frame_data),"raw", "BGR;16", 0, 1).save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
        else:
            Image.frombytes("RGB", (width, height), bytes(base_frame),"raw", "BGR;16", 0, 1).save(sys.argv[2])
    elif version == 2:
        bpp = struct.unpack("<L", file_buf.read(4))[0]
        width = struct.unpack("<L", file_buf.read(4))[0]
        height = struct.unpack("<L", file_buf.read(4))[0]
        frames = struct.unpack("<L", file_buf.read(4))[0]
        assert bpp in [16], f"{bpp}-bit PAF{version} images is not supported."

        frame_offsets = []

        for _ in range(frames): 
            frame_offsets.append(struct.unpack(">L", file_buf.read(4))[0])

        footer_offset = struct.unpack(">L", file_buf.read(4))[0]
        f_tmp = file_buf.tell()
        file_buf.seek(footer_offset)
        if (file_buf.read(9) != b"EndOfPAF\0"):
            logging.warning("Missing EOF in PAF image")
        
        file_buf.seek(f_tmp)
        
        base_frame = pafDecodeFrame(file_buf, width, height)
        
        if frames > 1:
            frame = 1
            Image.frombytes("RGB", (width, height), bytes(base_frame),"raw", "BGR;16", 0, 1).save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
            frame_data = base_frame            
            for _ in range(frames-1):                
                frame += 1
                frame_data = pafXORBytes(frame_data, pafDecodeFrame(file_buf, width, height))
                Image.frombytes("RGB", (width, height), bytes(frame_data),"raw", "BGR;16", 0, 1).save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
        else:
            Image.frombytes("RGB", (width, height), bytes(base_frame),"raw", "BGR;16", 0, 1).save(sys.argv[2])
    elif version == 3:
        bpp = file_buf.read(1)[0]
        assert bpp in [16, 24, 32], f"{bpp}-bit PAF{version} images is not supported."

        width = struct.unpack("<L", file_buf.read(4))[0]
        height = struct.unpack("<L", file_buf.read(4))[0]
        frames = file_buf.read(1)[0]

        frame_offsets = []

        for _ in range(frames): 
            frame_offsets.append(struct.unpack(">L", file_buf.read(4))[0])

        footer_offset = struct.unpack(">L", file_buf.read(4))[0]
        f_tmp = file_buf.tell()
        file_buf.seek(footer_offset)
        if (file_buf.read(9) != b"EndOfPAF\0"):
            logging.warning("Missing EOF in PAF image")
        
        file_buf.seek(f_tmp)
        
        if bpp == 16:
            base_frame = pafDecodeFrame(file_buf, width, height)
            
            if frames > 1:
                frame = 1
                Image.frombytes("RGB", (width, height), bytes(base_frame),"raw", "BGR;16", 0, 1).save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
                frame_data = base_frame            
                for _ in range(frames-1):                
                    frame += 1
                    frame_data = pafXORBytes(frame_data, pafDecodeFrame(file_buf, width, height))
                    Image.frombytes("RGB", (width, height), bytes(frame_data), "raw", "BGR;16", 0, 1).save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
            else:
                Image.frombytes("RGB", (width, height), bytes(base_frame), "raw", "BGR;16", 0, 1).save(sys.argv[2])   
        
        elif bpp == 24:
            base_frame = pafDecodeFrameRGB(file_buf, width, height)
        
            if frames > 1:
                frame = 1
                Image.frombytes("RGB", (width, height), bytes(base_frame), "raw", "BGR").save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
                frame_data = base_frame            
                for _ in range(frames-1):                
                    frame += 1
                    frame_data = pafXORBytes(frame_data, pafDecodeFrameRGB(file_buf, width, height))
                    Image.frombytes("RGB", (width, height), bytes(frame_data), "raw", "BGR").save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
            else:
                Image.frombytes("RGB", (width, height), bytes(base_frame), "raw", "BGR").save(sys.argv[2])   

        elif bpp == 32:
            base_frame = pafDecodeFrameRGBA(file_buf, width, height)
        
            if frames > 1:
                frame = 1
                aInvert(Image.frombytes("RGBA", (width, height), bytes(base_frame), "raw", "BGRA")).save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
                frame_data = base_frame            
                for _ in range(frames-1):                
                    frame += 1
                    frame_data = pafXORBytes(frame_data, pafDecodeFrameRGBA(file_buf, width, height))
                    aInvert(Image.frombytes("RGBA", (width, height), bytes(frame_data), "raw", "BGRA")).save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
            else:
                aInvert(Image.frombytes("RGBA", (width, height), bytes(base_frame), "raw", "BGRA")).save(sys.argv[2])         
