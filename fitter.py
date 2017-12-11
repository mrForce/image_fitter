from PIL import Image

images = ['homework4-1.png', 'homework4-2.png', 'homework4-3.png', 'homework4-4.png']
width = 8.5
height = 11

images = list()
for im_name in image_names:
    image = Image.open(im_name)
    image_bb = im.getbbox()
    
    
