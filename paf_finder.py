import os
import sys
import struct

def main():
    if len(sys.argv) < 2:
        print("Not enough arguments")
        sys.exit(1)	
    ftmp = bytearray()
    inp = open(sys.argv[1], "rb")
    dtbuf = inp.read()
    while dtbuf != b"":
        ftmp += dtbuf
        dtbuf = inp.read()

    if not (os.path.exists(sys.argv[1] + "_ext_paf")):  os.mkdir(sys.argv[1] + "_ext_paf")


    for V in range(9):        
        offset = ftmp.find(f"PAF{V}".encode("ascii"))	
        cnt = 0	
        while offset != -1:
            cnt += 1
            bpp = ftmp[offset+4]
            nextifeg = ftmp.find(b"EndOfPAF\0", offset+1)
            if nextifeg == -1:
                nextifeg = None
            else:
                nextifeg += 9
            open(f"{sys.argv[1]}_ext_paf/PAF_{cnt}_{V}_{bpp}.paf", "wb").write(ftmp[offset:nextifeg])
            offset = ftmp.find(f"PAF{V}".encode("ascii"), offset+1)	

if __name__ == "__main__":
	main()
