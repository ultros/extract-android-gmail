'''android-gm-extractor.py; April, 2013
contact@nsa.sh

This application extracts some data from
the Android based Gmail application and
outputs to standard output with HTML
formatting.
'''

import sys, time
import sqlite3, zlib

def write_css():
    '''css'''
    print '<style media="screen" type="text/css">'
    print '.content {border-style:dashed;border-width:2px;margin:15px}'
    print '.header {background:#F0F0F0;margin:15px}'
    print '.body {margin:15px}'
    print '</style>'

def epoch_to_date(otime):
    '''returns m/d/y h:m:s date from Unix Epoch'''
    utime = time.strftime('%m/%d/%Y %H:%M:%S', \
            time.gmtime(otime/1000))
    return utime

def bad_chars(string):
    '''Removes < and > from string.
    Returns cleaned string.'''
    chars = "<>"
    for char in ['<', '>']:
        if char in string:
            string = string.replace(char, '')
    return string

def main():
    con = sqlite3.connect(sys.argv[1])
    cur = con.cursor()

    cur.execute('SELECT _id, fromAddress, toAddresses, ' \
            'ccAddresses, bccAddresses, replyToAddresses, ' \
            'dateSentMs, dateReceivedMs, subject, ' \
            'bodyCompressed from messages')
    rows = cur.fetchall()

    print '<html><body>'
    write_css()
    email_count = 0
    for row in rows:
        em_id       = row[0]
        em_faddress = row[1]
        em_taddress = row[2]
        em_caddress = row[3]
        em_baddress = row[4]
        em_raddress = row[5]
        em_sdate    = row[6]
        em_rdate    = row[7]
        em_subject  = row[8]
        em_body     = row[9]

        print '<div class="content"><div class="header">'
        print '<strong>ID:</strong>', em_id, '<br><br>'
        print '<strong>From:</strong>', \
                bad_chars(em_faddress).encode('utf-8'),'<br>'
        print '<strong>Date Received (UTC +0):</strong>', \
                epoch_to_date(em_rdate), '<br><br>'
        print '<strong>To:</strong>', bad_chars(em_taddress).encode('utf-8'), '<br>'
        print '<strong>Date Sent (UTC +0):</strong>', epoch_to_date(em_sdate), \
                '<br><br>'
        print '<strong>CC:</strong>', bad_chars(em_caddress).encode('utf-8'), '<br>'
        print '<strong>BCC:</strong>', bad_chars(em_baddress).encode('utf-8'), '<br>'
        print '<strong>Reply-To Address:</strong>', bad_chars(em_raddress).encode('utf-8'), \
                '<br><br>'
        print '</div><div class="body">'
        print '<strong>Subject:</strong>', em_subject.encode('utf-8'), \
                '<br><br>'
        print '<strong>Body:</strong><br>'
        if em_body:
            dem_body = zlib.decompress(em_body)
            print dem_body
        print '</div></div>'
        email_count += 1
    print '</body></html>'
    #print email_count

    cur.close()
    con.close()

if __name__ == '__main__':
    main()
