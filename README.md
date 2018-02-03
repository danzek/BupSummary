# BupSummary
Gathers summary details from multiple McAfee BUP files. In other words, "unbup all the things, but just get some data".

# Usage

1. Place all BUP files in directories where each BUP file's *direct* parent folder is the hostname of the machine from whence the BUP file was extracted.
2. Navigate to the folder *one level above* the folder(s) named after each hostname containing the BUP files.
3. Run BupSummary and specify the output file/path. Example:

       python bupsummary.py -o output.csv

Example directory structure:

    Quarantine <-- run bupsummary.py from this directory
      |
      +--- Machine1
             |
             +--- 41f6e7ebce.bup
             +--- 56fcf12345.bup
      +--- Machine2
             |
             +--- f5c4abcd12.bup
             +--- deadbeef01.bup

## Sample Output

    Date,Timestamp,Timezone,Hostname,Bupname,Detection Name,Original Name,MD5,Bup Corrupt?
    2017-11-14,20:51:43,Central Standard Time,DC-ATL-1234,C:\Data\McAfeeQuar\DC-ATL-1234\41f6e7ebce.bup,Artemis!09D7A37B73CD (ED),C:\WINDOWS\SYSTEM32\LOK.EXE,09d7a37b73cd0c804bac7341f6e7ebce,False
    2017-11-13,01:22:14,Central Standard Time,DC-ATL-1234,C:\Data\McAfeeQuar\DC-ATL-1235\c20394bec6.bup,Trojan-FNTX!4E39362668C2 (ED),C:\DATA\CJ.EXE,d079b02b6a21bc70f10e60c20394bec6,False

## Homage

This code is largely based on [Bupectomy](https://github.com/PoorBillionaire/bupectomy) by Adam Witt. He had already begun rewriting it to accomplish this when I started working on it (not on GitHub).

## Resources / Acknowledgements

- McAfee Knowledge Center, ["How to restore a quarantined file not listed in the VSE Quarantine Manager" (KB72755)](https://kc.mcafee.com/corporate/index?page=content&id=KB72755)

- herrcore [punbup project](https://github.com/herrcore/punbup) (use this if you want to get the original malware from the BUP file(s))

- MalwareLu [XOR Tools project](https://github.com/MalwareLu/tools/blob/master/xortools.py)

## License

Copyright &copy; 2018 Dan O'Day & Adam Witt

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

See [`LICENSE`](LICENSE) file included in repository.
