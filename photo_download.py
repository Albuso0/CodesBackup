import urllib
import urllib2
import urllib3
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


def query(queryurl):
    cookie = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    urllib2.install_opener(opener)

    try:
        fp = urllib2.urlopen("%s" % (queryurl))
        s = fp.read()
    except urllib2.HTTPError, e:
        if e.getcode() == 500:
            return None
        else:
            raise
    
    pattern = re.compile('(?i)href="\./(.*?\.jpg)"')
    cnt = 0
    plist = []
    for result in pattern.findall(s):
        plist.append(result)
    return plist
    
if __name__ == '__main__':
    # try:
    #     results = query()
    # except:
    #     print 'Failed access data',
    #     sys.stdout.flush()
    #     time.sleep(1)
    logfp = open('log_fail.txt', 'a')
    
    url = 'http://www.isit2015.org/photos'
    folders = [
        'Jun14-Tutorials',
        'Jun14-Welcome Reception',
        'Jun15',
        'Jun16-Awards Luncheon',
        'Jun16-Panel and Cocktail',
        'Jun16',
        'Jun17-Poster',
        'Jun17',
        'Jun18-Banquet',
        'Jun18-Shannon Awardee Luncheon',
        'Jun18',
        'Jun19'
    ]
    for folder in folders:
        # print '%s/%s' %(url,folder.replace(' ','%20'))
        results = query( '%s/%s' %(url,folder.replace(' ','%20')) )
        
        for img in results:
            try:
                print 'Downloading %s/%s'%(folder,img)
                urllib.urlretrieve ('%s/%s/%s'%(url,folder,img), '%s/%s'%(folder,img))
            except:
                logstr = '%s/%s' % (folder,img)
                print '%s faild!'% logstr
                logfp.write(logstr)
                logfp.flush()

    logfp.close()
