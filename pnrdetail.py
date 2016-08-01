from bs4 import BeautifulSoup
import requests
import re
from random import randint
from datetime import datetime
import mechanize
import cookielib
from flask import Flask

# new app using flask
app = Flask(__name__)

@app.route('/')
def api_root():
    return 'Developed by sinwar'

@app.route('/pnr/<pnrnumber>')
def details(pnrnumber):
    
    url_pnr = "http://www.indianrail.gov.in/pnr_Enq.html"
    br = mechanize.Browser()
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    br.open("http://www.indianrail.gov.in/pnr_Enq.html")
    br.select_form(name='pnr_stat')
    br["lccp_pnrno1"] = pnrnumber
    res = br.submit()
    content = res.read()

    if content.find("Please try again later") > 0:
        return "Service unavailable 23:30 to 00:30"
    elif content.find("FLUSHED PNR / PNR NOT YET GENERATED") > 0:
        return "Wrong PNR"
    elif content.find("Facility Not Avbl due to Network Connectivity Failure") > 0:
        return "Facility not available"
    elif content.find("This is circular journey authority PNR") > 0:
        return "Circular Journey"
    elif content.find("Invalid PNR NO") > 0:
        return "Invalid pnr number"
    elif content.find("The Train Is Cancelled") > 0:
        return "Train cancelled"


    soup = BeautifulSoup(content,'html.parser')
    
    response_json = {}

    response_json["pnr"] = pnrnumber
    #set ticket_type
    ticket_type_re = re.compile("\(.*\)")
    enq_heading = soup.find("td", {"class": "Enq_heading"}).text
    if ticket_type_re.findall(enq_heading):
        ticket_type = str(ticket_type_re.findall(enq_heading)[0])
        ticket_type = ticket_type.lstrip("\(").rstrip("\)")
    else:
        ticket_type = "Unknown"
    response_json["ticket_type"] = ticket_type
    #get tables
    tables = soup.findAll("table", {"class": "table_border"})
    #get journey_rows
    journey_cols = tables[0].findAll("tr")[2].findAll("td")
    #get train_number
    response_json["train_number"] = str(journey_cols[0].text).lstrip("*")
    #get train_name
    response_json["train_name"] = str(journey_cols[1].text).strip()
    #get boarding_date
    boarding_date = str(journey_cols[2].text).split("-")
    boarding_date = boarding_date[0] + "-" + boarding_date[1].strip() + "-" + boarding_date[2]
    response_json["boarding_date"] = datetime.strptime(boarding_date, "%d-%m-%Y")
    #get from
    response_json["from"] = str(journey_cols[3].text).strip()
    #get to
    response_json["to"] = str(journey_cols[4].text).strip()
    #get reserved_upto
    response_json["reserved_upto"] = str(journey_cols[5].text).strip()
    #get boarding_point
    response_json["boarding_point"] = str(journey_cols[6].text).strip()
    #get class
    response_json["class"] = str(journey_cols[7].text).strip()

    #get passengers
    passengers = []
    totalPassengers = 0
    rows = tables[1].findAll("tr")
    rowLength = len(rows)
    for i in range(1, rowLength):
        cols = rows[i].findAll("td")
        if str(cols[0].text).split()[0] == "Passenger":
            totalPassengers = totalPassengers + 1
            passengerData = {}
            booking_data = str(cols[1].text).split()
            booking_status = ""
            for element in booking_data:
                booking_status = booking_status + " " + element
            booking_status = booking_status.strip()
            passengerData["booking_status"] = booking_status
            current_data = str(cols[2].text).split()
            current_status = ""
            for element in current_data:
                current_status = current_status + " " + element
            current_status = current_status.strip()
            passengerData["current_status"] = current_status
            passengers.append(passengerData)
        elif str(cols[0].text).split()[0] == "Charting":
            charting_data = str(cols[1].text).split()
            charting_status = ""
            for element in charting_data:
                charting_status = charting_status + " " + element
            charting_status = charting_status.strip()
            #get charting_status
            response_json["charting_status"] = charting_status
            #get total_passengers
    response_json["total_passengers"] = totalPassengers
    #get passenger_status
    response_json["passenger_status"] = passengers

    return response_json



if __name__ == '__main__':
    app.run(debug=True)
