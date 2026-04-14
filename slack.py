from src.core.process import Process
from src.utils import config
version = "2.0.0"

if __name__ == '__main__':
    print("Version " + version)
    settings = config.read()
    for setting in settings:
        Process(setting).run()
