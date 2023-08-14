
from datetime import datetime
import os
from .setup import P

import subprocess
import json
import re


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
            cur_dir = os.path.dirname(__file__)
            channel_json_path = f"{cur_dir}/file/Channel.json"
            epg2xml_json_path = f"{cur_dir}/file/epg2xml.json"
            xmltv_path = f"{cur_dir}/file/xmltv.xml"

            MYEPG.createDirectory(f"{cur_dir}/file")
            
            if os.path.exists(epg2xml_json_path)==False:
                P.logger.info(f'init - user_epg2xml : {epg2xml_json_path}')
                subprocess.call(f"epg2xml run --config {epg2xml_json_path}", shell=True)  

            P.logger.info('epg_update_script start')
            subprocess.call(f"epg2xml update_channels --config {epg2xml_json_path} --channelfile {channel_json_path}", shell=True)  

            P.logger.info('epg_update_script make epg2xml.json')
            with open(channel_json_path, 'r', encoding='utf-8') as f:
                channel_json_data = json.load(f)

                epg2xml_default = {
                    "GLOBAL": {
                        "ENABLED": True,
                        "FETCH_LIMIT": 2,
                        "ID_FORMAT": "{ServiceId}.{Source.lower()}",
                        "ADD_REBROADCAST_TO_TITLE": False,
                        "ADD_EPNUM_TO_TITLE": True,
                        "ADD_DESCRIPTION": True,
                        "ADD_XMLTV_NS": False,
                        "GET_MORE_DETAILS": False,
                        "ADD_CHANNEL_ICON": True,
                    },
                    "KT": {
                        "MY_CHANNELS": channel_json_data['KT']['CHANNELS'],
                        "ENABLED": eval(P.ModelSetting.get('KT'))
                    },
                    "LG": {
                        "MY_CHANNELS": channel_json_data['LG']['CHANNELS'],
                        "ENABLED": eval(P.ModelSetting.get('LG'))
                    },
                    "SK": {
                        "MY_CHANNELS": channel_json_data['SK']['CHANNELS'],
                        "ENABLED": eval(P.ModelSetting.get('SK'))
                    },
                    "DAUM": {
                        "MY_CHANNELS": channel_json_data['DAUM']['CHANNELS'],
                        "ENABLED": eval(P.ModelSetting.get('DAUM'))
                    },
                    "NAVER": {
                        "MY_CHANNELS": channel_json_data['NAVER']['CHANNELS'],
                        "ENABLED": eval(P.ModelSetting.get('NAVER'))
                    },
                    "WAVVE": {
                        "MY_CHANNELS": channel_json_data['WAVVE']['CHANNELS'],
                        "ENABLED": eval(P.ModelSetting.get('WAVVE'))
                    },
                    "TVING": {
                        "MY_CHANNELS": channel_json_data['TVING']['CHANNELS'],
                        "ENABLED": eval(P.ModelSetting.get('TVING'))
                    },
                    "SPOTV": {
                        "MY_CHANNELS": channel_json_data['SPOTV']['CHANNELS'],
                        "ENABLED": eval(P.ModelSetting.get('SPOTV'))
                    },
                }

                with open(epg2xml_json_path, 'w', encoding='utf-8') as make_json:
                    txt = json.dumps(epg2xml_default, ensure_ascii=False, indent=2)
                    txt = re.sub(r",\n\s{8}\"", ', "', txt)
                    txt = re.sub(r"\s{6}{\s+(.*)\s+}", r"      { \g<1> }", txt)
                    make_json.write(txt)

            P.logger.info('epg_update_script make xml')
            subprocess.call(f"epg2xml run --config {epg2xml_json_path} --channelfile {channel_json_path} --xmlfile {xmltv_path}", shell=True)
            P.logger.info('epg_update_script end')
        except Exception as e: 
            P.logger.exception(f'Exception:{str(e)}')

    @classmethod
    def createDirectory(cls, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print("Error: Failed to create the directory.")