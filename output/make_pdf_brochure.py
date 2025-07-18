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
            fontSize=16,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # Gemstone name style
        self.name_style = ParagraphStyle(
            'GemstoneName',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        )
        
        # Description style
        self.desc_style = ParagraphStyle(
            'Description',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=11
        )
        
        # Areas style
        self.areas_style = ParagraphStyle(
            'Areas',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=4,
            alignment=TA_LEFT,
            fontName='Helvetica-Oblique',
            textColor=colors.darkred
        )
        
        # Language header style
        self.lang_style = ParagraphStyle(
            'Language',
            parent=self.styles['Heading3'],
            fontSize=10,
            spaceAfter=3,
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

    def resize_image(self, image_path: Path, max_width: float = 2.0 * inch, max_height: float = 1.5 * inch) -> tuple[str, float, float]:
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

    def create_gemstone_entry(self, gemstone_data: Dict[str, Any]) -> List:
        """Create a table entry for a single gemstone."""
        # Get image path
        image_filename = gemstone_data.get('image_filename', '')
        image_path = self.images_folder / image_filename
        
        # Create image element
        if image_path.exists():
            img_path, img_width, img_height = self.resize_image(image_path)
            img_element = Image(img_path, width=img_width, height=img_height)
        else:
            img_element = Paragraph(f"Image not found:<br/>{image_filename}", self.desc_style)

        # Extract data
        english_data = gemstone_data.get('english', {})
        german_data = gemstone_data.get('german', {})
        
        # Create text content
        content_elements = []
        
        # English section
        content_elements.append(Paragraph("🇬🇧 English", self.lang_style))
        content_elements.append(Paragraph(f"<b>{english_data.get('name', 'Unknown')}</b>", self.name_style))
        
        # Wrap description text
        eng_desc = self.wrap_text(english_data.get('description', 'No description available'), 150)
        content_elements.append(Paragraph(eng_desc, self.desc_style))
        
        # Areas found
        eng_areas = english_data.get('areas_found', [])
        if eng_areas:
            areas_text = f"<b>Found in:</b> {', '.join(eng_areas)}"
            content_elements.append(Paragraph(areas_text, self.areas_style))
        
        # Confidence
        confidence = english_data.get('confidence', 0)
        content_elements.append(Paragraph(f"<b>Confidence:</b> {confidence}%", self.areas_style))
        
        content_elements.append(Spacer(1, 8))
        
        # German section
        content_elements.append(Paragraph("🇩🇪 Deutsch", self.lang_style))
        content_elements.append(Paragraph(f"<b>{german_data.get('name', 'Unbekannt')}</b>", self.name_style))
        
        # Wrap description text
        ger_desc = self.wrap_text(german_data.get('description', 'Keine Beschreibung verfügbar'), 150)
        content_elements.append(Paragraph(ger_desc, self.desc_style))
        
        # Areas found
        ger_areas = german_data.get('areas_found', [])
        if ger_areas:
            areas_text = f"<b>Gefunden in:</b> {', '.join(ger_areas)}"
            content_elements.append(Paragraph(areas_text, self.areas_style))
        
        # Combine all content elements
        text_content = content_elements
        
        return [img_element, text_content]

    def create_brochure_page(self, gemstones: List[Dict[str, Any]]) -> List:
        """Create a page with up to 4 gemstones (2x2 grid)."""
        story = []
        
        # Create table data for the page
        table_data = []
        
        # Process gemstones in pairs for 2x2 layout
        for i in range(0, len(gemstones), 2):
            row = []
            
            # First gemstone in the row
            if i < len(gemstones):
                gemstone_entry = self.create_gemstone_entry(gemstones[i])
                row.extend(gemstone_entry)
            else:
                row.extend(['', ''])
            
            # Second gemstone in the row
            if i + 1 < len(gemstones):
                gemstone_entry = self.create_gemstone_entry(gemstones[i + 1])
                row.extend(gemstone_entry)
            else:
                row.extend(['', ''])
            
            table_data.append(row)
        
        # Create table
        table = Table(table_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table)
        return story

    def generate_brochure(self, output_filename: str = "gemstone_brochure.pdf"):
        """Generate the complete PDF brochure."""
        # Load analysis data
        gemstones = self.load_analysis_data()
        
        if not gemstones:
            print("No gemstone data available. Please run the analysis first.")
            return
        
        # Filter out any gemstones with errors
        valid_gemstones = [g for g in gemstones if 'error' not in g]
        
        if not valid_gemstones:
            print("No valid gemstone analyses found.")
            return
        
        print(f"Creating brochure with {len(valid_gemstones)} gemstones...")
        
        # Set up PDF document
        output_path = self.output_folder / output_filename
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Build the story
        story = []
        
        # Add title page
        story.append(Paragraph("Semi-Precious Gemstone Collection", self.title_style))
        story.append(Paragraph("Halbedelstein-Sammlung", self.title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Analysis of {len(valid_gemstones)} gemstone specimens", self.desc_style))
        story.append(Paragraph(f"Analyse von {len(valid_gemstones)} Edelstein-Exemplaren", self.desc_style))
        story.append(Spacer(1, 30))
        
        # Process gemstones in groups of 4 per page
        for i in range(0, len(valid_gemstones), 4):
            page_gemstones = valid_gemstones[i:i+4]
            page_story = self.create_brochure_page(page_gemstones)
            story.extend(page_story)
            
            # Add page break if not the last page
            if i + 4 < len(valid_gemstones):
                story.append(PageBreak())
        
        # Build the PDF
        try:
            doc.build(story)
            print(f"✅ Brochure successfully created: {output_path}")
            print(f"📄 Total pages: {(len(valid_gemstones) + 3) // 4 + 1}")  # +1 for title page
            return str(output_path)
        except Exception as e:
            print(f"❌ Error creating brochure: {e}")
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
        print("📋 Layout: 4 gemstones per page (2x2 grid)")
        print("🌐 Languages: English and German descriptions")
        print("📸 Features: Images with detailed descriptions and geographic information")

if __name__ == "__main__":
    main()