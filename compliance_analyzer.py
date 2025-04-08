import os
import json
import re
import replicate
from typing import Dict, List, Tuple, Any, Optional
import gdpr_web_scraper
from fallback_analyzer import GDPRFallbackAnalyzer

class GDPRReplicateAnalyzer:

    """
    A class to analyze GDPR compliance of documents using the Replicate API
    to access Meta Llama or similar models.
    """
    
    def __init__(self, api_token: Optional[str] = None, use_web_scraper: bool = True):
        """
        Initialize the GDPR compliance analyzer with Replicate API.
        
        Args:
            api_token: Replicate API token. If None, will look for REPLICATE_API_TOKEN environment variable.
        """
        # Set API token
        self.api_token = api_token or os.environ.get("REPLICATE_API_TOKEN")
        self.model_loaded = self.api_token is not None
        
        # Set environment variable if provided
        if self.api_token and "REPLICATE_API_TOKEN" not in os.environ:
            os.environ["REPLICATE_API_TOKEN"] = self.api_token
            
        # Model configuration
        self.model_name = "meta/meta-llama-3.1-405b-instruct"  # Using the base model
        
        # Initialize scraper if needed
        self.scraper = None
        if use_web_scraper:
            try:
                self.scraper = gdpr_web_scraper.GDPRWebScraper()
                print("Using web scraper to get the latest GDPR requirements")
            except Exception as e:
                print(f"Error initializing web scraper: {e}")
                print("Using predefined GDPR requirements")
        
        # Get GDPR requirements
        self.gdpr_data = self.get_gdpr_requirements()
        
        # Keywords to search for various compliance aspects
        self.compliance_keywords = {
            "consent": [
                "explicit consent", "opt-in", "consent form", "consent management",
                "withdraw consent", "consent records"
            ],
            "anonymization": [
                "anonymization", "pseudonymization", "encryption", "data protection",
                "personal data security", "data minimization"
            ],
            "policy_updates": [
                "policy update", "regular review", "policy version", "last updated",
                "policy change", "notification of changes"
            ],
            "data_subject_rights": [
                "right to access", "right to erasure", "right to be forgotten",
                "data portability", "right to object", "DSAR", "subject access request"
            ],
            "data_breach": [
                "data breach", "security incident", "breach notification", "72 hours",
                "breach detection", "incident response"
            ],
            "third_party": [
                "third party", "data processor", "vendor", "data transfer",
                "international transfer", "data sharing agreement"
            ]
        }
    
    def get_gdpr_requirements(self) -> Dict[str, Any]:
        """
        Get the latest GDPR regulations and requirements.
        """
        if self.scraper:
            try:
                # Try to get requirements from the scraper
                scraped_requirements = self.scraper.get_gdpr_requirements()
                if scraped_requirements and scraped_requirements.get("key_requirements"):
                    print("Successfully fetched GDPR requirements from the web")
                    scraped_requirements["is_live_data"] = True
                    return scraped_requirements
                else:
                    print("Failed to get complete GDPR requirements from the web, using fallback")
            except Exception as e:
                print(f"Error getting GDPR requirements from the web: {e}")
                print("Using predefined GDPR requirements")

        # Fallback to predefined requirements  
        return {
            "is_live_data": False,
            "recent_changes": "As of 2025, GDPR regulations emphasize stricter data anonymization practices, and data subject access requests (DSARs) must be processed within 14 days instead of the previous 30.",
            "key_requirements": [
                "Predefined: Data Minimization: Collect only the necessary data.",
                "Predefined: Data Subject Rights: Ensure users can easily access, delete, and transfer their data.",
                "Predefined: Data Breach Notification: Notify authorities within 72 hours of a breach.",
                "Predefined: Accountability and Record Keeping: Maintain records of all processing activities.",
                "Predefined: Lawful Basis: Process data only with a valid legal basis.",
                "Predefined: Transparency: Provide clear privacy notices about data usage."
            ],
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
                    "Predefined: Ensure all data subject requests are processed within 14 days."
                ],
                "data_breach": [
                    "Predefined: Implement automated breach detection systems.",
                    "Predefined: Create a response team and clear procedures for handling data breaches.",
                    "Predefined: Establish templates for notifying authorities and affected users."
                ],
                "third_party": [
                    "Predefined: Audit all third-party data processors for GDPR compliance.",
                    "Predefined: Update data processing agreements with all vendors.",
                    "Predefined: Implement regular compliance checks for third-party services."
                ]
            }
        }

    def update_gdpr_requirements(self) -> None:
        """
        Update GDPR requirements from the web if a scraper is available.
        This can be called to refresh the requirements data.
        """
        if self.scraper:
            try:
                new_requirements = self.scraper.get_gdpr_requirements()
                if new_requirements and new_requirements.get("key_requirements"):
                    self.gdpr_data = new_requirements
                    print("Successfully updated GDPR requirements from the web")
                    return
            except Exception as e:
                print(f"Error updating GDPR requirements: {e}")
        
        print("Could not update GDPR requirements from the web")

    def update_gdpr_requirements(self) -> None:
        """
        Update GDPR requirements from the web if a scraper is available.
        This can be called to refresh the requirements data.
        """
        if self.scraper:
            try:
                new_requirements = self.scraper.get_gdpr_requirements()
                if new_requirements and new_requirements.get("key_requirements"):
                    self.gdpr_data = new_requirements
                    print("Successfully updated GDPR requirements from the web")
                    return
            except Exception as e:
                print(f"Error updating GDPR requirements: {e}")
        
        print("Could not update GDPR requirements from the web")
    
    def _analyze_with_replicate(self, document_text: str) -> Dict[str, List[str]]:
        """
        Use Replicate API to analyze the document for GDPR compliance issues.
        
        Args:
            document_text: The text content of the document to analyze
            
        Returns:
            Dictionary with weak points and suggested actions
        """
        if not self.model_loaded:
            return {"weak_points": ["Replicate API not available. Using rule-based analysis only."], "actions": []}
            
        # Truncate document if it's too long for the context window
        max_length = 15000  # Llama models have a large context window, but we'll be conservative
        if len(document_text) > max_length:
            document_text = document_text[:max_length] + "..."
        
        # Add recent GDPR changes to the prompt context
        gdpr_context = f"Recent GDPR changes: {self.gdpr_data['recent_changes']}\n\n"
        gdpr_context += "Key GDPR requirements:\n"
        for i, req in enumerate(self.gdpr_data["key_requirements"][:5]):  # Include top 5 requirements
            gdpr_context += f"- {req}\n"
        
        # Add recent GDPR changes to the prompt context
        gdpr_context = f"Recent GDPR changes: {self.gdpr_data['recent_changes']}\n\n"
        gdpr_context += "Key GDPR requirements:\n"
        for i, req in enumerate(self.gdpr_data["key_requirements"][:5]):  # Include top 5 requirements
            gdpr_context += f"- {req}\n"
        
        # Craft a prompt for the LLM to analyze GDPR compliance
        prompt = f"""You are a GDPR compliance expert with knowledge of the latest requirements:

{gdpr_context}

Analyze the following document for GDPR compliance issues.
Focus on these areas: consent management, data anonymization, policy updates, data subject rights, 
data breach procedures, and third-party data processing.

For each area where the document is lacking, provide specific weaknesses and suggested actions.
Format your response as JSON with 'weak_points' and 'actions' arrays.

Here is the document:

{document_text}

JSON Response:"""
        
        try:
            # Set up input parameters for the Replicate API
            input_params = {
                "prompt": prompt,
                "temperature": 0.1,  # Low temperature for more focused and deterministic output
                "top_p": 1.0,
                "max_tokens": 2000,
                "presence_penalty": 0
            }
            
            # Call the Replicate API
            response_text = ""
            for event in replicate.stream(
                self.model_name,
                input=input_params
            ):
                response_text += str(event)
                print("response: ", response_text)
            
            # Try to extract JSON from response
            try:
                # Find JSON pattern in the response
                json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
                if json_match:
                    print("json match")
                    json_str = json_match.group(1)
                    analysis = json.loads(json_str)
                    return analysis
                else:
                    # Parse text response if JSON not found
                    weak_points = []
                    actions = []
                    
                    if "weak" in response_text.lower() or "issue" in response_text.lower():
                        weak_points_section = re.search(r'weak[^\n]*:(.*?)action', response_text, re.DOTALL | re.IGNORECASE)
                        if weak_points_section:
                            for line in weak_points_section.group(1).split('\n'):
                                if line.strip() and not line.strip().startswith('*'):
                                    weak_points.append(line.strip())
                    
                    if "action" in response_text.lower() or "recommend" in response_text.lower():
                        actions_section = re.search(r'action[^\n]*:(.*)', response_text, re.DOTALL | re.IGNORECASE)
                        if actions_section:
                            for line in actions_section.group(1).split('\n'):
                                if line.strip() and not line.strip().startswith('*'):
                                    actions.append(line.strip())
                    
                    return {"weak_points": weak_points, "actions": actions}
            except Exception as e:
                print(f"Error parsing LLM response: {e}")
                return {"weak_points": ["Error analyzing with LLM."], "actions": []}
        except Exception as e:
            print(f"Replicate API error: {e}")
            return {"weak_points": [f"Error using Replicate API: {str(e)}"], "actions": []}
    
    def _keyword_analysis(self, document_text: str) -> Dict[str, bool]:
        """
        Perform keyword-based analysis of the document.
        
        Args:
            document_text: The text content of the document
            
        Returns:
            Dictionary of compliance categories and whether they are mentioned
        """
        document_text_lower = document_text.lower()
        results = {}
        
        # Check for each compliance category
        for category, keywords in self.compliance_keywords.items():
            # Category is covered if ANY keyword is found
            category_covered = any(keyword.lower() in document_text_lower for keyword in keywords)
            results[category] = category_covered
            
        return results
    
    def analyze_document(self, document_text: str) -> Tuple[List[str], List[str]]:
        """
        Analyze a GDPR compliance document and identify weak points.
        
        Args:
            document_text: Text content of the document to analyze
            
        Returns:
            A tuple containing (weak_points, action_plan)
        """
        # Perform keyword analysis
        keyword_results = self._keyword_analysis(document_text)
        
        # Initialize results
        weak_points = []
        action_plan = []
        
        # Try to use Replicate API for advanced analysis if available
        if self.model_loaded:
            llm_analysis = self._analyze_with_replicate(document_text)
            
            # Add LLM-identified weak points
            for point in llm_analysis.get("weak_points", []):
                # Convert dict to tuple of items for comparison
                if point and not any(set(point.items()).issubset(set(existing.items())) for existing in weak_points):
                    weak_points.append(point)
                # Convert dict to JSON string for comparison
                # point_str = json.dumps(point, sort_keys=True)
                # if point and not any(json.dumps(existing, sort_keys=True) == point_str for existing in weak_points):
                #     weak_points.append(point)
                # Convert dict to JSON string for comparison
                # point_str = json.dumps(point, sort_keys=True)
                # if point and not any(json.dumps(existing, sort_keys=True) == point_str for existing in weak_points):
                #     weak_points.append(point)
            
            # Add LLM-suggested actions
            for action in llm_analysis.get("actions", []):
                if action and not any(action in existing for existing in action_plan):
                    action_plan.append(action)
        
        # Add results from keyword analysis
        for category, is_covered in keyword_results.items():
            if not is_covered:
                weak_points.append(self.gdpr_data["common_weak_points"][category])
                
                # Add relevant action items
                for action in self.gdpr_data["action_templates"][category]:
                    if not any(action in existing for existing in action_plan):
                        action_plan.append(action)
        
        # Remove duplicates while preserving order
        weak_points = list(dict.fromkeys(weak_points))
        action_plan = list(dict.fromkeys(action_plan))
        
        
        # Add general recommendations based on recent changes
        if action_plan:
            action_plan.insert(0, f"Recent GDPR changes to address: {self.gdpr_data['recent_changes']}")
        
        # Add key requirements as a reference
        if action_plan:
            action_plan.append("Ensure all key GDPR requirements are met, including:")
            for req in self.gdpr_data["key_requirements"]:
                action_plan.append(f"- {req}")
        
        return weak_points, action_plan


# Factory function to get the appropriate analyzer
def get_gdpr_analyzer(use_replicate=True, api_token=None, use_web_scraper: bool = True):
    """
    Factory function to get the appropriate GDPR analyzer.
    
    Args:
        use_replicate: Whether to try using the Replicate API
        api_token: Replicate API token
        
    Returns:
        A GDPR analyzer instance
    """
    if use_replicate:
        try:
            # Try to create the Replicate analyzer
            analyzer = GDPRReplicateAnalyzer(api_token)
            print("Analyzer:")
            print(analyzer)
            if analyzer.model_loaded:
                print(f"Using {analyzer.model_name} via Replicate for GDPR analysis")
                return analyzer
            else:
                print("Replicate API token not available, falling back to rule-based analysis")
                return GDPRFallbackAnalyzer()
        except Exception as e:
            print(f"Error initializing Replicate analyzer: {e}")
            print("Falling back to rule-based analysis")
            return GDPRFallbackAnalyzer()
    else:
        # Use the fallback analyzer
        return GDPRFallbackAnalyzer()


# Simple test function to demonstrate streaming output
def test_streaming():
    """Test streaming from Replicate API"""
    if "REPLICATE_API_TOKEN" not in os.environ:
        print("Please set REPLICATE_API_TOKEN environment variable")
        return
        
    prompt = "Explain the key principles of GDPR in 5 bullet points."
    
    input_params = {
        "prompt": prompt,
        "temperature": 0.5,
        "top_p": 0.9,
        "max_tokens": 500
    }
    
    print("Streaming response from Replicate API:")
    print("--------------------------------------")
    for event in replicate.stream(
        "meta/meta-llama-3.1-70b",
        input=input_params
    ):
        print(event, end="")
    print("\n--------------------------------------")


# Test function for the analyzer
def test_analyzer():
    """Test the GDPR analyzer with a sample document"""
    analyzer = get_gdpr_analyzer(use_replicate=True)
    
    sample_document = """
    Our privacy policy outlines how we collect and process user data.
    We use cookies to enhance user experience on our platform.
    Users can contact our support team with any questions about their data.
    We may share data with third parties for analytics purposes.
    """
    
    weak_points, action_plan = analyzer.analyze_document(sample_document)
    
    print("Weak Points:")
    for point in weak_points:
        print(f"- {point}")
    
    print("\nAction Plan:")
    for action in action_plan:
        print(f"- {action}")


if __name__ == "__main__":
    # Uncomment to test streaming
    # test_streaming()
    
    # Test analyzer
    test_analyzer()