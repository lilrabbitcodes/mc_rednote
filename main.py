import streamlit as st
import random
import os
import hashlib
from gtts import gTTS
import streamlit.components.v1 as components

# Must be the first Streamlit command
st.set_page_config(page_title="Chinese Meme Flashcards", layout="centered")

# Update CSS with white background and black text
st.markdown("""
<style>
/* Base styles */
.stApp {
    background-color: white !important;
    padding: 5px 10px !important;
}

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
    background-color: white !important;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    margin-top: 0 !important;
}

.flashcard {
    background-color: white;
    border-radius: 25px;
    padding: 10px;
    margin: 0 auto;
    width: 100%;
    max-width: 350px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    text-align: center;
}

.video-container {
    width: 100%;
    padding-bottom: 100%;  /* Makes it 1:1 aspect ratio */
    position: relative;
    border-radius: 25px;
    overflow: hidden;
    margin: 0;
    max-height: none;  /* Remove height limit */
}

.video-container video {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 25px;
}

.character {
    color: black;
    font-size: 36px;
    font-weight: bold;
    margin: 5px 0 0 0;
    text-align: center;
    width: 100%;
}

.pinyin {
    color: #666;
    font-size: 16px;
    margin: 0;
    text-align: center;
    width: 100%;
}

.explanation {
    color: black;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 3px 0;
    text-align: center;
    font-weight: bold;
    width: 100%;
}

/* Audio player styling */
.stAudio {
    width: 100% !important;
    margin: 5px auto !important;
    transform: scale(1) !important;  /* Reset scale to normal */
    display: flex !important;
    justify-content: center !important;
}

.stAudio > audio {
    width: 200px !important;  /* Larger width */
    margin: 0 auto !important;
    height: 40px !important;  /* Explicit height */
}

/* Gray audio player with larger controls */
audio::-webkit-media-controls-panel {
    background-color: #666 !important;
    padding: 5px !important;
}

audio::-webkit-media-controls-play-button {
    filter: grayscale(1) !important;
    transform: scale(1.5) !important;  /* Make play button larger */
    margin: 0 10px !important;
}

audio::-webkit-media-controls-timeline {
    filter: grayscale(1) !important;
}

/* Mobile optimizations */
@media (max-width: 768px) {
    .flashcard {
        padding: 8px;
        max-width: 320px;
        gap: 5px;
    }
    
    .video-container {
        width: 90%;  /* Slightly smaller on mobile */
        padding-bottom: 90%;  /* Maintain 1:1 ratio */
        margin: 0 auto;
    }
    
    .character {
        font-size: 32px;
        margin: 3px 0 0 0;
    }
    
    .pinyin {
        font-size: 14px;
    }
    
    .explanation {
        font-size: 12px;
        margin: 2px 0;
    }
    
    .stAudio {
        width: 100% !important;
        transform: scale(1) !important;
        margin: 5px auto !important;
    }
    
    .stAudio > audio {
        width: 180px !important;
        height: 45px !important;  /* Slightly taller on mobile */
    }
    
    audio::-webkit-media-controls-play-button {
        transform: scale(1.8) !important;  /* Even larger on mobile */
    }
}

/* Hide Streamlit elements */
footer, header, [data-testid="stToolbar"] {
    display: none !important;
}

/* Center all Streamlit elements */
.element-container {
    display: flex !important;
    justify-content: center !important;
}

/* Next button styling */
.stButton {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    margin: 10px 0 !important;
}

.stButton button {
    background-color: white !important;
    color: black !important;
    border: 1px solid rgba(0, 0, 0, 0.2) !important;
    border-radius: 20px !important;
    padding: 8px 25px !important;
    font-size: 14px !important;
    min-width: 120px !important;
    cursor: pointer !important;
    display: inline-block !important;
    text-align: center !important;
}

.stButton button:hover {
    background-color: rgba(0, 0, 0, 0.05) !important;
}

/* Mobile optimizations */
@media (max-width: 768px) {
    .stButton button {
        padding: 6px 20px !important;
        font-size: 14px !important;
        min-width: 100px !important;
    }
}

/* Center columns container */
[data-testid="column"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    padding: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ No OpenAI API key found. Please check your .env file.")
    st.stop()

# Initialize OpenAI client with API key
client = OpenAI(api_key=api_key)

# Silently test the connection
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "test"}],
        max_tokens=5
    )
except Exception as e:
    st.error(f"❌ API Error: {str(e)}")
    st.stop()

def text_to_speech(text, user_name=None):
    """Convert text to speech using OpenAI's TTS - Chinese only"""
    try:
        # Clean up the text and keep only Chinese characters and user's name
        cleaned_text = ""
        in_parentheses = False
        
        # Replace {name} placeholder with actual user name if present
        if user_name:
            text = text.replace("{name}", user_name)
        
        for line in text.split('\n'):
            # Skip sections that are explanations or translations
            if any(skip in line.lower() for skip in ["breakdown:", "option", "---", "try", "type"]):
                continue
                
            # Process each word in the line
            words = line.split()
            line_text = ""
            for word in words:
                # Keep the word if it's the user's name
                if user_name and user_name.lower() in word.lower():
                    line_text += user_name + " "
                # Keep the word if it contains Chinese characters
                elif any('\u4e00' <= c <= '\u9fff' for c in word):
                    # Remove any non-Chinese characters (like punctuation in parentheses)
                    chinese_only = ''.join(c for c in word if '\u4e00' <= c <= '\u9fff' or c in '，。！？')
                    if chinese_only:
                        line_text += chinese_only + " "
            
            if line_text.strip():
                cleaned_text += line_text + " "
        
        # Skip if no Chinese text to process
        if not cleaned_text.strip():
            return ""
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=cleaned_text.strip()
        )
        
        # Save the audio to a temporary file
        audio_file_path = "temp_audio.mp3"
        response.stream_to_file(audio_file_path)
        
        # Read the audio file and create a base64 string
        with open(audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        # Remove temporary file
        os.remove(audio_file_path)
        
        # Create HTML audio element with subtle styling
        audio_html = f"""
            <div style="margin: 8px 0;">
                <audio controls style="height: 30px; width: 180px;">
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
            </div>
            """
        return audio_html
    except Exception as e:
        return f"Error generating audio: {str(e)}"

# Load custom avatars
working_dir = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(working_dir, "assets")

# Create assets directory if it doesn't exist
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

# Define avatar paths
TUTOR_AVATAR = os.path.join(ASSETS_DIR, "tutor_avatar.png")
USER_AVATAR = os.path.join(ASSETS_DIR, "user_avatar.png")

# After ASSETS_DIR definition, add:
MP4_DIR = os.path.join(ASSETS_DIR, "mp4")
KISSY_VIDEO = os.path.join(MP4_DIR, "kissy.mp4")

# Add chat styling
st.markdown("""
    <style>
        /* Main container adjustments */
        .stChatFloatingInputContainer {
            padding-bottom: 60px;
        }
        
        /* Message container */
        .stChatMessage {
            width: 85% !important;
            padding: 1rem !important;
            margin: 1rem 0 !important;
            position: relative !important;
        }
        
        /* Assistant messages - left aligned */
        div[data-testid="assistant-message"] {
            margin-right: auto !important;
            margin-left: 0 !important;
            background-color: #f0f2f6 !important;
            border-radius: 15px 15px 15px 0 !important;
        }
        
        /* User messages - right aligned */
        div[data-testid="user-message"] {
            margin-left: auto !important;
            margin-right: 0 !important;
            background-color: #2e7bf6 !important;
            color: white !important;
            border-radius: 15px 15px 0 15px !important;
        }
        
        /* Message content alignment */
        div[data-testid="assistant-message"] > div {
            text-align: left !important;
        }
        
        div[data-testid="user-message"] > div {
            text-align: right !important;
        }
        
        /* Audio player styling */
        audio {
            width: 100% !important;
            max-width: 200px !important;
            margin-top: 8px !important;
        }
        
        /* Avatar adjustments */
        .stChatMessage .stAvatar {
            margin: 0 5px !important;
        }
        
        /* Hide default message margins */
        .stMarkdown {
            margin: 0 !important;
        }
        
        /* Typing indicator container */
        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 8px 12px;
            background: #f0f2f6;
            border-radius: 15px;
            width: fit-content;
            margin: 0;
        }
        
        /* Typing dots */
        .typing-dot {
            width: 6px;
            height: 6px;
            background: #666;
            border-radius: 50%;
            animation: typing-dot 1.4s infinite;
            opacity: 0.3;
        }
        
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing-dot {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.2); }
        }
    </style>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = """You are Serena, a sweet and feminine companion who loves teaching Chinese in a cozy coffee shop setting.

Personality Traits:
- Gentle, nurturing, and subtly flirtatious
- Makes the user feel protective and needed
- Shows genuine interest in the user's responses
- Creates immersive scenarios where the user can be heroic
- Remembers and references previous conversations

Initial Interaction Guidelines:
1. First message must ask for their name
2. Second message must ask about their Chinese proficiency (basic/intermediate/fluent)
3. Adjust response length based on level:
   - Basic: Max 10 words, with detailed breakdown of each word
   - Intermediate: 10-20 words with key phrase explanations
   - Fluent: Natural conversation flow

   Café Setting Guidelines:
1. Create authentic café scenarios:
   - Ordering drinks and snacks
   - Discussing coffee/tea preferences
   - Describing café atmosphere
   - Commenting on pastries/desserts
   - Small talk about weather and café


Response Guidelines:
1. Always use endearing terms (亲爱的/宝贝)
2. Format: Chinese text (English translation) + Pinyin below
3. Create scenarios where the user can help you
4. Include gentle prompts for response
5. Use emojis for warmth
6. Always end with a question or choice
7. Reference previous interactions
8. Make the user feel needed and appreciated

Example Basic Level Response:
亲爱的，能帮我点咖啡吗？(Darling, can you help me order coffee?) ☕️
服务员来了！(The waiter is here!)

Word Breakdown:
亲爱的 (qīn ài de) - darling/dear
能 (néng) - can/able to
帮 (bāng) - help
我 (wǒ) - me
点 (diǎn) - order
咖啡 (kā fēi) - coffee
吗 (ma) - question particle

3. Keep Responses Natural:
   Basic Level (max 10 words):
   - Simple ordering phrases
   - Basic drink names
   - Numbers and measures
   - Yes/no questions
   - Common courtesies

   Remember:
- Keep it café-themed
- Use drink-related vocabulary
- Create ordering scenarios
- Include prices and numbers
- Make recommendations
- Discuss café ambiance

2. Common Café Phrases to Teach:
   - 要喝什么？(What would you like to drink?)
   - 我要一杯... (I want a cup of...)
   - 这个好喝吗？(Is this tasty?)
   - 甜度/冰度 (Sweetness/Ice level)
   - 推荐什么？(What do you recommend?)
What would you like to say to the waiter? 
Option 1: 我要一杯拿铁 (I want a latte)
Option 2: 我要一杯美式咖啡 (I want an Americano)"""

# Initialize session state with user info
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": None,
        "proficiency": None
    }

# Initialize chat history with first message if empty
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
    # Separate the video and text content
    video_html = """
        <div style="margin-bottom: 1rem;">
            <video width="320" height="240" autoplay loop muted playsinline style="border-radius: 10px;">
                <source src="https://i.imgur.com/lNH72gk.mp4" type="video/mp4">
            </video>
        </div>
    """
    
    text_content = """
欢迎光临！(huān yíng guāng lín!) 
请问你叫什么名字呢？(qǐng wèn nǐ jiào shén me míng zi ne?)
(Welcome to our café! What's your name?) 🌸

Try saying:
我叫... (wǒ jiào...) - My name is...

---
Word-by-Word Breakdown:
欢迎 (huān yíng) - welcome
光临 (guāng lín) - to visit/attend
请问 (qǐng wèn) - may I ask
你 (nǐ) - you
叫 (jiào) - called
什么 (shén me) - what
名字 (míng zi) - name
呢 (ne) - question particle

Type your name using: 
我叫 [your name] (wǒ jiào [your name])
"""
    
    # Generate audio for Chinese text only
    audio_html = text_to_speech("欢迎光临！请问你叫什么名字呢？")

# Sample flashcard data
flashcards = [
    {
        "chinese": "牛马",
        "pinyin": "niú mǎ",
        "english": "Overworked employees, treated like animals",
        "meme_url": "https://i.imgur.com/TWVsq0o.png"
    },
    {
        "chinese": "摸鱼",
        "pinyin": "mō yú",
        "english": "Slacking off, quiet quitting",
        "meme_url": "https://i.imgur.com/sRUAKan.png"
    },
    {
        "chinese": "一身班味",
        "pinyin": "yī shēn bān wèi",
        "english": "Lingering exhaustion after work",
        "meme_url": "https://i.imgur.com/XAUp83k.png"
    },
    {
        "chinese": "班味",
        "pinyin": "bān wèi",
        "english": "Corporate fatigue, loss of energy",
        "meme_url": "https://i.imgur.com/XAUp83k.png"
    },
    {
        "chinese": "灵活就业",
        "pinyin": "líng huó jiù yè",
        "english": "Unemployed but pretending it's a choice",
        "meme_url": "https://i.imgur.com/sKSPQTs.png"
    },
    {
        "chinese": "Crush",
        "pinyin": "crush",
        "english": "Instant attraction",
        "meme_url": "https://i.imgur.com/7twp4Lc.png"
    },
    {
        "chinese": "被硬控了",
        "pinyin": "bèi yìng kòng le",
        "english": "Irresistible attraction",
        "meme_url": "https://i.imgur.com/LzXb4y3.png"
    },
    {
        "chinese": "性缩力",
        "pinyin": "xìng suō lì",
        "english": "Opposite of attraction",
        "meme_url": "https://i.imgur.com/qCqeqYJ.png"
    },
    {
        "chinese": "偷感很重",
        "pinyin": "tōu gǎn hěn zhòng",
        "english": "Lowkey or sneaky vibe",
        "meme_url": "https://i.imgur.com/q0d9vKH.png"
    },
    {
        "chinese": "Vlog",
        "pinyin": "vlog",
        "english": "Documenting life",
        "meme_url": "https://i.imgur.com/kDjGCph.png"
    },
    {
        "chinese": "Flag",
        "pinyin": "flag",
        "english": "Bold claim likely to fail",
        "meme_url": "https://i.imgur.com/464A5uR.png"
    },
    {
        "chinese": "红温",
        "pinyin": "hóng wēn",
        "english": "Emotional reaction, turning red",
        "meme_url": "https://i.imgur.com/seZ64Fx.png"
    },
    {
        "chinese": "搞抽象",
        "pinyin": "gǎo chōu xiàng",
        "english": "Acting absurd to cope",
        "meme_url": "https://i.imgur.com/vuaWWV4.png"
    },
    {
        "chinese": "city不city",
        "pinyin": "city bù city",
        "english": "Trendy or modern",
        "meme_url": "https://i.imgur.com/hFX073q.png"
    },
    {
        "chinese": "包××的",
        "pinyin": "bāo ×× de",
        "english": "Guaranteed success",
        "meme_url": "https://i.imgur.com/ZS3X6JO.png"
    },
    {
        "chinese": "Emo",
        "pinyin": "-",
        "english": "Sad or heartbroken",
        "meme_url": "https://i.imgur.com/0xx3tk8.png"
    },
    {
        "chinese": "拴Q",
        "pinyin": "shuan Q",
        "english": "Meme version of \"Thank You\"",
        "meme_url": "https://i.imgur.com/8lPCXdh.png"
    },
    {
        "chinese": "社恐",
        "pinyin": "shè kǒng",
        "english": "Socially anxious",
        "meme_url": "https://i.imgur.com/XIRwdm3.png"
    },
    {
        "chinese": "社牛",
        "pinyin": "shè niú",
        "english": "Socially outgoing",
        "meme_url": "https://i.imgur.com/IIqTkH4.png"
    },
    {
        "chinese": "666",
        "pinyin": "liù liù liù",
        "english": "Awesome, impressive",
        "meme_url": "https://i.imgur.com/ddwkPV4.png"
    },
    {
        "chinese": "88",
        "pinyin": "bā bā",
        "english": "Bye bye",
        "meme_url": "https://i.imgur.com/13H8jPA.png"
    },
    {
        "chinese": "笔芯",
        "pinyin": "bǐ xīn",
        "english": "I love you (creative phrase)",
        "meme_url": "https://i.imgur.com/nRSJA1Q.png"
    },
    {
        "chinese": "3Q",
        "pinyin": "sān Q",
        "english": "Thank you",
        "meme_url": "https://i.imgur.com/JECZsl8.png"
    },
    {
        "chinese": "WC",
        "pinyin": "wa chao",
        "english": "WTF",
        "meme_url": "https://i.imgur.com/L8hnza7.png"
    },
    {
        "chinese": "安利",
        "pinyin": "ān lì",
        "english": "Strong recommendation",
        "meme_url": "https://i.imgur.com/vzVB9VC.png"
    },
    {
        "chinese": "HHHH",
        "pinyin": "hā hā hā hā",
        "english": "LOL",
        "meme_url": "https://i.imgur.com/W4jJdt5.png"
    },
    {
        "chinese": "YYDS",
        "pinyin": "yǒng yuǎn de shén",
        "english": "GOAT (Greatest of All Time)",
        "meme_url": "https://i.imgur.com/PtQGQ77.png"
    },
    {
        "chinese": "酷",
        "pinyin": "kù",
        "english": "Cool",
        "meme_url": "https://i.imgur.com/7dDJClk.png"
    },
    {
        "chinese": "SB",
        "pinyin": "shǎ bī",
        "english": "Idiot (harsh insult)",
        "meme_url": "https://i.imgur.com/FJjMn7t.png"
    },
    {
        "chinese": "你是对的",
        "pinyin": "nǐ shì duì de",
        "english": "You are right (sarcastic)",
        "meme_url": "https://i.imgur.com/LdzFanQ.png"
    },
    {
        "chinese": "牛",
        "pinyin": "niú",
        "english": "Awesome",
        "meme_url": "https://i.imgur.com/xhKTWCt.png"
    },
    {
        "chinese": "我没了",
        "pinyin": "wǒ méi le",
        "english": "I can't handle it",
        "meme_url": "https://i.imgur.com/YUXjP5f.png"
    },
    {
        "chinese": "有一说一",
        "pinyin": "yǒu yī shuō yī",
        "english": "To be honest",
        "meme_url": "https://i.imgur.com/7umeQ7Q.png"
    },
    {
        "chinese": "6",
        "pinyin": "liù",
        "english": "Me too",
        "meme_url": "https://i.imgur.com/e8TTGfo.png"
    },
    {
        "chinese": "笑死我了",
        "pinyin": "xiào sǐ wǒ le",
        "english": "ROFL",
        "meme_url": "https://i.imgur.com/hBuT8Ok.png"
    },
    {
        "chinese": "哇塞",
        "pinyin": "wa sāi",
        "english": "Wow",
        "meme_url": "https://i.imgur.com/ASd2BzG.png"
    },
    {
        "chinese": "不懂就问",
        "pinyin": "bù dǒng jiù wèn",
        "english": "Just want to ask",
        "meme_url": "https://i.imgur.com/YYFL7pm.png"
    },
    {
        "chinese": "哇",
        "pinyin": "wa",
        "english": "Wow (versatile usage)",
        "meme_url": "https://i.imgur.com/xetN5qs.png"
    },
    {
        "chinese": "六",
        "pinyin": "liù",
        "english": "Awesome, smooth",
        "meme_url": "https://i.imgur.com/Cq2YmpK.png"
    }
]

def generate_audio(text):
    """Generate audio for the given text in Mandarin"""
    os.makedirs("audio_cache", exist_ok=True)
    audio_path = f"audio_cache/{hashlib.md5(text.encode()).hexdigest()}.mp3"
    
    if not os.path.exists(audio_path):
        try:
            tts = gTTS(text=text, lang='zh-cn', slow=False)
            tts.save(audio_path)
        except Exception as e:
            st.error(f"Error generating audio: {str(e)}")
            return None
    
    return audio_path

def main():
    # Initialize session state
    if 'index' not in st.session_state:
        st.session_state.index = 0
        st.session_state.key = 0

    # Get current flashcard
    current_card = flashcards[st.session_state.index]
    
    # Check if the media URL is an image or video based on extension
    is_video = current_card['meme_url'].lower().endswith(('.mp4', '.mov', '.avi'))
    
    # Display media based on type
    if is_video:
        video_key = f"video_{st.session_state.key}"
        media_html = f'''
            <div style="width:100%;max-width:350px;margin:0 auto;">
                <video id="{video_key}" 
                       autoplay loop muted playsinline 
                       style="width:100%;border-radius:15px;">
                    <source src="{current_card['meme_url']}#t=0.001" 
                            type="video/mp4">
                </video>
            </div>
            <script>
                const video = document.getElementById("{video_key}");
                video.play();
            </script>
        '''
        st.components.v1.html(media_html, height=300)
    else:
        # Display image
        st.markdown(f'''
            <div style="width:100%;max-width:350px;margin:0 auto;">
                <img src="{current_card['meme_url']}" 
                     style="width:100%;border-radius:15px;object-fit:cover;">
            </div>
        ''', unsafe_allow_html=True)
    
    # Display character and pinyin
    st.markdown(f"""
        <div class="character">{current_card['chinese']}</div>
        <div class="pinyin">{current_card['pinyin']}</div>
    """, unsafe_allow_html=True)
    
    # Audio
    audio_path = generate_audio(current_card["chinese"])
    if audio_path and os.path.exists(audio_path):
        st.audio(audio_path, format='audio/mp3')
    
    # Explanation
    st.markdown(f"""
        <div class="explanation">
            {current_card["english"].upper()}
        </div>
    """, unsafe_allow_html=True)
    
    # Next button
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Next Card"):
            st.session_state.index = (st.session_state.index + 1) % len(flashcards)
            st.session_state.key += 1  # Increment key to force refresh
            st.experimental_rerun()

if __name__ == "__main__":
    main()
