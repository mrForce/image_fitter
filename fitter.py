from PIL import Image
import math
"""
This distributes k images, each with some area, onto n pages. 

It tries to distribute them so as to minimize the maximum area on a page. It uses the Sorted Load Balance algorithm for this (which is just a heuristic)
"""

def distribute(images, num_pages):
    images_sorted = sorted(images, key=lambda x: x.area(), reverse=True)
    image_assignment = [{'area': 0, 'images':[]} for page in range(0, num_pages)]
    for image in images_sorted:
        lowest_area_page = min(image_assignment, key=lambda x: x['area'])
        lowest_area_page.area += image.area()
        lowest_area_page.images.append(image)
    return image_assignment

class NoFeasibleSolutionError(Exception):
    pass
class NoFeasiblePageFitError(NoFeasibleSolutionError):
    def __init__(self, message):
        self.message = message

class FitterImage:
    def __init__(self, pil_image):
        self.pil_image = pil_image
        self.image_bb = image_bb
        self.width = pil_image.width
        self.height = pil_image.height
        self.scaling_factor = 1.0
    def getPILImage(self):
        return self.pil_image
    def getWidth(self):
        return (1.0*self.width)/scaling_factor
    def getHeight(self):
        return (1.0*self.height)/scaling_factor
    def area(self):
        return self.getWidth()*self.getHeight()
    def setScalingFactor(self, scaling_factor):
        self.scaling_factor = scaling_factor
    def getScalingFactor(self):
        return self.scaling_factor

    
class Page:
    #images should a list of FitterImage objects
    def __init__(self, images, width_inches, height_inches):
        self.images = images
        self.width_pixels = 300*width
        self.height_pixels = 300*height
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
        height, rectangles = self.testfit(low)
        if low > self.height_pixels:
            raise NoFeasiblePageFitError('No way to fit images onto page')
        middle = (high + low)/2
        for x in range(0, 20):
            height, rectangles = self.testfit(middle)
            if height <= self.height_pixels:
                low = middle
            else:
                high = middle
            middle = (high + low)/2
        height, rectangles = self.testfit(middle)
        if height <= self.height_pixels:
            return zip(self.images, rectangles)
        else:
            height, rectangles = self.testfit(low)
            return zip(self.images, rectangles)
        
    

images = ['homework4-1.png', 'homework4-2.png', 'homework4-3.png', 'homework4-4.png']
width = 8.5
height = 11
num_pages = 2

images = list()
for im_name in image_names:
    image = Image.open(im_name)
    images.append(image)

page_assigment = distribute(images, num_pages)
print('page assignment')
print(page_assignment)
pages = list()
for i in range(0, num_pages):
    fitter_images = [FitterImage(image) for image in pages_assigment[i]['images']]
    page = Page(fitter_images, width, height)
    pages.append(page)
    try:
        height, rectangles = page.fitImagesOnPage()
    except NoFeasiblePageFitError:
        print('no feasible page solution')
    else:
        visualize(page.width_pixels, height, rectangles)
    
