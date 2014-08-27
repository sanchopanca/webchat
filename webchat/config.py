import ConfigParser
import os.path


INI_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        os.path.pardir, 'config.ini')

conf = ConfigParser.ConfigParser()
conf.readfp(open(INI_FILE))

DB_FILE = conf.get('global', 'data_base')
