from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import json
import sys
import re
import requests
import os
import time
import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('facebook_scraper')

def clean_text(text):
    """Clean text with robust Unicode support"""
    if not text or not isinstance(text, str):
        return ""
    
    # Handle text cleaning more robustly with proper Unicode support
    try:
        # First attempt to clean Facebook's Unicode escape sequences
        text = text.encode('utf-8').decode('unicode_escape')
    except UnicodeError:
        # If that fails, just use the original text
        pass
    
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_date_time(text):
    """Extract date and time from text using various patterns"""
    # Try to find date in format "Month Day, Year at Time"
    date_time_pattern = re.compile(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\s+(?:at|@)\s+(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))', re.IGNORECASE)
    date_match = date_time_pattern.search(text)
    
    if date_match:
        date_time_str = date_match.group(0)
        # Try to parse this into start_time and end_time
        try:
            # Extract just the date part
            date_part = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}', date_time_str, re.IGNORECASE).group(0)
            # Extract just the time part
            time_part = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))', date_time_str, re.IGNORECASE).group(0)
            
            # Format for Lu.ma API (ISO format)
            date_obj = datetime.datetime.strptime(f"{date_part} {time_part}", "%B %d, %Y %I:%M %p")
            start_time = date_obj.isoformat()
            
            # Default end time is 2 hours after start
            end_time = (date_obj + datetime.timedelta(hours=2)).isoformat()
            
            return date_part, time_part, start_time, end_time
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse date/time: {e}")
    
    # If we couldn't extract structured date/time, just return the raw matches
    date_pattern = re.compile(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}', re.IGNORECASE)
    time_pattern = re.compile(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)(?:\s*[-–]\s*\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))?)', re.IGNORECASE)
    
    date_match = date_pattern.search(text)
    time_match = time_pattern.search(text)
    
    date_str = date_match.group(0) if date_match else "No date found"
    time_str = time_match.group(0) if time_match else "No time found"
    
    return date_str, time_str, None, None

def get_event_data(driver, url):
    """Extract data from a Facebook event page"""
    logger.info(f"Scraping event: {url}")
    
    try:
        driver.get(url)
        # Wait for the body to be present
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Scroll down to load more content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
    except TimeoutException:
        logger.error(f"Timeout waiting for page to load: {url}")
        return {
            "title": "Error loading page",
            "description": "Timeout waiting for page to load",
            "url": url
        }
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Initialize data structure with default values
    data = {
        "title": "No title found",
        "description": "No description found",
        "date": "No date found",
        "time": "No time found",
        "start_time": None,
        "end_time": None,
        "location": "No location found",
        "address": "",
        "organizer": "No organizer found",
        "ticket_link": "",
        "image_url": "",
        "url": url
    }
    
    # Try to extract from JSON-LD (most reliable when available)
    script_tags = soup.find_all("script", type="application/ld+json")
    json_ld_found = False
    
    for script in script_tags:
        try:
            json_data = json.loads(script.string)
            if isinstance(json_data, list):
                for item in json_data:
                    if item.get("@type") == "Event":
                        json_ld_found = True
                        data["title"] = clean_text(item.get("name", data["title"]))
                        data["description"] = clean_text(item.get("description", data["description"]))
                        
                        # Handle dates
                        if item.get("startDate"):
                            data["start_time"] = item.get("startDate")
                            data["date"] = item.get("startDate").split("T")[0] if "T" in item.get("startDate") else item.get("startDate")
                        
                        if item.get("endDate"):
                            data["end_time"] = item.get("endDate")
                            
                        # Handle location
                        if isinstance(item.get("location"), dict):
                            data["location"] = item.get("location", {}).get("name", data["location"])
                            if item.get("location", {}).get("address"):
                                if isinstance(item["location"]["address"], dict):
                                    data["address"] = item["location"]["address"].get("streetAddress", "")
                                else:
                                    data["address"] = str(item["location"]["address"])
                        
                        # Handle organizer
                        if isinstance(item.get("organizer"), dict):
                            data["organizer"] = item.get("organizer", {}).get("name", data["organizer"])
                        elif isinstance(item.get("organizer"), list) and len(item["organizer"]) > 0:
                            if isinstance(item["organizer"][0], dict):
                                data["organizer"] = item["organizer"][0].get("name", data["organizer"])
                        
                        # Handle image
                        if item.get("image"):
                            if isinstance(item["image"], list) and len(item["image"]) > 0:
                                data["image_url"] = item["image"][0]
                            else:
                                data["image_url"] = item["image"]
                        
                        # Handle URL
                        if item.get("url"):
                            data["url"] = item["url"]
                        
                        # Handle ticket link
                        if item.get("offers") and isinstance(item["offers"], list):
                            for offer in item["offers"]:
                                if offer.get("url"):
                                    data["ticket_link"] = offer["url"]
                                    break
                        break
            elif json_data.get("@type") == "Event":
                json_ld_found = True
                data["title"] = clean_text(json_data.get("name", data["title"]))
                data["description"] = clean_text(json_data.get("description", data["description"]))
                
                # Handle dates
                if json_data.get("startDate"):
                    data["start_time"] = json_data.get("startDate")
                    data["date"] = json_data.get("startDate").split("T")[0] if "T" in json_data.get("startDate") else json_data.get("startDate")
                
                if json_data.get("endDate"):
                    data["end_time"] = json_data.get("endDate")
                    
                # Handle location
                if isinstance(json_data.get("location"), dict):
                    data["location"] = json_data.get("location", {}).get("name", data["location"])
                    if json_data.get("location", {}).get("address"):
                        if isinstance(json_data["location"]["address"], dict):
                            data["address"] = json_data["location"]["address"].get("streetAddress", "")
                        else:
                            data["address"] = str(json_data["location"]["address"])
                
                # Handle organizer
                if isinstance(json_data.get("organizer"), dict):
                    data["organizer"] = json_data.get("organizer", {}).get("name", data["organizer"])
                elif isinstance(json_data.get("organizer"), list) and len(json_data["organizer"]) > 0:
                    if isinstance(json_data["organizer"][0], dict):
                        data["organizer"] = json_data["organizer"][0].get("name", data["organizer"])
                
                # Handle image
                if json_data.get("image"):
                    if isinstance(json_data["image"], list) and len(json_data["image"]) > 0:
                        data["image_url"] = json_data["image"][0]
                    else:
                        data["image_url"] = json_data["image"]
                
                # Handle URL
                if json_data.get("url"):
                    data["url"] = json_data["url"]
                
                # Handle ticket link
                if json_data.get("offers") and isinstance(json_data["offers"], list):
                    for offer in json_data["offers"]:
                        if offer.get("url"):
                            data["ticket_link"] = offer["url"]
                            break
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON-LD: {url}")
            pass
    
    # If JSON-LD wasn't found or was incomplete, fall back to meta tags and DOM parsing
    if not json_ld_found or data["title"] == "No title found":
        # Extract title
        title_tag = soup.find("meta", property="og:title") or soup.find("title")
        if title_tag:
            data["title"] = clean_text(title_tag.get("content", title_tag.text) if title_tag.name == "meta" else title_tag.text)
    
    # Extract description
    if data["description"] == "No description found":
        desc_tag = soup.find("meta", property="og:description") or soup.find("meta", name="description")
        if desc_tag:
            data["description"] = clean_text(desc_tag.get("content"))
        else:
            # Try to find description in the page content
            desc_div = soup.find("div", string=re.compile("Details|About this event", re.IGNORECASE))
            if desc_div and desc_div.find_next("div"):
                data["description"] = clean_text(desc_div.find_next("div").text)
    
    # Extract image URL
    if not data["image_url"]:
        image_tag = soup.find("meta", property="og:image")
        if image_tag:
            data["image_url"] = image_tag.get("content")
        else:
            # Try to find the main event image
            event_image = soup.find("img", class_=re.compile("event.*image|cover.*image", re.IGNORECASE))
            if event_image:
                data["image_url"] = event_image.get("src")
    
    # Extract organizer
    if data["organizer"] == "No organizer found":
        # Look for "Hosted by" text
        for element in soup.find_all(string=re.compile("Hosted by|Organized by", re.IGNORECASE)):
            if element and element.find_next():
                next_element = element.find_next()
                if next_element.name == "a":
                    data["organizer"] = clean_text(next_element.text)
                    break
                elif next_element.find("a"):
                    data["organizer"] = clean_text(next_element.find("a").text)
                    break
        
        # If still not found, try other methods
        if data["organizer"] == "No organizer found":
            organizer_link = soup.find("a", href=re.compile(r"/pages/|/groups/|/profile\.php"))
            if organizer_link:
                data["organizer"] = clean_text(organizer_link.text)
    
    # Extract ticket link
    if not data["ticket_link"]:
        # Look for ticket links with common patterns
        ticket_patterns = ["ticket", "register", "sign up", "book", "rsvp", "join"]
        for pattern in ticket_patterns:
            ticket_link = soup.find("a", string=re.compile(pattern, re.IGNORECASE))
            if ticket_link:
                data["ticket_link"] = ticket_link.get("href")
                if not data["ticket_link"].startswith("http"):
                    data["ticket_link"] = "https://www.facebook.com" + data["ticket_link"]
                break
        
        # If still not found, look for buttons
        if not data["ticket_link"]:
            for pattern in ticket_patterns:
                ticket_button = soup.find("button", string=re.compile(pattern, re.IGNORECASE))
                if ticket_button and ticket_button.find_parent("a"):
                    data["ticket_link"] = ticket_button.find_parent("a").get("href")
                    if not data["ticket_link"].startswith("http"):
                        data["ticket_link"] = "https://www.facebook.com" + data["ticket_link"]
                    break
    
    # Extract date and time if not already found
    if not data["start_time"] or data["date"] == "No date found":
        # First try to find structured date/time elements
        date_time_div = soup.find("div", string=re.compile("Date and time|When", re.IGNORECASE))
        if date_time_div and date_time_div.find_next("div"):
            date_time_text = date_time_div.find_next("div").text
            date_str, time_str, start_time, end_time = extract_date_time(date_time_text)
            data["date"] = date_str
            data["time"] = time_str
            if start_time:
                data["start_time"] = start_time
            if end_time:
                data["end_time"] = end_time
        else:
            # Fall back to searching the entire page
            date_str, time_str, start_time, end_time = extract_date_time(driver.page_source)
            data["date"] = date_str
            data["time"] = time_str
            if start_time:
                data["start_time"] = start_time
            if end_time:
                data["end_time"] = end_time
    
    # Extract location if not already found
    if data["location"] == "No location found":
        # Try to find location elements
        location_div = soup.find("div", string=re.compile("Location|Where|Venue", re.IGNORECASE))
        if location_div and location_div.find_next("div"):
            data["location"] = clean_text(location_div.find_next("div").text)
        else:
            # Try regex patterns
            location_match = re.search(r"Location:\s*(.*?)(?:\n|<br>|</div>)", driver.page_source)
            if location_match:
                data["location"] = clean_text(location_match.group(1))
            else:
                # Look for address elements
                address_div = soup.find("div", string=re.compile("Address", re.IGNORECASE))
                if address_div and address_div.find_next("div"):
                    data["location"] = clean_text(address_div.find_next("div").text)
    
    # Clean up any remaining default values
    for key, value in data.items():
        if value in ["No title found", "No description found", "No date found", "No time found", "No location found", "No organizer found"]:
            if key == "title" and value == "No title found":
                # Title is critical - if we can't find it, try one more approach
                h1_tags = soup.find_all("h1")
                if h1_tags and len(h1_tags) > 0:
                    data[key] = clean_text(h1_tags[0].text)
            elif key == "organizer" and value == "No organizer found":
                # For organizer, use the page name if available
                page_name = soup.find("meta", property="og:site_name")
                if page_name:
                    data[key] = clean_text(page_name.get("content"))
    
    logger.info(f"Successfully scraped event: {data['title']}")
    return data

def get_page_events(driver, page_url):
    """Extract all event links from a Facebook page's events section"""
    logger.info(f"Scraping events page: {page_url}")
    
    try:
        driver.get(page_url)
        # Wait for the body to be present
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Scroll down a few times to load more events
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
    except TimeoutException:
        logger.error(f"Timeout waiting for page to load: {page_url}")
        return []
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    event_links = []
    
    # Look for links to individual events on the page
    for a_tag in soup.find_all("a", href=re.compile(r"/events/\d+")):
        href = a_tag.get("href", "")
        # Ensure it's an event link and not something else
        if "/events/" in href and "?event_time_id=" not in href:
            full_link = "https://www.facebook.com" + href if href.startswith("/") else href
            # Remove any query parameters
            full_link = full_link.split("?")[0]
            if full_link not in event_links:
                event_links.append(full_link)
    
    logger.info(f"Found {len(event_links)} event links on page")
    
    # Limit to maximum 10 events to prevent timeouts
    if len(event_links) > 10:
        logger.info(f"Limiting to 10 events to prevent timeouts")
        event_links = event_links[:10]
    
    events_data = []
    for link in event_links:
        try:
            event_data = get_event_data(driver, link)
            events_data.append(event_data)
        except Exception as e:
            logger.error(f"Error scraping event {link}: {str(e)}")
            # Add a placeholder for the failed event
            events_data.append({
                "title": "Error scraping event",
                "description": f"Failed to scrape event: {str(e)}",
                "url": link
            })
    
    return events_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No Facebook URL provided"}))
        sys.exit(1)

    facebook_url = sys.argv[1]
    logger.info(f"Processing URL: {facebook_url}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    
    try:
        service = Service(executable_path="/usr/local/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        if "/events/" in facebook_url and not facebook_url.endswith("/events") and not facebook_url.endswith("/events/"): 
            # Single event URL
            data = get_event_data(driver, facebook_url)
            print(json.dumps([data])) # Always return a list for consistency
        elif facebook_url.endswith("/events") or facebook_url.endswith("/events/"): 
            # Page events section URL
            data = get_page_events(driver, facebook_url)
            print(json.dumps(data))
        else:
            logger.error(f"Invalid URL format: {facebook_url}")
            print(json.dumps({"error": "Invalid Facebook URL type. Please provide an event URL or a page events section URL."}), file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        print(json.dumps({"error": f"Scraping failed: {str(e)}"}), file=sys.stderr)
        sys.exit(1)
    finally:
        if 'driver' in locals():
            driver.quit()


