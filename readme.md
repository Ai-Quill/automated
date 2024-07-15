# AutoPilot

AutoPilot is a Python-based automation portal that allows users to run various automation scripts directly from a web interface built using Streamlit.

## Features

- **AudioBook Converter**: Convert PDF files into audiobooks.
- **Tab Opener**: Open multiple URLs with a single click.
- **Image Downloader**: Download and view images from the web.
- **Code Analyzer**: Analyze Python code using Pylint and Flake8.
- **Fake Data Generator**: Generate realistic-looking fake datasets.
- **Background Remover**: Remove backgrounds from images.
- **Resource Monitor**: Monitor system resources.
- **Bulk Email Sender**: Send bulk emails efficiently.
- **Clipboard Manager**: Keep track of everything copied.
- **Article Summarizer**: Generate summaries of articles.
- **Spell Checker**: Detect and correct spelling and grammar mistakes.
- **Link Checker**: Check the web connectivity of multiple URLs.
- **News Reader**: Scrape and read trending news headlines out loud.
- **QR Code Generator**: Create customized QR codes.
- **URL Shortener**: Convert long URLs into short ones.
- **Hydration Reminder**: Stay hydrated with regular water reminders.
- **YouTube Downloader**: Download YouTube videos in both audio and video formats.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/autopilot.git
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
    
3. Ensure `chromedriver` is installed and available in your PATH for image downloading using `selenium`.

## Usage

1. Run the AutoPilot app:
    ```sh
    streamlit run app.py
    ```

2. Open your web browser and navigate to `localhost:8501`.

3. Use the sidebar to select and run various automation scripts as needed.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
