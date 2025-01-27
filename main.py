import streamlit as st
import os
import hashlib
from gtts import gTTS
from io import BytesIO
import base64
import time
import tempfile

# Must be the first Streamlit command
st.set_page_config(page_title="Chinese Meme Flashcards", layout="centered")

# At the top of the file, add more detailed error handling
try:
    from gtts import gTTS
    AUDIO_ENABLED = True
except ImportError as e:
    AUDIO_ENABLED = False
    st.error(f"Detailed error: {str(e)}")
    st.warning("Audio functionality is not available. Installing required packages...")
    try:
        import subprocess
        subprocess.check_call(["pip", "install", "gTTS==2.5.0", "click>=7.0"])
        from gtts import gTTS
        AUDIO_ENABLED = True
        st.success("Successfully installed audio packages!")
    except Exception as e:
        st.error(f"Failed to install packages: {str(e)}")

# CSS styles
st.markdown("""
    <style>
.stApp {
    background-color: white !important;
    padding: 5px 10px !important;
    color: black !important;
}

.character {
    font-size: 36px;
    font-weight: bold;
    margin: 10px 0;
    text-align: center;
    color: black !important;
}

.pinyin {
    font-size: 18px;
    color: #666;
    margin: 5px 0;
    text-align: center;
}

.explanation {
    font-size: 16px;
    margin: 10px 0;
    text-align: center;
    text-transform: uppercase;
    font-weight: bold;
    color: black !important;
}

/* Button styling */
.stButton {
    text-align: center !important;
    display: flex !important;
    justify-content: center !important;
}

.stButton > button {
    background-color: white !important;
    color: black !important;
    border: 2px solid black !important;
    border-radius: 5px !important;
    padding: 5px 15px !important;
    font-weight: 500 !important;
    margin: 0 auto !important;
}

.stButton > button:hover {
    background-color: #f0f0f0 !important;
    border-color: black !important;
        }
        
        /* Audio player styling */
.stAudio {
    width: 50% !important;
    margin: 5px auto !important;
    display: flex !important;
    justify-content: center !important;
}

.stAudio > audio {
    width: 90px !important;
    height: 30px !important;
}

audio::-webkit-media-controls-panel {
    background-color: #666666 !important;  /* Darker grey */
}

audio::-webkit-media-controls-play-button {
    transform: scale(1.2) !important;
    margin: 0 8px !important;
    color: white !important;
}

audio::-webkit-media-controls-current-time-display,
audio::-webkit-media-controls-time-remaining-display {
    color: white !important;
    font-size: 12px !important;
}

/* Center column content */
[data-testid="column"] {
    display: flex !important;
    justify-content: center !important;
}

/* Mobile optimization */
.main-container {
    max-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 10px;
}

/* Adjust image container */
.image-container {
    flex: 0 0 auto;
    margin-bottom: 10px;
}

/* Text content */
.text-content {
    flex: 0 0 auto;
    margin: 10px 0;
}

/* Button container */
.button-container {
    flex: 0 0 auto;
    margin-top: 10px;
}

/* Audio container styling */
.audio-container {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
            width: 100% !important;
    margin: 15px auto !important;
}

.audio-container audio {
    width: 35px !important;
    height: 35px !important;
    border-radius: 50% !important;
    background-color: #666666 !important;
}

/* Hide audio controls except play button */
.audio-container audio::-webkit-media-controls-panel {
    background-color: #666666 !important;
    display: flex !important;
    justify-content: center !important;
}

.audio-container audio::-webkit-media-controls-play-button {
    transform: scale(1.2) !important;
            margin: 0 !important;
        }
        
.audio-container audio::-webkit-media-controls-timeline,
.audio-container audio::-webkit-media-controls-current-time-display,
.audio-container audio::-webkit-media-controls-time-remaining-display,
.audio-container audio::-webkit-media-controls-volume-slider,
.audio-container audio::-webkit-media-controls-mute-button {
    display: none !important;
}

/* Center all content */
.main-container {
    max-height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 10px !important;
    text-align: center !important;
}

.text-content {
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    margin: 10px 0 !important;
}

.character, .pinyin, .explanation {
    width: 100% !important;
    text-align: center !important;
}

.image-container {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    margin-bottom: 15px !important;
}

.button-container {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    margin-top: 15px !important;
        }
    </style>
""", unsafe_allow_html=True)

def get_audio(text):
    """Simple audio generation with mobile support"""
    try:
        # Special cases for pronunciation
        special_cases = {
            "HHHH": "哈哈哈哈",
            "666": "六六六",
            "88": "八八",
            "3Q": "三Q",
            "WC": "哇草",
            "SB": "傻逼",
        }
        
        # English words to pronounce as-is
        english_words = ["Vlog", "Flag", "Crush", "Emo"]
        
        # Generate audio
        if text in english_words:
            tts = gTTS(text=text, lang='en', slow=False)
        elif text == "city不city":
            tts = gTTS(text="city 不 city", lang='zh-cn', slow=False)
        else:
            text_to_speak = special_cases.get(text, text)
            tts = gTTS(text=text_to_speak, lang='zh-cn', slow=False)

        # Save to BytesIO
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        return audio_bytes.read()
    except:
        return None

# Flashcard data
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
        "pinyin": "emo",
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

def main():
    # Initialize session state
    if 'index' not in st.session_state:
        st.session_state.index = 0

    # Create a container with fixed height for mobile optimization
    with st.container():
        st.markdown("""
            <style>
            /* Mobile optimization */
            .main-container {
                max-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                padding: 10px;
            }
            
            /* Adjust image container */
            .image-container {
                flex: 0 0 auto;
                margin-bottom: 10px;
            }
            
            /* Text content */
            .text-content {
                flex: 0 0 auto;
                margin: 10px 0;
            }
            
            /* Button container */
            .button-container {
                flex: 0 0 auto;
                margin-top: 10px;
            }
            </style>
        """, unsafe_allow_html=True)

        # Get current flashcard
        current_card = flashcards[st.session_state.index]
        
        # Main container
        st.markdown("""
            <div class="main-container">
        """, unsafe_allow_html=True)
        
        # Image
        st.markdown(f'''
            <div class="image-container">
                <img src="{current_card['meme_url']}" 
                     style="width:100%;max-width:350px;border-radius:15px;object-fit:cover;margin:0 auto;display:block;">
            </div>
        ''', unsafe_allow_html=True)
        
        # Text content
        st.markdown(f"""
            <div class="text-content">
                <div class="character">{current_card['chinese']}</div>
                <div class="pinyin">{current_card['pinyin']}</div>
                <div class="explanation">{current_card['english']}</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Audio implementation with mobile support
        if 'last_index' not in st.session_state:
            st.session_state.last_index = -1
            
        # Only regenerate audio if card changed
        if st.session_state.last_index != st.session_state.index:
            audio_data = get_audio(current_card["chinese"])
            st.session_state.last_index = st.session_state.index
            if audio_data:
                st.audio(audio_data, format='audio/mp3')
        
        # Next button
        st.markdown("""
            <div class="button-container">
        """, unsafe_allow_html=True)
        if st.button("Next Card"):
            st.session_state.index = (st.session_state.index + 1) % len(flashcards)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
