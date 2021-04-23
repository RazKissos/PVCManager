from discord import Status
import configparser
import os

class BotData:
    BOT_NAME = str()
    TOKEN = str()
    BOT_PREFIX = str()
    STATUS = Status.online

    def read_config_data(self, path: str):
        """
        Reads the bot config info from the config file and stores it in the BotData class.

        @param path: path to config file.
        @type path: str
        """
        cfg_parser = configparser.ConfigParser()
        if os.path.exists(path):
            cfg_parser.read(path)
        else:
            raise Exception("config file path does not exist!")
        self.BOT_PREFIX = cfg_parser['data']['prefix']
        self.TOKEN = cfg_parser['data']['token']
    
    def read_json(self, path:str):
        """
        Makes sure the json file exists, if it doesn't exist the program will creat it itself.
        
        @param path: path to a specific json file.
        @type path: str 
        """
        # Create file, if already exists then nothing happens.
        if not os.path.exists(path):
            creator = open(path, 'w+')
            creator.close()
        
        # File must exist.
        f = open(path, 'r') 
        f_str = f.read()
        # Check if contains valid json.
        if len(f_str) >= 2:
            if "{" != f_str[0] or "}" != f_str[-1]:
                writer = open(path, 'w')
                writer.write("{}")
                writer.close()
        else:
            # No valid json, override with empty json.
            writer = open(path, 'w')
            writer.write("{}")
            writer.close()

        f.close()