import streamlit as st
import subprocess
import os
import time
import yaml
import inspect
from rembg import remove
from PIL import Image
from simple_image_download import simple_image_download as simp
from faker import Faker
import random
import pandas as pd
import qrcode
from plyer import notification
import requests
import pyttsx3
import pyshorteners
import numpy as np
import webbrowser
import lmproof
import smtplib
from email.message import EmailMessage
import psutil
import pyperclip
import yt_dlp
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageFont


# Load YAML file
def load_scripts_from_yaml(yaml_file):
    with open(yaml_file, 'r') as stream:
        data = yaml.safe_load(stream)
        return data

# Save uploaded file
def save_uploaded_file(uploadedfile):
    if not os.path.exists("tempDir"):
        os.makedirs("tempDir")
    
    file_path = os.path.join("tempDir", uploadedfile.name)
    with open(file_path, "wb") as f:
        f.write(uploadedfile.getbuffer())
    return file_path

# Load scripts data from yaml file
scripts_data = load_scripts_from_yaml('scripts.yaml')


# Handling different input types, including select and slider
def handle_inputs(selected_script):
    inputs = {}
    operation = None

    # Handle initial inputs
    for input_item in selected_script['inputs']:
        key = input_item['name']
        if input_item['type'] == 'file':
            inputs[input_item['name']] = st.file_uploader(f"Upload {input_item['name']}", type=input_item['format'].split(', '), key=key)
        elif input_item['type'] == 'files':
            inputs[input_item['name']] = st.file_uploader(f"Upload {input_item['name']}", type=input_item['format'].split(', '), accept_multiple_files=True, key=key)
        elif input_item['type'] == 'text' and 'options' in input_item:
            inputs[input_item['name']] = st.selectbox(f"Select {input_item['name']}", input_item['options'], key=key)
        elif input_item['type'] == 'text':
            inputs[input_item['name']] = st.text_input(f"Enter {input_item['name']}", key=key)
        elif input_item['type'] == 'number':
            inputs[input_item['name']] = st.number_input(f"Enter {input_item['name']}", min_value=1, step=1, key=key)
        elif input_item['type'] == 'textarea':
            inputs[input_item['name']] = st.text_area(f"Input {input_item['name']} (one per line)", key=key)
        elif input_item['type'] == 'select':
            inputs[input_item['name']] = st.selectbox(f"Choose {input_item['name']}", options=input_item['options'], key=key)
            if input_item['name'] == 'Operation':
                operation = inputs[input_item['name']]
        elif input_item['type'] == 'slider':
            inputs[input_item['name']] = st.slider(f"Adjust {input_item['name']}", min_value=float(input_item.get('min', 0)), max_value=float(input_item.get('max', 3)), value=float(input_item.get('value', 1)), step=float(input_item.get('step', 0.1)), key=key)
        
    # Conditionally render inputs based on Operation
    if operation:
        st.write(f"Selected Operation: {operation}")
        dependent_inputs = {
            "Convert Format": ["Format"],
            "Combine Images": ["Second Image"],
            "Resize": ["New Width", "New Height"],
            "Flip": ["Direction"],
            "Blur": ["Blur Radius"],
            "Add Shadow": [],
            "Crop": ["Left", "Upper", "Right", "Lower"],
            "Adjust Brightness": ["Brightness"],
            "Add Watermark": ["Watermark Text"],
            "Rotate": ["Angle"],
        }
        for dependent_input in dependent_inputs.get(operation, []):
            for input_item in selected_script['inputs']:
                if input_item['name'] == dependent_input:
                    key = f"{operation}_{dependent_input}"
                    if input_item['type'] == 'file':
                        inputs[dependent_input] = st.file_uploader(f"Upload {dependent_input}", type=input_item['format'].split(', '), key=key)
                    elif input_item['type'] == 'text':
                        inputs[dependent_input] = st.text_input(f"Enter {dependent_input}", key=key)
                    elif input_item['type'] == 'number':
                        inputs[dependent_input] = st.number_input(f"Enter {dependent_input}", min_value=1, step=1, key=key)
                    elif input_item['type'] == 'select':
                        inputs[dependent_input] = st.selectbox(f"Choose {dependent_input}", options=input_item['options'], key=key)
                    elif input_item['type'] == 'slider':
                        inputs[dependent_input] = st.slider(f"Adjust {dependent_input}", min_value=float(input_item.get('min', 0.0)), max_value=float(input_item.get('max', 3.0)), value=float(input_item.get('value', 1.0)), step=float(input_item.get('step', 0.1)), key=key)

    return inputs


def main():
    if 'selected_script_title' not in st.session_state:
        st.session_state.selected_script_title = ''

    with open("style.css") as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

    st.title('Python Automated Scripts')

    st.markdown(" ")

    st.sidebar.title("Python Automation Portal")

    st.sidebar.markdown("""
    This application allows users to run various Python automation scripts.
    Select a script from the dropdown below to get started.
    """)

    categories = sorted(set(script['category'] for script in scripts_data['scripts']))
    selected_categories = st.sidebar.multiselect("Filter by Categories", options=categories, default=categories)
    st.sidebar.markdown("---")
    st.sidebar.markdown(
            '<h5>Made with ❤ in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://twitter.com/tuantruong">@tuantruong</a></h5>',
            unsafe_allow_html=True,
        )

    if not selected_categories:
        selected_scripts = scripts_data['scripts']
    else:
        selected_scripts = [script for script in scripts_data['scripts'] if script['category'] in selected_categories]

    script_titles = [script['title'] for script in selected_scripts]

    selected_script_title = st.selectbox(
        "Choose an Automation Script", 
        script_titles, 
        index=script_titles.index(st.session_state.selected_script_title) if st.session_state.selected_script_title in script_titles else 0
    )
    st.session_state.selected_script_title = selected_script_title

    selected_script = next(script for script in selected_scripts if script['title'] == selected_script_title)

    st.markdown(f"### {selected_script['title']}")
    st.write(selected_script['description'])

    inputs = handle_inputs(selected_script)

    if st.button("Run Script"):
        run_selected_script(selected_script, inputs)

    with st.expander("Function Code"):
        function_code = get_function_code_by_id(selected_script['id'])
        st.code(function_code, language='python')


def get_function_code_by_id(script_id):
    function_code = {
        1: run_background_remover,
        2: run_qr_code_generator,
        3: run_fake_data_generator,
        4: run_url_shortener,
        5: run_youtube_downloader,
        6: run_bulk_email_sender,
        7: run_image_downloader,
        8: run_audiobook_converter,
        9: run_code_analyzer,
        10: run_resource_monitor,
        11: run_clipboard_manager,
        12: run_spell_checker,
        13: run_link_checker,
        14: run_news_reader,
        15: run_article_summarizer,
        16: run_image_editor,
    }
    function = function_code.get(script_id)
    return inspect.getsource(function) if function else "Function not implemented."

def run_selected_script(script, inputs):
    if script['id'] == 1:
        run_background_remover(inputs['Image file'])
    elif script['id'] == 2:
        run_qr_code_generator(inputs['Link'], inputs['Filename'])
    elif script['id'] == 3:
        run_fake_data_generator(inputs['Number of entries'])
    elif script['id'] == 4:
        run_url_shortener(inputs['Long URL'])
    elif script['id'] == 5:
        run_youtube_downloader(inputs)
    elif script['id'] == 6:
        run_bulk_email_sender(inputs['Sender email'], inputs['Sender password'], inputs['Emails file'])
    elif script['id'] == 7:
        run_image_downloader(inputs)
    elif script['id'] == 8:
        run_audiobook_converter(inputs['PDF file'])
    elif script['id'] == 9:
        run_code_analyzer(inputs['Python files'])
    elif script['id'] == 10:
        run_resource_monitor(inputs['CPU threshold'], inputs['Memory threshold'], inputs['GPU threshold'], inputs['Battery threshold'])
    elif script['id'] == 11:
        run_clipboard_manager()
    elif script['id'] == 12:
        run_spell_checker(inputs['Input text'])
    elif script['id'] == 13:
        run_link_checker(inputs)
    elif script['id'] == 14:
        run_news_reader(inputs['News API key'])
    elif script['id'] == 15:
        run_article_summarizer(inputs['Article URL'])
    elif script['id'] == 16:
        run_image_editor(inputs)

def run_background_remover(input_img_file):
    input_img_path = save_uploaded_file(input_img_file)
    output_img_path = input_img_path.replace('.', '_rmbg.').replace('jpg', 'png').replace('jpeg', 'png')

    try:
        # Open the input image
        inp = Image.open(input_img_path)

        # Remove the background
        output = remove(inp)

        # Save the output image in PNG format to support RGBA
        output.save(output_img_path, "PNG")

        # Display the images side by side
        col1, col2 = st.columns(2)

        with col1:
            st.header("Before")
            st.image(input_img_path, caption="Original Image")
            with open(input_img_path, "rb") as img_file:
                st.download_button(label="Download Original Image", data=img_file, file_name=os.path.basename(input_img_path), mime="image/jpeg")

        with col2:
            st.header("After")
            st.image(output_img_path, caption="Image with Background Removed")
            with open(output_img_path, "rb") as img_file:
                st.download_button(label="Download Processed Image", data=img_file, file_name=os.path.basename(output_img_path), mime="image/png")

        st.success("Background removed successfully!")

    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_qr_code_generator(link, filename):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_file_path = os.path.join("tempDir", filename)
        img.save(img_file_path)
        st.image(img_file_path, caption=f"QR Code for {link}")
        with open(img_file_path, "rb") as img_file:
            st.download_button(label="Download QR Code", data=img_file, file_name=filename, mime="image/png")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_fake_data_generator(num_entries):
    try:
        fake = Faker()
        data = []
        for _ in range(num_entries):
            entry = {
                "Name": fake.name(),
                "Address": fake.address(),
                "Email": fake.email(),
                "Phone Number": fake.phone_number(),
                "Date of Birth": fake.date_of_birth(minimum_age=18, maximum_age=65),
                "Random Number": random.randint(1, 100),
                "Job Title": fake.job(),
                "Company": fake.company(),
                "Lorem Ipsum Text": fake.text()
            }
            data.append(entry)
        fake_data_df = pd.DataFrame(data)
        st.write(fake_data_df)
        st.success("Fake data generated successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_url_shortener(long_url):
    try:
        s = pyshorteners.Shortener()
        short_url = s.tinyurl.short(long_url)
        st.write("### Shortened URL")
        st.write(short_url)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_youtube_downloader(inputs):
    youtube_url = inputs['YouTube URL']
    format_choice = inputs['Format']

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best' if format_choice == 'Video' else 'bestaudio/best',
        'outtmpl': os.path.join('tempDir', '%(title)s.%(ext)s')
    }

    # Download video
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(youtube_url, download=True)

        download_path = ydl.prepare_filename(result)

        label = "Download Video" if format_choice == 'Video' else "Download Audio"
        mime_type = "video/mp4" if format_choice == 'Video' else "audio/mp3"

        st.success(f"{label} downloaded successfully!")

        with open(download_path, "rb") as file:
            st.download_button(label=label, data=file, file_name=os.path.basename(download_path), mime=mime_type)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_bulk_email_sender(sender_email, sender_password, emails_file):
    file_path = save_uploaded_file(emails_file)
    try:
        df = pd.read_excel(file_path)
        for index, item in df.iterrows():
            email = item[0]
            subject = item[1]
            content = item[2]

            email_msg = EmailMessage()
            email_msg['from'] = sender_email
            email_msg['to'] = email
            email_msg['subject'] = subject
            email_msg.set_content(content)

            with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(sender_email, sender_password)
                smtp.send_message(email_msg)
                st.write(f"Email sent to {email}")
        st.success("All emails sent successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_image_downloader(inputs):
    keyword = inputs['Keyword for images']
    num_images = inputs['Number of images']
    try:
        response = simp.simple_image_download()
        image_paths = response.download(keyword, num_images)
        
        st.success("Images downloaded successfully!")
        
        # Displaying images and providing download links
        if image_paths:
            downloaded_images = response.downloaded_images
            for image_path in downloaded_images:
                st.image(image_path, caption=os.path.basename(image_path))
                with open(image_path, "rb") as img_file:
                    st.download_button(label="Download Image", data=img_file, file_name=os.path.basename(image_path), mime="image/jpeg")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_audiobook_converter(pdf_file):
    import time

    # Ensure the temporary directory exists
    temp_dir = "tempDir"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    file_path = save_uploaded_file(pdf_file)
    try:
        import PyPDF2
        import pyttsx3

        # Open the PDF file
        file = open(file_path, 'rb')
        readpdf = PyPDF2.PdfReader(file)
        
        text_to_speech = ""

        for pagenumber in range(len(readpdf.pages)):
            page = readpdf.pages[pagenumber]
            text = page.extract_text()
            text_to_speech += text + "\n"

        # Generate a unique filename
        timestamp = int(time.time())
        original_filename = os.path.splitext(os.path.basename(file_path))[0]
        audio_filename = os.path.join(temp_dir, f'{original_filename}_{timestamp}.wav')
        
        # Initialize TTS engine
        engine = pyttsx3.init()  # object creation

        # Set properties
        engine.setProperty('rate', 125)  # setting up new voice rate
        engine.setProperty('volume', 1.0)  # setting up volume level between 0 and 1

        # Set voice
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)  # changing index, changes voices. 1 for female

        # Save Voice to a file
        engine.save_to_file(text_to_speech, audio_filename)
        engine.runAndWait()
        engine.stop()

        file.close()

        st.success("Audiobook created successfully!")
        with open(audio_filename, "rb") as file:
            st.download_button(label="Download Audiobook", data=file, file_name=f'{original_filename}_{timestamp}.wav', mime="audio/mpeg")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_code_analyzer(code_files):
    if code_files:
        try:
            all_pylint_results = []
            all_flake8_results = []

            for file in code_files:
                file_path = save_uploaded_file(file)
                st.write(f"Analyzing file: {file.name}")

                # Run pylint and capture output
                pylint_process = subprocess.run(
                    f"pylint {file_path}",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                pylint_result = pylint_process.stdout
                all_pylint_results.append(f"### Pylint results for {file.name}\n```\n{pylint_result}\n```\n")

                # Run flake8 and capture output
                flake8_process = subprocess.run(
                    f"flake8 {file_path}",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                flake8_result = flake8_process.stdout
                all_flake8_results.append(f"### Flake8 results for {file.name}\n```\n{flake8_result}\n```\n")

            st.success("Code analysis completed!")

            # Display all results in markdown
            st.markdown("\n".join(all_pylint_results) + "\n" + "\n".join(all_flake8_results))

        except Exception as e:
            st.error(f"An error occurred: {e}")

def run_resource_monitor(cpu_threshold, memory_threshold, gpu_threshold, battery_threshold):
    while True:
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            gpu_usage = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()

            if cpu_usage >= cpu_threshold:
                st.warning(f"CPU usage is high: {cpu_usage}%")
            if memory_usage >= memory_threshold:
                st.warning(f"Memory usage is high: {memory_usage}%")
            if gpu_usage >= gpu_threshold:
                st.warning(f"GPU usage is high: {gpu_usage}%")
            if battery is not None and battery.percent <= battery_threshold:
                st.warning(f"Battery level is low: {battery.percent}%")

            time.sleep(300)  # Wait for 5 minutes before checking the resources again
        except Exception as e:
            st.error(f"An error occurred: {e}")
            break

def run_clipboard_manager():
    st.title("Clipboard Manager")
    
    # Placeholder for clipboard content list
    if 'clipboard_contents' not in st.session_state:
        st.session_state.clipboard_contents = []

    def update_clipboard():
        new_item = pyperclip.paste()
        if new_item and new_item not in st.session_state.clipboard_contents:
            st.session_state.clipboard_contents.append(new_item)
        st.experimental_rerun()

    # Display the clipboard contents
    st.write("### Clipboard Contents")
    if st.session_state.clipboard_contents:
        for i, item in enumerate(st.session_state.clipboard_contents):
            st.write(f"- {item}")

    # Update clipboard every 5 seconds
    st.button("Refresh Clipboard", on_click=update_clipboard)
    
    time.sleep(5)  # Wait for 5 seconds
    update_clipboard()

def run_spell_checker(sample_text):
    try:
        proof = lmproof.load("en")
        error_free_text = proof.proofread(sample_text)
        st.write("### Corrected Text")
        st.write(error_free_text)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_article_summarizer(url):
    try:
        from bs4 import BeautifulSoup
        def scrape_webpage(url):
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text(separator='\n', strip=True)

        def summarize_article(article_text):
            model_name = "facebook/bart-large-cnn"
            tokenizer = BartTokenizer.from_pretrained(model_name)
            model = BartForConditionalGeneration.from_pretrained(model_name)
            inputs = tokenizer("summarize: " + article_text, return_tensors="pt")
            summary_ids = model.generate(inputs.input_ids, max_length=150, min_length=30)
            return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        article_text = scrape_webpage(url)
        summary = summarize_article(article_text)
        st.write("### Summarized Article")
        st.write(summary)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_spell_checker(sample_text):
    try:
        proof = lmproof.load("en")
        error_free_text = proof.proofread(sample_text)
        st.write("### Corrected Text")
        st.write(error_free_text)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_link_checker(inputs):
    links_file = inputs.get('Links file')
    links_text = inputs.get('Links text')

    links = []
    if links_file is not None:
        file_path = save_uploaded_file(links_file)
        with open(file_path) as file:
            links = file.readlines()
    else:
        links = links_text.split('\n')

    try:
        def get_status(website):
            try:
                status = requests.get(website).status_code
                return "Working" if status == 200 else "Error 404"
            except:
                return "Connection Failed!!"

        web_status_dict = {website: get_status(website) for website in links}
        st.write(web_status_dict)

        csv_name = st.text_input("Enter CSV file name to save results", "web_status.csv")
        if st.button("Save to CSV"):
            with open(csv_name, "w", newline='') as csvfile:
                fieldnames = ["Website", "Status"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for website, status in web_status_dict.items():
                    writer.writerow({"Website": website, "Status": status})
            st.success("Data uploaded to CSV file!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_news_reader(api_key):
    try:
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)

        def speak(audio):
            engine.say(audio)
            engine.runAndWait()

        def trndnews():
            url = f"http://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
            page = requests.get(url).json()
            articles = page["articles"]
            results = [ar["title"] for ar in articles]
            for i, result in enumerate(results):
                st.write(f"{i+1}. {result}")
                speak(result)

        trndnews()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        
def run_image_editor(inputs):
    input_img_file = inputs['Image file']
    operation = inputs['Operation']  # This will handle the operation selection

    input_img_path = save_uploaded_file(input_img_file)
    try:
        # Open the input image
        img = Image.open(input_img_path)
        st.image(img, caption="Original Image")
        st.write("Processing...")

        output_img = None
        output_img_path = None

        # Process the selected option
        if operation == "Convert Format":
            format = inputs['Format']
            output_img_path = os.path.join("tempDir", f"converted_image.{format}")
            img.save(output_img_path, format=format.upper())

        elif operation == "Combine Images":
            second_img_file = inputs['Second Image']
            if second_img_file:
                second_img_path = save_uploaded_file(second_img_file)
                img2 = Image.open(second_img_path)
                combined_img = Image.new('RGB', (img.width + img2.width, max(img.height, img2.height)))
                combined_img.paste(img, (0, 0))
                combined_img.paste(img2, (img.width, 0))
                output_img = combined_img
                output_img_path = os.path.join("tempDir", "combined_image.png")
                combined_img.save(output_img_path)

        elif operation == "Resize":
            new_width = inputs['New Width']
            new_height = inputs['New Height']
            resized_img = img.resize((new_width, new_height))
            output_img = resized_img
            output_img_path = os.path.join("tempDir", "resized_image.png")
            resized_img.save(output_img_path)

        elif operation == "Flip":
            direction = inputs['Direction']
            flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT) if direction == "Horizontal" else img.transpose(Image.FLIP_TOP_BOTTOM)
            output_img = flipped_img
            output_img_path = os.path.join("tempDir", "flipped_image.png")
            flipped_img.save(output_img_path)

        elif operation == "Blur":
            blur_radius = inputs['Blur Radius']
            blurred_img = img.filter(ImageFilter.GaussianBlur(blur_radius))
            output_img = blurred_img
            output_img_path = os.path.join("tempDir", "blurred_image.png")
            blurred_img.save(output_img_path)

        elif operation == "Add Shadow":
            shadow_img = ImageOps.expand(img, border=20, fill="black")
            output_img = shadow_img
            output_img_path = os.path.join("tempDir", "shadow_image.png")
            shadow_img.save(output_img_path)

        elif operation == "Crop":
            left = inputs['Left']
            upper = inputs['Upper']
            right = inputs['Right']
            lower = inputs['Lower']
            cropped_img = img.crop((left, upper, right, lower))
            output_img = cropped_img
            output_img_path = os.path.join("tempDir", "cropped_image.png")
            cropped_img.save(output_img_path)

        elif operation == "Adjust Brightness":
            brightness_factor = inputs['Brightness']
            enhancer = ImageEnhance.Brightness(img)
            bright_img = enhancer.enhance(brightness_factor)
            output_img = bright_img
            output_img_path = os.path.join("tempDir", "brightness_adjusted_image.png")
            bright_img.save(output_img_path)

        elif operation == "Add Watermark":
            watermark_text = inputs['Watermark Text']
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            textwidth, textheight = draw.textsize(watermark_text, font)
            width, height = img.size
            x = (width - textwidth) - 10
            y = (height - textheight) - 10
            draw.text((x, y), watermark_text, font=font)
            output_img = img
            output_img_path = os.path.join("tempDir", "watermarked_image.png")
            img.save(output_img_path)

        elif operation == "Rotate":
            angle = inputs['Angle']
            rotated_img = img.rotate(angle, expand=True)
            output_img = rotated_img
            output_img_path = os.path.join("tempDir", "rotated_image.png")
            rotated_img.save(output_img_path)

        # Display before and after images side by side
        if output_img_path:
            col1, col2 = st.columns(2)
            with col1:
                st.header("Before")
                st.image(img, caption="Original Image")
            with col2:
                st.header("After")
                st.image(output_img_path, caption=f"Image with {operation}")

            mime_type = "image/png" if operation in ["Add Shadow", "Combined Images"] else f"image/{format}"
            with open(output_img_path, "rb") as file:
                st.download_button(label=f"Download {operation} Image", data=file, file_name=os.path.basename(output_img_path), mime=mime_type)

    except Exception as e:
        st.error(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
