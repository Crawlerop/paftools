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

def pafDecodeFrame8(file_buf: io.BytesIO, width: int, height: int):
    RGB332 = b"\x00\x00\x00\x00\x00\x55\x00\x00\xaa\x00\x00\xff\x00\x24\x00\x00\x24\x55\x00\x24\xaa\x00\x24\xff\x00\x48\x00\x00\x48\x55\x00\x48\xaa\x00\x48\xff\x00\x6c\x00\x00\x6c\x55\x00\x6c\xaa\x00\x6c\xff\x00\x90\x00\x00\x90\x55\x00\x90\xaa\x00\x90\xff\x00\xb4\x00\x00\xb4\x55\x00\xb4\xaa\x00\xb4\xff\x00\xd8\x00\x00\xd8\x55\x00\xd8\xaa\x00\xd8\xff\x00\xfc\x00\x00\xfc\x55\x00\xfc\xaa\x00\xfc\xff\x24\x00\x00\x24\x00\x55\x24\x00\xaa\x24\x00\xff\x24\x24\x00\x24\x24\x55\x24\x24\xaa\x24\x24\xff\x24\x48\x00\x24\x48\x55\x24\x48\xaa\x24\x48\xff\x24\x6c\x00\x24\x6c\x55\x24\x6c\xaa\x24\x6c\xff\x24\x90\x00\x24\x90\x55\x24\x90\xaa\x24\x90\xff\x24\xb4\x00\x24\xb4\x55\x24\xb4\xaa\x24\xb4\xff\x24\xd8\x00\x24\xd8\x55\x24\xd8\xaa\x24\xd8\xff\x24\xfc\x00\x24\xfc\x55\x24\xfc\xaa\x24\xfc\xff\x48\x00\x00\x48\x00\x55\x48\x00\xaa\x48\x00\xff\x48\x24\x00\x48\x24\x55\x48\x24\xaa\x48\x24\xff\x48\x48\x00\x48\x48\x55\x48\x48\xaa\x48\x48\xff\x48\x6c\x00\x48\x6c\x55\x48\x6c\xaa\x48\x6c\xff\x48\x90\x00\x48\x90\x55\x48\x90\xaa\x48\x90\xff\x48\xb4\x00\x48\xb4\x55\x48\xb4\xaa\x48\xb4\xff\x48\xd8\x00\x48\xd8\x55\x48\xd8\xaa\x48\xd8\xff\x48\xfc\x00\x48\xfc\x55\x48\xfc\xaa\x48\xfc\xff\x6c\x00\x00\x6c\x00\x55\x6c\x00\xaa\x6c\x00\xff\x6c\x24\x00\x6c\x24\x55\x6c\x24\xaa\x6c\x24\xff\x6c\x48\x00\x6c\x48\x55\x6c\x48\xaa\x6c\x48\xff\x6c\x6c\x00\x6c\x6c\x55\x6c\x6c\xaa\x6c\x6c\xff\x6c\x90\x00\x6c\x90\x55\x6c\x90\xaa\x6c\x90\xff\x6c\xb4\x00\x6c\xb4\x55\x6c\xb4\xaa\x6c\xb4\xff\x6c\xd8\x00\x6c\xd8\x55\x6c\xd8\xaa\x6c\xd8\xff\x6c\xfc\x00\x6c\xfc\x55\x6c\xfc\xaa\x6c\xfc\xff\x90\x00\x00\x90\x00\x55\x90\x00\xaa\x90\x00\xff\x90\x24\x00\x90\x24\x55\x90\x24\xaa\x90\x24\xff\x90\x48\x00\x90\x48\x55\x90\x48\xaa\x90\x48\xff\x90\x6c\x00\x90\x6c\x55\x90\x6c\xaa\x90\x6c\xff\x90\x90\x00\x90\x90\x55\x90\x90\xaa\x90\x90\xff\x90\xb4\x00\x90\xb4\x55\x90\xb4\xaa\x90\xb4\xff\x90\xd8\x00\x90\xd8\x55\x90\xd8\xaa\x90\xd8\xff\x90\xfc\x00\x90\xfc\x55\x90\xfc\xaa\x90\xfc\xff\xb4\x00\x00\xb4\x00\x55\xb4\x00\xaa\xb4\x00\xff\xb4\x24\x00\xb4\x24\x55\xb4\x24\xaa\xb4\x24\xff\xb4\x48\x00\xb4\x48\x55\xb4\x48\xaa\xb4\x48\xff\xb4\x6c\x00\xb4\x6c\x55\xb4\x6c\xaa\xb4\x6c\xff\xb4\x90\x00\xb4\x90\x55\xb4\x90\xaa\xb4\x90\xff\xb4\xb4\x00\xb4\xb4\x55\xb4\xb4\xaa\xb4\xb4\xff\xb4\xd8\x00\xb4\xd8\x55\xb4\xd8\xaa\xb4\xd8\xff\xb4\xfc\x00\xb4\xfc\x55\xb4\xfc\xaa\xb4\xfc\xff\xd8\x00\x00\xd8\x00\x55\xd8\x00\xaa\xd8\x00\xff\xd8\x24\x00\xd8\x24\x55\xd8\x24\xaa\xd8\x24\xff\xd8\x48\x00\xd8\x48\x55\xd8\x48\xaa\xd8\x48\xff\xd8\x6c\x00\xd8\x6c\x55\xd8\x6c\xaa\xd8\x6c\xff\xd8\x90\x00\xd8\x90\x55\xd8\x90\xaa\xd8\x90\xff\xd8\xb4\x00\xd8\xb4\x55\xd8\xb4\xaa\xd8\xb4\xff\xd8\xd8\x00\xd8\xd8\x55\xd8\xd8\xaa\xd8\xd8\xff\xd8\xfc\x00\xd8\xfc\x55\xd8\xfc\xaa\xd8\xfc\xff\xfc\x00\x00\xfc\x00\x55\xfc\x00\xaa\xfc\x00\xff\xfc\x24\x00\xfc\x24\x55\xfc\x24\xaa\xfc\x24\xff\xfc\x48\x00\xfc\x48\x55\xfc\x48\xaa\xfc\x48\xff\xfc\x6c\x00\xfc\x6c\x55\xfc\x6c\xaa\xfc\x6c\xff\xfc\x90\x00\xfc\x90\x55\xfc\x90\xaa\xfc\x90\xff\xfc\xb4\x00\xfc\xb4\x55\xfc\xb4\xaa\xfc\xb4\xff\xfc\xd8\x00\xfc\xd8\x55\xfc\xd8\xaa\xfc\xd8\xff\xfc\xfc\x00\xfc\xfc\x55\xfc\xfc\xaa\xfc\xfc\xff"
    def rgb332_get(num):
        index = num*3
        return RGB332[index:index+3]

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
        o_buf += rgb332_get(file_buf.read(1)[0])*length
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
        assert bpp in [8,16], f"{bpp}-bit PAF{version} images is not supported."
        
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
                for fr in range(frames-1):                
                    frame += 1                
                    file_buf.seek(frame_offsets[fr+1]) 

                    frame_data = pafXORBytes(frame_data, pafDecodeFrame(file_buf, width, height))
                    Image.frombytes("RGB", (width, height), bytes(frame_data),"raw", "BGR;16", 0, 1).save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
            else:
                Image.frombytes("RGB", (width, height), bytes(base_frame),"raw", "BGR;16", 0, 1).save(sys.argv[2])
        elif bpp == 8:
            base_frame = pafDecodeFrame8(file_buf, width, height)
            
            if frames > 1:
                frame = 1
                Image.frombytes("RGB", (width, height), bytes(base_frame)).save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
                frame_data = base_frame            
                for fr in range(frames-1):                
                    frame += 1                
                    file_buf.seek(frame_offsets[fr+1]) 

                    frame_data = pafXORBytes(frame_data, pafDecodeFrame8(file_buf, width, height))
                    Image.frombytes("RGB", (width, height), bytes(frame_data)).save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
            else:
                Image.frombytes("RGB", (width, height), bytes(base_frame)).save(sys.argv[2])

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
            for fr in range(frames-1):                
                frame += 1                
                file_buf.seek(frame_offsets[fr+1])

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
                for fr in range(frames-1):                
                    frame += 1                
                    file_buf.seek(frame_offsets[fr+1])

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
                for fr in range(frames-1):                
                    frame += 1                
                    file_buf.seek(frame_offsets[fr+1])

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
                for fr in range(frames-1):                
                    frame += 1                
                    file_buf.seek(frame_offsets[fr+1])

                    frame_data = pafXORBytes(frame_data, pafDecodeFrameRGBA(file_buf, width, height))
                    aInvert(Image.frombytes("RGBA", (width, height), bytes(frame_data), "raw", "BGRA")).save(f"{os.path.splitext(sys.argv[2])[0]}_{frame}{os.path.splitext(sys.argv[2])[1]}")
            else:
                aInvert(Image.frombytes("RGBA", (width, height), bytes(base_frame), "raw", "BGRA")).save(sys.argv[2])         
