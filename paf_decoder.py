import os
import io
import sys
import struct
import logging

from PIL import Image, ImageTk

RAW = False

MONOCHROME_INVERT = False
PAL_2BPP_IS_SINGLE = False

PAD_2BPP = False

PAL_2BPP = [0, 0x60, 0xc0, 0xff]
PAL_2BPP_INVERT = [x for x in reversed(PAL_2BPP)]

RGB332 = b"\x00\x00\x00\x00\x00\x55\x00\x00\xaa\x00\x00\xff\x00\x24\x00\x00\x24\x55\x00\x24\xaa\x00\x24\xff\x00\x48\x00\x00\x48\x55\x00\x48\xaa\x00\x48\xff\x00\x6c\x00\x00\x6c\x55\x00\x6c\xaa\x00\x6c\xff\x00\x90\x00\x00\x90\x55\x00\x90\xaa\x00\x90\xff\x00\xb4\x00\x00\xb4\x55\x00\xb4\xaa\x00\xb4\xff\x00\xd8\x00\x00\xd8\x55\x00\xd8\xaa\x00\xd8\xff\x00\xfc\x00\x00\xfc\x55\x00\xfc\xaa\x00\xfc\xff\x24\x00\x00\x24\x00\x55\x24\x00\xaa\x24\x00\xff\x24\x24\x00\x24\x24\x55\x24\x24\xaa\x24\x24\xff\x24\x48\x00\x24\x48\x55\x24\x48\xaa\x24\x48\xff\x24\x6c\x00\x24\x6c\x55\x24\x6c\xaa\x24\x6c\xff\x24\x90\x00\x24\x90\x55\x24\x90\xaa\x24\x90\xff\x24\xb4\x00\x24\xb4\x55\x24\xb4\xaa\x24\xb4\xff\x24\xd8\x00\x24\xd8\x55\x24\xd8\xaa\x24\xd8\xff\x24\xfc\x00\x24\xfc\x55\x24\xfc\xaa\x24\xfc\xff\x48\x00\x00\x48\x00\x55\x48\x00\xaa\x48\x00\xff\x48\x24\x00\x48\x24\x55\x48\x24\xaa\x48\x24\xff\x48\x48\x00\x48\x48\x55\x48\x48\xaa\x48\x48\xff\x48\x6c\x00\x48\x6c\x55\x48\x6c\xaa\x48\x6c\xff\x48\x90\x00\x48\x90\x55\x48\x90\xaa\x48\x90\xff\x48\xb4\x00\x48\xb4\x55\x48\xb4\xaa\x48\xb4\xff\x48\xd8\x00\x48\xd8\x55\x48\xd8\xaa\x48\xd8\xff\x48\xfc\x00\x48\xfc\x55\x48\xfc\xaa\x48\xfc\xff\x6c\x00\x00\x6c\x00\x55\x6c\x00\xaa\x6c\x00\xff\x6c\x24\x00\x6c\x24\x55\x6c\x24\xaa\x6c\x24\xff\x6c\x48\x00\x6c\x48\x55\x6c\x48\xaa\x6c\x48\xff\x6c\x6c\x00\x6c\x6c\x55\x6c\x6c\xaa\x6c\x6c\xff\x6c\x90\x00\x6c\x90\x55\x6c\x90\xaa\x6c\x90\xff\x6c\xb4\x00\x6c\xb4\x55\x6c\xb4\xaa\x6c\xb4\xff\x6c\xd8\x00\x6c\xd8\x55\x6c\xd8\xaa\x6c\xd8\xff\x6c\xfc\x00\x6c\xfc\x55\x6c\xfc\xaa\x6c\xfc\xff\x90\x00\x00\x90\x00\x55\x90\x00\xaa\x90\x00\xff\x90\x24\x00\x90\x24\x55\x90\x24\xaa\x90\x24\xff\x90\x48\x00\x90\x48\x55\x90\x48\xaa\x90\x48\xff\x90\x6c\x00\x90\x6c\x55\x90\x6c\xaa\x90\x6c\xff\x90\x90\x00\x90\x90\x55\x90\x90\xaa\x90\x90\xff\x90\xb4\x00\x90\xb4\x55\x90\xb4\xaa\x90\xb4\xff\x90\xd8\x00\x90\xd8\x55\x90\xd8\xaa\x90\xd8\xff\x90\xfc\x00\x90\xfc\x55\x90\xfc\xaa\x90\xfc\xff\xb4\x00\x00\xb4\x00\x55\xb4\x00\xaa\xb4\x00\xff\xb4\x24\x00\xb4\x24\x55\xb4\x24\xaa\xb4\x24\xff\xb4\x48\x00\xb4\x48\x55\xb4\x48\xaa\xb4\x48\xff\xb4\x6c\x00\xb4\x6c\x55\xb4\x6c\xaa\xb4\x6c\xff\xb4\x90\x00\xb4\x90\x55\xb4\x90\xaa\xb4\x90\xff\xb4\xb4\x00\xb4\xb4\x55\xb4\xb4\xaa\xb4\xb4\xff\xb4\xd8\x00\xb4\xd8\x55\xb4\xd8\xaa\xb4\xd8\xff\xb4\xfc\x00\xb4\xfc\x55\xb4\xfc\xaa\xb4\xfc\xff\xd8\x00\x00\xd8\x00\x55\xd8\x00\xaa\xd8\x00\xff\xd8\x24\x00\xd8\x24\x55\xd8\x24\xaa\xd8\x24\xff\xd8\x48\x00\xd8\x48\x55\xd8\x48\xaa\xd8\x48\xff\xd8\x6c\x00\xd8\x6c\x55\xd8\x6c\xaa\xd8\x6c\xff\xd8\x90\x00\xd8\x90\x55\xd8\x90\xaa\xd8\x90\xff\xd8\xb4\x00\xd8\xb4\x55\xd8\xb4\xaa\xd8\xb4\xff\xd8\xd8\x00\xd8\xd8\x55\xd8\xd8\xaa\xd8\xd8\xff\xd8\xfc\x00\xd8\xfc\x55\xd8\xfc\xaa\xd8\xfc\xff\xfc\x00\x00\xfc\x00\x55\xfc\x00\xaa\xfc\x00\xff\xfc\x24\x00\xfc\x24\x55\xfc\x24\xaa\xfc\x24\xff\xfc\x48\x00\xfc\x48\x55\xfc\x48\xaa\xfc\x48\xff\xfc\x6c\x00\xfc\x6c\x55\xfc\x6c\xaa\xfc\x6c\xff\xfc\x90\x00\xfc\x90\x55\xfc\x90\xaa\xfc\x90\xff\xfc\xb4\x00\xfc\xb4\x55\xfc\xb4\xaa\xfc\xb4\xff\xfc\xd8\x00\xfc\xd8\x55\xfc\xd8\xaa\xfc\xd8\xff\xfc\xfc\x00\xfc\xfc\x55\xfc\xfc\xaa\xfc\xfc\xff"

def output_file(data: bytes, output: str, width: int, height: int, bpp: int):
    if bpp == 1:
        temp = Image.frombytes("L", (width + ((8 - (width % 8)) if (width % 8) else 0), height), bytes([0 if x == 1 else 255 for x in data] if MONOCHROME_INVERT else [255 if x == 1 else 0 for x in data]))                
        temp.crop([0,0,width, height]).save(output)        
    elif bpp == 2:
        temp = Image.frombytes("L", (width + ((4 - (width % 4)) if (width % 4) else 0), height), bytes(([0 if x >= 1 else 255 for x in data] if MONOCHROME_INVERT else [255 if x >= 1 else 0 for x in data]) if PAL_2BPP_IS_SINGLE else [PAL_2BPP_INVERT[x] for x in data] if MONOCHROME_INVERT else [PAL_2BPP[x] for x in data]))        
        temp.crop([0,0,width, height]).save(output)        
    elif bpp == 8:
        temp = Image.frombytes("P", (width, height), data)
        temp.putpalette(RGB332)
        temp.save(output)
    elif bpp == 16:
        Image.frombytes("RGB", (width, height), data, "raw", "BGR;16", 0, 1).save(output)  
    elif bpp == 18:
        Image.frombytes("RGB", (width, height), data).save(output) 
    elif bpp == 24:
        Image.frombytes("RGB", (width, height), data, "raw", "BGR").save(output)    
    elif bpp == 32:
        aInvert(Image.frombytes("RGBA", (width, height), data, "raw", "BGRA")).save(output)

def getFormat(data: bytes, width: int, height: int, bpp: int):
    if bpp == 1:
        temp = Image.frombytes("L", (width + ((8 - (width % 8)) if (width % 8) else 0), height), bytes([0 if x == 1 else 255 for x in data] if MONOCHROME_INVERT else [255 if x == 1 else 0 for x in data]))                
        return temp.crop([0,0,width, height])        
    elif bpp == 2:
        temp = Image.frombytes("L", (width + ((4 - (width % 4)) if (width % 4) else 0), height), bytes(([0 if x >= 1 else 255 for x in data] if MONOCHROME_INVERT else [255 if x >= 1 else 0 for x in data]) if PAL_2BPP_IS_SINGLE else [PAL_2BPP_INVERT[x] for x in data] if MONOCHROME_INVERT else [PAL_2BPP[x] for x in data]))        
        return temp.crop([0,0,width, height])        
    elif bpp == 8:
        temp = Image.frombytes("P", (width, height), data)
        temp.putpalette(RGB332)
        return temp
    elif bpp == 16:
        return Image.frombytes("RGB", (width, height), data, "raw", "BGR;16", 0, 1)  
    elif bpp == 18:
        return Image.frombytes("RGB", (width, height), data) 
    elif bpp == 24:
        return Image.frombytes("RGB", (width, height), data, "raw", "BGR")    
    elif bpp == 32:
        return aInvert(Image.frombytes("RGBA", (width, height), data, "raw", "BGRA"))        

def rgb18to24(data: bytes):
    offset = 0
    output = bytearray()

    while offset<len(data):
        pixel = struct.unpack("<L", data[offset:offset+4])[0]        
        output += struct.pack("<BBB", (pixel >> 26) << 2, ((pixel >> 20) & 63) << 2, ((pixel >> 14) & 63) << 2)        
        offset += 4

    return bytes(output)

def pafDecodeFrame(file_buf: io.BytesIO, width: int, height: int, bpp: int):
    if bpp == 1:
        width += ((8 - (width % 8)) if (width % 8) else 0)
    elif bpp == 2:
        width += ((4 - (width % 4)) if (width % 4) else 0)        

    multiplier = 1 if bpp in [1,2] else 4 if bpp == 18 else bpp//8
    out_buffer = io.BytesIO(bytes((width*height)*multiplier))
    out_buffer.seek(0)

    if bpp in [1,2]:
        while file_buf.tell() < len(file_buf.getvalue()):
            length = 1
            pixel = 0
                           
            rle_type = struct.unpack(">B", file_buf.read(1))[0]                            

            if rle_type >= 0x40 and rle_type < 0x80:
                if (rle_type >> 5) & 1:
                    data2 = struct.unpack(">H", file_buf.read(2))[0]                                                
                    
                    length = ((rle_type & 0x1f) << 14) | data2 >> 2 if bpp == 2 else ((rle_type & 0x1f) << 15) | data2 >> 1
                    pixel = data2 & 3 if bpp == 2 else data2 & 1                        
                else:
                    data2 = struct.unpack(">B", file_buf.read(1))[0]
                    
                    length = ((rle_type & 0x1f) << 6) | data2 >> 2 if bpp == 2 else ((rle_type & 0x1f) << 7) | data2 >> 1
                    pixel = data2 & 3 if bpp == 2 else data2 & 1
            elif rle_type >= 0x80 and rle_type < 0xc0:                    
                if bpp == 1:
                    for i in range(6):                                           
                        out_buffer.write(((rle_type >> (5-i)) & 1).to_bytes(1, "little"))

                else:
                    out_buffer.write(((rle_type >> 4) & 3).to_bytes(1, "little"))
                    out_buffer.write(((rle_type >> 2) & 3).to_bytes(1, "little"))
                    out_buffer.write((rle_type & 3).to_bytes(1, "little"))

                continue
            elif rle_type >= 0xc0:                      
                f = file_buf.read(1)

                if not f:
                    if bpp == 1:
                        if PAD_2BPP:
                            #if ((rle_type >> 5) & 1) != 0: 
                            #    out_buffer.write(((rle_type >> 5) & 1).to_bytes(1, "little"))                            
                            pass
                        else:
                            for i in range(6):                                           
                                out_buffer.write(((rle_type >> (5-i)) & 1).to_bytes(1, "little"))

                    else:
                        if PAD_2BPP: 
                            pass
                            #if ((rle_type >> 4) & 3) != 0:
                            #    out_buffer.write(((rle_type >> 4) & 3).to_bytes(1, "little"))
                        else:
                            out_buffer.write(((rle_type >> 4) & 3).to_bytes(1, "little"))
                            out_buffer.write(((rle_type >> 2) & 3).to_bytes(1, "little"))
                            out_buffer.write((rle_type & 3).to_bytes(1, "little"))
                    
                    continue
                
                data = (rle_type & 0x3f) << 8 | f[0]

                if bpp == 1:
                    for i in range(14):                                                 
                        out_buffer.write(((data >> (13-i)) & 1).to_bytes(1, "little"))

                else:
                    out_buffer.write(((data >> 12) & 3).to_bytes(1, "little"))
                    out_buffer.write(((data >> 10) & 3).to_bytes(1, "little"))
                    out_buffer.write(((data >> 8) & 3).to_bytes(1, "little"))
                    out_buffer.write(((data >> 6) & 3).to_bytes(1, "little"))
                    out_buffer.write(((data >> 4) & 3).to_bytes(1, "little"))                                            
                    out_buffer.write(((data >> 2) & 3).to_bytes(1, "little"))
                    out_buffer.write((data & 3).to_bytes(1, "little"))
                    
                continue          
            else:
                length = rle_type >> 2 if bpp == 2 else rle_type >> 1
                pixel = rle_type & 3 if bpp == 2 else rle_type & 1
                            
            out_buffer.write(pixel.to_bytes(1, "little")*length)
                
        if out_buffer.tell()<len(out_buffer.getvalue()):                            
            padding = len(out_buffer.getvalue()) - out_buffer.tell()                

            out_buffer.seek(out_buffer.tell() - 1)                        
            out_buffer.write(out_buffer.read(1) * padding)
    else:
        while file_buf.tell() < len(file_buf.getvalue()):       
            length = 1        
            rle_type = struct.unpack(">B", file_buf.read(1))[0]        

            if rle_type >= 193 and rle_type < 224:
                length = rle_type & 0x1f

            elif rle_type >= 224 and rle_type < 240:                
                length = ((rle_type & 0xf) << 8) | file_buf.read(1)[0]

            elif rle_type >= 240:
                length = ((rle_type & 0xf) << 16) | struct.unpack(">H", file_buf.read(2))[0]            
                
            else:
                file_buf.seek(file_buf.tell()-1)

            out_buffer.write(file_buf.read(4 if bpp == 18 else bpp//8) * length)
        
        if out_buffer.tell()<len(out_buffer.getvalue()):            
            padding = (len(out_buffer.getvalue()) - out_buffer.tell()) // (4 if bpp == 18 else bpp//8)            

            out_buffer.seek(out_buffer.tell() - (4 if bpp == 18 else bpp//8))                        
            out_buffer.write(out_buffer.read(4 if bpp == 18 else bpp//8) * padding)

    if bpp == 18:
        return rgb18to24(out_buffer.getvalue())
    
    else:
        return out_buffer.getvalue()
        
    '''
    if bpp in [1,2]:
        BPP1 = [b"\x00", b"\xff"]
        BPP2 = [b"\x00", b"\x60", b"\xc0", b"\xff"]

        o_buf = bytearray()
        while file_buf.tell() < len(file_buf.getvalue()):       
            count = 1
            pixel = 0

            rle_type = struct.unpack(">B", file_buf.read(1))[0]            

            if rle_type >= 0x40 and rle_type < 0x80:
                if (rle_type >> 5) & 1:
                    data2 = struct.unpack(">B", file_buf.read(1))[0]
                    data3 = struct.unpack(">B", file_buf.read(1))[0]

                    count = ((rle_type & 0x1f) << 14) | (data2 << 6) | (data3 >> 2) if bpp == 2 else ((rle_type & 0x3f) << 15) | (data2 << 7) | (data3 >> 1)
                    pixel = data3 & 3 if bpp == 2 else data3 & 1
                    pass
                else:
                    data2 = struct.unpack(">B", file_buf.read(1))[0]
                    count = ((rle_type & 0x1f) << 6) | (data2 >> 2) if bpp == 2 else ((rle_type & 0x3f) << 7) | (data2 >> 1)
                    pixel = data2 & 3 if bpp == 2 else data2 & 1
            elif rle_type >= 0x80 and rle_type < 0xc0:
                if bpp == 1:
                    for i in range(6):                        
                        #print(5-i)
                        o_buf += BPP1[(rle_type >> (5-i)) & 1]                     
                else:
                    o_buf += BPP2[(rle_type >> 4) & 3]   
                    o_buf += BPP2[(rle_type >> 2) & 3]   
                    o_buf += BPP2[rle_type & 3]   

                continue
            elif rle_type >= 0xc0:   
                if bpp == 1:
                    for i in range(6):                                                
                        o_buf += BPP1[(rle_type >> (5-i)) & 1]                     
                else:
                    o_buf += BPP2[(rle_type >> 4) & 3]   
                    o_buf += BPP2[(rle_type >> 2) & 3]   
                    o_buf += BPP2[rle_type & 3]

                data2 = file_buf.read(1)[0]
                if bpp == 1:
                    for i in range(8):                                                
                        o_buf += BPP1[(data2 >> (7-i)) & 1]                     
                else:
                    o_buf += BPP2[(data2 >> 6) & 3] 
                    o_buf += BPP2[(data2 >> 4) & 3]   
                    o_buf += BPP2[(data2 >> 2) & 3]   
                    o_buf += BPP2[data2 & 3]      

                continue          
            else:
                count = rle_type >> 2 if bpp == 2 else rle_type >> 1
                pixel = rle_type & 3 if bpp == 2 else rle_type & 1

            #print("R:",hex(rle_type),hex(count), pixel)
            o_buf += (BPP2[pixel] if bpp == 2 else BPP1[pixel])*count

        return o_buf    

    p_bit = b""
    o_buf = bytearray()
    while file_buf.tell() < len(file_buf.getvalue()):       
        length = 1        
        rle_type = struct.unpack(">B", file_buf.read(1))[0]        
        if rle_type >= 193 and rle_type < 224:
            length = rle_type & 0x1f
        elif rle_type >= 224 and rle_type < 240:
            file_buf.seek(file_buf.tell()-1)
            length = struct.unpack(">H", file_buf.read(2))[0] & 0xfff
        elif rle_type >= 240:
            length = struct.unpack(">H", file_buf.read(2))[0]            
        else:
            file_buf.seek(file_buf.tell()-1)



        if bpp == 8:
            p_bit = rgb332_get(file_buf.read(1)[0])
        else:
            p_bit = file_buf.read(4 if bpp == 18 else int(bpp/8))

        o_buf += p_bit*length

    if bpp == 8:
        bpp = 24

    if len(o_buf) < (width*height)*(int(bpp/8)):
        padding_needed = (width*height)
        if not FIX_1PX_DOTS:
            p_bit = b"\0"*int(bpp/8)
        o_buf += p_bit * (padding_needed-int(len(o_buf)/(bpp/8)))
        assert len(o_buf) == padding_needed*(bpp/8), f"{len(o_buf)} - {padding_needed}"

    if bpp == 18:
        o_buf = rgb18to24(o_buf)
    return bytes(o_buf)
    '''

def pafXORBytes(b1, b2):
    return bytes(bytearray(a ^ b for a, b in zip(b1, b2)))

def aInvert(i1: Image.Image):    
    a_data = b"".join([struct.pack("<B", a^0xff) for a in i1.getdata(3)])
    p = i1.copy()    
    p.putalpha(Image.frombytes("L", i1.size, a_data))
    return p

class __PAFFrame():
    def __init__(self, width, height, bpp, image):
        self.width = width
        self.height = height
        self.bpp = bpp
        self.image = image

doXOR = False

def loadPAF(file_buf):
    assert file_buf.read(3) == b"PAF", "Not a valid PAF image."

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

    assert bpp in [1,2,8,16,18,24,32], f"{bpp}-bit PAF images are not supported."    

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
        
    isStart = True
    canvas = None

    for frame in paf_frames:            
        if isStart or not doXOR:
            canvas = pafDecodeFrame(frame, width, height, bpp)
            isStart = False
        else:
            canvas = pafXORBytes(canvas, pafDecodeFrame(frame, width, height, bpp))
        yield __PAFFrame(width, height, bpp, getFormat(canvas, width, height, bpp))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        import tkinter as tk
        from tkinter import messagebox, filedialog
        imgTk = None

        class PAFCanvas(tk.Canvas):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.bind("<Configure>", self.on_resize)  


            def on_resize(self, event):
                if imgTk:
                    photo.delete("all")
                    photo.create_image(event.width/2,event.height/2,anchor=tk.CENTER,image=imgTk)
            
        paf_images = None
        curFrame = 0

        def handleKeyboard(e):
            global curFrame, paf_images
            if e.keycode == 37:
                if not paf_images: return
                if curFrame <= 0: return
                curFrame -= 1

                setPafFrame(curFrame)
            elif e.keycode == 39:
                if not paf_images: return
                if curFrame >= len(paf_images)-1: return

                curFrame += 1
                setPafFrame(curFrame)

        def setPafFrame(frame):            
            imgTk = ImageTk.PhotoImage(paf_images[frame].image)
            infoBar.config(text=f"{paf_images[frame].width}x{paf_images[frame].height}x{paf_images[frame].bpp}bpp {frame+1} out of {len(paf_images)}")

            photo.image = imgTk
            photo.create_image(photo.winfo_width()/2,photo.winfo_height()/2,anchor=tk.CENTER,image=imgTk)

        class gifExportDialog(tk.Frame):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # self allow the variable to be used anywhere in the class
                self.set = False
                self.duration = -1
                self.loop = -1
                self.initUI()             

            def __checkDigit(self, P):                
                if str.isdigit(P) or P == "" or P == "-" or P == "-1":
                    return True
                else:
                    return False

            def initUI(self):

                checkDigit = (self.register(self.__checkDigit))                                

                self.master.title("GIF Export Settings")
                self.pack(fill=tk.BOTH, expand=True)

                frame1 = tk.Frame(self)
                frame1.pack(fill=tk.X)

                lbl1 = tk.Label(frame1, text="Duration", width=6)
                lbl1.pack(side=tk.LEFT, padx=5, pady=10)

                self.entry1 = tk.Entry(frame1, validate='all', validatecommand=(checkDigit, '%P'))
                self.entry1.insert(0, "100")
                
                self.entry1.pack(fill=tk.X, padx=5, expand=True)

                frame2 = tk.Frame(self)
                frame2.pack(fill=tk.X)

                lbl2 = tk.Label(frame2, text="Loop Count", width=6)
                lbl2.pack(side=tk.LEFT, padx=5, pady=10)

                self.entry2 = tk.Entry(frame2, validate='all', validatecommand=(checkDigit, '%P'))
                self.entry2.insert(0, "0")

                self.entry2.pack(fill=tk.X, padx=5, expand=True)

                frame3 = tk.Frame(self)
                frame3.pack(fill=tk.X)

                # Command tells the form what to do when the button is clicked
                btn = tk.Button(frame3, text="OK", command=self.onSubmit)
                btn.pack(side=tk.LEFT, padx=5, pady=10)

                btn2 = tk.Button(frame3, text="Cancel", command=self.onCancel)
                btn2.pack(side=tk.RIGHT, padx=5, pady=10)

            def onSubmit(self):
                self.set = True
                self.duration = int(self.entry1.get())
                self.loop = int(self.entry2.get())
                self.master.destroy()

            def onCancel(self):
                self.master.destroy()                

        def openPaf():
            global imgTk, paf_images, curFrame, MONOCHROME_INVERT, PAL_2BPP_IS_SINGLE, PAD_2BPP, doXOR

            MONOCHROME_INVERT = mono_invert.get()
            PAL_2BPP_IS_SINGLE = pal_2bpp_1bpp.get()
            PAD_2BPP = pad_2bpp_data.get()
            doXOR = do_xor.get()

            file = filedialog.askopenfile("rb", filetypes=[("PAF image", "*.paf")])            
            if file != None:                  
                photo.delete("all")
                paf_images = None
                imgTk = None
                file_menu.entryconfig("Save", state="disabled")

                try:
                    paf_images = [x for x in loadPAF(file)]

                    root.geometry(f"{max(256, paf_images[0].image.width)}x{max(256, paf_images[0].image.height)}")

                    curFrame = 0                                                                  
                    setPafFrame(0)

                    file_menu.entryconfig("Save", state="normal")
                except Exception as e:                    
                    messagebox.showerror("PAF Viewer", e)

        def savePaf():
            global paf_images

            file = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG image", "*.png"), ("BMP image", "*.bmp"), ("JPG image", "*.jpg"), ("RAW image", "*.raw"), ("GIF image", "*.gif")])           
            if file:
                if len(paf_images) <= 1:
                    if file.endswith(".bmp"):
                        paf_images[0].image.convert("RGB").save(file)
                    elif file.endswith(".jpg"):
                        paf_images[0].image.convert("RGB").save(file)
                    elif file.endswith(".raw"):
                        open(file, "wb").write(paf_images[0].image.tobytes())
                    elif file.endswith(".gif"):
                        paf_images[0].image.save(file)
                    else:
                        if not file.endswith(".png"): file += ".png"
                        paf_images[0].image.save(file)                                            
                else:
                    if file.endswith(".raw"):                        
                        temp = open(file, "wb")
                        for f in paf_images:
                            temp.write(f.image.tobytes())
                    elif file.endswith(".gif"):
                        frames = [x.image for x in paf_images]   

                        gifSettingWindow = tk.Toplevel()
                        gifSetting = gifExportDialog(gifSettingWindow)
                        
                        gifSettingWindow.grab_set()
                        gifSettingWindow.wait_window()

                        if not gifSetting.set: return

                        if gifSetting.loop == -1:
                            frames[0].save(file, save_all=True, append_images=frames[1:], duration=gifSetting.duration, include_color_table=True)
                        else:
                            frames[0].save(file, save_all=True, append_images=frames[1:], duration=gifSetting.duration, loop=gifSetting.loop, include_color_table=True)
                    else:
                        count = 0
                        for f in paf_images:
                            count += 1
                            frame_file = f"{os.path.splitext(file)[0]}_{count}{os.path.splitext(file)[1]}"                            

                            if file.endswith(".bmp"):
                                f.image.convert("RGB").save(frame_file)
                            elif file.endswith(".jpg"):
                                f.image.convert("RGB").save(frame_file)                                                    
                            else:
                                if not frame_file.endswith(".png"): frame_file += ".png"
                                f.image.save(frame_file)   
                    

        root = tk.Tk()       
        root.geometry("256x256") 
        root.title("PAF Viewer")

        root.bind("<KeyPress>", handleKeyboard)

        menu_bar = tk.Menu(root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=openPaf)
        file_menu.add_command(label="Save", command=savePaf, state="disabled")        
        file_menu.add_command(label="Exit", command=root.quit)

        menu_bar.add_cascade(label="File", menu=file_menu)

        mono_invert = tk.BooleanVar()
        pal_2bpp_1bpp = tk.BooleanVar()
        pad_2bpp_data = tk.BooleanVar()
        do_xor = tk.BooleanVar(value=1)

        option_menu = tk.Menu(menu_bar, tearoff=0)
        option_menu.add_checkbutton(label="Invert grayscale palette", onvalue=1, offvalue=0, variable=mono_invert)
        option_menu.add_checkbutton(label="Force 1bpp on 2bpp image", onvalue=1, offvalue=0, variable=pal_2bpp_1bpp)
        option_menu.add_checkbutton(label="2bpp padding", onvalue=1, offvalue=0, variable=pad_2bpp_data)
        option_menu.add_checkbutton(label="Do frame XOR", onvalue=1, offvalue=0, variable=do_xor)

        menu_bar.add_cascade(label="Option", menu=option_menu)

        photo = PAFCanvas(root, bg="white", width=0, height=0)
        photo.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        root.config(menu=menu_bar)

        infoBar = tk.Label(root, text="PAF Viewer", relief=tk.SUNKEN, anchor="w")
        infoBar.pack(side=tk.BOTTOM, fill=tk.X)

        root.mainloop()
    else:
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

        assert bpp in [1,2,8,16,18,24,32], f"{bpp}-bit PAF images is not supported."    

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
