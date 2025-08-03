import os, json
import openai
from dotenv import load_dotenv
from pathlib import Path
import logging

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger("gpt")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def standardize_universities (choice_list : list[str], school_name : str) -> list[str] :

    logger.debug(f"[Standardize Universities] : {choice_list}")
    
    SCHOOL_LIST_PATH = DATA_DIR / f"{school_name}_list.json"
    
    with open(SCHOOL_LIST_PATH, encoding = "utf-8") as f :
        BASE_SCHOOL_LIST = json.load(f)
    
    base_json = json.dumps(BASE_SCHOOL_LIST, ensure_ascii=False)
    choices_json = json.dumps(choice_list, ensure_ascii=False)

    with open(DATA_DIR / "prompt.txt", encoding = "utf-8") as f :
        prompt = f.read().format(base = base_json, choices = choices_json)

    response = openai.chat.completions.create(
        model = "gpt-4.1-mini",
        messages = [
            {"role" : "system", "content" : "You standardize university names."},
            {"role" : "user",   "content" : prompt}
        ],
        temperature = 0
    )
    
    content = response.choices[0].message.content
    
    return_list = content.split("\n")
    
    logger.debug(f"[Standardize Universities] : {return_list}")
    
    try :
        return return_list
    
    except Exception as e :
        logger.error(f"[Standardize Universities] : {e}")
        return choice_list
