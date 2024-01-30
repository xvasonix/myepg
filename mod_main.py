from tool import ToolUtil
from flask import send_file, jsonify, render_template, abort
from .setup import P
from .myepg_handle import MYEPG, delete_directory
import os, traceback
from plugin import F, PluginModuleBase  


logger = P.logger
package_name = P.package_name
ModelSetting = P.ModelSetting
scheduler = F.scheduler


class ModuleMain(PluginModuleBase):

    def __init__(self, P):
        super(ModuleMain, self).__init__(P, name='main', first_menu='setting', scheduler_desc="epg2xml API")
        self.db_default = {
            f'{self.name}_db_version' : '1',
            f'{self.name}_auto_start' : 'False',
            f'{self.name}_interval' : '0 3 * * *',
            'KT': 'False',
            'LG': 'False',
            'SK': 'False',
            'DAUM': 'False',
            'NAVER': 'False',
            'WAVVE': 'False',
            'TVING': 'False',
            'SPOTV': 'False',
            'block_wavve': 'False',
            'use_alive_m3u': 'False',
            'epg_updated_time': '',
            'alive_m3uall_url': ToolUtil.make_apikey_url(f"/alive/api/m3uall"),
            # 'match_m3u_epg': 'False',
        }


    def process_menu(self, sub, req):
        arg = ModelSetting.to_dict()
        arg['api_epgall'] = ToolUtil.make_apikey_url(f"/{package_name}/api/epgall")
        if sub == 'setting':
            arg['is_include'] = scheduler.is_include(self.get_scheduler_name())
            arg['is_running'] = scheduler.is_running(self.get_scheduler_name())

        return render_template(f'{package_name}_{self.name}_{sub}.html', arg=arg)

    
    def process_command(self, command, arg1, arg2, arg3, req):
        ret = {'ret':'success'}
        if command == 'delete_setting_file':
            file_folder_path = os.path.join(os.path.dirname(__file__), 'file')
            delete_directory(file_folder_path)
            ret = {f'ret':'success', 'msg':'삭제 명령을 전달하였습니다.'}
        elif command == 'make_epg':
            logger.info('make_epg')
            MYEPG.epg_update_script()
            updated_time = ModelSetting.get('epg_updated_time')
            ret = {'ret':'success', 'updated_time': updated_time, 'msg':'생성을 시작합니다.'}
        return jsonify(ret)


    def process_api(self, sub, req):
        try:
            if sub == 'epgall':
                xmltv_path = os.path.join(os.path.dirname(__file__), 'file', 'xmltv.xml')
                return send_file(xmltv_path, mimetype='application/xml')
        except Exception as e: 
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())


    def scheduler_function(self):
        try:
            MYEPG.epg_update_script()            
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
