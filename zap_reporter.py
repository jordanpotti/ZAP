#!/usr/bin/env python

import time
import string
import urllib2
from pprint import pprint
from zapv2 import ZAPv2
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
import commands
import os
import fileinput

#Start ZAP is if it is not already started

output = commands.getoutput('ps aux | grep java')
if 'arsenal' not in output:
    os.system('nohup ./ZAP_2.5.0/zap.sh &')
    print 'Starting ZAP'
    t = 0
    while t < 15:
        print '.\r'
        t = t+1
        time.sleep(1)

#Opens "target list" which has lists of URLs

with open("Target_List.txt") as f:
	for line in f:
		print line

		target = '%s' % line

		zap = ZAPv2()

		print 'Accessing target %s' % target

		zap.urlopen(target)

		time.sleep(2)

		print 'Spidering target %s' % target
		scanid = zap.spider.scan(target)

		time.sleep(2)
		while (int(zap.spider.status(scanid)) < 100):
   		 print 'Spider progress %: ' + zap.spider.status(scanid)
   		 time.sleep(2)
		
		print 'Spider completed'

		time.sleep(5)

		print 'Scanning target %s' % target
		scanid = zap.ascan.scan(target)
		while (int(zap.ascan.status(scanid)) < 100):
		    print 'Scan progress %: ' + zap.ascan.status(scanid)
		    time.sleep(5)

		print '\nScan completed'
	
		output = '/home/user/arsenal/webscan.html'

		zap.core.htmlreport(output)
	
		time.sleep(10)
			
		proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8080'})
		opener = urllib2.build_opener(proxy)
		urllib2.install_opener(opener)
		
		url = 'http://zap/OTHER/core/other/htmlreport'
			
		timestr = time.strftime("%Y-%m-%d_%H:%M:%S")
		
		target = string.replace(target, "//","_")
		target = string.replace(target, ".","_")		

		f = urllib2.urlopen(url)
		data = f.read()
		with open("%s_%s.txt" % (target, timestr), "wb") as code:
			code.write(data)


		urllib2.urlopen('http://zap/HTML/core/action/deleteAllAlerts/?zapapiformat=HTML')
		urllib2.urlopen('http://zap/HTML/core/action/newSession/?zapapiformat=HTML&name=&overwrite=NEW')
                
		#Enter your emails addresses here

		fromaddr = "GMAIL ADDRESS"
		toaddr = "EMAIL ADDRESS"
 
		msg = MIMEMultipart()
 
		msg['From'] = fromaddr
		msg['To'] = toaddr
		msg['Subject'] = "ZAP Security Report %s" % timestr
 
		body = "Security report attached for %s\n\nSlashes and periods have been replaced with underscores for naming purposes.\n\n!! Please Review Report and Investigate Alerts !!" %target
 
		msg.attach(MIMEText(body, 'plain'))
 
		filename = "%s_%s.html" % (target, timestr)
		attachment = open("%s_%s.html" % (target, timestr), "rb")
 
		part = MIMEBase('application', 'octet-stream')
		part.set_payload((attachment).read())
		encoders.encode_base64(part)
		part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
 
		msg.attach(part)
 		
		#Send report to email from your gmail account

		server = smtplib.SMTP_SSL("smtp.gmail.com:465")

		#Enter your gmail password below
		
		server.login(fromaddr, "GMAIL Account PASSWORD")
		text = msg.as_string()
                server.sendmail(fromaddr, toaddr, text)
		server.quit()
                print '\nReport Sent\n'
