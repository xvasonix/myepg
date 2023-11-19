import os
import subprocess
from .setup import P


package_dir = os.path.join(os.path.dirname(__file__), 'epg2xml')
P.logger.debug(f'epg2xml package directory : {package_dir}')

try:
    if os.path.exists(package_dir) and os.path.exists(os.path.join(package_dir, '.git')):
        command = ['git', '-C', package_dir, 'reset', '--hard', 'HEAD']
        ret = subprocess.run(command, capture_output=True, text=True)
        P.logger.debug(ret.stdout.rstrip())
        command = ['git', '-C', package_dir, 'pull']
        ret = subprocess.run(command, capture_output=True, text=True)
        P.logger.debug(ret.stdout.rstrip())
        P.logger.info('epg2xml is installed')
    else:
        P.logger.info('epg2xml is not installed')
        os.system(f"git clone https://github.com/epg2xml/epg2xml.git {package_dir}")
        P.logger.info('epg2xml package installation completed')
except Exception as e:
    P.logger.exception(f'epg2xml is not installed {str(e)}')
    os.system(f"git clone https://github.com/epg2xml/epg2xml.git {package_dir}")
    P.logger.info('epg2xml package installation completed')
    # os.system(f"pip install {cur_dir}")


try:
    from bs4 import BeautifulSoup
    P.logger.info('bs4 is installed')
except Exception as e:
    P.logger.exception(f'BeautifulSoup is not installed {str(e)}')
    os.system("pip install beautifulsoup4>=4.8")


try:
    import requests
    P.logger.info('requests is installed')
except Exception as e:
    P.logger.exception(f'requests is not installed {str(e)}')
    os.system("pip install requests")     
    