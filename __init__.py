import os

try:
    import epg2xml
except:
    os.system("python -m pip install git+https://github.com/epg2xml/epg2xml.git")