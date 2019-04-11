import os
import confuse

appName = 'ZombieProjectsWatcher'
os.environ[appName.upper()+'DIR'] = '.'
CONFIG = confuse.Configuration(appName, __name__)
