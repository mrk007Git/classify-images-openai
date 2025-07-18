#!/usr/bin/env python3
"""
PDF Brochure Generator for Gemstone Analysis

Generates beautiful PDF brochures from gemstone analysis results with bilingual 
descriptions and professional layout.

License: MIT License
Copyright (c) 2025

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

DISCLAIMER: This tool generates brochures based on AI analysis results. 
Information provided is for educational purposes only and should not be used 
for professional appraisal or commercial decisions.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from PIL import Image as PILImage
import textwrap

class GemstoneBrochureGenerator:
    def __init__(self, analysis_file: str = "output/combined_gemstone_analysis.json"):
        """Initialize the brochure generator."""
        self.analysis_file = Path(analysis_file)
        self.images_folder = Path("images")
        self.output_folder = Path("output")
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Set up custom paragraph styles for the brochure."""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # Gemstone name style
        self.name_style = ParagraphStyle(
            'GemstoneName',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        )
        
        # Description style
        self.desc_style = ParagraphStyle(
            'Description',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=15
        )
        
        # Areas style
        self.areas_style = ParagraphStyle(
            'Areas',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_LEFT,
            fontName='Helvetica-Oblique',
            textColor=colors.darkred
        )
        
        # Language header style
        self.lang_style = ParagraphStyle(
            'Language',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=6,
            spaceBefore=10,
            alignment=TA_LEFT,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )

    def load_analysis_data(self) -> List[Dict[str, Any]]:
        """Load the gemstone analysis data from JSON file."""
        try:
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('results', [])
        except FileNotFoundError:
            print(f"Error: Analysis file {self.analysis_file} not found.")
            print("Please run the main analysis script first.")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.analysis_file}")
            return []

    def resize_image(self, image_path: Path, max_width: float = 4.0 * inch, max_height: float = 3.0 * inch) -> tuple[str, float, float]:
        """Resize image to fit in the specified dimensions while maintaining aspect ratio."""
        try:
            # Open the image to get dimensions
            with PILImage.open(image_path) as img:
                width, height = img.size
                
            # Calculate scaling factor
            width_scale = max_width / width
            height_scale = max_height / height
            scale = min(width_scale, height_scale)
            
            new_width = width * scale
            new_height = height * scale
            
            return str(image_path), new_width, new_height
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return str(image_path), max_width, max_height

    def wrap_text(self, text: str, max_length: int = 80) -> str:
        """Wrap text to fit within specified character limit."""
        if len(text) <= max_length:
            return text
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return ' '.join(lines)

    def create_gemstone_page(self, gemstone_data: Dict[str, Any]) -> List:
        """Create a full page for a single gemstone."""
        story = []
        
        # Get image path and create image element
        image_filename = gemstone_data.get('image_filename', '')
        image_path = self.images_folder / image_filename
        
        if image_path.exists():
            img_path, img_width, img_height = self.resize_image(image_path)
            img_element = Image(img_path, width=img_width, height=img_height)
            
            # Center the image
            img_table = Table([[img_element]], colWidths=[6*inch])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(img_table)
        else:
            story.append(Paragraph(f"Image not found: {image_filename}", self.desc_style))
        
        story.append(Spacer(1, 15))
        
        # Extract data
        english_data = gemstone_data.get('english', {})
        german_data = gemstone_data.get('german', {})
        
        # English section
        story.append(Paragraph("🇬🇧 English", self.lang_style))
        story.append(Paragraph(f"{english_data.get('name', 'Unknown')}", self.name_style))
        
        eng_desc = english_data.get('description', 'No description available')
        story.append(Paragraph(eng_desc, self.desc_style))
        
        # Areas found
        eng_areas = english_data.get('areas_found', [])
        if eng_areas:
            areas_text = f"<b>Geographic locations:</b> {', '.join(eng_areas)}"
            story.append(Paragraph(areas_text, self.areas_style))
        
        # Confidence
        confidence = english_data.get('confidence', 0)
        story.append(Paragraph(f"<b>AI Confidence Level:</b> {confidence}%", self.areas_style))
        
        story.append(Spacer(1, 15))
        
        # German section
        story.append(Paragraph("🇩🇪 Deutsch", self.lang_style))
        story.append(Paragraph(f"{german_data.get('name', 'Unbekannt')}", self.name_style))
        
        ger_desc = german_data.get('description', 'Keine Beschreibung verfügbar')
        story.append(Paragraph(ger_desc, self.desc_style))
        
        # Areas found in German
        ger_areas = german_data.get('areas_found', [])
        if ger_areas:
            areas_text = f"<b>Geografische Standorte:</b> {', '.join(ger_areas)}"
            story.append(Paragraph(areas_text, self.areas_style))
        
        # Confidence in German
        story.append(Paragraph(f"<b>KI-Vertrauensniveau:</b> {confidence}%", self.areas_style))
        
        return story

    def generate_brochure(self, output_filename: str = "gemstone_brochure.pdf"):
        """Generate the complete PDF brochure with one gemstone per page."""
        # Load analysis data
        gemstones = self.load_analysis_data()
        
        if not gemstones:
            print("No gemstone data available. Please run the analysis first.")
            return None
        
        # Filter out any gemstones with errors
        valid_gemstones = [g for g in gemstones if 'error' not in g]
        
        if not valid_gemstones:
            print("No valid gemstone analyses found.")
            return None
        
        print(f"Creating brochure with {len(valid_gemstones)} gemstones (one per page)...")
        
        # Set up PDF document
        output_path = self.output_folder / output_filename
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=25*mm,
            leftMargin=25*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        # Build the story
        story = []
        
        # Add title page
        story.append(Spacer(1, 50))
        story.append(Paragraph("Semi-Precious Gemstone Collection", self.title_style))
        story.append(Paragraph("Halbedelstein-Sammlung", self.title_style))
        story.append(Spacer(1, 40))
        
        # Add subtitle with specimen count
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.desc_style,
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        story.append(Paragraph(f"Analysis of {len(valid_gemstones)} gemstone specimens using AI technology", subtitle_style))
        story.append(Paragraph(f"Analyse von {len(valid_gemstones)} Edelstein-Exemplaren mit KI-Technologie", subtitle_style))
        story.append(Spacer(1, 30))
        
        # Add description
        intro_text = """This collection showcases semi-precious gemstones analyzed using advanced artificial intelligence. 
        Each specimen has been carefully examined to provide detailed information about its characteristics, 
        geographic origins, and mineralogical properties."""
        story.append(Paragraph(intro_text, self.desc_style))
        
        intro_text_de = """Diese Sammlung zeigt Halbedelsteine, die mit fortschrittlicher künstlicher Intelligenz analysiert wurden. 
        Jedes Exemplar wurde sorgfältig untersucht, um detaillierte Informationen über seine Eigenschaften, 
        geografischen Ursprünge und mineralogischen Eigenschaften zu liefern."""
        story.append(Paragraph(intro_text_de, self.desc_style))
        
        story.append(PageBreak())
        
        # Add each gemstone on its own page
        for i, gemstone in enumerate(valid_gemstones):
            # Add page number at the top
            page_num_style = ParagraphStyle(
                'PageNumber',
                parent=self.desc_style,
                fontSize=10,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            story.append(Paragraph(f"Specimen {i+1} of {len(valid_gemstones)} | Exemplar {i+1} von {len(valid_gemstones)}", page_num_style))
            story.append(Spacer(1, 10))
            
            # Add gemstone content
            gemstone_story = self.create_gemstone_page(gemstone)
            story.extend(gemstone_story)
            
            # Add page break if not the last gemstone
            if i < len(valid_gemstones) - 1:
                story.append(PageBreak())
        
        # Build the PDF
        try:
            doc.build(story)
            print(f"✅ Brochure successfully created: {output_path}")
            print(f"📄 Total pages: {len(valid_gemstones) + 1}")  # +1 for title page
            return str(output_path)
        except Exception as e:
            print(f"❌ Error creating brochure: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """Main function to generate the gemstone brochure."""
    print("=== Gemstone PDF Brochure Generator ===")
    print()
    
    # Check if analysis data exists
    analysis_file = Path("output/combined_gemstone_analysis.json")
    if not analysis_file.exists():
        print("❌ Error: No analysis data found.")
        print("Please run the main gemstone analysis script first (main.py)")
        return
    
    # Generate brochure
    generator = GemstoneBrochureGenerator()
    output_file = generator.generate_brochure()
    
    if output_file:
        print()
        print("=== Brochure Generation Complete ===")
        print(f"📱 PDF saved as: {output_file}")
        print("📋 Layout: One gemstone per page with large image")
        print("🌐 Languages: English and German descriptions")
        print("📸 Features: High-quality images with detailed bilingual descriptions")
        print("📊 Geographic information and AI confidence levels included")
        print("💡 Tip: Open the PDF to view your beautiful gemstone collection!")

if __name__ == "__main__":
    main()