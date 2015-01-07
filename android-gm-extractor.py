'''android-gm-extractor.py; April, 2013
contact@nsa.sh

This application extracts some data from
the Android based Gmail application and
outputs to standard output with HTML
formatting.

========================================
Updated by CBRYCE on 20150107

Added ability to feed directory or
individual file for processing. In
addition allowed output to be sorted
by specified directory, account name,
and individual message.

If directory handed to script, it will
process each file containing gmail
information.


'''

import sys
import time
import sqlite3
import zlib


def write_css(outFile):
    '''css'''
    outFile.write("""
    <style media="screen" type="text/css">
    .content {border-style:dashed;border-width:2px;margin:15px}
    .header {background:#F0F0F0;margin:15px}
    .body {margin:15px}
    </style>
    """)


def epoch_to_date(otime):
    '''returns m/d/y h:m:s date from Unix Epoch'''
    utime = time.strftime('%m/%d/%Y %H:%M:%S', \
            time.gmtime(otime/1000))
    return utime


def bad_chars(string):
    '''Removes < and > from string.
    Returns cleaned string.'''
    for char in ['<', '>']:
        if char in string:
            string = string.replace(char, '')
    return string


def main(path, outputPath):
    con = sqlite3.connect(path)
    cur = con.cursor()

    cur.execute('SELECT _id, fromAddress, toAddresses, ' \
            'ccAddresses, bccAddresses, replyToAddresses, ' \
            'dateSentMs, dateReceivedMs, subject, ' \
            'bodyCompressed from messages')
    rows = cur.fetchall()

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

        outputFile = open(outputPath+"/"+str(em_id)+"__"+str(em_subject), 'w')

        outputFile.write('<html><body>')
        write_css(outputFile)

        outputFile.write('<div class="content"><div class="header">''<strong>ID:</strong>' + str(em_id) +
                         '<br><br>'+'<strong>From:</strong>' + bad_chars(em_faddress).encode('utf-8') + '<br>' +
                         '<strong>Date Received (UTC +0):</strong>' + epoch_to_date(em_rdate) + '<br><br>' +
                         '<strong>To:</strong>' + bad_chars(em_taddress).encode('utf-8') + '<br>' +
                         '<strong>Date Sent (UTC +0):</strong>' + epoch_to_date(em_sdate) + '<br><br>'
                         '<strong>CC:</strong>' + bad_chars(em_caddress).encode('utf-8') + '<br>' +
                         '<strong>BCC:</strong>' + bad_chars(em_baddress).encode('utf-8') + '<br>' +
                         '<strong>Reply-To Address:</strong>' + bad_chars(em_raddress).encode('utf-8') +
                         '<br><br>' + '</div><div class="body">' +
                         '<strong>Subject:</strong>' + em_subject.encode('utf-8') + '<br><br>' +
                         '<strong>Body:</strong><br>')

        if em_body:
            dem_body = zlib.decompress(em_body)
            outputFile.write(dem_body)
        outputFile.write('</div></div>')
        email_count += 1
    outputFile.write('</body></html>')
    #print email_count

    cur.close()
    con.close()


def scan_for_files(path):

    filesToProcess = []
    account_info = dict()

    import os

    for root, subdirs, files in os.walk(path):
        for fileEntry in files:
            # if fileEntry.startswith('internal.') and fileEntry.endswith('.db') and fileEntry.__contains__('@'):
            #     accountNameInternal = fileEntry.strip('internal.')
            #     accountNameInternal = accountNameInternal.strip('.db')
            #
            #     account_info['account'] = accountNameInternal
            #     account_info['path'] = os.path.join(root, fileEntry)
            #
            #     filesToProcess.append(account_info)
            #     account_info = dict()

            if fileEntry.startswith('mailstore.') and fileEntry.endswith('.db') and fileEntry.__contains__('@'):
                accountNameInternal = fileEntry.split('mailstore.', 1)[1]
                accountNameInternal = accountNameInternal.split('.db')[0]

                account_info['account'] = accountNameInternal
                account_info['path'] = os.path.join(root, fileEntry)

                filesToProcess.append(account_info)
                account_info = dict()

    return filesToProcess

if __name__ == '__main__':
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="The database or directory containing the databases. Will automatically scan "
                                       "for databases to process within subdirectories. If a file, it will begin "
                                       "parsing it.", metavar="/path/to/dir/or/file.db")
    parser.add_argument("destination", help="The output directory. Will create if non-existant.",
                        metavar="/path/to/output/dir/")

    args = parser.parse_args()

    if os.path.isdir(args.source):
        filesToProcess = scan_for_files(args.source)

        for fileEntry in filesToProcess:
            accountOutputPath = os.path.join(args.destination, fileEntry['account'].split('@', 1)[0])
            if not os.path.exists(accountOutputPath):
                os.makedirs(accountOutputPath)
            main(fileEntry['path'], accountOutputPath)

    elif os.path.isfile(args.source):
        accountName = os.path.basename(args.source)
        accountName = accountName.split('@', 1)[0]
        accountOutputPath = os.path.join(args.destination, accountName)
        os.makedirs(accountOutputPath)
        main(args.source, accountOutputPath)

    else:
        raise "No input detected. Please try again..."
        quit()

