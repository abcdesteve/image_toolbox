from PIL import Image,ImageOps,ImageFilter

def sketch(img):
    width, height = img.size
    grey=img.convert('L')
    invert=ImageOps.invert(grey)
    blur=invert.filter(ImageFilter.GaussianBlur(5))
    for x in range(width):
        for y in range(height):
            pos=(x,y)
            a=grey.getpixel(pos)
            b=blur.getpixel(pos)
            blur.putpixel(pos,min(int(a+a*b/(256-b)),255))
    return blur