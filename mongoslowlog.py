__author__ = "Saurav Yadav"
from optparse import OptionParser
import sys
import argparse
import subprocess
import time
import csv, re
import smtplib
import os
from email.utils import COMMASPACE, formatdate
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

mloginfo_bin = "/usr/local/python2.7/bin/mloginfo"
Server = "X.X.X.X"  # SMTP server's IP 
timestr = time.strftime("%Y%m%d")

parser = OptionParser(usage='usage: %prog [options] arguments')
parser.add_option("-f", "--file", action="store", type="string", dest="mongoslowlog", help="File name/path to parse and send slow log report")
parser.add_option("-d", "--database", action="store", type="string", dest="database", default="all", help="database name for which report needs to be generated or all as default value")
parser.add_option("-c", "--count", dest="count", default=20, help="# of slow query or 20 by default")
parser.add_option("-i", "--email", dest="email", default="devops@gmail.com", help="First Email-ID")
parser.add_option("-j", "--email1", dest="email1", default="devops@gmail.com", help="Second Email-ID")

(options, args) = parser.parse_args()

#if len(args) != 1:
#    parser.error("incorrect number of arguments")

## Do not proceed if line count is too low ##
with open(options.mongoslowlog) as f:
        if sum(1 for _ in f) <= 70:
                sys.exit()

if not options.mongoslowlog:
        parser.error('File name/path not given, check help for more details')
        parser.print_help()

file = options.mongoslowlog
count = options.count
email_id = [options.email, options.email1]

if options.database == "all":
        database = "*"
else:
        database = options.database

MailFrom = "devops@gmail.com"
MailTo = email_id
Subject = database + "::Mongo Slowlog Report"
Txt = """Team,<br />
<br />
Please find the attached mongo slow-query report. For any query/help or suggestion contact DevOPS.<br />
<br />
--<br />
Thanks<br />
Dev-OPS<br />
"""

compliedfile = "/tmp/mongoslow-%s-%s"  % (database,timestr,)
compliedfile_out  = compliedfile + ".csv"
Header = "namespace                                operation        pattern                                                                                                                                                         count    min (ms)    max (ms)    mean (ms)    95%-ile (ms)    sum (ms)"
Header = "%s\r\n" % Header
with open(compliedfile, "w") as myfile:
       myfile.truncate()
       myfile.write(Header)
       myfile.close()

command = "%s %s --queries  --no-progressbar" % (mloginfo_bin,file)
commandP1 = "egrep ^%s" % (database)
commandP2 = "head -n%s" % (count)

output = subprocess.Popen(
                    command.split( ), stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)

grep = subprocess.Popen(
                    commandP1.split( ), stdin=output.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output.stdout.close()

count = subprocess.Popen(
                    commandP2.split( ), stdin=grep.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
grep.stdout.close()

output.wait()
grep.wait()
count.wait()

fo = open(compliedfile, 'a')
for line in iter(count.stdout.readline, ''):
        fo.write(line)
fo.close()

count.stdout.close()

def csv_convert(file_from, file_to):
        rf = open(file_from, 'r') 
        wf = open(file_to,'w')
        writer = csv.writer(wf)

        for row in rf.readlines():
                csvout = re.compile("[^\S\r\n]{2,}").split(row)
                csvout = map(lambda s: s.strip(), csvout)
                writer.writerow(csvout)
        rf.close()
        wf.close()

csv_convert(compliedfile, compliedfile_out)
compliedfile_out = [compliedfile_out]

def send_mail(send_from, send_to, subject, text, files=[], server="localhost"):
        assert type(send_to)==list
        assert type(files)==list

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach( MIMEText(text.encode('utf-8'), 'html') )

        for f in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload( open(f,"rb").read() )
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
            msg.attach(part)

        smtp = smtplib.SMTP(server)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()

send_mail(MailFrom , MailTo, Subject, Txt, compliedfile_out , Server )