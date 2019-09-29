from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import os
import time
from ics import Calendar,Event
import datetime

def main():

    cal=Calendar()
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # https://sites.google.com/a/chromium.org/chromedriver/download
    # put driver executable file in the script directory
    chrome_driver = os.path.join(os.getcwd(), "chromedriver")

    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

    driver.get("https://utdallas.edu/calendar")
# Find the javascript button that displays this months events and clicks it
    elem1=driver.find_element_by_id("cal-this-month")
    elem1.click()
    time.sleep(2)



#So here the problem, you need to be able to parse through the different strings of the event names and event dates without those two quantities intersecting,
#Also you need to be able to determine which building(s) the events are placed in, if there are conflucts, how they are written ect, you might even need to start
#doing sub depths within the web pages for each event to get more information and that would require getting the event links


# This will proceed with scrapping everything from the main page, instead of diving into every
#   event page individually
    # unparsedEvents=driver.find_elements_by_id("forEvents")
    #
    # eventNames=[]
    # eventTimes=[]
    # eventPlaces=[]
    # eventDates=[]
    #
    #
    # # print(unparsedEvents[0].text)
    #
    # print(createUsableElements(unparsedEvents[0].text))

# This will proceed with scrapping everything from specific event pages
    # Creates a list of events from the web page, as long as they have the
    #   event title class, which is required for a valid entry anyway
    unparsedEvents=driver.find_elements_by_class_name("eventTitle")
    subLink = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

    # Go through each event entry, gather data and determine whether they are valid entries
    #   If they are, print their information and add them to the cal (Calendar()) object
    for i in range(len(unparsedEvents)):
        eventObject = Event()
        eventLink=unparsedEvents[i].get_attribute('href')
        subLink.get(eventLink)

        eventTitle=subLink.find_elements_by_id("evtitle")
        eventDate=subLink.find_elements_by_class_name("startDate")
        eventStartTime=subLink.find_elements_by_class_name("startTime")
        eventEndTime=subLink.find_elements_by_class_name("stopTime")
        eventLocation=subLink.find_elements_by_class_name("fn")
        eventDescription=subLink.find_elements_by_class_name("detailholder")

        if(len(eventTitle)!=0):
            eventTitle=eventTitle[0].text
        else:
            continue

        if(len(eventDate)!=0):
            eventDate=eventDate[0].text
            eventDate=dateParser(eventDate)

        if(len(eventStartTime)!=0):
            eventStartTime=eventStartTime[0].text
            eventStartTime=timeParser(eventStartTime)

        if(len(eventEndTime)!=0):
            eventEndTime=eventEndTime[0].text
            eventEndTime=timeParser(eventEndTime)
            if(eventStartTime==-1):
                continue

            if(len(eventStartTime)==0):
                eventStartTime=eventEndTime
        else:
            continue

        if(len(eventLocation)!=0):
            eventLocation=eventLocation[0].text

        if(len(eventDescription)!=0):
            eventDescriptionString=""
            for x in range(0,len(eventDescription)):
                eventDescriptionString+=eventDescription[x].text

        print(eventTitle+" ("+eventLocation+") ")
        print(eventDescriptionString)
        print(eventDate)
        print(eventStartTime," - ",eventEndTime)
        print("#############")

        eventObject.name=eventTitle
        eventObject.begin=eventDate+' '+eventStartTime
        eventObject.end=eventDate+' '+eventEndTime
        eventObject.description=eventDescriptionString
        cal.events.add(eventObject)



    with open('UTD_Cal.ics', 'w') as icsFile:
        icsFile.writelines(cal)



# Not sure what this function is meant to do but is required* if you parse events
#   without diving into specific event links

# def createUsableElements(listOfChars):
#     listOfLines=[]
#     lineString=""
#     for i in range(len(listOfChars)):
#         if(listOfChars[i]!='\n'):
#             lineString+=listOfChars[i]
#         else:
#             listOfLines.append(lineString)
#             lineString=""
#     return listOfLines

# def searchSublinkAndInitialise(linkToEventInfo)

def dateParser(utdDateFormat):
    returnableDateFormat=str(datetime.datetime.now().year)
    month=utdDateFormat.split(" ")[1]
    day=utdDateFormat.split(" ")[2]
    months=["Jan.","Feb.","Mar.","Apr.","May","Jun.","Jul.","Aug.","Sep.","Oct.","Nov.","Dec."]
    if(len(str(months.index(month)))==1):
        returnableDateFormat+=("-0"+str(months.index(month)+1))
    else:
        returnableDateFormat+=("-"+str(months.index(month)+1))

    if(len(str(day))==1):
        returnableDateFormat+=("-0"+str(day))
    else:
        returnableDateFormat+=("-"+str(day))

    return returnableDateFormat


# This function was created to navigate the hell that is a lack of
#   a single standard for time in the UTD events, also converting
#   it into iCal parseable format
def timeParser(utdTimeFormat):

    if(utdTimeFormat=="noon"):
        return ("12:00:00")
    if(len(str(utdTimeFormat))==1 or ((not "a.m." in utdTimeFormat) and (not "p.m." in utdTimeFormat))):
        return -1

    time=utdTimeFormat.split(" ")[0]
    # print(utdTimeFormat)
    dayOrNight=utdTimeFormat.split(" ")[1]
    if(dayOrNight=="a.m."):
        if (not (':') in time):
            if(len(str(time))==1):
                return "0"+time+":00:00"
            return time+":00:00"
        if(len(str(time).split(":")[0])==1):
            return "0"+(time+":00")
        return (time+":00")
    elif(dayOrNight=="p.m."):
        if(not (':') in time):
            if((int(time.split(":")[0]))==12):
                return "12:00:00"
            if((int(time.split(":")[0])+12)>23):
                return str(24-int(time.split(":")[0])+12)+":00:00"
            return str(int(time.split(":")[0])+12)+":00:00"
        if((int(time.split(":")[0]))==12):
            return "12:"+time.split(":")[1]+":00"
        if((int(time.split(":")[0])+12)>23):
            return "00:"+time.split(":")[1]+":00"
        return (str(int(time.split(":")[0])+12)+":"+time.split(":")[1]+":00")

# This function was created as the iCal file kept importing the times as GMT,
#   instead of CDT, annoying to say the least
def timeParserGMT_CDT(utdTimeFormat):

    # The purpose of this function is to rectify the error that events are interpreted in the gmt
    # timezone by the local calendar instead of the wanted cdt timezone, to convert from cdt to gmt
    # you would need to add 5 hours.

    # To feed the times to the ics, the time format needs to be in the format of HH:mm:ss

    # Some time entries only include the word "noon"

    # Some time entries have only a single number or do not include am or pm specifiers,
    # These entries are typically unimportant and are not events that are part of the Calendar

    # The normal structure of the time inputs are h:mm a.m./p.m. , none have references to seconds
    # However there are some time entries that do not include minutes, so they would boil down to
    # h a.m./p.m. without additional information, these do not have the character ":"

    print(utdTimeFormat)





main()
