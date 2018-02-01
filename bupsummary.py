#!/usr/bin/env python
"""
Gathers summary details from multiple McAfee BUP files, i.e., "unbup all the things, but just get some data"

Copyright (c) 2018 Dan O'Day <d@4n68r.com> & Adam Witt <accidentalassist@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import codecs
import hashlib
import json
import os
import re
from argparse import ArgumentParser

import olefile


class BupSummary(object):
    def __init__(self):

        self.streams = {}
        self.details_dict = {}
        self.details = None

    def extract_files(self, bup):
        ole = olefile.OleFileIO(bup)
        for item in ole.listdir():
            if ole.get_size(item[0]) == 0:
                return False
            else:
                encoded_stream = ole.openstream(item[0]).read()
                self.streams[item[0]] = encoded_stream
        return True

    def single_byte_xor(self, buf):
        # thanks to xortools.py: https://github.com/MalwareLu/tools/blob/master/xortools.py#L4
        # and https://github.com/herrcore/punbup/blob/master/punbup.py#L41
        for item in self.streams:
            key = ord('\x6a')
            out = ''
            for i in buf:
                out += chr(ord(i) ^ key)
            return out

    def details_to_json(self, hostname, bupname, corrupt):
        if corrupt:
            self.details_dict = {"hostname": hostname, "bupname": bupname, "corrupt": corrupt}
        else:
            self.details_dict["hostname"] = hostname
            self.details_dict["bupname"] = bupname
            self.details_dict["corrupt"] = "False"
            current_header = None
            unencoded_details_file = self.single_byte_xor(self.streams["Details"])

            for line in unencoded_details_file.splitlines():
                parse_header = re.search("\[([a-zA-Z0-9_]{3,})\]", line)
            
                if parse_header:
                    current_header = parse_header.group(1)
                    self.details_dict[current_header] = {}

                if "=" in line:
                    values = line.split("=")
                    self.details_dict[current_header][values[0]] = values[1]

        self.details = json.dumps(self.details_dict)

    def hash_sample(self, hostname=None, bupname=None):
        try:
            sample = self.single_byte_xor(self.streams["File_0"])
            hash = hashlib.md5(sample).hexdigest()
        except KeyError:
            hash = "File_0 stream not found"

        final_details = json.loads(self.details)
        final_details["md5"] = hash
        # print hostname + bupname
        try:
            final_details["OriginalName"] = final_details["File_0"]["OriginalName"].decode("utf8")
        except KeyError:
            final_details["OriginalName"] = "OriginalName key not present"
        except UnicodeEncodeError:
            # really ugly unicode hack when UTF8 decoding fails, eliminates all non-ascii characters
            final_details["OriginalName"] = "{0} (Unicode char(s) ignored)".format(final_details["File_0"]["OriginalName"].encode("ascii", "ignore").decode("utf8"))

        self.details = json.dumps(final_details)


def main():
    program_description = "BupSummary: Gather summary details from multiple BUP files"
    p = ArgumentParser(description=program_description)
    p.add_argument("-o", "--output", help="Output File")
    args = p.parse_args()

    # check for required arg param
    if not args.output or args.output == '':
        print "You must specify an output file name. Run with -h parameter to see help."
        return

    current_path = os.getcwd()  # automatically works recursively from pwd
    print program_description
    print "IMPORTANT! Read below:"
    print "1.  This program assumes that BUP files are in parent folders and the parent folder name is the hostname"
    print "    that the BUP file came from!"
    print "2.  This automatically will begin looking for BUP files recursively from your current working directory (pwd)!"
    print "    That means beginning from {0}".format(current_path)
    choice = raw_input("Do you understand? (Y/n): ")
    if not choice or choice.strip() == '' or choice.strip().lower() == 'y' or choice.strip().lower() == "yes":
        with codecs.open(args.output, mode="wb", encoding="utf8") as o:
            o.write("Date,Timestamp,Timezone,Hostname,Bupname,Detection Name,Original Name,MD5,Bup Corrupt?\n")
            for root, dirs, files in os.walk(current_path):
                for f in files:
                    if f.lower().endswith(".bup"):
                        absolute_bup_path = os.path.join(root, f)
                        print "Processing {0} ... ".format(absolute_bup_path),  # show progress
                        b = BupSummary()
                        hostname = absolute_bup_path.split(os.sep)[-2]  # get parent folder name of file (machine name)
                        if not b.extract_files(absolute_bup_path):
                            b.details_to_json(hostname=hostname, bupname=absolute_bup_path, corrupt=True)
                            print "CORRUPT"
                        else:
                            b.details_to_json(hostname=hostname, bupname=absolute_bup_path, corrupt=False)
                            print "OK"
                            b.hash_sample(hostname=hostname, bupname=absolute_bup_path)

                        dd = json.loads(b.details)
                        if dd["corrupt"] == True:  # seems redundant but only works when written this way!
                            corruptbup = ",,,{0},{1},,,{2}\n".format(dd["hostname"], dd["bupname"], dd["corrupt"])
                            o.write(corruptbup.encode("utf8"))
                        else:
                            unbupped = "{0},{1},{2},{3},{4},{5},{6},{7},{8}\n".format(
                                dd["Details"]["CreationYear"] + "-" + dd["Details"]["CreationMonth"] + "-" + dd["Details"]["CreationDay"],
                                dd["Details"]["CreationHour"] + ":" + dd["Details"]["CreationMinute"] + ":" + dd["Details"]["CreationSecond"],
                                dd["Details"]["TimeZoneName"],
                                dd["hostname"],
                                dd["bupname"],
                                dd["Details"]["DetectionName"],
                                dd["OriginalName"],
                                dd["md5"],
                                dd["corrupt"]
                            )
                            o.write(unbupped.encode("utf8"))
        print "Program finished."
    else:
        print "Exiting...\nPlease navigate to desired working directory and rerun script from that location."


if __name__ == "__main__":
    main()
