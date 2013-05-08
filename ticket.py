#coding=UTF-8
import urllib
import urllib2
import cookielib
import math
import random
import os
import re
import time
import sys
from xml.dom.minidom import parseString
from datetime import date, datetime
#import bubble

stations = []
trains = []

def download_station():
    global stations
    stationurl = "http://dynamic.12306.cn/TrainQuery/autocomplete.do?method=getStationName&inputValue=&date=%04d%02d%02d" % (datetime.now().year, datetime.now().month, datetime.now().day)
    fp = urllib2.urlopen(stationurl)
    s = fp.read()
    dom = parseString(s)
    for node in dom.getElementsByTagName("complete")[0].getElementsByTagName("option"):
        stations.append(node.getAttribute("value"))

def download_train():
    global trains
    trainurl = "http://dynamic.12306.cn/TrainQuery/autocomplete.do"
    fp = urllib2.urlopen(trainurl, urllib.urlencode({"method" : "getTrainName", "inputValue" : "-", "date" : "%04d%02d%02d" % (datetime.now().year, datetime.now().month, datetime.now().day)}))
    s = fp.read()
    dom = parseString(s)

def query(date, start = "", end = ""):
    cookie = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    urllib2.install_opener(opener)

    queryurl = "http://dynamic.12306.cn/otsquery/query/queryRemanentTicketAction.do"
    postdata = urllib.urlencode({
            "method" : "queryLeftTicket",
            "orderRequest.train_date" : "%d-%02d-%02d" % (date.year, date.month, date.day),
            "orderRequest.from_station_telecode" : start,
            "orderRequest.to_station_telecode" : end,
            "orderRequest.train_no" : "",
            "trainPassType" : "QB",
            "trainClass" : "Z#T#",
            "includeStudent" : "00",
            "seatTypeAndNum" : "",
            "orderRequest.start_time_str" : "00:00--24:00"
    })

    try:
        # print "%s?%s" % (queryurl, postdata)
        fp = urllib2.urlopen("%s?%s" % (queryurl, postdata))
        s = fp.read()
    except urllib2.HTTPError, e:
        if e.getcode() == 500:
            return None
        else:
            raise
    s = s.decode("utf-8")
    s = s.encode("gbk")
    
    pattern = re.compile('onStopOut\(\)\'>([^<]*)[^&]*(&nbsp;)*([^&]+)[^0-9]*(\d+:\d+),[^&]*(&nbsp;)*([^&]+)[^0-9]*(\d+:\d+),(\d+:\d+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)', re.UNICODE)
    tlist = []
    for result in pattern.findall(s):
        tmp = [result[0], result[2], result[3], result[5], result[6], result[7], result[8], result[9], result[10], result[11], result[12], result[13], result[14], result[15], result[16], result[17], result[18]]
        for i in range(len(tmp)):
            if tmp[i] == "<font color='darkgray'>无<\/font>":
                tmp[i] = "无"
        
        noticket = True
        for i in [9, 12]:
            if tmp[i] != "无" and tmp[i] != "--":
                noticket = False
                break

        if noticket == True:
            continue
        
        tlist.append(tmp)
    return tlist

if __name__ == '__main__':
    # download_station()
    #download_train()

    startdate = 2
    enddate = 13

    logfp = open('log.txt', 'a')
    
    t = 0
    while True:
        print '-' * 64, '%d' % t, '-' * 64
        t += 1
        for day in range(startdate, enddate + 1):
            ticketday = date(2013, 2, day)
            try:
                results = query(ticketday, "BJP", "HFH")
            except:
                print 'Failed access data for ', ticketday
                sys.stdout.flush()
                time.sleep(1)
                continue

            if len(results) != 0:
                logstr = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n" + ticketday.strftime('%Y-%m-%d') + "\n"

                fmt = "%9s %9s %9s %9s %9s %9s %9s %9s %9s %9s %9s %9s %9s %9s %9s %9s %9s\n"
                logstr += fmt % ("车次", "发站", "发时", "到站", "到时", "历时", "商务座", "特等座", "一等座", "二等座", "高软", "软卧", "硬卧", "软座", "硬座", "无座", "其他")
                # logstr += "车次\t发站\t发时\t到站\t到时\t历时\t商务座\t特等座\t一等座\t二等座\t高软\t软卧\t硬卧\t软座\t硬座\t无座\t其他\n"

                realticket = False  # the website really sucks, it even reports fake tickets!!!
                for result in results:
                    realticket = True
                    logstr += fmt % (result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], 
                                     result[8], result[9], result[10], result[11], result[12], result[13], result[14], result[15], result[16])                    
                    # logstr += "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
                    #     % (result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7],
                    #        result[8], result[9], result[10], result[11], result[12], result[13], result[14], result[15], result[16])

                if realticket == True:                    
                    logfp.write(logstr.replace('\t', '    '))
                    logfp.flush()
                    print logstr,
                
                    sys.stdout.flush()
                    
                    ticstr = '%s\r\n' % ticketday
                    for result in results:
                        ticstr += '%s, %s - %s, ' % (result[0], result[2], result[4])
                        if result[8] != "无" and result[8] != "--":
                            ticstr += "一等座: %s  " % result[8]
                        if result[9] != "无" and result[9] != "--":
                            ticstr += "二等座: %s  " % result[9]
                        if result[10] != "无" and result[10] != "--":
                            ticstr += "高级软卧: %s  " % result[10]
                        if result[11] != "无" and result[11] != "--":
                            ticstr += "软卧: %s  " % result[11]
                        if result[12] != "无" and result[12] != "--":
                            ticstr += "硬卧: %s  " % result[12]
                        if result[13] != "无" and result[13] != "--":
                            ticstr += "软座: %s  " % result[13]
                        if result[14] != "无" and result[14] != "--":
                            ticstr += "硬座: %s  " % result[14]
                        if result[15] != "无" and result[15] != "--":
                            ticstr += "无座: %s  " % result[15]
                        ticstr += "\n"
                        
#                    bubble.NotifyTicket(ticstr)
                
        sys.stdout.flush()
        time.sleep(5)

    logfp.close()
