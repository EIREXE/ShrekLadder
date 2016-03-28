import configparser, os

config_parser = configparser.ConfigParser()
config_parser.readfp(open('config.ini'))
config = lambda a: config_parser.get('config', a)
configi = lambda a: config_parser.getint('config', a)