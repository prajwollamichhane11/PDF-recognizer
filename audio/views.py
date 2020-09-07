import os
import sys
import subprocess
import re
from PyPDF2 import PdfFileWriter, PdfFileReader
from pdf2image import convert_from_path

#######################################
from django.shortcuts import render
from django.http import HttpResponse
#######################################
from audio.forms import StudentForm
from audio.functions import handle_uploaded_file
#######################################
import cv2
import pytesseract
from pytesseract import Output
#######################################


def imageProcessor(fileName):
    # Convert PDF into pages
    def pdf2pages(fileName):


        PATH = "audio/static/upload/"
        # changing the uploaded file's name
        dir_path = os.path.dirname(PATH)

        file_path = os.path.join(dir_path, str(fileName))
        rename_file_path = dir_path + "/upload.pdf"

        os.rename(file_path, rename_file_path)

        # finding the pdf just uploaded
        file_pathdir = os.listdir(dir_path)
        file_path = os.path.join(dir_path, str(file_pathdir[0]))

        output_path = "audio/static/upload/outputs/"

        try:  
            os.mkdir(output_path)  
        except OSError as error:  
            print(error) 

        inputDoc = PdfFileReader(open(file_path, "rb"))
        path = 'audio/static/upload/outputs/' + 'pdfs' 
        print("******"+path)
        try:  
            os.mkdir(path)  
        except OSError as error:  
            print(error)  
        for i in range(inputDoc.numPages):
            output = PdfFileWriter()
            output.addPage(inputDoc.getPage(i))
            print("Here")
            with open("audio/static/upload/outputs/pdfs/" + "%s.pdf" % i, "wb") as outputStream:
                output.write(outputStream)
        return path

    # Converts the one page pdfs to images            
    def pdf2images(path):

        for pdf in os.listdir(path): 
            pdfPath = os.path.join(path,pdf)
            imageSavePath = "audio/static/upload/outputs/" + "images"

            try:  
               os.mkdir(imageSavePath)  
            except OSError as error:  
                print(error)

            print(pdf)
            # ("the input pdf","DPI" for the image output)
            print(pdfPath)
            pages = convert_from_path(pdfPath,120)
            imgName = pdf.split('.')[0]
            imgName = imgName + ".jpeg"
            for page in pages:
                print(pages)
                print(page)
                page.save(imageSavePath+ "/" + imgName,"JPEG")
        return imageSavePath

    path = pdf2pages(fileName)
    pdf2images(path)
    
    return path

def sortImages(imgNames):
    Names = []
    pgNames = []
    for i in range(len(imgNames)):
        name = imgNames[i].split('.')[0]
        Names.append(int(name))

    Names = sorted(Names)
    for i in range(len(imgNames)):
        Names[i] = str(Names[i]) + ".jpeg"


    return Names



def index(request):
    if request.method == 'POST':
        uploadedFile = StudentForm(request.POST, request.FILES)
        if uploadedFile.is_valid():
            fileName = request.FILES['file']
            handle_uploaded_file(request.FILES['file'])

            path = imageProcessor(fileName)
            imgNames = sortImages(os.listdir("audio/static/upload/outputs/images"))

            context = {
                'path' : path,
                'imgNames' : imgNames,
            }

            # Title, Summary, Polarity, wordHighlights = audioProcessor()
            return render(request,"home.html", context)
            # return  HttpResponse("File uploaded successfuly")
    else:  
        uploadedFile = StudentForm()  
        return render(request,"index.html",{'form':uploadedFile})


def searchResults(imgName, usrQuery, countQuery):
    tessdata_dir_config = r'--oem 3 --psm 6'

    curImage =  "audio/static/upload/outputs/images/" + imgName

    img = cv2.imread(curImage)

    # Adding custom options
    d = pytesseract.image_to_data(img, output_type=Output.DICT, lang='eng', config=tessdata_dir_config)

    # No. of words on the image file
    n_boxes = len(d['level'])

    # Copying the image into the variable overlay
    overlay = img.copy()

    # Check the presence of string with this variable
    isString = "no"

    # Input Query to search for 
    inpQry = usrQuery
    qry_Words = inpQry.split(" ")
    lenQry = len(qry_Words)

    for i in range(n_boxes):
        
        # Checking each word from list of words in d["text"]
        text = d['text'][i:i+lenQry]
        text = " ".join(text)

        if text == inpQry:
            isString = "yes"
            countQuery += 1

            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])

            for j in range(lenQry):
                (x1, y1, w1, h1) = (d['left'][i+j], d['top'][i+j], d['width'][i+j], d['height'][i+j])

                cv2.rectangle(overlay, (x, y), (x1 + w1, y1 + h1), (255, 0, 0), -1)

                x = x1
                y = y1

            # (x, y, w, h) = (d['left'][i+lenQry], d['top'][i], d['width'][i], d['height'][i])
            # (x1, y1, w1, h1) = (d['left'][i], d['top'][i + 1], d['width'][i + 1], d['height'][i + 1])

            # cv2.rectangle(overlay, (x, y), (x1, y1 + h1), (255, 0, 0), -1)


    # Transparency factor for word shading
    alpha = 0.4

    # Following line overlays transparent rectangle over the image
    img_new = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    print(img_new.shape)
    print(img.shape)

    # resizing image without loosing aspect ratio
    r = 1000.0 / img_new.shape[1]
    dim = (1000, int(img_new.shape[0] * r))
    # perform the actual resizing of the image and show it

    dims = (img_new.shape[0]+50,img_new.shape[0]+50)
    # , interpolation=cv2.INTER_AREA
    # cv2.namedWindow('custom window', cv2.WINDOW_KEEPRATIO)
    

    # Saving the image 
    cv2.imwrite("audio/static/upload/outputs/result_images/"+ imgName, img_new) 
    # resized = cv2.resize(img_new, (850,850))

    # cv2.imshow('img', resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


    return (isString, countQuery)


def search(request):
    if request.method == 'GET':
        usrQuery = request.GET.dict()
        
        print("-----------")
        print(usrQuery)
        print("-----------")

        for k,v in usrQuery.items():
            usrQuery = str(v)

        imgNames = sortImages(os.listdir("audio/static/upload/outputs/images"))

        searched_output = "audio/static/upload/outputs/result_images/"

        try:  
            os.mkdir(searched_output)  
        except OSError as error:  
            print(error)

        countQuery = 0
        queryPages = []

        for image in imgNames:
            isString, countQuery = searchResults(image, usrQuery, countQuery)

            if isString == "yes":
                queryPages.append(int(image.split(".")[0]))

        pagNames = []
        for img in imgNames:
            pagNames.append(img.split(".")[0])


        context = {
            'imgNames' : pagNames,
            'countQuery' : countQuery,
            'queryPages' : queryPages,
        }
    return render(request, "result.html" ,context)
     
