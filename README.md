# Gemstone Image Analysis with OpenAI

This project uses OpenAI's GPT-4 Vision API to analyze semi-precious gemstone images and provide structured output in both English and German.

## Features

- Analyzes gemstone images using OpenAI's latest vision model (gpt-4o-mini)
- Provides structured output with:
  - Gemstone name
  - Detailed description
  - Geographic areas where found
  - Confidence level
- Output in both English and German
- Saves individual and combined JSON results
- Generates summary reports
- Creates PDF brochures of analyzed gemstones

## Setup

⚠️ **COST WARNING**: This software uses OpenAI's paid API services. Each image analysis will incur charges to your OpenAI account. See [Cost Information](#cost-estimation) below for details.

1. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Set up OpenAI API Key**
   - Edit the `.env` file
   - Replace `your_openai_api_key_here` with your actual OpenAI API key
   - You can get an API key from: https://platform.openai.com/api-keys
   - **Important**: Ensure you have sufficient credits in your OpenAI account

3. **Add Images**
   - Place your gemstone images in the `images/` folder
   - Supported format: PNG files

## Usage

Run the analysis:
```powershell
python main.py
```

Generate a beautiful PDF brochure of your analyzed gemstones:
```powershell
python make_pdf_brochure.py
```

## Output

The script creates an `output/` folder with:

- **Individual analysis files**: `{image_name}_analysis.json`
- **Combined results**: `combined_gemstone_analysis.json`
- **Summary report**: `analysis_summary.json`
- **PDF Brochure**: `gemstone_brochure.pdf`

## Output Format

Each analysis includes:

```json
{
  "english": {
    "name": "Amethyst",
    "description": "A purple variety of quartz...",
    "areas_found": ["Brazil", "Uruguay", "Madagascar"],
    "confidence": 85
  },
  "german": {
    "name": "Amethyst",
    "description": "Eine violette Varietät von Quarz...",
    "areas_found": ["Brasilien", "Uruguay", "Madagaskar"],
    "confidence": 85
  },
  "image_filename": "IMG_5982_bg_removed.png"
}
```

## Requirements

- Python 3.7+
- OpenAI API key
- Internet connection for API calls

## Cost Estimation

💰 **OpenAI API Costs**: This software uses OpenAI's paid API and **will charge your account** for each image analyzed.

- **Model used**: GPT-4o-mini (vision model)
- **Estimated cost**: $0.01-0.05 per image (varies by image size and description length)
- **Example**: Analyzing 25 gemstones ≈ $0.25-1.25 total
- **Your responsibility**: Monitor your OpenAI account usage and billing
- **Cost control**: Set usage limits in your OpenAI account dashboard

📊 **Cost factors**:
- Image file size (larger images cost more)
- Response length (detailed descriptions cost more)
- API pricing changes (check current rates at https://openai.com/pricing)

⚠️ **Important**: The authors are not responsible for any OpenAI API charges incurred.

## Important Disclaimers

⚠️ **AI Analysis Accuracy**: This tool uses artificial intelligence for gemstone identification. Results are provided for informational and educational purposes only. AI analysis may not be 100% accurate and should not be relied upon for:
- Professional gemstone appraisal
- Commercial transactions
- Investment decisions
- Insurance claims
- Scientific research requiring certified analysis

🔬 **Professional Verification Required**: For accurate identification, always consult with:
- Certified gemologists
- Professional mineralogists
- Accredited gemological laboratories
- Licensed appraisers

💎 **Use at Your Own Risk**: The creators of this software are not responsible for any decisions made based on AI analysis results.

💰 **API Costs**: You are responsible for all OpenAI API charges incurred while using this software. Monitor your usage and set appropriate billing limits.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

- ✅ **Free to use**: Commercial and personal use allowed
- ✅ **Modify and distribute**: Create derivative works
- ✅ **No liability**: Authors not responsible for any damages
- ✅ **No warranty**: Software provided "as is"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

This is an open-source project provided as-is. For issues or questions:
1. Check existing GitHub issues
2. Create a new issue with detailed information
3. Community support only - no commercial support provided
