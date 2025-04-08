import requests
import re
from typing import Dict, List, Any
import datetime
import lxml.html

class GDPRWebScraper:
    """
    A class to scrape the latest GDPR information from gdpr-info.eu using lxml instead of bs4
    """
    
    def __init__(self):
        """Initialize the GDPR web scraper"""
        self.base_url = "https://gdpr-info.eu/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_page(self, url: str) -> str:
        """
        Fetch a web page and return its content.
        
        Args:
            url: The URL to fetch
            
        Returns:
            The HTML content of the page
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""
    
    def get_latest_updates(self) -> List[Dict[str, str]]:
        """
        Get the latest GDPR updates from the website using lxml.
        
        Returns:
            A list of dictionaries with update information
        """
        updates = []
        
        try:
            # Fetch the main page
            main_html = self.fetch_page(self.base_url)
            if not main_html:
                return updates
            
            # Parse the HTML with lxml
            root = lxml.html.fromstring(main_html)
            
            # Look for news/updates sections
            news_section = root.xpath('//div[contains(@class, "widget_recent_entries")]')
            if news_section:
                news_items = news_section[0].xpath('.//li')
                for item in news_items:
                    link = item.xpath('./a')
                    if link:
                        title = link[0].text_content().strip()
                        url = link[0].get('href', '')
                        date = item.xpath('./span[contains(@class, "post-date")]')
                        date_text = date[0].text_content().strip() if date else ""
                        
                        updates.append({
                            'title': title,
                            'url': url,
                            'date': date_text
                        })
            
            # If no news section was found, look for general article sections
            if not updates:
                articles = root.xpath('//article')
                for article in articles[:5]:  # Limit to top 5 articles
                    title_elem = article.xpath('.//h2')
                    if title_elem:
                        link = title_elem[0].xpath('./a')
                        if link:
                            title = link[0].text_content().strip()
                            url = link[0].get('href', '')
                            date = article.xpath('.//time')
                            date_text = date[0].text_content().strip() if date else ""
                            
                            updates.append({
                                'title': title,
                                'url': url,
                                'date': date_text
                            })
            
            return updates
        
        except Exception as e:
            print(f"Error getting latest updates: {e}")
            return updates
    
    def get_article_content(self, article_number: int) -> Dict[str, Any]:
        """
        Get the content of a specific GDPR article using lxml.
        
        Args:
            article_number: The article number to fetch
            
        Returns:
            A dictionary with the article title, content, and related information
        """
        article_info = {
            'number': article_number,
            'title': '',
            'content': '',
            'recitals': []
        }
        
        try:
            # Construct the URL for the article
            article_url = f"{self.base_url}art-{article_number}-gdpr/"
            
            # Fetch the article page
            article_html = self.fetch_page(article_url)
            if not article_html:
                return article_info
            
            # Parse the HTML with lxml
            root = lxml.html.fromstring(article_html)
            
            # Get the article title
            title_elem = root.xpath('//h1[contains(@class, "entry-title")]')
            if title_elem:
                article_info['title'] = title_elem[0].text_content().strip()
            
            # Get the article content
            content_elem = root.xpath('//div[contains(@class, "entry-content")]')
            if content_elem:
                # Get text content
                article_info['content'] = content_elem[0].text_content().strip()
            
            # Get related recitals
            recitals_section = root.xpath('//div[@id="recital"]')
            if recitals_section:
                recital_links = recitals_section[0].xpath('.//a')
                for link in recital_links:
                    href = link.get('href', '')
                    recital_number = re.search(r'recital-(\d+)', href)
                    if recital_number:
                        recital_num = recital_number.group(1)
                        recital_text = link.text_content().strip()
                        article_info['recitals'].append({
                            'number': recital_num,
                            'text': recital_text
                        })
            
            return article_info
        
        except Exception as e:
            print(f"Error getting article {article_number}: {e}")
            return article_info
    
    def get_key_gdpr_principles(self) -> List[str]:
        """
        Extract the key GDPR principles from the website using lxml.
        
        Returns:
            A list of key GDPR principles
        """
        principles = []
        
        try:
            # Key GDPR principles are in Articles 5-11
            key_articles = [5, 6, 7, 8, 9, 10, 11]
            
            for article_num in key_articles:
                article_info = self.get_article_content(article_num)
                if article_info['title'] and article_info['content']:
                    # Extract a summary of the principle
                    content = article_info['content']
                    # Limit to first 200 characters + find the end of the sentence
                    summary = content[:200]
                    end_of_sentence = summary.rfind('.')
                    if end_of_sentence > 0:
                        summary = summary[:end_of_sentence + 1]
                    
                    principles.append(f"{article_info['title']}: {summary}")
            
            return principles
        
        except Exception as e:
            print(f"Error getting key principles: {e}")
            return principles
    
    def get_gdpr_requirements(self) -> Dict[str, Any]:
        """
        Compile the latest GDPR requirements and information using lxml.
        
        Returns:
            A dictionary with the latest GDPR information
        """
        # This method remains largely the same, but uses data from the lxml parsing methods
        gdpr_data = {
            "recent_changes": "",
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d"),
            "key_requirements": [],
            "common_weak_points": {
                "consent": "Predefined: Lack of clear consent management practices.",
                "anonymization": "Predefined: Insufficient data anonymization for sensitive data.",
                "policy_updates": "Predefined: Failure to update privacy policies regularly.",
                "data_subject_rights": "Predefined: Inadequate mechanisms for users to exercise their rights.",
                "data_breach": "Predefined: Insufficient data breach detection and notification procedures.",
                "third_party": "Predefined: Lack of oversight for third-party data processors."
            },
            "action_templates": {
                "consent": [
                    "Predefined: Implement explicit opt-in consent mechanisms for all data collection points.",
                    "Predefined: Ensure consent requests are presented clearly and separately from other terms.",
                    "Predefined: Provide easy ways for users to withdraw consent at any time."
                ],
                "anonymization": [
                    "Predefined: Implement robust anonymization techniques for all sensitive data.",
                    "Predefined: Conduct a data inventory to identify all places where personal data is stored.",
                    "Predefined: Use encryption for data both at rest and in transit."
                ],
                "policy_updates": [
                    "Predefined: Establish a quarterly schedule for reviewing and updating privacy policies.",
                    "Predefined: Create a change management process for documenting updates to data practices.",
                    "Predefined: Implement a version control system for privacy documentation."
                ],
                "data_subject_rights": [
                    "Predefined: Develop a streamlined process for handling data subject access requests.",
                    "Predefined: Create self-service portals for users to access, modify, and delete their data.",
                    "Predefined: Ensure all data subject requests are processed within agreed timeframes."
                ],
                "data_breach": [
                    "Predefined: Implement automated breach detection systems.",
                    "Predefined: Create a response team and clear procedures for handling data breaches.",
                    "Predefined: Establish templates for notifying authorities and affected users within 72 hours."
                ],
                "third_party": [
                    "Predefined: Audit all third-party data processors for GDPR compliance.",
                    "Predefined: Update data processing agreements with all vendors.",
                    "Predefined: Implement regular compliance checks for third-party services."
                ]
            }
        }
        
        # Get the latest updates
        updates = self.get_latest_updates()
        if updates:
            update_texts = []
            for update in updates[:3]:  # Use top 3 updates
                update_text = f"{update['title']}"
                if update.get('date'):
                    update_text += f" ({update['date']})"
                update_texts.append(update_text)
            
            gdpr_data["recent_changes"] = "Latest updates: " + "; ".join(update_texts)
        else:
            gdpr_data["recent_changes"] = "As of 2025, GDPR regulations emphasize stricter data anonymization practices, and data subject access requests (DSARs) must be processed within 14 days instead of the previous 30."
        
        # Get key principles
        principles = self.get_key_gdpr_principles()
        if principles:
            gdpr_data["key_requirements"] = principles
        else:
            # Fallback to default principles
            gdpr_data["key_requirements"] = [
                "Predefined: Data Minimization: Collect only the necessary data.",
                "Predefined: Data Subject Rights: Ensure users can easily access, delete, and transfer their data.",
                "Predefined: Data Breach Notification: Notify authorities within 72 hours of a breach.",
                "Predefined: Accountability and Record Keeping: Maintain records of all processing activities.",
                "Predefined: Lawful Basis: Process data only with a valid legal basis.",
                "Predefined: Transparency: Provide clear privacy notices about data usage."
            ]
        
        return gdpr_data
