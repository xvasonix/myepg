
import os
from .setup import P

import subprocess
import json
import re
import copy
import shutil


_epg2xml_default = {
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
        "MY_CHANNELS": [],
    },
    "LG": {
        "MY_CHANNELS": [],
    },
    "SK": {
        "MY_CHANNELS": [],
    },
    "DAUM": {
        "MY_CHANNELS": [],
    },
    "NAVER": {
        "MY_CHANNELS": [],
    },
    "WAVVE": {
        "MY_CHANNELS": [],
    },
    "TVING": {
        "MY_CHANNELS": [],
    },
    "SPOTV": {
        "MY_CHANNELS": [],
    },
}


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
            P.logger.info('epg_update_script start')

            cur_dir = os.path.dirname(__file__)
            epg2xml_json_path = f"{cur_dir}/file/epg2xml.json"
            channel_json_path = f"{cur_dir}/file/Channel.json"
            xmltv_xml_path = f"{cur_dir}/file/xmltv.xml"
            
            # cls.deleteDirectory(f"{cur_dir}/file")
            cls.createDirectory(f"{cur_dir}/file")

            # main_A1 에 따라 epg2xml.json 수정/생성
            if cls.checkEpg2xml(epg2xml_json_path):      
                P.logger.info('Epg2xml 수정')
                cls.checkChannel(channel_json_path)
            else:
                P.logger.info('Epg2xml 생성')

            cls.updateChannel(epg2xml_json_path, channel_json_path)
            cls.setEpg2xml(epg2xml_json_path, channel_json_path)
            cls.makeXmltv(epg2xml_json_path, channel_json_path, xmltv_xml_path)

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
    def setEpg2xml(cls, path, channel_path):
        try:
            P.logger.info(f'epg2xml_json start')
            epg2xml_json = cls.getEpg2xml(path)
            with open(channel_path, 'r', encoding='utf-8') as f:
                channel_json_data = json.load(f)
                
                if 'KT' in channel_json_data.keys():
                    epg2xml_json['KT']['MY_CHANNELS'] = channel_json_data['KT']['CHANNELS']
                    epg2xml_json['KT']['ENABLED'] = eval(P.ModelSetting.get('main_KT'))

                if 'LG' in channel_json_data.keys():
                    epg2xml_json['LG']['MY_CHANNELS'] = channel_json_data['LG']['CHANNELS']
                    epg2xml_json['LG']['ENABLED'] = eval(P.ModelSetting.get('main_LG'))

                if 'SK' in channel_json_data.keys():
                    epg2xml_json['SK']['MY_CHANNELS'] = channel_json_data['SK']['CHANNELS']
                    epg2xml_json['SK']['ENABLED'] = eval(P.ModelSetting.get('main_SK'))
                
                if 'DAUM' in channel_json_data.keys():
                    epg2xml_json['DAUM']['MY_CHANNELS'] = channel_json_data['DAUM']['CHANNELS'] 
                    epg2xml_json['DAUM']['ENABLED'] = eval(P.ModelSetting.get('main_DAUM'))
                
                if 'NAVER' in channel_json_data.keys():
                    epg2xml_json['NAVER']['MY_CHANNELS'] = channel_json_data['NAVER']['CHANNELS']
                    epg2xml_json['NAVER']['ENABLED'] = eval(P.ModelSetting.get('main_NAVER'))
                
                if 'WAVVE' in channel_json_data.keys() and eval(P.ModelSetting.get('main_A1'))==False:
                    epg2xml_json['WAVVE']['MY_CHANNELS'] = channel_json_data['WAVVE']['CHANNELS']
                    epg2xml_json['WAVVE']['ENABLED'] = eval(P.ModelSetting.get('main_WAVVE'))

                if 'TVING' in channel_json_data.keys():
                    epg2xml_json['TVING']['MY_CHANNELS'] = channel_json_data['TVING']['CHANNELS']
                    epg2xml_json['TVING']['ENABLED'] = eval(P.ModelSetting.get('main_TVING'))                
                
                if 'SPOTV' in channel_json_data.keys():
                    epg2xml_json['SPOTV']['MY_CHANNELS'] = channel_json_data['SPOTV']['CHANNELS']
                    epg2xml_json['SPOTV']['ENABLED'] = eval(P.ModelSetting.get('main_SPOTV'))

            with open(path, 'w', encoding='utf-8') as f:
                txt = json.dumps(epg2xml_json, ensure_ascii=False, indent=2)
                txt = re.sub(r",\n\s{8}\"", ', "', txt)
                txt = re.sub(r"\s{6}{\s+(.*)\s+}", r"      { \g<1> }", txt)
                f.write(txt)

            P.logger.info(f'epg2xml_json end')
        except Exception as e: 
            P.logger.exception(f'Exception:{str(e)}')

            
    @classmethod
    def checkEpg2xml(cls, path):
        try: 
            if not os.path.exists(path):  
                # epg2xml 파일이 없으면 기본값 복제해서 생성
                P.logger.info(f'checkEpg2xml {path} 없음')
                epg2xml_default = copy.deepcopy(_epg2xml_default)
                epg2xml_default['WAVVE']['ENABLED'] = not eval(P.ModelSetting.get('main_A1'))
                cls.makeEpg2xml(path, epg2xml_default)

                return False
            else: 
                # 각 소스 ENABLED 을 True 로 해야 Channel.json 채널 목록 불러올 수 있음 
                P.logger.info(f'checkEpg2xml {path} 수정')
                epg2xml_json = cls.getEpg2xml(path)
                epg2xml_json['KT']['ENABLED'] = True
                epg2xml_json['LG']['ENABLED'] = True
                epg2xml_json['SK']['ENABLED'] = True
                epg2xml_json['DAUM']['ENABLED'] = True
                epg2xml_json['NAVER']['ENABLED'] = True
                epg2xml_json['WAVVE']['ENABLED'] = not eval(P.ModelSetting.get('main_A1'))       
                epg2xml_json['TVING']['ENABLED'] = True
                epg2xml_json['SPOTV']['ENABLED'] = True

                with open(path, 'w', encoding='utf-8') as f:
                    txt = json.dumps(epg2xml_json, ensure_ascii=False, indent=2)
                    f.write(txt)

                return True
        except Exception as e: 
            P.logger.exception(f'Exception:{str(e)}')


    @classmethod
    def getChannel(cls, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                channel_json = json.load(f)
                return channel_json
        except Exception as e: 
            P.logger.exception(f'Exception:{str(e)}')

            
    @classmethod
    def checkChannel(cls, path):
        try: 
            P.logger.info(f'checkChannel start')
            if os.path.exists(path):  
                # Channel 파일 수정X 그냥 삭제 하고 다시 받게 끔 
                P.logger.info(f'checkChannel {path} 있음')
                # 채널 파일이 있고 A1 사용자면 WAVVE 제거
                channel_json = cls.getChannel(path)
                if 'WAVVE' in channel_json.keys():
                    if eval(P.ModelSetting.get('main_A1')):
                        # P.logger.info(f'WAVVE 소스 O - A1 사용자 - 삭제')  
                        cls.deleteFile(path)
                    # else:
                    #     P.logger.info(f'WAVVE 소스 O - 일반 사용자 - 유지') 
                else:
                    #웨이브 키가 없고 일반 유저 - 삭제 
                    if not eval(P.ModelSetting.get('main_A1')): 
                        # P.logger.info(f'WAVVE 소스 X - 일반 사용자 - 삭제') 
                        cls.deleteFile(path)
                    # else:
                    #     P.logger.info(f'WAVVE 소스 X - A1유저 - 유지')     
            P.logger.info(f'checkChannel end')
        except Exception as e: 
            P.logger.exception(f'Exception:{str(e)}')


    @classmethod
    def createDirectory(cls, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            P.logger.exception(f"Error: Failed to create the {path}.")


    @classmethod
    def deleteDirectory(cls, path):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                P.logger.info(f"설정 폴더 삭제 : {path}")
            else:
                P.logger.info(f"설정 폴더 없음 : {path}")
        except OSError:
            P.logger.exception(f"Error: Failed to delete the {path}.")


    @classmethod
    def deleteFile(cls, path):
        try:
            if os.path.exists(path):
                os.remove(path)
                P.logger.info(f"파일 삭제 : {path}")
            else:
                P.logger.info(f"파일 없음 : {path}")
        except OSError:
            P.logger.exception(f"Error: Failed to delete the {path}.")


    @classmethod
    def makeEpg2xml(cls, config_path, data_json):
        P.logger.info(f"init - user_epg2xml : {config_path} - main_A1 값 : {eval(P.ModelSetting.get('main_A1'))}")
        try:
            # subprocess.call(f"epg2xml run --config {epg2xml_json_path}", shell=True)  
            with open(config_path, 'w', encoding='utf-8') as f:
                txt = json.dumps(data_json, ensure_ascii=False, indent=2)
                txt = re.sub(r",\n\s{8}\"", ', "', txt)
                txt = re.sub(r"\s{6}{\s+(.*)\s+}", r"      { \g<1> }", txt)
                f.write(txt)
        except OSError:
            P.logger.exception("Error: Failed to create the directory.")


    # 첫 실행시에 file/channel.json 만들어짐
    @classmethod
    def updateChannel(cls, config_path, channel_path):
        P.logger.info(f'updateChannel start')
        command = ['epg2xml', 'update_channels', '--config', f'{config_path}', '--channelfile', f'{channel_path}']
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            for line in proc.stderr:
                P.logger.info(line[24:].strip())
                
        P.logger.info(f'updateChannel end')


    @classmethod
    def makeXmltv(cls, config_path, channel_path, xml_path):
        P.logger.info(f'makeXmltv start')
        command = ['epg2xml', 'run', '--config', f'{config_path}', '--channelfile', f'{channel_path}', '--xmlfile', f'{xml_path}']
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            for line in proc.stderr:
                P.logger.info(line[24:].strip())

        P.logger.info(f'makeXmltv end')