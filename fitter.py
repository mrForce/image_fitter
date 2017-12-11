from PIL import Image
import math
from spp.ph import phspprg
from spp import visualize
from collections import namedtuple

"""
This distributes k images, each with some area, onto n pages. 

It tries to distribute them so as to minimize the maximum area on a page. It uses the Sorted Load Balance algorithm for this (which is just a heuristic)
"""

def distribute(images, num_pages):
    images_sorted = sorted(images, key=lambda x: x.area(), reverse=True)
    image_assignment = [{'area': 0, 'images':[]} for page in range(0, num_pages)]
    for image in images_sorted:
        print(image)
        lowest_area_page = min(image_assignment, key=lambda x: x['area'])
        lowest_area_page['area'] += image.area()
        lowest_area_page['images'].append(image)
    return image_assignment

class NoFeasibleSolutionError(Exception):
    pass
class NoFeasiblePageFitError(NoFeasibleSolutionError):
    def __init__(self, message):
        self.message = message

class FitterImage:
    def __init__(self, pil_image, name):
        self.pil_image = pil_image
        self.width = pil_image.width
        self.height = pil_image.height
        self.scaling_factor = 1.0
        self.name = name
    def getPILImage(self):
        return self.pil_image
    def getWidth(self):
        return (1.0*self.width)/self.scaling_factor
    def getHeight(self):
        return (1.0*self.height)/self.scaling_factor
    def area(self):
        return self.getWidth()*self.getHeight()
    def setScalingFactor(self, scaling_factor):
        self.scaling_factor = scaling_factor
    def getScalingFactor(self):
        return self.scaling_factor
    def __repr__(self):
        return 'FitterImage with name: {0} of height: {1}, width: {2}, area: {3}'.format(self.name, self.getHeight(), self.getWidth(), self.area())
    
class Page:
    #images should a list of FitterImage objects
    def __init__(self, images, width_inches, height_inches):
        self.images = images
        self.width_pixels = int(300*width)
        self.height_pixels = int(300*height)
    def getImages(self):
        return self.images
    def testFit(self, scaling_factor):
        boxes = list()
        for image in self.images:
            image.setScalingFactor(scaling_factor)
            boxes.append([image.getWidth(), image.getHeight()])
        height, rectangles = phspprg(self.width_pixels, boxes)
        height_two, rectangles_two = phspprg(self.width_pixels, boxes, sorting='height')
        if height < height_two:
            return (height, rectangles)
        else:
            return (height_two, rectangles_two)
    #returns a list of tuples, [(FitterImage, namedtuple('Rectangle', ['x', 'y', 'w', 'h']))]
    def fitImagesOnPage(self):
        images_area = sum([image.area() for image in self.images])
        high = math.sqrt(1.0*images_area/(self.width_pixels*self.height_pixels))
        height, rectangles = self.testFit(high)
        if height <= self.height_pixels:
            return zip(self.images, rectangles)
        #so "low" is actually a higher scaling factor -- the higher the scaling factor, the smaller each image is relative to the page
        low = 2.0*high
        height, rectangles = self.testFit(low)
        if low > self.height_pixels:
            raise NoFeasiblePageFitError('No way to fit images onto page')
        middle = (high + low)/2
        for x in range(0, 20):
            height, rectangles = self.testFit(middle)
            if height <= self.height_pixels:
                low = middle
            else:
                high = middle
            middle = (high + low)/2
        height, rectangles = self.testFit(middle)
        if height <= self.height_pixels:
            return zip(self.images, rectangles)
        else:
            height, rectangles = self.testFit(low)
            return zip(self.images, rectangles)
        
    

image_names = ['one.jpg', 'two.jpg', 'three.png', 'four.jpg', 'five.jpg', 'six.jpg', 'seven.jpg']
width = 8.5
height = 11
num_pages = 2

images = list()
for im_name in image_names:
    image = Image.open(im_name)
    images.append(FitterImage(image, im_name))

page_assignment = distribute(images, num_pages)
print('page assignment')
print(page_assignment)
pages = list()
for i in range(0, num_pages):
    fitter_images = [image for image in page_assignment[i]['images']]
    page = Page(fitter_images, width, height)
    pages.append(page)
    try:
        results = page.fitImagesOnPage()
    except NoFeasiblePageFitError:
        print('no feasible page solution')
    else:
        rectangles = [x[1] for x in results]
        visualize(page.width_pixels, page.height_pixels, rectangles)
        page_image = Image.new('RGB', (page.width_pixels, page.height_pixels))
        for j in range(0, len(rectangles)):
            rectangle = rectangles[j]
            print(rectangle)
            x = int(rectangle[0])
            y = int(rectangle[1])
            new_width = rectangle[2]
            new_height = rectangle[3]
            old_width = 1.0*fitter_images[j].width
            old_height = 1.0*fitter_images[j].height
            flipped = False
            if (old_width/old_height > 1.0 and new_width/new_height < 1.0) or (old_width/old_height < 1.0 and new_width/new_height > 1.0):
                flipped = True
                print('flipped!')
            name = fitter_images[j].name
            print('fitter image: {0}, had w/h of: {1}, now it is: {2}'.format(name, 1.0*fitter_images[j].width/fitter_images[j].height, 1.0*new_width/new_height))
            image = fitter_images[j].getPILImage()
            if flipped:
                image = image.rotate(90, expand=True)
            resized_image = image.resize((int(new_width), int(new_height)))
            page_image.paste(resized_image, (x, page.height_pixels - (y + int(new_height))))
        page_image.save('page_{0}.jpg'.format(i))
            
            
