from PIL import Image
import os
import glob

counter = 0
pngs = glob.glob(os.path.join("smileys", '*.png'))
print(pngs)

for image in pngs:
    counter += 1
    number = counter if counter > 9 else "0" + str(counter)
    im = Image.open(image)
    nx, ny = im.size
    print(nx, ny)
    im2 = im.resize((64, 64), Image.BICUBIC)
    im2.save(f"icons_{image}")
