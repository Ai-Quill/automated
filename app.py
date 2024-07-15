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
from transformers import BartForConditionalGeneration, BartTokenizer
import requests
import pyttsx3
import pyshorteners
import numpy as np
import webbrowser
import lmproof
import smtplib
from email.message import EmailMessage
import psutil
import threading



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

def main():
    st.sidebar.title("Python Automation Portal")
    
    
    st.sidebar.markdown("""
    This application allows users to run various Python automation scripts.
    Select a script from the dropdown below to get started.
    """)

    categories = sorted(set(script['category'] for script in scripts_data['scripts']))
    selected_categories = st.sidebar.multiselect("Filter by Categories", options=categories, default=categories)

    if not selected_categories:
        selected_scripts = scripts_data['scripts']
    else:
        selected_scripts = [script for script in scripts_data['scripts'] if script['category'] in selected_categories]

    script_titles = [script['title'] for script in selected_scripts]
    selected_script_title = st.selectbox("Choose an Automation Script", script_titles)
    selected_script = next(script for script in selected_scripts if script['title'] == selected_script_title)

    st.markdown(f"### {selected_script['title']}")
    st.write(selected_script['description'])
    
    inputs = {}
    for input_item in selected_script['inputs']:
        if input_item['type'] == 'file':
            inputs[input_item['name']] = st.file_uploader(f"Upload {input_item['name']}", type=input_item['format'].split(', '))
        elif input_item['type'] == 'files':
            inputs[input_item['name']] = st.file_uploader(f"Upload {input_item['name']}", type=input_item['format'].split(', '), accept_multiple_files=True)
        elif input_item['type'] == 'text':
            inputs[input_item['name']] = st.text_input(f"Enter {input_item['name']}")
        elif input_item['type'] == 'number':
            inputs[input_item['name']] = st.number_input(f"Enter {input_item['name']}", min_value=1, step=1)
        elif input_item['type'] == 'textarea':
            inputs[input_item['name']] = st.text_area(f"Input {input_item['name']} (one per line)")

    if st.button("Run Script"):
        run_selected_script(selected_script, inputs)
        
    with st.expander("Function Code"):
        function_code = get_function_code_by_id(selected_script['id'])
        st.code(function_code, language='python')

def get_function_code_by_id(script_id):
    function_code = {
        1: run_audiobook_converter,
        2: run_tab_opener,
        3: run_image_downloader,
        4: run_code_analyzer,
        5: run_fake_data_generator,
        6: run_background_remover,
        7: run_task_reminder,
        8: run_resource_monitor,
        9: run_bulk_email_sender,
        10: run_clipboard_manager,
        11: run_article_summarizer,
        12: run_spell_checker,
        13: run_link_checker,
        14: run_news_reader,
        15: run_qr_code_generator,
        16: run_url_shortener,
        # 17: run_screen_recorder,
        18: run_hydration_reminder,
    }
    function = function_code.get(script_id)
    return inspect.getsource(function) if function else "Function not implemented."

def run_selected_script(script, inputs):
    if script['id'] == 1:
        run_audiobook_converter(inputs['PDF file'])
    elif script['id'] == 2:
        run_tab_opener(inputs)
    elif script['id'] == 3:
        run_image_downloader(inputs)
    elif script['id'] == 4:
        run_code_analyzer(inputs['Python files'])
    elif script['id'] == 5:
        run_fake_data_generator(inputs['Number of entries'])
    elif script['id'] == 6:
        run_background_remover(inputs['Image file'])
    elif script['id'] == 7:
        run_task_reminder(inputs['Reminder text'], inputs['Delay in minutes'])
    elif script['id'] == 8:
        run_resource_monitor(inputs['CPU threshold'], inputs['Memory threshold'], inputs['GPU threshold'], inputs['Battery threshold'])
    elif script['id'] == 9:
        run_bulk_email_sender(inputs['Sender email'], inputs['Sender password'], inputs['Emails file'])
    elif script['id'] == 10:
        run_clipboard_manager()
    elif script['id'] == 11:
        run_article_summarizer(inputs['Article URL'])
    elif script['id'] == 12:
        run_spell_checker(inputs['Input text'])
    elif script['id'] == 13:
        run_link_checker(inputs)
    elif script['id'] == 14:
        run_news_reader(inputs['News API key'])
    elif script['id'] == 15:
        run_qr_code_generator(inputs['Link'], inputs['Filename'])
    elif script['id'] == 16:
        run_url_shortener(inputs['Long URL'])
    # elif script['id'] == 17:
    #     run_screen_recorder(inputs['Recording duration'])
    elif script['id'] == 18:
        run_hydration_reminder(inputs['Interval duration in minutes'])

# Full source code for all functions

def run_audiobook_converter(pdf_file):
    # Ensure the temporary directory exists
    temp_dir = "tempDir"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    file_path = save_uploaded_file(pdf_file)
    try:
        import PyPDF2
        import pyttsx3

        # Initialize TTS engine
        # speaker = pyttsx3.init()
        # speaker.setProperty('rate', 150)
        # speaker.setProperty('volume', 1.0)

        # voices = speaker.getProperty('voices')
        # for voice in voices:
        #     if "english" in voice.name.lower() and "us" in voice.name.lower():
        #         speaker.setProperty('voice', voice.id)
        #         break

        # Open the PDF file
        file = open(file_path, 'rb')
        readpdf = PyPDF2.PdfReader(file)
        
        text_to_speech = ""

        for pagenumber in range(len(readpdf.pages)):
            page = readpdf.pages[pagenumber]
            text = page.extract_text()
            text_to_speech += text + "\n"

        audio_filename = os.path.join(temp_dir, 'audiobook.wav')
        # speaker.save_to_file(text_to_speech, mp3_filename)
        # speaker.runAndWait()
        
        # # Stop the TTS engine
        # speaker.stop()
        # file.close()
        
        engine = pyttsx3.init()  # object creation

        """ RATE"""
        rate = engine.getProperty('rate')  # getting details of current speaking rate
        print(rate)  # printing current voice rate
        engine.setProperty('rate', 125)  # setting up new voice rate

        """VOLUME"""
        volume = engine.getProperty('volume')  # getting to know current volume level (min=0 and max=1)
        print(volume)  # printing current volume level
        engine.setProperty('volume', 1.0)  # setting up volume level  between 0 and 1

        """VOICE"""
        voices = engine.getProperty('voices')  # getting details of current voice
        # engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
        engine.setProperty('voice', voices[1].id)  # changing index, changes voices. 1 for female

        # engine.say(text_to_speech)
        
        # engine.runAndWait()
        # engine.stop()

        """Saving Voice to a file"""
        # On linux make sure that 'espeak' and 'ffmpeg' are installed
        print(text_to_speech)
        engine.say(text_to_speech)
        engine.save_to_file(text_to_speech, audio_filename)
        engine.runAndWait()
        engine.stop()
        file.close()

        st.success("Audiobook created successfully!")
        with open(audio_filename, "rb") as file:
            st.download_button(label=f"Download Audiobook", data=file, file_name='audiobook.wav', mime="audio/wav")
    except Exception as e:
        st.error(f"An error occurred: {e}")



def run_tab_opener(inputs):
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
        for link in links:
            webbrowser.open(link.strip())
        st.success("Tabs opened successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_image_downloader(inputs):
    keyword = inputs['Keyword for images']
    num_images = inputs['Number of images']
    try:
        response = simp.simple_image_download()
        response.download(keyword, num_images)
        st.success("Images downloaded successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_code_analyzer(code_files):
    if code_files:
        for file in code_files:
            file_path = save_uploaded_file(file)
            st.write(f"Analyzing file: {file.name}")
            subprocess.run(f"pylint {file_path}", shell=True)
            subprocess.run(f"flake8 {file_path}", shell=True)
        st.success("Code analysis completed!")

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

def run_background_remover(input_img_file):
    input_img_path = save_uploaded_file(input_img_file)
    output_img_path = input_img_path.replace('.', '_rmbg.')
    try:
        inp = Image.open(input_img_path)
        output = remove(inp)
        output.save(output_img_path)
        st.image(output_img_path, caption="Image with background removed")
        st.success("Background removed successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def run_task_reminder(reminder, delay_minutes):
    try:
        st.write("Setting up reminder...")
        time.sleep(2)
        st.write("All set!")
        time.sleep(delay_minutes * 60)
        st.info(reminder)
        st.success("Reminder sent!")
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

def run_clipboard_manager():
    st.write("Clipboard Manager not supported in Streamlit interface. Use tkinter window instead.")
    # Further implementation can be the same as before but note it won't work in Streamlit

def run_article_summarizer(url):
    try:
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
        img.save(filename)
        st.image(filename, caption=f"QR Code for {link}")
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

# def run_screen_recorder(record_seconds):
#     try:
#         import cv2
#         os.environ['DISPLAY'] = ':0'
#         SCREEN_SIZE = tuple(pyautogui.size())
#         fourcc = cv2.VideoWriter_fourcc(*'MJPG')
#         fps = 12.0
#         out = cv2.VideoWriter("video.mp4", fourcc, fps, SCREEN_SIZE)

#         for _ in range(int(record_seconds * fps)):
#             img = pyautogui.screenshot()
#             frame = np.array(img)
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             out.write(frame)

#         out.release()
#         st.video("video.mp4")
#     except Exception as e:
#         st.error(f"An error occurred: {e}")

def run_hydration_reminder(interval_minutes):
    try:
        while True:
            st.info("Please Drink Water")
            time.sleep(interval_minutes * 60)
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
