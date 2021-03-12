#Move selective file mantaining directory tree
import os
from shutil import copy2

rootdir = f'./bench-batch/'
dst = f"./moved/"
for subdir, dirse, files in os.walk(rootdir):
    break

# print(subdir,dirse, files)

for gra in dirse:
    for subdir, dirse, files in os.walk(rootdir+gra):
        break
    print(gra)
    for one in dirse:
        print(one)
        os.makedirs(os.path.dirname(dst+gra+f"/{one}/"), exist_ok=True)
        copy2(rootdir+gra+f"/{one}/cache.json", dst+gra+f"/{one}/cache.json")
        copy2(rootdir+gra+f"/{one}/res.json", dst+gra+f"/{one}/res.json")
