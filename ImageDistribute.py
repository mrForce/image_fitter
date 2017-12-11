"""
This distributes k images, each with some area, onto n pages. 

It tries to distribute them so as to minimize the maximum area on a page. It uses the Sorted Load Balance algorithm for this
"""

def distribute(images, num_pages):
    images_sorted = sorted(images, key=lambda x: x.area(), reverse=True)
    image_assignment = [{'area': 0, 'images':[]} for page in range(0, num_pages)]
    for image in images_sorted:
        lowest_area_page = min(image_assignment, key=lambda x: x['area'])
        lowest_area_page.area += image.area()
        lowest_area_page.images.append(image)
    return image_assignment
