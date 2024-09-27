import json 
import requests
from bs4 import BeautifulSoup
from state import AgentGraphState
from langchain_core.messages import HumanMessage
import jsonschema

def is_garbled(text):
    # A simple heuristic to detect garbled text: high proportion of non-ASCII characters
    non_ascii_count = sum(1 for char in text if ord(char) > 127)
    return non_ascii_count > len(text) * 0.3

def clean_text(text):
    # Remove or replace problematic characters
    return ''.join(char for char in text if ord(char) < 128)

def validate_json(json_data):
    schema = {
        "type": "object",
        "properties": {
            "source": {"type": "string"},
            "content": {"type": "string"}
        },
        "required": ["source", "content"]
    }
    try:
        jsonschema.validate(instance=json_data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError:
        return False

def scrape_website(state: AgentGraphState, research=None):
    research_data = research().content
    try:
        research_data = json.loads(research_data)
    except json.JSONDecodeError:
        error_message = "Error: Invalid JSON in research data"
        state["scraper_response"].append(HumanMessage(role="system", content=error_message))
        return {"scraper_response": state["scraper_response"]}

    try:
        url = research_data["selected_page_url"]
    except KeyError as e:
        url = research_data["error"]

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text content
        texts = soup.stripped_strings
        content = " ".join(texts)
        
        # Check for garbled text
        if is_garbled(content):
            content = "error in scraping website, garbled text returned"
        else:
            # Limit the content to 4000 characters
            content = content[:4000]
        content = clean_text(content)
        scraped_data = {"source": url, "content": content}
        
        if not validate_json(scraped_data):
            raise ValueError("Invalid JSON structure in scraped data")
        
        state["scraper_response"].append(HumanMessage(role="system", content=str({"source": url, "content": content})))
        
        return {"scraper_response": state["scraper_response"]}
    
    except requests.HTTPError as e:
        if e.response.status_code == 403:
            content = f"error in scraping website, 403 Forbidden for url: {url}"
        else:
            content = f"error in scraping website, {str(e)}"
        
        state["scraper_response"].append(HumanMessage(role="system", content=str({"source": url, "content": content})))
        return {"scraper_response": state["scraper_response"]}
    except requests.RequestException as e:
        content = f"error in scraping website, {str(e)}"
        state["scraper_response"].append(HumanMessage(role="system", content=str({"source": url, "content": content})))
        return {"scraper_response": state["scraper_response"]}
    except UnicodeEncodeError as e:
        content = f"Error encoding scraped content: {str(e)}. Attempting to clean text."
        cleaned_content = clean_text(content)
        message_content = json.dumps({"source": url, "content": cleaned_content}, ensure_ascii=False)
        state["scraper_response"].append(HumanMessage(role="system", content=message_content))
        return {"scraper_response": state["scraper_response"]}
