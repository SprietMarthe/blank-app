from typing import Dict, List, Tuple, Any, Optional
import gdpr_web_scraper


class GDPRFallbackAnalyzer:
    """
    A fallback analyzer that doesn't require any LLM.
    This uses simple rule-based analysis for GDPR compliance.
    """
    
    def __init__(self):
        """Initialize the fallback GDPR analyzer"""

        # Initialize scraper if needed
        self.scraper = None
        try:
            self.scraper = gdpr_web_scraper.GDPRWebScraper()
            print("Using web scraper to get the latest GDPR requirements")
        except Exception as e:
            print(f"Error initializing web scraper: {e}")
            print("Using predefined GDPR requirements")

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
        """
        Get the GDPR requirements.
        If a web scraper is available, it will be used to get the latest information.
        Otherwise, predefined values will be used.
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
