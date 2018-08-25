## import numpy as np is a convention
import numpy as np
## we need matplotlib just to read and show data
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from math import sqrt
from PIL import Image, ImageFont, ImageDraw
#from operator import itemgetter, attrgetter, methodcaller
import functools




def lookForNextPlot(new_img,plots,index,nb_of_row,nb_of_col,background,power):
    current_plot = plots[index]
    x = current_plot[0]
    y = current_plot[1]
    for i in [-2,-1,0,1,2]:
        for j in [-2,-1,0,1,2]:
            if x+i > 0 and y+j > 0 and x+i < nb_of_col and y+j < nb_of_row:
                if new_img[y+j][x+i]["isChecked"] == 0 and new_img[y+j][x+i]["isHiero"] == 1:
                    new_img[y+j][x+i]["isChecked"] = 1
                    new_plot = [x+i,y+j]
                    plots.append(new_plot)
    return(new_img)



def startNewLocalization(new_img,row,col,nb_of_row,nb_of_col,background,power):
    plots = []
    new_plot = [col,row]
    plots.append(new_plot)
    please_continue = True
    index = 0
    while index < len(plots):
        new_img = lookForNextPlot(new_img,plots,index,nb_of_row,nb_of_col,background,power)
        index += 1
    return(plots)


def lookIfIsHieroglyph(intensity,background,power=40):
    if (int(intensity) - int(background)) > power or (int(background) - int(intensity)) > power:
        isHieroglyph = 1
    else:
        isHieroglyph = 0
    return(isHieroglyph)

def get_background_from_image(image_np):
    background=image_np[0,0,0]
    return background

def locateHieroglyphs(image,image_np,list_of_hieroglyphs,background='', power=20):
    if background=='':
        background=get_background_from_image(image_np)
#    print(image_np[0,0,0])
    nb_of_row = image_np.shape[0]
    nb_of_col = image_np.shape[1]
#    print(nb_of_row)
#    print(nb_of_col)
    listOfLocalizedHiero = []
    minIntensity = 255
    maxIntensity = 0
    new_img = [[{"intensity":0,"isHiero":0,"isChecked":0} for x in range(nb_of_col)] for y in range(nb_of_row)]
    for row in range(nb_of_row):
        for col in range(nb_of_col):
            intensity = image_np[row][col][0]
            new_img[row][col]["intensity"] = intensity

            isHiero = lookIfIsHieroglyph(intensity,background,power)
            new_img[row][col]["isHiero"] = isHiero

    print("finished determine isHiero")

    for row in range(nb_of_row):
        for col in range(nb_of_col):
            #if new_img[row][col]["isHiero"] == 1:
                #dr = ImageDraw.Draw(img)
                #dr.line(((col,row),(col,row)), fill="red")

            if new_img[row][col]["isHiero"] == 1 and new_img[row][col]["isChecked"] == 0:
                new_img[row][col]["isChecked"] = 1
                plots = startNewLocalization(new_img,row,col,nb_of_row,nb_of_col,background,power)
                if len(plots) > 20:
                    new_hiero = HieroGlyph(plots)
                    list_of_hieroglyphs.append(new_hiero)
                    new_hiero.surround_hiero(image)

def compare_hiero(x, y):
    to_return = 0
    if x.line < y.line:
        to_return = -1
    elif x.line > y.line:
        to_return = 1
    else:
        if x.minX==y.minX and x.maxX==y.maxX and x.minY==y.minY and x.maxY==y.maxY:
            to_return = 0
        else:
            if x.maxX < y.minX:
                to_return = -1
            elif x.minX > y.maxX:
                to_return = 1
            else:
                if x.maxY < y.minY:
                    to_return = -1
                elif x.minY > y.maxY:
                    to_return = 1
                else:
                    if x.minY < y.minY:
                        to_return = -1
                    else:
                        to_return = 1
    return(to_return)

class HieroGlyph:
    widths = []
    heights = []
    def __init__(self, plots):
        self.plots = plots
        self.minX, self.maxX, self.minY, self.maxY = self.get_minX_maxX_minY_maxY()
        self.width=self.maxX-self.minX
        self.height=self.maxY-self.minY
        HieroGlyph.widths.append(self.width)
        HieroGlyph.heights.append(self.height)
        self.line = 0

    def get_minX_maxX_minY_maxY(self):
        minX = self.plots[0][0]
        maxX = self.plots[0][0]
        minY = self.plots[0][1]
        maxY = self.plots[0][1]
        for plot in self.plots:
            if plot[0] > maxX:
                maxX = plot[0]
            elif plot[0] < minX:
                minX = plot[0]
            if plot[1] > maxY:
                maxY = plot[1]
            elif plot[1] < minY:
                minY = plot[1]
        return minX, maxX, minY, maxY

    def create_image(self,original_image_np, background=''):
        if background=='':
            background=original_image_np[0,0]
            bg_color = (background[0],background[1],background[2])
        hiero_im = Image.new("RGB", (self.width+6,self.height+6), bg_color)
        hiero_dr = ImageDraw.Draw(hiero_im)
        for plot in self.plots:
            newX = plot[0]-self.minX+3
            newY = plot[1]-self.minY+3
            new_color = original_image_np[plot[1]][plot[0]]
            hiero_dr.point((newX,newY),(new_color[0],new_color[1],new_color[2]))
#        plt.imshow(hiero_im)
#        plt.show()


    def surround_hiero(self,original_image):
        minX, maxX, minY, maxY = self.minX-3, self.maxX+3, self.minY-3, self.maxY+3

        dr = ImageDraw.Draw(original_image)
        dr.line(((minX,minY),(maxX,minY)), fill="red", width=2)
        dr.line(((maxX,minY),(maxX,maxY)), fill="red", width=2)
        dr.line(((maxX,maxY),(minX,maxY)), fill="red", width=2)
        dr.line(((minX,maxY),(minX,minY)), fill="red", width=2)


img_black_white = Image.open('img/Sans Titre9.png').convert('LA')
img_black_white_np = np.array(img_black_white)

img_color = Image.open('img/Sans Titre9.png').convert('RGB')
img_color_np = np.array(img_color)

print(img_color_np.shape)
# Create figure and axes#
# fig,ax = plt.subplots(1)

list_of_hieroglyphs = []

locateHieroglyphs(img_black_white,img_black_white_np,list_of_hieroglyphs,230,45)

list_of_hieroglyphs = sorted(list_of_hieroglyphs,key=functools.cmp_to_key(compare_hiero))

list_of_hieroglyphs[27].create_image(img_color_np)

plt.imshow(img_black_white)
plt.show()
