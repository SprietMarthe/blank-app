import os
import json
import re
from typing import Dict, List, Tuple, Any, Optional
from llama_cpp import Llama

class GDPRLlamaAnalyzer:
    """
    A class to analyze GDPR compliance of documents using the Llama model.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the GDPR compliance analyzer with Llama model.
        
        Args:
            model_path: Path to the Llama model file. If None, will use the default model path.
        """
        # Set default model path if not provided
        if model_path is None:
            # This path would need to be adjusted to where you have your Llama model
            model_path = "llama-2-7b-chat.ggmlv3.q4_0.bin"
        
        # Initialize Llama model
        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=4096,  # Context window size
                n_batch=512  # Batch size for processing
            )
            self.model_loaded = True
        except Exception as e:
            print(f"Error loading Llama model: {e}")
            print("Operating in fallback mode without Llama. Analysis will be based on rules only.")
            self.model_loaded = False
        
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
        return {
            "recent_changes": "As of 2025, GDPR regulations emphasize stricter data anonymization practices, and data subject access requests (DSARs) must be processed within 14 days instead of the previous 30.",
            "key_requirements": [
                "Data Minimization: Collect only the necessary data.",
                "Data Subject Rights: Ensure users can easily access, delete, and transfer their data.",
                "Data Breach Notification: Notify authorities within 72 hours of a breach.",
                "Accountability and Record Keeping: Maintain records of all processing activities.",
                "Lawful Basis: Process data only with a valid legal basis.",
                "Transparency: Provide clear privacy notices about data usage."
            ],
            "common_weak_points": {
                "consent": "Lack of clear consent management practices.",
                "anonymization": "Insufficient data anonymization for sensitive data.",
                "policy_updates": "Failure to update privacy policies regularly.",
                "data_subject_rights": "Inadequate mechanisms for users to exercise their rights.",
                "data_breach": "Insufficient data breach detection and notification procedures.",
                "third_party": "Lack of oversight for third-party data processors."
            },
            "action_templates": {
                "consent": [
                    "Implement explicit opt-in consent mechanisms for all data collection points.",
                    "Ensure consent requests are presented clearly and separately from other terms.",
                    "Provide easy ways for users to withdraw consent at any time."
                ],
                "anonymization": [
                    "Implement robust anonymization techniques for all sensitive data.",
                    "Conduct a data inventory to identify all places where personal data is stored.",
                    "Use encryption for data both at rest and in transit."
                ],
                "policy_updates": [
                    "Establish a quarterly schedule for reviewing and updating privacy policies.",
                    "Create a change management process for documenting updates to data practices.",
                    "Implement a version control system for privacy documentation."
                ],
                "data_subject_rights": [
                    "Develop a streamlined process for handling data subject access requests.",
                    "Create self-service portals for users to access, modify, and delete their data.",
                    "Ensure all data subject requests are processed within 14 days."
                ],
                "data_breach": [
                    "Implement automated breach detection systems.",
                    "Create a response team and clear procedures for handling data breaches.",
                    "Establish templates for notifying authorities and affected users."
                ],
                "third_party": [
                    "Audit all third-party data processors for GDPR compliance.",
                    "Update data processing agreements with all vendors.",
                    "Implement regular compliance checks for third-party services."
                ]
            }
        }
    
    def _analyze_with_llama(self, document_text: str) -> Dict[str, List[str]]:
        """
        Use Llama model to analyze the document for GDPR compliance issues.
        
        Args:
            document_text: The text content of the document to analyze
            
        Returns:
            Dictionary with weak points and suggested actions
        """
        if not self.model_loaded:
            return {"weak_points": ["Llama model not available. Using rule-based analysis only."], "actions": []}
            
        # Truncate document if it's too long for the context window
        max_length = 3000  # Leave room for prompt and response
        if len(document_text) > max_length:
            document_text = document_text[:max_length] + "..."
        
        # Craft a prompt for Llama to analyze GDPR compliance
        prompt = f"""
        You are a GDPR compliance expert. Analyze the following document for GDPR compliance issues.
        Focus on these areas: consent management, data anonymization, policy updates, data subject rights, 
        data breach procedures, and third-party data processing.
        
        For each area where the document is lacking, provide specific weaknesses and suggested actions.
        Format your response as JSON with 'weak_points' and 'actions' arrays.
        
        Here is the document:
        
        {document_text}
        
        JSON Response:
        """
        
        # Get response from Llama
        response = self.llm(
            prompt, 
            max_tokens=1024,
            temperature=0.1,  # Low temperature for more focused and deterministic output
            stop=["```"]  # Stop at end of JSON
        )
        
        response_text = response["choices"][0]["text"]
        
        # Try to extract JSON from response
        try:
            # Find JSON pattern in the response
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if json_match:
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
            print(f"Error parsing Llama response: {e}")
            return {"weak_points": ["Error analyzing with Llama model."], "actions": []}
    
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
        
        # Try to use Llama for advanced analysis if available
        if self.model_loaded:
            llama_analysis = self._analyze_with_llama(document_text)
            
            # Add Llama-identified weak points
            for point in llama_analysis.get("weak_points", []):
                if point and not any(point in existing for existing in weak_points):
                    weak_points.append(point)
            
            # Add Llama-suggested actions
            for action in llama_analysis.get("actions", []):
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


class GDPRFallbackAnalyzer:
    """
    A fallback analyzer that doesn't require Llama or any ML models.
    This uses simple rule-based analysis for GDPR compliance.
    """
    
    def __init__(self):
        """Initialize the fallback GDPR analyzer"""
        self.gdpr_data = self.get_gdpr_requirements()
        
        # Keywords for different compliance categories
        self.compliance_keywords = {
            "consent": [
                "explicit consent", "opt-in", "consent form", "consent management",
                "consent", "opt out", "permission"
            ],
            "anonymization": [
                "anonymization", "pseudonymization", "encryption", "data protection",
                "personal data security", "data minimization", "anonymize"
            ],
            "policy_updates": [
                "policy update", "regular review", "policy version", "last updated",
                "policy change", "notification of changes", "review"
            ],
            "data_subject_rights": [
                "right to access", "right to erasure", "right to be forgotten",
                "data portability", "right to object", "DSAR", "subject access request",
                "access rights", "user rights"
            ],
            "data_breach": [
                "data breach", "security incident", "breach notification", "72 hours",
                "breach detection", "incident response", "security breach"
            ],
            "third_party": [
                "third party", "data processor", "vendor", "data transfer",
                "international transfer", "data sharing agreement", "third-party"
            ]
        }
    
    def get_gdpr_requirements(self) -> Dict[str, Any]:
        """Get the GDPR requirements"""
        return {
            "recent_changes": "As of 2025, GDPR regulations emphasize stricter data anonymization practices, and data subject access requests (DSARs) must be processed within 14 days instead of the previous 30.",
            "key_requirements": [
                "Data Minimization: Collect only the necessary data.",
                "Data Subject Rights: Ensure users can easily access, delete, and transfer their data.",
                "Data Breach Notification: Notify authorities within 72 hours of a breach.",
                "Accountability and Record Keeping: Maintain records of all processing activities.",
                "Lawful Basis: Process data only with a valid legal basis.",
                "Transparency: Provide clear privacy notices about data usage."
            ],
            "common_weak_points": {
                "consent": "Lack of clear consent management practices.",
                "anonymization": "Insufficient data anonymization for sensitive data.",
                "policy_updates": "Failure to update privacy policies regularly.",
                "data_subject_rights": "Inadequate mechanisms for users to exercise their rights.",
                "data_breach": "Insufficient data breach detection and notification procedures.",
                "third_party": "Lack of oversight for third-party data processors."
            },
            "action_templates": {
                "consent": [
                    "Implement explicit opt-in consent mechanisms for all data collection points.",
                    "Ensure consent requests are presented clearly and separately from other terms.",
                    "Provide easy ways for users to withdraw consent at any time."
                ],
                "anonymization": [
                    "Implement robust anonymization techniques for all sensitive data.",
                    "Conduct a data inventory to identify all places where personal data is stored.",
                    "Use encryption for data both at rest and in transit."
                ],
                "policy_updates": [
                    "Establish a quarterly schedule for reviewing and updating privacy policies.",
                    "Create a change management process for documenting updates to data practices.",
                    "Implement a version control system for privacy documentation."
                ],
                "data_subject_rights": [
                    "Develop a streamlined process for handling data subject access requests.",
                    "Create self-service portals for users to access, modify, and delete their data.",
                    "Ensure all data subject requests are processed within 14 days."
                ],
                "data_breach": [
                    "Implement automated breach detection systems.",
                    "Create a response team and clear procedures for handling data breaches.",
                    "Establish templates for notifying authorities and affected users."
                ],
                "third_party": [
                    "Audit all third-party data processors for GDPR compliance.",
                    "Update data processing agreements with all vendors.",
                    "Implement regular compliance checks for third-party services."
                ]
            }
        }
        
    def analyze_document(self, document_text: str) -> Tuple[List[str], List[str]]:
        """
        Analyze a document for GDPR compliance using keyword-based rules.
        
        Args:
            document_text: Text content of the document to analyze
            
        Returns:
            A tuple containing (weak_points, action_plan)
        """
        document_text_lower = document_text.lower()
        
        # Initialize results
        weak_points = []
        action_plan = []
        
        # Check each compliance category
        for category, keywords in self.compliance_keywords.items():
            # Check if ANY of the keywords are present
            category_covered = any(keyword.lower() in document_text_lower for keyword in keywords)
            
            # If keywords for this category are not found, consider it a weak point
            if not category_covered:
                weak_points.append(self.gdpr_data["common_weak_points"][category])
                
                # Add relevant action items
                for action in self.gdpr_data["action_templates"][category]:
                    action_plan.append(action)
        
        # Look for specific missing clauses
        if "14 day" not in document_text_lower and "fourteen day" not in document_text_lower:
            weak_points.append("Missing updated timeline for Data Subject Access Requests (now 14 days)")
            action_plan.append("Update policy to reflect the new 14-day timeline for responding to DSARs")
            
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
def get_gdpr_analyzer(use_llama=True, model_path=None):
    """
    Factory function to get the appropriate GDPR analyzer.
    
    Args:
        use_llama: Whether to try using the Llama model
        model_path: Path to the Llama model file
        
    Returns:
        A GDPR analyzer instance
    """
    if use_llama:
        try:
            # Try to import Llama
            import llama_cpp
            
            # Try to create the Llama analyzer
            analyzer = GDPRLlamaAnalyzer(model_path)
            if analyzer.model_loaded:
                print("Using Llama for GDPR analysis")
                return analyzer
            else:
                print("Llama model loading failed, falling back to rule-based analysis")
                return GDPRFallbackAnalyzer()
        except ImportError:
            print("llama-cpp-python not installed, falling back to rule-based analysis")
            return GDPRFallbackAnalyzer()
    else:
        # Use the fallback analyzer
        return GDPRFallbackAnalyzer()


# Simple test function
def test_analyzer():
    """Test the GDPR analyzer with a sample document"""
    analyzer = get_gdpr_analyzer(use_llama=True)
    
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
    test_analyzer()
