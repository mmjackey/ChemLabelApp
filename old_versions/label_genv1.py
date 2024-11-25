# importing modules 
from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfbase import pdfmetrics 
from reportlab.lib import colors 
from reportlab.lib.pagesizes import landscape,A4

# initializing variables with values 
fileName = 'sample.pdf'
documentTitle = 'sample'
title = 'sofab'
subTitle = 'AHHHHHHH'
textLines = [ 
	'Sticker draft version 1', 
	'this is a text document.', 
] 
image = 'barcode.png'

# creating a pdf object 
pdf = canvas.Canvas(fileName) 

## change orientation of page
#canvas.Canvas.setPageSize(pdf, (landscape(A4)))

# setting the title of the document 
pdf.setTitle(documentTitle) 


# creating the title by setting it's font 
# and putting it on the canvas  
pdf.setFont('Courier-Bold', 36) 
pdf.drawCentredString(300, 770, title) 

# creating the subtitle by setting it's font, 
# colour and putting it on the canvas 
pdf.setFillColorRGB(0, 0, 255) 
pdf.setFont("Courier-Bold", 24) 
pdf.drawCentredString(290, 720, subTitle) 

# drawing a line 
pdf.line(30, 710, 550, 710) 

# creating a multiline text using 
# textline and for loop 
text = pdf.beginText(40, 680) 
text.setFont("Courier", 18) 
text.setFillColor(colors.red) 
for line in textLines: 
	text.textLine(line) 
pdf.drawText(text) 

# drawing a image at the 
# specified (x.y) position 
pdf.drawInlineImage(image, 130, 400) 

# saving the pdf 
pdf.save() 
