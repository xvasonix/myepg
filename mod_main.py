from tool import ToolUtil
from flask import send_file, jsonify, render_template
from .setup import *
from .myepg_handle import MYEPG
import os, traceback


class ModuleMain(PluginModuleBase):

    def __init__(self, P):
        super(ModuleMain, self).__init__(P, name='main', first_menu='setting', scheduler_desc="epg2xml API")
        self.db_default = {
            f'{self.name}_db_version' : '1',
            f'{self.name}_auto_start' : 'False',
            f'{self.name}_interval' : '0 3 * * *',
            f'{self.name}_A1': 'False',
            f'{self.name}_KT': 'False',
            f'{self.name}_LG': 'False',
            f'{self.name}_SK': 'False',
            f'{self.name}_DAUM': 'False',
            f'{self.name}_NAVER': 'False',
            f'{self.name}_WAVVE': 'False',
            f'{self.name}_TVING': 'False',
            f'{self.name}_SPOTV': 'False',
            f'{self.name}_match': 'False',
            f'epg_updated_time': '',
        }


    def process_menu(self, sub, req):
        arg = P.ModelSetting.to_dict()
        arg['api_epgall'] = ToolUtil.make_apikey_url(f"/{P.package_name}/api/epgall")
        if sub == 'setting':
            arg['is_include'] = F.scheduler.is_include(self.get_scheduler_name())
            arg['is_running'] = F.scheduler.is_running(self.get_scheduler_name())
        return render_template(f'{P.package_name}_{self.name}_{sub}.html', arg=arg)
    
    
    def process_command(self, command, arg1, arg2, arg3, req):
        ret = {'ret':'success'}
        if command == 'delete_setting_file':
            P.logger.info('delete_setting_file')
            MYEPG.deleteDirectory(f"{os.path.dirname(__file__)}/file")
            # P.logger.info(f"설정 파일 삭제 : {file_folder_path}")
            ret = {f'ret':'success', 'msg':'삭제 명령을 전달하였습니다.'}
        elif command == 'make_epg':
            P.logger.info('make_epg')
            # epg_updated_time = P.ModelSetting.get('epg_updated_time')
            # ret = {'ret':'success', 'msg':epg_updated_time}
            MYEPG.epg_update_script()
            ret = {'ret':'success', 'msg':'생성을 시작합니다.'}
        return jsonify(ret)


    def process_api(self, sub, req):
        try:
            if sub == 'epgall':
                xmltv_path = os.path.join(os.path.dirname(__file__), 'file', 'xmltv.xml')
                return send_file(xmltv_path, mimetype='application/xml')
        except Exception as e: 
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())


    def scheduler_function(self):
        try:
            MYEPG.epg_update_script()            
        except Exception as e:
            P.logger.error(f'Exception:{str(e)}')
            P.logger.error(traceback.format_exc())