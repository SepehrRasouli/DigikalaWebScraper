# Python scraper to scrape any given subject from www.digikala.com 
# and write them Into excel
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os


writerdict = {}


DigikalaFilters =[
"&only_plus=1&","&only_fresh=1&","&has_ship_by_seller=1&",
"&has_jet_delivery=1&","&has_selling_stock=1&","&has_ready_to_shipment=1&",
"&seller_condition[0]=digikala&","&seller_condition[1]=official&","&seller_condition[2]=trusted&",
"&seller_condition[3]=roosta&","&sortby=7&","&sortby=22&","&sortby=4&",
"&sortby=1&","&sortby=20&","&sortby=21&","&sortby=25&"
]


def cleanizer(filename):
    """Cleans up Extracted Data"""
    print("Cleaning Up More...")


    if filename == 'Pricesextracted.txt':
        # To handle تومان better
        with open(filename,"r",encoding="utf-8") as readdata:
            data = readdata.readlines()
            data = [x.strip() for x in data]
        meta = ""
        fileClear(filename)
        with open(filename,"a",encoding="utf-8") as writedata:
            for element in data:
                if element == "تومان" or element == '':
                    continue
                if element =="None":
                    writedata.write("ناموجود"+"\n")
                    continue

                    
                else:
                    writedata.write(element+meta+" تومان "+"\n")


    if filename == "DiscountValuesextracted.txt":
        with open(filename,"r",encoding="utf-8") as readdata:
            data = readdata.readlines()
            data = [x.strip() for x in data]
        fileClear(filename)
        with open(filename,"a",encoding="utf-8") as writedata:
            for element in data:
                if element:
                    writedata.write(element+"\n")

                else:
                    continue


    if filename == "Starsextracted.txt":
        with open(filename,"r",encoding="utf-8") as readdata:
            data = readdata.readlines()
            data = [x.strip() for x in data]
        fileClear(filename)
        with open(filename,"a",encoding="utf-8") as writedata:
            for element in data:
                if element.startswith("(") or element == '':
                    continue
                else:
                    writedata.write(element+"\n")
        


    else:
        # This works fine for others.
        with open(filename,"r",encoding="utf-8") as readdata:
            data = readdata.readlines()
            data = [x.strip() for x in data]

        fileClear(filename)
        with open(filename,"a",encoding="utf-8") as writedata:
            for element in data:
                if element == "فروش ویژه" or element == "Ad" or element == '':
                    continue
                else:
                    writedata.write(element+"\n")


def writetodict(filename,meta):
    """Writes Data To A Dict."""
    global writerdict
    with open(filename,"r",encoding="utf-8") as f:
        data = f.readlines()
        data = [x.strip() for x in data]
    writerdict[meta] = data
    os.remove(filename)


def writer(excelFile):
    """ Writes Data To Excel."""
    #checkfilevalidity
    print("Writing Data...")
    global writerdict
    if os.path.isfile(excelFile):
        try:
            df = pd.DataFrame.from_dict(writerdict,orient='index')
            df = df.transpose()
            writer = pd.ExcelWriter(excelFile)
            df.to_excel(writer,index=0)
            writer.save()
        except PermissionError:
            print("Please Close The excel file")
            greetUser()
    else:
        print("Excel File dosent exist. Aborting...")
        greetUser()


def fileClear(filename):
    """Removes All Contents of a file"""
    with open(filename,"w") as temp:
        temp.write(" ")


def extractdata(subject,pageRange,selectedDigikalaFilters):
    """Gets data from digikala search"""

    fileClear("data.txt")
    for num in range(1,pageRange):
        try:
            with open("data.txt","a",encoding="utf-8") as f:
                meta = "&sortby=22" if num > 1 else ''
                r = requests.get(f"https://www.digikala.com/search/?{''.join(selectedDigikalaFilters)}q={subject}&pageno={num}{meta}")
                print(f"https://www.digikala.com/search/?{''.join(selectedDigikalaFilters)}q={subject}&pageno={num}{meta}")
                f.write(str(r.text)+"\n")
        except ConnectionError:
            print("Got An Connection Error. Please Check your internet Connection")



def extractor(filename):
    """Extracts the wanted content."""
    print("Extracting Data...")
    meta = ""
    if 'productDiscountsResult.txt' == filename:
        meta = "DiscountValues"
    elif 'productStarsResult.txt' == filename:
        meta = "Stars"
    elif "productNamesResult.txt" ==  filename:
        meta = "Names"
    else:
        meta = "Prices"
    getExtractedFile = f"{meta}extracted.txt"
    fileClear(getExtractedFile)

    with open(getExtractedFile,"a",encoding="utf-8") as result:
        with open(filename,"r",encoding="utf-8") as mainFile:
            lines = mainFile.readlines()
            regexed = re.sub(r"<[^>]*>","\n",''.join(lines))
            for char in regexed:
                if char in [',',']','[','[,']:
                    continue
                else:
                    result.write(char)

    print("Cleaning Up...")
    os.remove(filename)
    cleanizer(getExtractedFile)
    writetodict(getExtractedFile,meta) 

    
        


def discountValuesScarpe():
    print("Extracting Discount Values...")
    with open("data.txt","r",encoding="utf-8") as datafile:
        with open("productDiscountsResult.txt","a+",encoding="utf-8") as result:
            data = datafile.readlines()
            soup = BeautifulSoup(''.join(data),"html.parser")
            containers = soup.find_all('div',attrs={'class':'c-product-box__row c-product-box__row--price'})
            for container in containers:
                if  "c-price__discount-oval" in str(container):
                    result.write(str(container.find("div",attrs={'class':"c-price__discount-oval"}))+"\n")
                    continue
                else:
                    result.write("%۰"+"\n")
                    continue
                    
    extractor("productDiscountsResult.txt")



def starsScarper():
    print("Extracting Stars...")
    with open("data.txt","r",encoding="utf-8") as datafile:
        with open("productStarsResult.txt","a+",encoding="utf-8") as result:
            data = datafile.readlines()
            soup = BeautifulSoup(''.join(data),"html.parser")
            containers = soup.find_all('div',attrs={'class':'c-product-box__content'})
            for container in containers:
                if  "c-product-box__engagement-rating" in str(container):
                    result.write(str(container.find("div",attrs={'class':"c-product-box__engagement-rating"}))+"\n")
                    continue
                else:
                    result.write("۰.۰"+"\n")
                    continue
                    
    extractor("productStarsResult.txt")



def productNamesScarpe():
    print("Extracting product names...")
    with open("data.txt","r",encoding="utf-8") as datafile:
        with open("productNamesResult.txt","a+",encoding="utf-8") as result:
            data = datafile.readlines()
            soup = BeautifulSoup(''.join(data),"html.parser")
            productName = soup.find_all("a",attrs= ["js-product-url"])
            if productName and productName != " ":
                result.write(str(productName))

            else:
                result.write("Not Found.")
                    
    extractor("productNamesResult.txt")



def pricesScarpe():
    print("Extracting Prices...")
    with open("data.txt","r",encoding="utf-8") as datafile:
        with open("productPricesResult.txt","a+",encoding="utf-8") as result:
            data = datafile.readlines()
            soup = BeautifulSoup(''.join(data),"html.parser")
            containers = soup.find_all('div',attrs={'class':'c-product-box__row c-product-box__row--price'})
            for container in containers:
                if container.find('div',class_="c-price__value c-price__value--plp js-plp-product-card-price"):
                    result.write(str(container.find('div',class_="c-price__value c-price__value--plp js-plp-product-card-price").find('div',class_='c-price__value-wrapper'))+"\n")
                else:
                    result.write(str(container.find('div',class_="c-price__value-wrapper"))+"\n")        
    extractor("productPricesResult.txt")




def check(userInput):
    checklist = []
    alphabet = "abcdefghijklmnopqrstuvwxyz,ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()/\«»<>_+"
    for char in alphabet:
        if char in userInput:
            checklist.append(False)
        checklist.append(True)

    if all(checklist):
        return True 

    



    

def greetUser():
    global excelFile
    usecurrentdata = 0
    """ Greets User And Takes Scraping Options."""
    print("Hello User. I can scarpe digikala and write data to excel")
    print("*"*10)
    selectedScarpingOptions = []
    selectedDigikalaFilters = []
    subject = input("Subject > ")
    #TODO: Make Sure That pageRange Is A int

    pageRange = input("How Many Pages? > ")

    if not check(pageRange):
        print("Invalid Number.")
        greetUser()

    if not pageRange:
        print("Invalid Number.")
        greetUser()
    try:
        pageRange = int(pageRange) + 1 # Because of range function\
    except ValueError as error:
        print(f"Got An {error}. Did you Give Too Many Numbers?")
        greetUser()

    excelFile = input("Excel File > ")

    if excelFile == " " or "":
        greetUser()
    if excelFile.endswith(".xlsx"):
        pass
    else:
        excelFile += ".xlsx"


    print("*"*10)
    print("Scarping Options : *Select One Or More Options and seperate them with spaces* ")
    print("""
    1- Product Names 2- Product Prices 
    3- Product Discount Values 4 - Stars""")
    print("*"*10)


    userInput = input("> ")

    result = check(userInput)

    # Add selected scarping options to list

    if result and userInput != '':
        for number in set(userInput.split()):
            if int(number) > 4:
                print("Invalid Option")
                greetUser()

            else:
                if int(number) == 1:
                    selectedScarpingOptions.append("productNamesScarpe()")

                if int(number) == 2:
                    selectedScarpingOptions.append("pricesScarpe()")

                if int(number) == 3:
                    selectedScarpingOptions.append("discountValuesScarpe()") 

                if int(number) == 4:
                    selectedScarpingOptions.append("starsScarper()")



    else:
        print("Alphabet Character Or ',' Detected.")
        greetUser()


    print("Use Current Digikala Web Data ?[Y/N]")
    yon = input("> ")
    if yon.lower().startswith("y"):
        usecurrentdata = 1

    elif yon.lower().startswith("n"):
        usecurrentdata = 0

    else:
        print("Wrong Choice. ")
        greetUser()

    print("Digikala Filters : ")
    print("*"*10)
    print("Select One Or More Options and seperate them with spaces: ")
    print("""
    ** Choosing Too Much Options Or Bad Options Might Affect Digikala Searchs.**
    1- Only DigiPlus                            10- Seller = Indigenous Seller                        
    2- Only SuperMarkets                        11- Bestselling
    3- Ship By Seller                           12- Most relevant
    4- Fast Delivery                            13- Most visited  
    5- Only Avalaibles                          14- Newests
    6- Only Avalaibles In DigiKala's Store      15- Cheapest 
    7- Seller = DigiKala                        16- Most Expensives
    8- Seller = Officials                       17- Fastest post 
    9- Seller = Trusted                         18- None
    """)
    userInput = input("> ")
    result = check(userInput)

    if result == True:
        print("Extracting Data From Digikala...")
        userInput = set(userInput.split())
        for i in userInput:
            i = int(i)
            if i == 18:
                break

        else:
            for selectedOption in userInput:
                if int(selectedOption) < 18:
                    selectedOption = int(selectedOption) -1
                    selectedDigikalaFilters.append(DigikalaFilters[selectedOption]) # Add Elements By Index
                    continue
                else:
                    continue
    else:
        print("Invalid Choice.")
        greetUser()                


    if usecurrentdata == 0:
        extractdata(subject,pageRange,selectedDigikalaFilters)
    else:
        if os.path.isfile("data.txt"):
            pass
        else:
            print("data.txt Not found. Gathering Data...")
            extractdata(subject,pageRange,selectedDigikalaFilters)
    for option in selectedScarpingOptions:
        exec(option)
    writer(excelFile)
    os.remove("data.txt")

    print("Finish.\n\n\n")
    print("*"*10)
    greetUser()


greetUser()
