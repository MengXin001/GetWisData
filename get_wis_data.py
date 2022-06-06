import datetime
import numpy as np
import urllib
import requests
import re
def get_html(url):
    res = requests.get(url)
    res.encoding = 'utf-8'
    html = res.text
    return html
class Down(object):
    def __init__(self, stationid, dtime):
        self.stationid = stationid
        self.dtime = dtime
    def initid(self, stationid):#Initcode
        BABJ1 = ['51463','52533','52983','53463','53772','53845','54218','54511','54727','57083','57127','57131']
        BABJ2 = ['56187','56778','57494','57687','57816','58238','58362','59280','59431']
        BABJ3 = ['51076','51431','52681','52866','53915','54374','54662','54857','57178']
        BABJ4 = ['56146','56571','57461','57516','57749','57972','58150','58457','58847','59316','59758','59981']
        BABJ5 = ['50557','50953','51709','51777','53068','53513','54102','54161','54292','56029','56080']
        BABJ6 = ['56739','56964','57957','57993','58027','58424','58606','58633','58665','59211']
        BABJ7 = ['50527','50774','51644','51828','52418','52818','53614']
        BABJ8 = ['55299','55591','56137','56691','56985','57447','58203','58725','59134','59265']
        BABJ9 = ['51839','52203','52267','52323','52836','54135']
        VHHH  = ['45004']
        codelist = [BABJ1,BABJ2,BABJ3,BABJ4,BABJ5,BABJ6,BABJ7,BABJ8,BABJ9,VHHH]
        cnlist = ['BABJ1','BABJ2','BABJ3','BABJ4','BABJ5','BABJ6','BABJ7','BABJ8','BABJ9','VHHH']
        list = 0
        for code in codelist:
            if self.stationid in code:
                list = list
            else:
                list = list + 1
                codename = cnlist[list]
        return codename
  
    def download(self):#dtime=114514191981 1145 14 19 1981
        codename = self.initid(self.stationid)
        if codename == "VHHH":#Seturl
            url = "https://wis/d/o/VHHH/BUFR/Upper_air/TEMP/"+ self.dtime[0:8] + "/" + self.dtime[8:] +"00/"
        else:
            url = "https://wis/d/o/BABJ/BUFR/Upper_air/TEMP/"#Todo
        #return url
        text = get_html(url)
        fn = re.search('A_IUSC02VHHH.{36}', text).group()
        urllib.request.urlretrieve(url + fn, fn)
        return url + fn

Durl = Down("45004","202206060000")
print(Durl.download())
