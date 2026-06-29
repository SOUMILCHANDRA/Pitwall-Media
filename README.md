# Pitwall-Media

Automated graphic generator for Formula 1 news

[Quick Links: [Introduction](#introduction) · [Tech Stack](#tech-stack) · [Prerequisites / Requirements](#prerequisites--requirements) · [Installation](#installation) · [Configuration](#configuration) · [Usage](#usage) · [Project Structure](#project-structure) · [Features](#features) · [Development](#development) · [Contributing](#contributing) · [License](#license) · [FAQ](#faq)]

## Introduction

Pitwall-Media is a lightweight Python‑based tool that creates race‑day graphics for Formula 1 news outlets. It fetches live session data, processes the information, and renders ready‑to‑publish images using HTML templates and a custom GUI.

The project is fully open‑source and can be extended with additional data sources or visual styles.

## Tech Stack

- **Language:** Python 3.12, HTML, Batchfile
- **Core libraries:** `fastf1`, `pandas`, `playwright`, `google‑genai`, `anthropic`, `jinja2`, `customtkinter`
- **Template engine:** Jinja2
- **Browser automation:** Playwright
- **Data source:** FastF1 (official Formula 1 timing API)

## Prerequisites / Requirements

- Windows 10/11 (Batchfile launcher) or any OS with Python 3.8+ installed
- Internet connection for live data retrieval
- Git (optional, for cloning the repository)

## Installation

1. Clone the repository  

   ```bash
   git clone https://github.com/SOUMILCHANDRA/Pitwall-Media.git
   cd Pitwall-Media
   ```

2. Create a virtual environment (recommended)

   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   .\venv\Scripts\activate    # Windows
   ```

3. Install Python dependencies  

   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Install Playwright browsers  

   ```bash
   playwright install
   ```

## Configuration

- Edit the **`config.yaml`** (or create one if missing) to set:
  - `output_path`: directory where generated graphics are saved
  - `template_path`: location of Jinja2 HTML templates
  - API keys for `google-genai` or `anthropic` if you wish to use AI‑enhanced captions

The file follows standard YAML syntax:

```yaml
output_path: ./output
template_path: ./templates
google_genai_key: YOUR_GOOGLE_API_KEY
anthropic_key: YOUR_ANTHROPIC_API_KEY
```

## Usage

Run the main script to generate graphics for the latest Grand Prix:

```bash
python main.py --event "Monaco Grand Prix" --session race
```

Or use the provided Windows batch launcher:

```bash
run.bat
```

The script will:

1. Download the latest session data via FastF1.
2. Render the HTML template with Jinja2.
3. Convert the rendered page to an image using Playwright.
4. Save the final graphic to the configured `output_path`.

## Project Structure

- `requirements.txt` – Python dependencies
- `main.py` – entry point for the generator
- `templates/` – Jinja2 HTML templates for graphics
- `output/` – generated images (created at runtime)
- `config.yaml` – user‑editable configuration file
- `.agents/` – auxiliary agent files (not required for core operation)
- `.github/` – CI/CD and contribution guidelines
- `run.bat` – Windows batch file that activates the virtual environment and runs `main.py`

## Features

- **Live data:** Pulls up‑to‑the‑minute timing and classification data.
- **Customizable templates:** Modify HTML/CSS to match your branding.
- **AI‑enhanced captions:** Optional integration with Google‑GenAI or Anthropic.
- **Cross‑platform rendering:** Uses Playwright to generate PNG/SVG output.
- **Simple CLI:** Minimal command‑line arguments for quick operation.

## Development

To contribute new templates or extend functionality:

1. Fork the repository.
2. Create a feature branch.  

   ```bash
   git checkout -b feature/your-feature
   ```

3. Install development dependencies (if any) and make your changes.
4. Run the test suite (currently none; add tests as needed).  

   ```bash
   pytest
   ```

5. Submit a pull request with a clear description of the changes.

## Contributing

Contributions are welcome! Please follow these guidelines:

- Keep code style consistent with PEP 8.
- Update `README.md` and `config.yaml` examples when adding new features.
- Document any new dependencies in `requirements.txt`.
- Ensure that generated graphics still meet the visual standards of existing templates.

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for full details.

## FAQ

**Q: Which Formula 1 sessions are supported?**  
A: Practice, Qualifying, and Race sessions are fully supported. Additional session types can be added by extending the FastF1 query logic.

**Q: Can I run the tool on macOS or Linux?**  
A: Yes. Use the Python entry point (`python main.py`) instead of the Windows batch file.

**Q: Do I need an API key for FastF1?**  
A: No. FastF1 accesses publicly available timing data without authentication.

**Q: How do I change the output image format?**  
A: Modify the Playwright screenshot options in `main.py`. The default is PNG; you can set `type: "jpeg"` for JPEG output.
