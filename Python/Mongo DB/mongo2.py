val = "16 800  mAh"
val = int(val[0:val.index("mAh")].replace(" ", ""))

print(val)

price = "1 999,-"
price = int(price[0:-2].replace(" ", ""))

print(price)

width = "82,5 mm (8,25 cm)"
print(float(width[0:width.index(" ")].replace(",", ".")))

usb_c = False
text = "Micro USB, USB-C, USB-A"
if text.find("USB-fsdC") > -1:
    usb_c = True
print(usb_c)
