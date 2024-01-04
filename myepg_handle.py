
import os
from .setup import P

import subprocess
import json
import re
import shutil
from datetime import datetime

import xml.etree.ElementTree as ET
import copy
from copy import deepcopy
from pathlib import Path
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from framework.init_main import Framework
FRAMEWORK = Framework.get_instance()


# _epg2xml_default = {
#     "GLOBAL": {
#         "ENABLED": True,
#         "FETCH_LIMIT": 2,
#         "ID_FORMAT": "{ServiceId}.{Source.lower()}",
#         # "ID_FORMAT": "{Name}",
#         "ADD_REBROADCAST_TO_TITLE": False,
#         "ADD_EPNUM_TO_TITLE": True,
#         "ADD_DESCRIPTION": True,
#         "ADD_XMLTV_NS": False,
#         "GET_MORE_DETAILS": False,
#         "ADD_CHANNEL_ICON": True,
#         "HTTP_PROXY": None,
#     },
#     "KT": {
#         "MY_CHANNELS": [],
#     },
#     "LG": {
#         "MY_CHANNELS": [],
#     },
#     "SK": {
#         "MY_CHANNELS": [],
#     },
#     "DAUM": {
#         "MY_CHANNELS": [],
#     },
#     "NAVER": {
#         "MY_CHANNELS": [],
#     },
#     "WAVVE": {
#         "MY_CHANNELS": [],
#     },
#     "TVING": {
#         "MY_CHANNELS": [],
#     },
#     "SPOTV": {
#         "MY_CHANNELS": [],
#     },
# }


class MYEPG:


    @classmethod
    def epg_update_script(cls):
        try:
            P.logger.info('epg_update_script start')

            file_folder_path = os.path.join(os.path.dirname(__file__), 'file')
            epg2xml_json_path = os.path.join(file_folder_path, 'epg2xml.json')
            channel_json_path = os.path.join(file_folder_path, 'Channel.json') 
            xmltv_xml_path = os.path.join(file_folder_path, 'xmltv.xml')

            # cls.deleteDirectory(file_folder_path)
            cls.makeDirectory(file_folder_path)
            cls.checkEpg2xml(epg2xml_json_path)  

            cls.setEnabled(epg2xml_json_path)
            cls.updateChannel(epg2xml_json_path, channel_json_path)
            
            if cls.checkChannel(channel_json_path):
                cls.setMyChannels(epg2xml_json_path, channel_json_path)

                cls.deleteFile(xmltv_xml_path)
                cls.makeXmltv(epg2xml_json_path, channel_json_path, xmltv_xml_path)
                if P.ModelSetting.get_bool('main_match'):
                    cls.match_channels(xmltv_xml_path)
            else:
                P.logger.error('No channel.json file')

            P.logger.info('epg_update_script end')
        except Exception as e: 
            P.logger.exception(f'Exception:{str(e)}')


    @classmethod
    def getEpg2xml(cls, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                epg2xml_json = json.load(f)
                return epg2xml_json
        except Exception as e: 
            P.logger.exception(f'Exception:{str(e)}')


    @classmethod
    def setEnabled(cls, path):
        try:
            P.logger.info('epg2xml_json setEnabled start')
            epg2xml_json = cls.getEpg2xml(path)
            # P.logger.debug(f'setEnabled, {json.dumps(epg2xml_json, ensure_ascii=False, indent=2)}')
                
            # if 'KT' in epg2xml_json.keys():
            #     epg2xml_json['KT']['ENABLED'] = P.ModelSetting.get_bool('main_KT')
            # if 'LG' in epg2xml_json.keys():
            #     epg2xml_json['LG']['ENABLED'] = P.ModelSetting.get_bool('main_LG')
            # if 'SK' in epg2xml_json.keys():
            #     epg2xml_json['SK']['ENABLED'] = P.ModelSetting.get_bool('main_SK')
            # if 'DAUM' in epg2xml_json.keys():
            #     epg2xml_json['DAUM']['ENABLED'] = P.ModelSetting.get_bool('main_DAUM')
            # if 'NAVER' in epg2xml_json.keys():
            #     epg2xml_json['NAVER']['ENABLED'] = P.ModelSetting.get_bool('main_NAVER')

            if 'WAVVE' in epg2xml_json.keys():
                proxy_url = cls.get_wavve_proxy()
                if proxy_url != '':
                    epg2xml_json['WAVVE']['ENABLED'] = P.ModelSetting.get_bool('main_WAVVE')
                    epg2xml_json['WAVVE']['HTTP_PROXY'] = proxy_url
                else:
                    if P.ModelSetting.get_bool('main_A1'):
                        epg2xml_json['WAVVE']['ENABLED'] = False
                        epg2xml_json['WAVVE']['HTTP_PROXY'] = None
                    else:
                        epg2xml_json['WAVVE']['ENABLED'] = P.ModelSetting.get_bool('main_WAVVE')
                        epg2xml_json['WAVVE']['HTTP_PROXY'] = None

            # if 'TVING' in epg2xml_json.keys():
            #     epg2xml_json['TVING']['ENABLED'] = P.ModelSetting.get_bool('main_TVING')               
            # if 'SPOTV' in epg2xml_json.keys():
            #     epg2xml_json['SPOTV']['ENABLED'] = P.ModelSetting.get_bool('main_SPOTV')
			
            with open(path, 'w', encoding='utf-8') as f:
                txt = json.dumps(epg2xml_json, ensure_ascii=False, indent=2)
                txt = re.sub(r",\n\s{8}\"", ', "', txt)
                txt = re.sub(r"\s{6}{\s+(.*)\s+}", r"      { \g<1> }", txt)
                f.write(txt)

            P.logger.info('epg2xml_json setEnabled end')
        except Exception as e: 
            P.logger.exception(f'Exception:{str(e)}')


    @classmethod
    def setMyChannels(cls, path, channel_path):
        try:
            P.logger.info('epg2xml_json setMyChannels start')
            epg2xml_json = cls.getEpg2xml(path)
            # P.logger.debug(f'setMyChannels, {json.dumps(epg2xml_json, ensure_ascii=False, indent=2)}')

            with open(channel_path, 'r', encoding='utf-8') as f:
                channel_json_data = json.load(f)
                # P.logger.debug(f'channel_json_data, {json.dumps(channel_json_data, ensure_ascii=False, indent=2)}')

                # if 'KT' in channel_json_data.keys() and epg2xml_json['KT']['ENABLED']:
                #     epg2xml_json['KT']['MY_CHANNELS'] = channel_json_data['KT']['CHANNELS']

                # if 'LG' in channel_json_data.keys() and epg2xml_json['LG']['ENABLED']:
                #     epg2xml_json['LG']['MY_CHANNELS'] = channel_json_data['LG']['CHANNELS']

                # if 'SK' in channel_json_data.keys() and epg2xml_json['SK']['ENABLED']:
                #     epg2xml_json['SK']['MY_CHANNELS'] = channel_json_data['SK']['CHANNELS']

                # if 'DAUM' in channel_json_data.keys() and epg2xml_json['DAUM']['ENABLED']:
                #     epg2xml_json['DAUM']['MY_CHANNELS'] = channel_json_data['DAUM']['CHANNELS'] 
                
                # if 'NAVER' in channel_json_data.keys() and epg2xml_json['NAVER']['ENABLED']:
                #     epg2xml_json['NAVER']['MY_CHANNELS'] = channel_json_data['NAVER']['CHANNELS']

                # if 'WAVVE' in channel_json_data.keys() and epg2xml_json['WAVVE']['ENABLED']:
                #     epg2xml_json['WAVVE']['MY_CHANNELS'] = channel_json_data['WAVVE']['CHANNELS']

                # if 'TVING' in channel_json_data.keys() and epg2xml_json['TVING']['ENABLED']:
                #     epg2xml_json['TVING']['MY_CHANNELS'] = channel_json_data['TVING']['CHANNELS']

                # if 'SPOTV' in channel_json_data.keys() and epg2xml_json['SPOTV']['ENABLED']:
                #     epg2xml_json['SPOTV']['MY_CHANNELS'] = channel_json_data['SPOTV']['CHANNELS']

              
                if P.ModelSetting.get_bool('main_KT'):
                    epg2xml_json['KT']['MY_CHANNELS'] = channel_json_data['KT']['CHANNELS']
                else:
                    epg2xml_json['KT']['MY_CHANNELS'] =[]

                if P.ModelSetting.get_bool('main_LG'):
                    epg2xml_json['LG']['MY_CHANNELS'] = channel_json_data['LG']['CHANNELS']
                else:
                    epg2xml_json['LG']['MY_CHANNELS'] =[]

                if P.ModelSetting.get_bool('main_SK'):
                    epg2xml_json['SK']['MY_CHANNELS'] = channel_json_data['SK']['CHANNELS']
                else:
                    epg2xml_json['SK']['MY_CHANNELS'] =[]

                if P.ModelSetting.get_bool('main_DAUM'):
                    epg2xml_json['DAUM']['MY_CHANNELS'] = channel_json_data['DAUM']['CHANNELS'] 
                else:
                    epg2xml_json['DAUM']['MY_CHANNELS'] =[]

                if P.ModelSetting.get_bool('main_NAVER'):
                    epg2xml_json['NAVER']['MY_CHANNELS'] = channel_json_data['NAVER']['CHANNELS']
                else:
                    epg2xml_json['NAVER']['MY_CHANNELS'] =[]

                # ENABLED = True/False 만으로도 막을 수 있음. MY_CHANNELS 여부 상관없음
                if 'WAVVE' in channel_json_data.keys() and epg2xml_json['WAVVE']['ENABLED']:
                    epg2xml_json['WAVVE']['MY_CHANNELS'] = channel_json_data['WAVVE']['CHANNELS']
                else:
                    epg2xml_json['WAVVE']['MY_CHANNELS'] =[]

                if P.ModelSetting.get_bool('main_TVING'):
                    epg2xml_json['TVING']['MY_CHANNELS'] = channel_json_data['TVING']['CHANNELS']
                else:
                    epg2xml_json['TVING']['MY_CHANNELS'] =[]

                if P.ModelSetting.get_bool('main_SPOTV'):
                    epg2xml_json['SPOTV']['MY_CHANNELS'] = channel_json_data['SPOTV']['CHANNELS']
                else:
                    epg2xml_json['SPOTV']['MY_CHANNELS'] =[]

            with open(path, 'w', encoding='utf-8') as f:
                txt = json.dumps(epg2xml_json, ensure_ascii=False, indent=2)
                txt = re.sub(r",\n\s{8}\"", ', "', txt)
                txt = re.sub(r"\s{6}{\s+(.*)\s+}", r"      { \g<1> }", txt)
                f.write(txt)
                
            P.logger.info('epg2xml_json setMyChannels end')
        except Exception as e: 
            P.logger.exception(f'Exception:{str(e)}')


    @classmethod
    def checkEpg2xml(cls, path):
        try: 
            if not os.path.exists(path):  
                P.logger.info(f'checkEpg2xml {path} 생성')
                # epg2xml_default = copy.deepcopy(_epg2xml_default)
                # cls.makeEpg2xml(path, epg2xml_default)

                # epg2xml run 으로 생성
                cls.makeEpg2xml_command(path)
        except Exception as e: 
            P.logger.exception(f'Exception: {str(e)}')

    @classmethod
    def getChannel(cls, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                channel_json = json.load(f)
                return channel_json
        except Exception as e: 
            P.logger.exception(f'Exception: {str(e)}')


    @classmethod
    def checkChannel(cls, path):
        try:
            if os.path.exists(path):
                return True
            else:
                return False
        except Exception as e:
            P.logger.exception(f"Exception: {str(e)}")


    @classmethod
    def makeDirectory(cls, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            P.logger.exception(f"Error: Failed to make the {path}.")


    @classmethod
    def deleteDirectory(cls, path):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                P.ModelSetting.set('epg_updated_time', '')
                P.logger.info(f"설정 폴더 삭제 : {path}")
        except OSError:
            P.logger.exception(f"Error: Failed to delete the {path}.")


    @classmethod
    def deleteFile(cls, path):
        try:
            if os.path.exists(path):
                os.remove(path)
                P.logger.info(f"파일 삭제 : {path}")
        except OSError:
            P.logger.exception(f"Error: Failed to delete the {path}.")


    @classmethod
    def makeEpg2xml(cls, config_path, data_json):
        try:
            P.logger.info("user_epg2xml start")

            with open(config_path, 'w', encoding='utf-8') as f:
                txt = json.dumps(data_json, ensure_ascii=False, indent=2)
                txt = re.sub(r",\n\s{8}\"", ', "', txt)
                txt = re.sub(r"\s{6}{\s+(.*)\s+}", r"      { \g<1> }", txt)
                f.write(txt)
        
            P.logger.info('user_epg2xml end')
        except Exception as e:
            P.logger.exception(f"Exception: {str(e)}")
        

    @classmethod
    def makeEpg2xml_command(cls, config_path):
        P.logger.info("makeEpg2xml_command start")

        # os.chdir(os.path.join(os.path.dirname(__file__), 'epg2xml'))
        # command = ['python', '-m', 'epg2xml', 'run', '--config', config_path]
        command = ['python', '-m', 'epg2xml', 'run', '--config', config_path, '--parallel']
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            for line in proc.stderr:
                cls.print_log(line)

        P.logger.info('makeEpg2xml_command end')


    @classmethod
    def updateChannel(cls, config_path, channel_path):
        P.logger.info('updateChannel start')

        # os.chdir(os.path.join(os.path.dirname(__file__), 'epg2xml'))
        # command = ['epg2xml', 'update_channels', '--config', config_path, '--channelfile', channel_path]
        command = ['python', '-m', 'epg2xml', 'update_channels', '--config', config_path, '--channelfile', channel_path, '--parallel']
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            for line in proc.stderr:
                cls.print_log(line)

        P.logger.info('updateChannel end')


    @classmethod
    def makeXmltv(cls, config_path, channel_path, xml_path):
        P.logger.info('makeXmltv start')

        # os.chdir(os.path.join(os.path.dirname(__file__), 'epg2xml'))
        # command = ['epg2xml', 'run', '--config', config_path', '--channelfile', channel_path, '--xmlfile', xml_path]
        command = ['python', '-m', 'epg2xml', 'run', '--config', config_path, '--channelfile', channel_path, '--xmlfile', xml_path, '--parallel']
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            for line in proc.stderr:
                cls.print_log(line)

            P.ModelSetting.set('epg_updated_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        P.logger.info('makeXmltv end')


    @classmethod
    def print_log(cls, line):
        pattern = "([0-9]+)/*([0-9]+)/*([0-9]+)\s*([0-9]+):*([0-9]+):*([0-9]+)\s"
        try:
            # P.logger.error(line[:].strip()) 
            if re.search(pattern, line) == None:
                P.logger.error(line[:].strip())                 
            else:           
                P.logger.info(line[29:].strip())        
        except Exception as e:
            P.logger.exception(f"Error: {str(e)}")


    @classmethod
    def get_wavve_proxy(cls) -> str:  
        try:      
            support_site = FRAMEWORK.PluginManager.get_plugin_instance('support_site')
            use_proxy = support_site.ModelSetting.get_bool('site_wavve_use_proxy')
            proxy_url = support_site.ModelSetting.get('site_wavve_proxy_url')
            return use_proxy and proxy_url or ""    
        except Exception as e:
            P.logger.exception(f"get_wavve_proxy : {str(e)}")
    

    @classmethod
    def load_yaml(cls, file):
        try:
            return yaml.load(file, Loader=Loader)
        except TypeError:
            with open(file, "r", encoding='utf-8') as fp:
                return yaml.load(fp, Loader=Loader)


    @classmethod
    def insert(cls, channel, channels):
        text = channel.find("display-name").text
        # P.logger.debug(text)
        for match in channels:
            if text.lower() != match['wavve'].lower():
                for m in match['name']:
                    # P.logger.debug(m, text)
                    if m.lower() == text.lower():
                        # P.logger.debug(f"{m}, {text}, {match['wavve']}")
                        name = ET.Element("display-name")
                        name.text = match['wavve']
                        channel.insert(0, name)
                        if (m.lower() == 'KBS1'.lower()) or (name.text.lower() == 'KBS1'.lower()):
                            name_1tv = ET.Element("display-name")
                            name_1tv.text = '1TV'
                            channel.insert(1, name_1tv)
                        if (m.lower() == 'KBS2'.lower()) or (name.text.lower() == 'KBS2'.lower()):
                            name_2tv = ET.Element("display-name")
                            name_2tv.text = '2TV'
                            channel.insert(1, name_2tv)
                            

    @classmethod
    def match_channels(cls, xml_path):
        try:
            P.logger.info('match_channels start')

            file = Path(os.path.dirname(__file__)).joinpath("match_channels.yaml")
            match_channels_yaml = cls.load_yaml(file)
            # P.logger.debug(match_channels_yaml)
            match_channels = deepcopy(match_channels_yaml['match_channels'])
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            [cls.insert(c, match_channels) for c in root.findall("channel")]

            with open(xml_path, 'wb') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE tv SYSTEM "xmltv.dtd">\n\n'.encode('utf8'))
                tree = ET.ElementTree(root)
                ET.indent(tree, space="\t", level=0)
                tree.write(f, encoding="utf-8")

            P.logger.info('match_channels end')
        except Exception as e:
            P.logger.exception(f"xmltv match_channels : {e}")
        