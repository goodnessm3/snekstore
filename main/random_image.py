from PIL import Image, ImageDraw, ImageFont
import random
import os


def random_image():

    out = Image.new("RGB", (250, 250), (255, 255, 255))
    d = ImageDraw.Draw(out)

    astr = ""
    while len(astr) < 8:
        astr += chr(random.randint(65, 90))
    d.multiline_text((10, 10), astr, fill=(0, 0, 0))

    fname = os.path.join("main", "static", "generated", f"{astr}.png")
    out.save(fname)  # need to specify the whole path for save location
    return f"generated/{astr}.png"  # RELATIVE
