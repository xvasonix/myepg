
import os
import subprocess
import json
import re
import shutil
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# import xml.etree.ElementTree as ET
# from copy import deepcopy
# from pathlib import Path

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from framework.init_main import Framework
FRAMEWORK = Framework.get_instance()
SystemModelSetting = FRAMEWORK.SystemModelSetting

from .setup import P

ModelSetting = P.ModelSetting
logger = P.logger


urls = []
providers = ['KT', 'LG', 'SK', 'DAUM', 'NAVER', 'WAVVE', 'TVING', 'SPOTV', 'SBS']
priority = ['WAVVE', 'TVING', 'SPOTV', 'SBS', 'KT', 'LG', 'SK', 'DAUM', 'NAVER']

        
class M3uParser:
    def __init__(self, text):
        self.text = text
        self.tracks = []


    def readM3u(self):
        self.readAllLines()
        self.parseFile()
        return self.tracks


    def readAllLines(self):
        self.lines = self.text.splitlines()
        # logger.info(self.lines)
        # logger.info(len(self.lines))
        return len(self.lines)


    def parseFile(self):
        numLine = len(self.lines)
        for n in range(numLine):
            line = self.lines[n]
            if line[0] == "#":
                self.manageLine(n)


    def manageLine(self, n):
        lineInfo = self.lines[n]
        lineLink = self.lines[n+1]
        if lineInfo != "#EXTM3U":
            m = re.search("tvg-id=\"(.*?)\"", lineInfo)
            id = m.group(1)
            m = re.search("tvg-name=\"(.*?)\"", lineInfo)
            name = m.group(1)
            m = re.search("tvg-logo=\"(.*?)\"", lineInfo)
            logo = m.group(1)
            m = re.search("group-title=\"(.*?)\"", lineInfo)
            group = m.group(1)
            m = re.search("tvg-chno=\"(.*?)\"", lineInfo)
            chno = m.group(1)
            m = re.search("tvh-chnum=\"(.*?)\"", lineInfo)
            chnum = m.group(1)
            m = re.search("[,](?!.*[,])(.*?)$", lineInfo)
            title = m.group(1)
            # logger.debug(id+"||"+name+"||"+logo+"||"+group+"||"+chno+"||"+chnum+"||"+title)
            
            track = {
                "title": title,
                "tvg-name": name,
                "tvg-ID": id,
                "tvg-logo": logo,
                "tvg-group": group,
                "tvg-chno": chno,
                "tvg-chnum": chnum,
                "titleFile": os.path.basename(lineLink),
                "link": lineLink
            }
            self.tracks.append(track)


def get_m3u_channels(m3u_url) -> list:
    channel_names = []
    try:
        response = requests.get(m3u_url, timeout=30)
        # logger.info(f'get_m3u_channels() : {response.status_code} / {response.reason}')
        response.raise_for_status()
        channel_names += [track['tvg-name'] for track in M3uParser(response.text).readM3u()]
        return channel_names
    except requests.exceptions.HTTPError:
        raise
    except Exception:
        logger.exception(f'm3u 로부터 채널 이름을 가져오는 중 예외: {m3u_url}')
        

def make_directory(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        logger.exception(f"Error: Failed to make the {path}.")


def delete_directory(path):
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
            ModelSetting.set('epg_updated_time', '')
            logger.info(f"설정 폴더 삭제 : {path}")
        else:
            logger.info(f"폴더가 없습니다 : {path}")
    except OSError:
        logger.exception(f"Error: Failed to delete the {path}.")


def delete_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
            P.logger.info(f"파일 삭제 : {path}")
    except OSError:
        logger.exception(f"Error: Failed to delete the {path}.")


def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e: 
        logger.exception(f'Exception:{str(e)}')


def save_json(path, json_data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            txt = json.dumps(json_data, ensure_ascii=False, indent=2)
            txt = re.sub(r",\n\s{8}\"", ', "', txt)
            txt = re.sub(r"\s{6}{\s+(.*)\s+}", r"      { \g<1> }", txt)
            f.write(txt)
    except Exception as e: 
        logger.exception(f'Exception:{str(e)}')


def load_yaml(file):
    try:
        return yaml.load(file, Loader=Loader)
    except TypeError:
        with open(file, "r", encoding='utf-8') as fp:
            return yaml.load(fp, Loader=Loader)


def get_wavve_proxy() -> str:  
    try:      
        support_site = FRAMEWORK.PluginManager.get_plugin_instance('support_site')
        use_proxy = support_site.ModelSetting.get_bool('site_wavve_use_proxy')
        proxy_url = support_site.ModelSetting.get('site_wavve_proxy_url')
        return use_proxy and proxy_url or ""    
    except Exception as e:
        logger.exception(f"get_wavve_proxy : {str(e)}")


def print_log(line):
    pattern = "([0-9]+)/*([0-9]+)/*([0-9]+)\s*([0-9]+):*([0-9]+):*([0-9]+)\s"
    try:
        # logger.error(line[:].strip()) 
        if re.search(pattern, line) == None:
            logger.error(line[:].strip())                 
        else:           
            logger.info(line[29:].strip())        
    except Exception as e:
        logger.exception(f"Exception: {str(e)}")

def get_m3u_tracks(m3u_url) -> list:
    tracks = []
    try:
        response = requests.get(m3u_url, timeout=30)
        # logger.info(f'get_m3u_channels() : {response.status_code} / {response.reason}')
        response.raise_for_status()
        tracks = M3uParser(response.text).readM3u()
        return tracks
    except requests.exceptions.HTTPError:
        raise
    except Exception:
        logger.exception(f'm3u 로부터 채널 이름을 가져오는 중 예외: {m3u_url}')

class MYEPG:

    @classmethod
    def epg_update_script(cls):
        try:
            logger.info('epg_update_script start()')
            
            plugin_path = os.path.dirname(__file__)
            file_folder_path = os.path.join(plugin_path, 'file')
            epg2xml_json_path = os.path.join(file_folder_path, 'epg2xml.json')
            channel_json_path = os.path.join(file_folder_path, 'Channel.json') 
            xmltv_xml_path = os.path.join(file_folder_path, 'xmltv.xml')

            # delete_directory(file_folder_path)
            make_directory(file_folder_path)
            cls.check_epg2xml(epg2xml_json_path)  

            cls.set_wavve_providers(epg2xml_json_path)
            cls.update_channels(epg2xml_json_path, channel_json_path)
            
            if cls.check_channels(channel_json_path):
                cls.set_my_channels(epg2xml_json_path, channel_json_path)
                delete_file(xmltv_xml_path)
                cls.make_xmltv(epg2xml_json_path, channel_json_path, xmltv_xml_path)                
            else:
                logger.error('No channel.json file')

            logger.info('epg_update_script() end')
        except requests.exceptions.HTTPError:
            raise          
        except Exception as e: 
            logger.exception(f'Exception:{str(e)}')


    @classmethod
    def set_wavve_providers(cls, epg2xml_path):
        try:
            logger.info('set_wavve_providers() start')
            epg2xml_json = load_json(epg2xml_path)

            if 'WAVVE' in epg2xml_json.keys():
                if ModelSetting.get_bool('block_wavve'):
                    epg2xml_json['WAVVE']['ENABLED'] = False
                    epg2xml_json['WAVVE']['HTTP_PROXY'] = None
                    epg2xml_json['WAVVE']['MY_CHANNELS'] = []
                    if 'WAVVE' in providers: providers.remove('WAVVE')
                    if 'WAVVE' in priority: priority.remove('WAVVE')
                else:
                    epg2xml_json['WAVVE']['ENABLED'] =  True                            
                    epg2xml_json['WAVVE']['HTTP_PROXY'] = proxy if (proxy := get_wavve_proxy()) != '' else None
                    epg2xml_json['WAVVE']['MY_CHANNELS'] = []
                    if 'WAVVE' not in providers: providers.insert(5, 'WAVVE')
                    if 'WAVVE' not in priority: priority.insert(0, 'WAVVE')

            save_json(epg2xml_path, epg2xml_json)

            logger.info('set_wavve_providers() end')
        except Exception as e: 
            logger.exception(f'Exception:{str(e)}')


    @classmethod
    def set_my_channels(cls, epg2xml_path, channel_path):
        try:
            logger.info('set_my_channels() start')
            epg2xml_json = load_json(epg2xml_path)
            channel_json = load_json(channel_path)

            if not ModelSetting.get_bool('use_alive_m3u'):
                # 기존 방식 
                for provider in providers:
                    # logger.info(f'{provider} : {ModelSetting.get_bool(provider)}')
                    if ModelSetting.get_bool(provider):
                        epg2xml_json[provider]['MY_CHANNELS'] = channel_json[provider]['CHANNELS']
                    else:
                        epg2xml_json[provider]['MY_CHANNELS'] =[]
            else:
                # 2024-01-30 alive m3u 채널명으로 추가
                for provider in providers:
                    epg2xml_json[provider]['MY_CHANNELS'] = []
                    # logger.info(f'reset_my_channels() : {provider}')
                    
                url = ModelSetting.get('alive_m3uall_url').strip()
                # logger.info(url)
                m3u_channels = []
                m3u_channels = get_m3u_channels(url)

                # 중복제거  
                # (ex: MBN, TV CHOSUN, 채널A, 연합뉴스TV, YTN, SBS Biz, SBS M, MBN 플러스, LIFETIME, ANIBOX ...)
                m3u_channels = list(dict.fromkeys(m3u_channels))   
                # logger.info(m3u_channels)

                for p in priority:
                    for channel in channel_json[p]['CHANNELS']:
                        for channel_name in m3u_channels:
                            if channel['Name'] == channel_name:
                                # logger.info(f"priority: {p} : {channel_name}")
                                epg2xml_json[p]['MY_CHANNELS'].append(channel)
                                m3u_channels.remove(channel_name)

                logger.info(f'EPG 정보 없는 채널 : {m3u_channels}')


            save_json(epg2xml_path, epg2xml_json)
            
            logger.info('set_my_channels() end')
        except requests.exceptions.HTTPError:
            raise            
        except Exception as e: 
            logger.exception(f'Exception:{str(e)}')


    @classmethod
    def add_ids_to_missing_channel(cls, key, value, epg2xml_list, channel_list):
        try: 
            for p in priority:
                for channel in channel_list[p]['CHANNELS']:
                    if channel['Name'] == value:        # EBS2, KBS1, KBS2
                        channel['Id'] = key             # EBS 2, 1TV, 2TV
                        logger.info(channel)
                        epg2xml_list[p]['MY_CHANNELS'].append(channel)
                        return 
        except Exception as e: 
            logger.exception(f'Exception: {str(e)}')


    @classmethod
    def check_epg2xml(cls, epg2xml_path):
        try: 
            if not os.path.exists(epg2xml_path):  
                logger.info(f'checkEpg2xml {epg2xml_path} 생성')
                cls.make_epg2xml(epg2xml_path)
        except Exception as e: 
            logger.exception(f'Exception: {str(e)}')


    @classmethod
    def check_channels(cls, channel_path):
        try:
            if os.path.exists(channel_path):
                return True
            else:
                return False
        except Exception as e:
            logger.exception(f"Exception: {str(e)}")
        

    @classmethod
    def make_epg2xml(cls, epg2xml_path):
        logger.info("make_epg2xml() start")

        # os.chdir(os.path.join(os.path.dirname(__file__), 'epg2xml'))
        # command = ['python', '-m', 'epg2xml', 'run', '--config', epg2xml_path, '--parallel']
        command = ['epg2xml', 'run', '--config', epg2xml_path, '--parallel']
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            for line in proc.stderr:
                print_log(line)

        logger.info('make_epg2xml() end')


    @classmethod
    def update_channels(cls, epg2xml_path, channel_path):
        P.logger.info('update_channels() start')

        # os.chdir(os.path.join(os.path.dirname(__file__), 'epg2xml'))
        # command = ['python', '-m', 'epg2xml', 'update_channels', '--config', epg2xml_path, '--channelfile', channel_path, '--parallel']
        command = ['epg2xml', 'update_channels', '--config', epg2xml_path, '--channelfile', channel_path, '--parallel']
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            for line in proc.stderr:
                print_log(line)

        P.logger.info('update_channels() end')


    @classmethod
    def make_xmltv(cls, epg2xml_path, channel_path, xml_path):
        logger.info('make_xmltv() start')

        # os.chdir(os.path.join(os.path.dirname(__file__), 'epg2xml'))
        # command = ['python', '-m', 'epg2xml', 'run', '--config', epg2xml_path, '--channelfile', channel_path, '--xmlfile', xml_path, '--parallel']
        command = ['epg2xml', 'run', '--config', epg2xml_path, '--channelfile', channel_path, '--xmlfile', xml_path, '--parallel']
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            for line in proc.stderr:
                print_log(line)
                
            if ModelSetting.get_bool('use_alive_plex_proxy'):
                alive = FRAMEWORK.PluginManager.get_plugin_instance('alive')
                if alive.ModelSetting.get_bool("use_plex_proxy"):
                    cls.create_dummy_epg(xml_path)

            ModelSetting.set('epg_updated_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        logger.info('make_xmltv() end')
        
    @classmethod
    def create_dummy_epg(cls, xml_path):
        logger.info('create_dummy_epg() start')
        
        try:
            ddns = SystemModelSetting.get("ddns").strip()
            lineup_url = f"{ddns}/alive/proxy/plex/lineup.json"
            #logger.info(f"lineup.json URL: {lineup_url}")

            # lineup.json 요청 및 파싱
            response = requests.get(lineup_url, timeout=30)
            response.raise_for_status()
            lineup_data = response.json()

            # XML 파싱
            tree = ET.parse(xml_path)
            root = tree.getroot()
    
            # 대소문자 구분 없이 매핑 (ID, GuideName 모두 lower() 처리)
            existing_channels = {channel.get('id').lower(): channel for channel in root.findall('channel')}
            name_to_channel = {}
            for channel in root.findall('channel'):
                name_elem = channel.find('display-name')
                if name_elem is not None and name_elem.text:
                    name = name_elem.text.lower()
                    name_to_channel[name] = channel
    
            processed_ids = set()
            processed_names = set()
    
            # 1단계: tvg-id (대소문자 무시)
            for item in lineup_data:
                channel_id = item['tvg-id'].lower()  # 소문자로 변환
                if channel_id in existing_channels:
                    channel = existing_channels[channel_id]
                    cls.update_exist_channel(channel, item)
                    processed_ids.add(channel_id)
                    processed_names.add(item['GuideName'].lower())  # 소문자로 저장
    
            # 2단계: GuideName (대소문자 무시)
            for item in lineup_data:
                guide_name_lower = item['GuideName'].lower()
                if guide_name_lower in processed_names:
                    continue
                if guide_name_lower in name_to_channel:
                    channel = name_to_channel[guide_name_lower]
                    cls.update_exist_channel(channel, item)
                    processed_names.add(guide_name_lower)
                    processed_ids.add(channel.get('id').lower())
                    
            if ModelSetting.get_bool('use_dummy_epg'):
                # 3단계: 신규 채널 생성
                for item in lineup_data:
                    channel_id_lower = item['tvg-id'].lower()
                    guide_name_lower = item['GuideName'].lower()
                    if channel_id_lower not in processed_ids and guide_name_lower not in processed_names:
                        cls.create_dummy_channel(root, item)
                        cls.create_dummy_programme(
                            root,
                            item,
                            title=item['GuideName']
                        )

    
            tree.write(xml_path, encoding='utf-8', xml_declaration=True)
            logger.info("XML 업데이트 완료")
    
        except Exception as e:
            logger.exception(f'Exception:{str(e)}')
        
        logger.info('create_dummy_epg() end')
    
    @classmethod
    def update_exist_channel(cls, channel, item):
        cls._set_channel_display_names(channel, item)
    
    @classmethod
    def create_dummy_channel(cls, root, item):
        # provider = item['tvg-id'].split('.')[1].lower() if '.' in item['tvg-id'] else 'UNKNOWN'
        new_channel = ET.Element('channel', id=item['tvg-id'])  # 원본 tvg-id 유지
        cls._set_channel_display_names(new_channel, item)
        root.append(new_channel)

    @classmethod
    def _set_channel_display_names(cls, channel, item):
        # 기존 display-name 제거

        removed_count = 0
        while True:
            dn = channel.find('display-name')
            if dn is None:
                break
            channel.remove(dn)
            removed_count += 1
        # logger.info(f"Removed {removed_count} display-name tags for {item['tvg-id']}")
            
        # provider = item['tvg-id'].split('.')[1].lower() if '.' in item['tvg-id'] else 'UNKNOWN'
        
        # 새 display-name 추가
        ET.SubElement(channel, 'display-name').text = item['GuideName']
        # tivimate에서 sbs 채널 epg 충돌
        # ET.SubElement(channel, 'display-name').text = provider
        ET.SubElement(channel, 'display-name').text = item['GuideNumber']
        ET.SubElement(channel, 'display-name').text = f"{item['GuideNumber']} {item['GuideName']}"
        # ET.SubElement(channel, 'display-name').text = f"{item['GuideNumber']} {provider}"

    @classmethod
    def create_dummy_programme(cls, root, item, title="방송 정보 없음", desc="방송 정보 없음", rating="전체 관람가"):
        # 현재 시각 (KST)
        now = datetime.now()
        start = (now - timedelta(hours=1)).strftime('%Y%m%d%H%M%S') + " +0900"
        stop = (now + timedelta(days=1)).strftime('%Y%m%d%H%M%S') + " +0900"

        # <programme> 태그 생성
        programme = ET.Element('programme', {
            'start': start,
            'stop': stop,
            'channel': item['tvg-id']
        })
    
        # <title lang="ko">...</title>
        title_elem = ET.SubElement(programme, 'title', {'lang': 'ko'})
        title_elem.text = title
    
        # <desc lang="ko">...</desc>
        desc_elem = ET.SubElement(programme, 'desc', {'lang': 'ko'})
        desc_elem.text = desc
    
        # <rating system="KMRB"><value>...</value></rating>
        rating_elem = ET.SubElement(programme, 'rating', {'system': 'KMRB'})
        value_elem = ET.SubElement(rating_elem, 'value')
        value_elem.text = rating
    
        # <programme> 추가
        root.append(programme)



