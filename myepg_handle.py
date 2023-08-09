
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
            if platform.system() == 'Windows':
                epg_sh = os.path.join(os.path.dirname(__file__), 'file', 'epg_update.bat')
                os.system(f"{epg_sh} {os.path.dirname(__file__)}")
            else:
                epg_sh = os.path.join(os.path.dirname(__file__), 'file', 'epg_update.sh')
                os.system(f"chmod -R 777 {os.path.dirname(__file__)}")
                os.system(f"{epg_sh} {os.path.dirname(__file__)}")
        except Exception as e: 
            P.logger.exception(f'Exception:{str(e)}')