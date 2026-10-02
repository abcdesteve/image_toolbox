from PIL import Image, ImageFilter, ImageDraw, ImageOps
import numpy


def sketch(img):
    mode = img.mode
    grey = numpy.int16(numpy.array(img.convert('L')))
    blur = numpy.int16(numpy.array(ImageOps.invert(
        img.convert('L')).filter(ImageFilter.GaussianBlur(5))))
    blur = numpy.int16(grey+grey*blur/(numpy.int16(255)-blur)) # a+a*b/(255-b)
    # blur = numpy.int16(grey*numpy.int16(255)/(numpy.int16(256)-blur)) # a*255/(256-b)
    blur[blur > 255] = 255
    return Image.fromarray(numpy.uint8(blur)).convert(mode)


def char(img_color):
    scale=8
    img_color = img_color.resize((img_color.width//scale, img_color.height//scale))
    img_black = img_color.convert('L')
    width, height = img_color.size
    code = r'''$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. '''

    img = Image.new(img_color.mode, (width*scale, height*scale), 'white')
    draw = ImageDraw.Draw(img)

    for y in range(height):
        for x in range(width):
            pos = (x, y)
            data = img_black.getpixel(pos)
            index = int(data/256*len(code))
            color = img_color.getpixel(pos)
            draw.text((x*scale, y*scale), code[index], color)

    return img
