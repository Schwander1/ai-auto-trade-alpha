#!/usr/bin/env python3
"""
Alpine Analytics - Canva Brand Automation
High-level brand automation using Canva API
Generates branded assets from templates
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any
import time

# Import Canva OAuth client
from canva_oauth2 import CanvaOAuth2Client

logger = logging.getLogger(__name__)

class AlpineBrandAutomation:
    """
    High-level brand automation using Canva API
    Generates branded assets from templates
    """
    
    def __init__(self):
        self.canva = CanvaOAuth2Client()
        self.brand_config = self._load_brand_config()
    
    def _load_brand_config(self) -> Dict[str, Any]:
        """Load Alpine brand configuration"""
        # Try to load from brand config file if it exists
        brand_config_path = Path(__file__).parent.parent / "alpine-frontend" / "lib" / "brand.ts"
        
        # For now, use hardcoded values matching the brand system
        return {
            "colors": {
                "black": {
                    "pure": "#000000",
                    "primary": "#0a0a0f",
                    "secondary": "#0f0f1a",
                    "tertiary": "#15151a",
                    "border": "#1a1a2e",
                },
                "neon": {
                    "cyan": "#18e0ff",
                    "cyanDark": "#00b8d4",
                    "pink": "#fe1c80",
                    "pinkDark": "#cc0066",
                    "purple": "#9600ff",
                    "purpleDark": "#5320f9",
                    "orange": "#ff5f01",
                    "orangeDark": "#cc4d00",
                },
                "semantic": {
                    "success": "#00ff88",
                    "error": "#ff2d55",
                    "warning": "#ff5f01",
                    "info": "#18e0ff",
                },
                "text": {
                    "primary": "#ffffff",
                    "secondary": "#a1a1aa",
                    "tertiary": "#71717a",
                    "inverse": "#000000",
                },
            },
            "metadata": {
                "name": "Alpine Analytics LLC",
                "tagline": "Adaptive AI Trading Signals",
                "website": "https://alpineanalytics.com",
                "email": "info@alpineanalytics.com",
            }
        }
    
    def generate_social_post(
        self,
        template_id: str,
        title: str,
        description: str,
        cta: str = "Learn More",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate branded social media post
        
        Args:
            template_id: Canva template ID for social post
            title: Post title
            description: Post description
            cta: Call-to-action text
            **kwargs: Additional template variables
            
        Returns:
            Generated design with export information
        """
        autofill_data = {
            "title": title,
            "description": description,
            "cta": cta,
            "brand_name": self.brand_config["metadata"]["name"],
            "brand_tagline": self.brand_config["metadata"]["tagline"],
            "brand_colors": self.brand_config["colors"],
            **kwargs
        }
        
        # Create design from template
        design = self.canva.create_design_from_template(template_id, autofill_data)
        design_id = design["id"]
        
        logger.info(f"Created design: {design_id}")
        
        # Export as PNG
        export = self.canva.export_design(design_id, format="PNG", quality="high")
        export_id = export["id"]
        
        # Wait for export
        result = self.canva.wait_for_export(design_id, export_id)
        
        return {
            "design_id": design_id,
            "export_id": export_id,
            "download_url": result.get("url"),
            "design": design,
        }
    
    def generate_pdf_report(
        self,
        template_id: str,
        title: str,
        content: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate branded PDF report"""
        autofill_data = {
            "title": title,
            "brand_name": self.brand_config["metadata"]["name"],
            "brand_tagline": self.brand_config["metadata"]["tagline"],
            "brand_colors": self.brand_config["colors"],
            **content,
            **kwargs
        }
        
        design = self.canva.create_design_from_template(template_id, autofill_data)
        design_id = design["id"]
        
        # Export as PDF
        export = self.canva.export_design(design_id, format="PDF", quality="high")
        export_id = export["id"]
        
        result = self.canva.wait_for_export(design_id, export_id)
        
        return {
            "design_id": design_id,
            "export_id": export_id,
            "download_url": result.get("url"),
            "design": design,
        }
    
    def list_templates(self) -> list:
        """List available Canva templates"""
        # Note: Canva API might not have a direct template listing endpoint
        # This would list user's designs that could be used as templates
        return self.canva.list_designs()


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Alpine Analytics Brand Automation")
    parser.add_argument("--generate-social", type=str, help="Generate social post (template ID)")
    parser.add_argument("--title", type=str, help="Post title")
    parser.add_argument("--description", type=str, help="Post description")
    parser.add_argument("--cta", type=str, default="Learn More", help="Call-to-action text")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    if args.generate_social:
        if not args.title or not args.description:
            print("❌ Error: --title and --description required for social post generation")
            exit(1)
        
        automation = AlpineBrandAutomation()
        result = automation.generate_social_post(
            template_id=args.generate_social,
            title=args.title,
            description=args.description,
            cta=args.cta
        )
        print(f"\n✅ Generated social post!")
        print(f"Design ID: {result['design_id']}")
        print(f"Download URL: {result['download_url']}")
    else:
        parser.print_help()

