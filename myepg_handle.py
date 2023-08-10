
from datetime import datetime
import os, platform
from support import logger

from .setup import P

class MYEPG:

    @classmethod
    def get_epgall(cls):
        try:
            import xml.etree.ElementTree as ET    
            xmltv_path = os.path.join(os.path.dirname(__file__), 'file', 'xmltv.xml')
            tree = ET.parse(xmltv_path)
            root = tree.getroot()
            return ET.tostring(root, encoding='utf-8')
        except Exception as e:
            P.logger.exception(f'error return xmltv.xml : {str(e)}')

    @classmethod
    def epg_update_script(cls):
        try:
            import subprocess
            cur_dir = os.path.dirname(__file__)
            subprocess.call(f"epg2xml run --config {cur_dir}/file/epg2xml.json --channelfile {cur_dir}/file/Channel.json --xmlfile {cur_dir}/file/xmltv.xml", shell=True)
            # subprocess.call(["epg2xml", "run", "--config", f"{cur_dir}/file/epg2xml.json", "--channelfile", f"{cur_dir}/file/Channel.json", "--xmlfile",  f"{cur_dir}/file/xmltv.xml"])
        except Exception as e: 
            P.logger.exception(f'Exception:{str(e)}')