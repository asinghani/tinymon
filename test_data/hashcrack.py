# Example program for brute-forcing the hash of a 8-digit PIN code
import hashlib
import sys

tgt_hash = sys.argv[1]
outfile = sys.argv[2]

# 6-digit PIN codes
MAX = 999999+1

last_percentage = 0
for i in range(MAX):
    percentage = (100*(i / MAX))
    if int(percentage) != int(last_percentage):
        print(f"progress = {round(percentage, 2)}%")
    last_percentage = percentage

    pincode = "{:06d}".format(i)

    if hashlib.sha256(pincode.encode()).hexdigest().lower() == tgt_hash.lower():
        print("FOUND", pincode)
        with open(outfile, "w+") as f:
            f.write(f"FOUND = {pincode}")
        sys.exit(0)

print("No result found")
with open(outfile, "w+") as f:
    f.write("No result found")
