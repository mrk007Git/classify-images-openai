#!/usr/bin/env python3
"""
Gemstone Image Analysis with OpenAI

This project uses OpenAI's GPT-4 Vision API to analyze semi-precious gemstone images 
and provide structured output in both English and German.

License: MIT License
Copyright (c) 2025

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

DISCLAIMER: This tool uses AI for gemstone identification. Results are for 
informational purposes only and should not be relied upon for professional 
appraisal, commercial transactions, or investment decisions. Always consult 
certified gemologists for accurate identification.
"""

import os
import json
import base64
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import io

# Load environment variables
load_dotenv()

class GemstoneAnalyzer:
    def __init__(self):
        """Initialize the gemstone analyzer with OpenAI client."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.images_folder = Path('images')
        self.output_folder = Path('output')
        
        # Create output folder if it doesn't exist
        self.output_folder.mkdir(exist_ok=True)
    
    def encode_image(self, image_path: Path) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_gemstone(self, image_path: Path) -> Dict[str, Any]:
        """Analyze a single gemstone image using OpenAI Vision API with structured output."""
        
        # Encode the image
        base64_image = self.encode_image(image_path)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this semi-precious gemstone image and provide detailed information. 
                                Please identify the type of gemstone, provide a detailed description of its characteristics, 
                                and specify where this type of gemstone is typically found geographically. 
                                Provide all information in both English and German."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "gemstone_analysis",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "english": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "The name of the gemstone"
                                        },
                                        "description": {
                                            "type": "string",
                                            "description": "Detailed description of the gemstone's appearance, color, clarity, and characteristics"
                                        },
                                        "areas_found": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            },
                                            "description": "Geographic locations where this gemstone is typically found"
                                        },
                                        "confidence": {
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 100,
                                            "description": "Confidence level of the identification (0-100%)"
                                        }
                                    },
                                    "required": ["name", "description", "areas_found", "confidence"],
                                    "additionalProperties": False
                                },
                                "german": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "Der Name des Edelsteins"
                                        },
                                        "description": {
                                            "type": "string",
                                            "description": "Detaillierte Beschreibung des Aussehens, der Farbe, Klarheit und Eigenschaften des Edelsteins"
                                        },
                                        "areas_found": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            },
                                            "description": "Geografische Orte, wo dieser Edelstein typischerweise gefunden wird"
                                        },
                                        "confidence": {
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 100,
                                            "description": "Vertrauensniveau der Identifikation (0-100%)"
                                        }
                                    },
                                    "required": ["name", "description", "areas_found", "confidence"],
                                    "additionalProperties": False
                                },
                                "image_filename": {
                                    "type": "string",
                                    "description": "The filename of the analyzed image"
                                }
                            },
                            "required": ["english", "german", "image_filename"],
                            "additionalProperties": False
                        }
                    }
                },
                max_tokens=1500
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("No content in API response")
            
            analysis = json.loads(content)
            analysis["image_filename"] = image_path.name
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing {image_path.name}: {str(e)}")
            return {
                "error": str(e),
                "image_filename": image_path.name,
                "english": {
                    "name": "Unknown",
                    "description": "Error occurred during analysis",
                    "areas_found": [],
                    "confidence": 0
                },
                "german": {
                    "name": "Unbekannt",
                    "description": "Fehler während der Analyse aufgetreten",
                    "areas_found": [],
                    "confidence": 0
                }
            }
    
    def analyze_all_images(self) -> List[Dict[str, Any]]:
        """Analyze all images in the images folder."""
        results = []
        
        # Get all PNG images from the images folder
        image_files = list(self.images_folder.glob("*.png"))
        
        if not image_files:
            print("No PNG images found in the images folder.")
            return results
        
        print(f"Found {len(image_files)} images to analyze...")
        
        for i, image_path in enumerate(image_files, 1):
            print(f"Analyzing image {i}/{len(image_files)}: {image_path.name}")
            
            analysis = self.analyze_gemstone(image_path)
            results.append(analysis)
            
            # Save individual result
            output_file = self.output_folder / f"{image_path.stem}_analysis.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            print(f"Saved analysis to {output_file}")
        
        return results
    
    def save_combined_results(self, results: List[Dict[str, Any]]):
        """Save all results to a combined JSON file."""
        combined_output = {
            "total_images": len(results),
            "analysis_date": "2025-07-11",
            "results": results
        }
        
        output_file = self.output_folder / "combined_gemstone_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_output, f, indent=2, ensure_ascii=False)
        
        print(f"Combined results saved to {output_file}")
    
    def generate_summary_report(self, results: List[Dict[str, Any]]):
        """Generate a summary report of the analysis."""
        summary = {
            "total_images_analyzed": len(results),
            "successful_analyses": len([r for r in results if "error" not in r]),
            "failed_analyses": len([r for r in results if "error" in r]),
            "gemstone_types_identified": {},
            "average_confidence": 0
        }
        
        # Count gemstone types and calculate average confidence
        gemstone_counts = {}
        total_confidence = 0
        successful_results = [r for r in results if "error" not in r]
        
        for result in successful_results:
            name = result["english"]["name"]
            confidence = result["english"]["confidence"]
            
            if name in gemstone_counts:
                gemstone_counts[name] += 1
            else:
                gemstone_counts[name] = 1
            
            total_confidence += confidence
        
        summary["gemstone_types_identified"] = gemstone_counts
        if successful_results:
            summary["average_confidence"] = total_confidence / len(successful_results)
        
        # Save summary
        summary_file = self.output_folder / "analysis_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Summary report saved to {summary_file}")
        return summary

def main():
    """Main function to run the gemstone analysis."""
    print("=== Gemstone Image Analysis with OpenAI ===")
    print()
    print("⚠️  COST WARNING: This tool uses OpenAI's paid API")
    print("💰 Each image analysis will charge your OpenAI account")
    print("📊 Estimated cost: $0.01-0.05 per image")
    print("🔍 Monitor your usage at: https://platform.openai.com/usage")
    print()
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
        print("❌ Error: Please set your OpenAI API key in the .env file")
        print("Edit the .env file and replace 'your_openai_api_key_here' with your actual API key")
        return
    
    # Initialize analyzer
    analyzer = GemstoneAnalyzer()
    
    # Analyze all images
    results = analyzer.analyze_all_images()
    
    if not results:
        print("No images were analyzed.")
        return
    
    # Save combined results
    analyzer.save_combined_results(results)
    
    # Generate summary report
    summary = analyzer.generate_summary_report(results)
    
    print()
    print("=== Analysis Complete ===")
    print(f"✅ Successfully analyzed {summary['successful_analyses']} images")
    if summary['failed_analyses'] > 0:
        print(f"❌ Failed to analyze {summary['failed_analyses']} images")
    print(f"📊 Average confidence: {summary['average_confidence']:.1f}%")
    print(f"💎 Gemstone types identified: {len(summary['gemstone_types_identified'])}")
    print()
    print("Results saved in the 'output' folder:")
    print("- Individual analysis files: {image_name}_analysis.json")
    print("- Combined results: combined_gemstone_analysis.json")
    print("- Summary report: analysis_summary.json")

if __name__ == "__main__":
    main()