import os
import streamlit as st
from yt_dlp import YoutubeDL
import openai
from semchunk import chunk
import whisper
import streamlit_shadcn_ui as ui

# Setup OpenAI client
openai_client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Setup Whisper Model
model_size = "base"  # Options: tiny, base, small, medium, large
whisper_model = whisper.load_model(model_size)

# Ensure ffmpeg is installed
os.system("apt-get update && apt-get install -y ffmpeg")

# @st.cache
def download_audio_from_url(url, download_path='videos'):
    videoinfo = YoutubeDL().extract_info(url=url, download=False)
    audio_filename = f"{download_path}/{videoinfo['id']}.mp3"

    # Download audio if it does not exist
    if not os.path.exists(audio_filename):
        options = {
            'format': 'bestaudio/best',
            'keepvideo': False,
            'outtmpl': audio_filename,
        }
        with YoutubeDL(options) as ydl:
            ydl.download([videoinfo['webpage_url']])
    
    return audio_filename

def transcribe_audio(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result['text']

def chunk_text(transcript, chunk_size=4096):
    chunks = chunk(
        text=transcript,
        chunk_size=chunk_size,
        token_counter=lambda x: len(x.split()),
        memoize=False
    )
    print(chunks)
    return chunks
    # return [chunk_item['chunk'] for chunk_item in chunks]

def process_segment(segment):
    prompt = f"""
    <instructions>
     You are an AI content writer skilled in crafting blog posts. You have been given a part of a transcript from a video. 
    Your task is to transform the transcript into a structured markdown blog post. 
    - output valid markdown
    - insert section headings and other formatting where appropriate
    - remove any verbal tics
    - keep the conversational content in the style of the transcript.
    - do not add any extraneous information: only include what is either mentioned in the transcript.
     Blog post will follow these guidelines:
    1. Write in an active voice to keep the content engaging and dynamic.
       Example: Passive voice: “The cake was baked by Mary.” Active voice: “Mary baked the cake.”
    2. Ensure the content is short  & descriptive, and free of unnecessary filler or jargon.
       Example: "The software simplifies complex tasks" instead of "The software is a robust solution that streamlines and optimizes complex, multifaceted tasks."
       Don’t add anything extra into the mix. Everything should be short. Every word and sentence should solve a problem for our reader.
    3. Use simple language that is accessible to an eighth-grade reading level.
       Example: "The study found that exercise helps improve mood" instead of "The research conducted by the institution indicated that engaging in physical activity has a positive impact on one's emotional state."
      Remember, the easier the post is: The more your readers will enjoy it. The bigger the potential audience.
    4. Avoid generic content by incorporating unique perspectives, experiences, and anecdotes.
       Example: "When I first started using this product, I was surprised by how much time it saved me. I remember one instance where I was able to complete a project in half the time it usually takes."
    5. Demonstrate expertise and build trust by sharing relevant personal stories and examples.
       Example: "As a professional chef with over 15 years of experience, I've learned that the key to a great meal is using fresh, high-quality ingredients. One of my favorite recipes that showcases this is..."
    6. Maintain a consistent, authentic, and relatable tone that reflects the writer's personality.
       Example: "Hey there, fellow foodies! I'm excited to share my latest culinary adventure with you. Get ready for some serious flavor explosions!"
    7. Prioritize the use of real-life images and visuals over AI-generated or stock content.
       Example: Use a photo of the actual dish prepared by the chef instead of a stock photo or an AI-generated image.
    8. Create or incorporate relevant, clear, and valuable illustrations to enhance the content.
       Example: Include an infographic that visually breaks down the steps in a recipe or a diagram that explains how a product works.
    9. Ensure all images have descriptive alt text to improve accessibility for all readers.
       Example: For an image of a sunset on a beach, use alt text like "A stunning orange and pink sunset over a sandy beach with calm ocean waves."
    10. Focus on writing about topics that allow for the creation of substantial, ethical, and valuable content.
        Example: Write an in-depth guide on "How to Start a Successful Online Business" rather than a superficial article on "Get Rich Quick Schemes."
    11. Use the writer's real name, face, and personal brand to build a connection with the audience.
        Example: Include an author bio with a headshot that says, "Jane Smith is a certified nutrition coach with a passion for helping people lead healthier lives."
    12. Craft content that encourages engagement, interaction, and fosters a sense of community among readers.
        Example: End a blog post with a question like, "Have you tried any of these techniques? Share your experiences in the comments below!"
    </instructions>
    <transcript>
    {segment}
    </transcript>
    """
    
    response = openai_client.chat.completions.create(
      messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
      ],
      model="gpt-4",
      max_tokens=1000,
      temperature=0.7
    )
    return response.choices[0].message.content

def combine_segments(segments):
    blog_post = ""
    for idx, segment in enumerate(segments):
        segment_text = process_segment(segment)
        blog_post += f"# Chapter {idx + 1}\n\n" + segment_text + "\n\n"
    return blog_post

def main():
    st.set_page_config(page_title="BlogGenie - Your AI-powered Blog Writer", layout="wide")

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child{
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with open("style.css") as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

    st.title('BlogGenie')
    st.subheader('Your AI-Powered Blog Writing Assistant')
    st.expander("Agent Details").markdown(f"""
        **BlogGenie is a crew of agents that:**

        **Content Outline Agent**: Quickly generates structured outlines based on your topic and ideas.

        **Content Creation Agent**: Transforms outlines into fully fleshed out blog posts with engaging content.

        **Content Optimization Agent**: Enhances your content for search engine visibility to reach a wider audience.

        **Image Generation Agent**: Automatically creates or finds relevant images to enrich your posts.

        **Publishing Agent**: Seamlessly formats and publishes your blog posts to your favorite platforms.

        Let **BlogGenie** handle the heavy lifting, so you can focus on what you do best: sharing your ideas with the world!
        """)
    st.markdown(" ")

    # Custom CSS for final result styling
    custom_css = """
    <style>
    .final-result-container {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-left: 40px;
    }
    .final-result-container h2 {
        color: #343a40;
    }
    .final-result-container p {
        font-size: 16px;
        line-height: 1.6;
        color: #495057;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # UI Input
    youtube_url = st.text_input("Enter YouTube Video URL:")
    process_btn = ui.button(text="Convert Video to Blog Post", key="process_btn")

    if youtube_url and process_btn:
        with st.spinner("Processing..."):
            try:
                # Step 1: Download Audio
                st.info("Downloading audio from YouTube...")
                audio_path = download_audio_from_url(youtube_url)
                st.info("Audio downloaded successfully.")

                # Step 2: Transcribe Audio with Whisper
                st.info("Transcribing audio using Whisper...")
                transcript = transcribe_audio(audio_path)

                # Ensure transcript is a string
                if not isinstance(transcript, str):
                    raise ValueError("The transcribed text is not a string.")

                # Step 3: Chunk Transcription
                st.info("Chunking transcribed text...")
                chunks = chunk_text(transcript)

                # Step 4: Process Segments
                st.info("Generating blog post content...")
                blog_post = combine_segments(chunks)

                # Display final result
                st.success("Blog post generated successfully!")
                st.markdown(f"""
                <div class="final-result-container">
                <h2>Here is the final blog post</h2>
                {blog_post}
                </div>
                """, unsafe_allow_html=True)

                # Download buttons for audio and markdown
                with open(audio_path, "rb") as f:
                    st.download_button("Download Audio", data=f, file_name="audio.mp3")
                st.download_button(
                    label="Download Markdown",
                    data=blog_post,
                    file_name='blog_post.md',
                    mime='text/markdown'
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    if not os.path.exists('videos'):
        os.makedirs('videos')
    main()
