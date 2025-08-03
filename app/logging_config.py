import logging
import os

LOG_DIR = "/home/ec2-user/email-pipeline/logs"
os.makedirs(LOG_DIR, exist_ok = True)

def setup_logging () :
    fmt = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    formatter = logging.Formatter(fmt)

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    
    # main.py logger (system logger)
    root_handler = logging.FileHandler(os.path.join(LOG_DIR, "webhook.log"))
    root_handler.setLevel(logging.DEBUG)
    root_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(root_handler)

    # utils.py logger (email logger)
    email_handler = logging.FileHandler(os.path.join(LOG_DIR, "email.log"))
    email_handler.setLevel(logging.DEBUG)
    email_handler.setFormatter(formatter)
    email_logger = logging.getLogger("email")
    email_logger.setLevel(logging.DEBUG)
    email_logger.addHandler(email_handler)
    email_logger.propagate = False

    # gpt_utils.py logger (gpt logger)
    gpt_handler = logging.FileHandler(os.path.join(LOG_DIR, "gpt.log"))
    gpt_handler.setLevel(logging.DEBUG)
    gpt_handler.setFormatter(formatter)
    gpt_logger = logging.getLogger("gpt")
    gpt_logger.setLevel(logging.DEBUG)
    gpt_logger.addHandler(gpt_handler)
    gpt_logger.propagate = False
