from PIL import Image, ImageDraw

def char(img_color):
    img_color = img_color.resize((img_color.width//6, img_color.height//6)).convert('RGBA')
    img_black = img_color.convert('L')
    width, height = img_color.size
    code = '''$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. '''

    img = Image.new('RGBA', (width*6, height*6), 'white')
    draw = ImageDraw.Draw(img)

    for y in range(height):
        for x in range(width):
            pos = (x, y)
            data = img_black.getpixel(pos)
            index = int(data/256*len(code))
            color = img_color.getpixel(pos)
            draw.text((x*6, y*6), code[index], fill=color)

    return img