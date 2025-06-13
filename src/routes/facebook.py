from flask import Blueprint, request, jsonify
import json
import sys
import os
import re
import requests
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('facebook_api')

facebook_bp = Blueprint("facebook", __name__)

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
            date_obj = datetime.strptime(f"{date_part} {time_part}", "%B %d, %Y %I:%M %p")
            start_time = date_obj.isoformat()
            
            # Default end time is 2 hours after start
            end_time = (date_obj + timedelta(hours=2)).isoformat()
            
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

def get_event_data(url):
    """Extract data from a Facebook event page using requests"""
    logger.info(f"Scraping event: {url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return {
                "title": "Error loading page",
                "description": f"Failed to load page: HTTP {response.status_code}",
                "url": url
            }
            
        html_content = response.text
        
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
        
        # Extract title from Open Graph meta tags
        og_title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html_content)
        if og_title_match:
            data["title"] = clean_text(og_title_match.group(1))
            
        # Extract description from Open Graph meta tags
        og_desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', html_content)
        if og_desc_match:
            data["description"] = clean_text(og_desc_match.group(1))
            
        # Extract image from Open Graph meta tags
        og_image_match = re.search(r'<meta property="og:image" content="([^"]+)"', html_content)
        if og_image_match:
            data["image_url"] = og_image_match.group(1)
            
        # Extract date and time from description or content
        date_str, time_str, start_time, end_time = extract_date_time(html_content)
        data["date"] = date_str
        data["time"] = time_str
        if start_time:
            data["start_time"] = start_time
        if end_time:
            data["end_time"] = end_time
            
        return data
        
    except Exception as e:
        logger.error(f"Error scraping event {url}: {str(e)}")
        return {
            "title": "Error scraping event",
            "description": f"Failed to scrape event: {str(e)}",
            "url": url
        }

def get_page_events(page_url):
    """Extract event links from a Facebook page's events section"""
    logger.info(f"Scraping events page: {page_url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        response = requests.get(page_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return [{
                "title": "Error loading page",
                "description": f"Failed to load page: HTTP {response.status_code}",
                "url": page_url
            }]
            
        html_content = response.text
        
        # Extract event links using regex
        event_links = []
        for match in re.finditer(r'href="(https://www\.facebook\.com/events/\d+[^"]*)"', html_content):
            link = match.group(1)
            if link not in event_links:
                event_links.append(link)
                
        # Also look for relative links
        for match in re.finditer(r'href="(/events/\d+[^"]*)"', html_content):
            relative_link = match.group(1)
            full_link = f"https://www.facebook.com{relative_link}"
            if full_link not in event_links:
                event_links.append(full_link)
        
        # Limit to 3 events to prevent timeouts
        if len(event_links) > 3:
            logger.info(f"Limiting to 3 events to prevent timeouts")
            event_links = event_links[:3]
            
        if not event_links:
            return [{
                "title": "No events found",
                "description": "Could not find any events on this page",
                "url": page_url
            }]
        
        # Get data for each event
        events_data = []
        for link in event_links:
            try:
                event_data = get_event_data(link)
                events_data.append(event_data)
            except Exception as e:
                logger.error(f"Error scraping event {link}: {str(e)}")
                events_data.append({
                    "title": "Error scraping event",
                    "description": f"Failed to scrape event: {str(e)}",
                    "url": link
                })
                
        return events_data
        
    except Exception as e:
        logger.error(f"Error scraping events page {page_url}: {str(e)}")
        return [{
            "title": "Error scraping events page",
            "description": f"Failed to scrape events page: {str(e)}",
            "url": page_url
        }]

@facebook_bp.route("/scrape", methods=["POST"])
def scrape_facebook_event():
    try:
        data = request.get_json()
        facebook_url = data.get("url")
        
        if not facebook_url:
            return jsonify({"error": "Facebook URL is required"}), 400
        
        # Direct scraping without subprocess
        if "/events/" in facebook_url and not facebook_url.endswith("/events") and not facebook_url.endswith("/events/"):
            # Single event URL
            data = get_event_data(facebook_url)
            return jsonify([data])  # Always return a list for consistency
        elif facebook_url.endswith("/events") or facebook_url.endswith("/events/"):
            # Page events section URL
            data = get_page_events(facebook_url)
            return jsonify(data)
        else:
            return jsonify({"error": "Invalid Facebook URL type. Please provide an event URL or a page events section URL."}), 400
            
    except Exception as e:
        logger.error(f"Error in scrape endpoint: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@facebook_bp.route("/import", methods=["POST"])
def import_to_luma():
    try:
        data = request.get_json()
        
        # Extract event data and configuration
        event_data = data.get("event_data")
        luma_api_key = data.get("luma_api_key")
        luma_calendar_id = data.get("luma_calendar_id")
        hosts = data.get("hosts", [])
        
        if not all([event_data, luma_api_key, luma_calendar_id]):
            return jsonify({"error": "Missing required data"}), 400
        
        # Create event directly without importing module
        headers = {
            "Authorization": f"Bearer {luma_api_key}",
            "Content-Type": "application/json"
        }

        # Prepare description with ticket link prepended
        description = event_data.get("description", "")
        ticket_link = event_data.get("ticket_link", "")
        if ticket_link and ticket_link != "":
            description = f"Register/Tickets: {ticket_link}\n\n" + description

        # Prepare hosts data
        luma_hosts = []
        for host in hosts:
            luma_hosts.append({
                "name": host.get("name"),
                "email": host.get("email"),
                "bio": host.get("bio", "")
            })

        # Prepare event data for Lu.ma API
        payload = {
            "calendar_id": luma_calendar_id,
            "name": event_data.get("title", "Facebook Event"),
            "description": description,
            "start_at": event_data.get("start_time"),
            "end_at": event_data.get("end_time"),
            "url": event_data.get("url"),
            "webinar_link": ticket_link,  # Map ticket link to webinar_link
            "timezone": event_data.get("timezone", "UTC"),
            "hosts": luma_hosts
        }

        # Add location if available
        if event_data.get("location") and event_data["location"] != "No location found":
            payload["geo_address_json"] = {
                "name": event_data["location"],
                "address": event_data.get("address", event_data["location"])
            }

        # Send request to create event
        response = requests.post("https://lu.ma/api/public/v1/event/create", headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        event_response = response.json()
        
        # Handle image upload if available
        image_url = event_data.get("image_url")
        if image_url and event_response.get("id"):
            event_id = event_response.get("id")
            try:
                # Download image
                image_response = requests.get(image_url, stream=True)
                if image_response.status_code == 200:
                    # Upload to Lu.ma
                    upload_headers = {
                        "Authorization": f"Bearer {luma_api_key}"
                    }
                    files = {"image": ("event_image.jpg", image_response.content)}
                    upload_response = requests.post(
                        f"https://lu.ma/api/public/v1/event/{event_id}/upload_image", 
                        headers=upload_headers, 
                        files=files
                    )
                    upload_response.raise_for_status()
            except Exception as e:
                logger.error(f"Error uploading image: {str(e)}")
        
        return jsonify({"success": True, "event": event_response})
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating event: {str(e)}")
        return jsonify({"error": f"Error creating event: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Error in import endpoint: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@facebook_bp.route("/calendar_info", methods=["POST"])
def get_calendar_info():
    try:
        data = request.get_json()
        luma_api_key = data.get("luma_api_key")
        luma_calendar_id = data.get("luma_calendar_id")
        
        if not all([luma_api_key, luma_calendar_id]):
            return jsonify({"error": "Missing API key or calendar ID"}), 400
        
        # Make a request to Lu.ma API to get calendar information
        headers = {
            "Authorization": f"Bearer {luma_api_key}",
            "Content-Type": "application/json"
        }
        
        # Try to get calendar info (this endpoint might not exist, so we'll handle gracefully)
        try:
            response = requests.get(f"https://lu.ma/api/public/v1/calendar/{luma_calendar_id}", headers=headers)
            if response.status_code == 200:
                calendar_data = response.json()
                return jsonify({
                    "calendar_id": luma_calendar_id,
                    "calendar_name": calendar_data.get("name", "Unknown Calendar"),
                    "calendar_url": calendar_data.get("url", f"https://lu.ma/calendar/{luma_calendar_id}")
                })
            else:
                # Fallback if calendar info endpoint doesn't exist
                return jsonify({
                    "calendar_id": luma_calendar_id,
                    "calendar_name": "Calendar",
                    "calendar_url": f"https://lu.ma/calendar/{luma_calendar_id}"
                })
        except requests.exceptions.RequestException:
            # Fallback if request fails
            return jsonify({
                "calendar_id": luma_calendar_id,
                "calendar_name": "Calendar",
                "calendar_url": f"https://lu.ma/calendar/{luma_calendar_id}"
            })
            
    except Exception as e:
        logger.error(f"Error in calendar_info endpoint: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
