"""
Example script showing how to use the GemstoneAnalyzer class
"""

from main import GemstoneAnalyzer
import os

def example_usage():
    """Example of how to use the gemstone analyzer."""
    
    # Check if API key is configured
    if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
        print("Please configure your OpenAI API key in the .env file first!")
        return
    
    # Initialize the analyzer
    analyzer = GemstoneAnalyzer()
    
    # Option 1: Analyze all images at once
    print("Analyzing all images...")
    results = analyzer.analyze_all_images()
    
    # Option 2: Analyze a single image (example)
    # from pathlib import Path
    # single_result = analyzer.analyze_gemstone(Path("images/IMG_5982_bg_removed.png"))
    # print(f"Single analysis result: {single_result}")
    
    # Save results
    analyzer.save_combined_results(results)
    summary = analyzer.generate_summary_report(results)
    
    print(f"Analysis complete! Processed {len(results)} images.")
    print(f"Check the 'output' folder for detailed results.")

if __name__ == "__main__":
    example_usage()
