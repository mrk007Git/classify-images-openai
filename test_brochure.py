"""
Test script to generate a sample brochure with a few gemstones
"""

import json
from pathlib import Path
from make_pdf_brochure import GemstoneBrochureGenerator

def create_sample_brochure():
    """Create a sample brochure with just the first 3 gemstones for testing."""
    
    # Load analysis data
    analysis_file = Path("output/combined_gemstone_analysis.json")
    if not analysis_file.exists():
        print("❌ Error: No analysis data found.")
        print("Please run the main gemstone analysis script first (main.py)")
        return
    
    try:
        with open(analysis_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_results = data.get('results', [])
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    # Take only first 3 valid gemstones for sample
    valid_gemstones = [g for g in all_results if 'error' not in g][:3]
    
    if not valid_gemstones:
        print("No valid gemstones found for sample.")
        return
    
    # Create sample data structure
    sample_data = {
        "total_images": len(valid_gemstones),
        "analysis_date": "2025-07-11",
        "results": valid_gemstones
    }
    
    # Save sample data
    sample_file = Path("output/sample_gemstone_analysis.json")
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    # Generate sample brochure
    generator = GemstoneBrochureGenerator(str(sample_file))
    output_file = generator.generate_brochure("sample_gemstone_brochure.pdf")
    
    if output_file:
        print(f"✅ Sample brochure created: {output_file}")
        print(f"📖 Contains {len(valid_gemstones)} gemstones for preview")

if __name__ == "__main__":
    print("=== Sample Brochure Generator ===")
    create_sample_brochure()
