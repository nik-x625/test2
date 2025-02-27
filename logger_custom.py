import logging
import yaml

def get_module_logger(mod_name):
    
    # this part needs optimisation
    with open("/opt/qlines_app/config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    
    logger = logging.getLogger(mod_name)
    logger.setLevel(logging.DEBUG)
    log_file_path =cfg["logger"]["log_file_path"]
    handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def get_module_logger_btc(mod_name):
    
    logger = logging.getLogger(mod_name)
    logger.setLevel(logging.DEBUG)
        
    handler = logging.FileHandler('/opt/qlines_app/btc.log')
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


if __name__=='__main__':
    loggerx = get_module_logger(__name__)
    loggerx.debug('test')

    
