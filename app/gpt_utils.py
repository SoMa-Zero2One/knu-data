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
    
    school_list_path = DATA_DIR / f"{school_name}_list.json"
    with open(school_list_path, encoding = "utf-8") as f :
        BASE_SCHOOL_LIST = json.load(f)
    
    base_json = json.dumps(BASE_SCHOOL_LIST, ensure_ascii=False)
    choices_json = json.dumps(choice_list, ensure_ascii=False)

    prompt_path = DATA_DIR / "prompt.txt"
    with open(prompt_path, encoding = "utf-8") as f :
        prompt = f.read().format(base = base_json, choices = choices_json)

    try : 
        # for openai api network error
        response = openai.chat.completions.create(
            model = "gpt-4.1-mini",
            messages = [
                {"role" : "system", "content" : "You standardize university names."},
                {"role" : "user",   "content" : prompt}
            ],
            temperature = 0
        )
        
        content = response.choices[0].message.content

        # for split error
        return_list = content.split("\n")
        logger.debug(f"[Standardize Universities] : {return_list}")
    
        return return_list
        
    except Exception as e :
        logger.error(f"[Standardize Universities] : {e}")
        return e 