#!/usr/bin/python

import sys
import json
sys.path.insert(0, '/usr/lib/python2.7/bridge/')
from urllib2 import Request, urlopen, URLError, HTTPError
from urllib import urlencode
import httplib

#this script was written in order to send a POST request to the server, and
#send back to arduino microcontroller the response of the server. This script
#is called through arduino YUN Bridge library, therefore name of this script
#and the name of the script it is run in the arduino sketch must match.
#In order to execute the POST request two informations are needed
# the nfc_id retrieved by the nfc reader, which is passed by arduino
#microcontroller as command line argument, and the base url
#which you can find here


#INSERT TOKEN IN PAGE 39


#url of the server also, it is possible to edit /etc/hosts in order to mask ip
baseurl='<yourHost>'

#taken from urls.py in labadmin repository on github
urls={'doorNFC':'/labadmin/labadmin/opendoorbynfc/','userUpd':'/labadmin/labadmin\updateUsers/','id':'/labadmin/labadmin/user/identity/','nfcUs':'/labadmin/labadmin/nfc/users/','cred':'labadmin/labadmin/card/credits/'}

data={}

def request(code):
        #formatting the post request
        data['code']=code
        params = urlencode(data)
        headers={"Content-Type":"application/x-www-form-urlencoded", "Authorization":"token <YourToken>"}
        #connecting to the server
        conn = httplib.HTTPSConnection(baseurl)
        try:
                conn.request("POST", urls['doorNFC'], params, headers)
                response = conn.getresponse()
        except HTTPError as e:
                print 'False'
                print 'Error code:',e.code
                return False
        except URLError as e:
                print 'False'
                print 'Reason:', e.reason
                return False
        except:
                print 'Generic Error'
                print False
                return False
        else:
                rjson=response.read()
                rdata = json.loads(rjson)
                try:
                        print rdata['open']
                        for user in rdata['users']:
                                print user['name']
                        return True
                #if the dictionary rdata is empty a TypeError will be raised
                except TypeError:
                        print "Card didn't match any user."
			return False

if __name__=="__main__":
        request(sys.argv[1])

