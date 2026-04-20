import streamlit as st
import pandas as pd
import re

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="AI Chat Analyzer", page_icon="💬", layout="centered")

st.title("💬 AI Chat Analyzer")
st.caption("Reveal hidden patterns in your conversation")
st.divider()

# FUNCTIONS

def parse_chat(lines):
    data = []
    for line in lines:
        match = re.match(r'(.+?) - (.+?): (.+)', line)
        if match:
            datetime, sender, message = match.groups()
            data.append([datetime, sender, message])

    df = pd.DataFrame(data, columns=["datetime", "sender", "message"])
    return df


def analyze_chat(df):
    count = df['sender'].value_counts()
    df['message_length'] = df['message'].apply(len)
    length = df.groupby('sender')['message_length'].mean()

    effort_score = {}
    for person in count.index:
        effort_score[person] = (count[person] * 0.5) + (length[person] * 0.5)

    return count, length, effort_score


def get_insight(effort_score):
    top_person = max(effort_score, key=effort_score.get)
    low_person = min(effort_score, key=effort_score.get)

    diff = effort_score[top_person] - effort_score[low_person]

    if diff > 5:
        return f"⚠️ {top_person} is putting significantly more effort. Possible imbalance detected."
    elif diff > 2:
        return "ℹ️ There is a slight imbalance in the conversation."
    else:
        return "✅ Conversation looks balanced."

# UI

uploaded_file = st.file_uploader("Upload chat WhatsApp (.txt)", type=["txt"])

if uploaded_file is not None:
    try:
        lines = uploaded_file.read().decode("utf-8").splitlines()

        df = parse_chat(lines)

        if df.empty:
            st.error("❌ File cannot be read, make sure the file format is correct")
        else:
            st.success("✅ Chat SUccesfully Analyzed")

            count, length, effort_score = analyze_chat(df)

            top_person = max(effort_score, key=effort_score.get)

            # METRICS

            st.subheader("📊 Analysis Result")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("🔥 Top Effort", top_person)

            with col2:
                st.metric("💬 Total Messages", len(df))

            with col3:
                st.metric("👥 Participants", df['sender'].nunique())

            # CHART
            
            st.subheader("📈 Message Distribution")
            st.bar_chart(count.sort_values())

            # INSIGHT

            st.subheader("🧠 Insight")
            st.write(get_insight(effort_score))

            # STARTER ANALYSIS

            df['new_chat'] = df['datetime'].ne(df['datetime'].shift())
            starter = df[df['new_chat']].groupby('sender').size()

            st.subheader("🚀 Conversation Starter")
            st.write(starter)

            # RAW DATA

            with st.expander("🔍 See raw data"):
                st.dataframe(df)

    except Exception as e:
        st.error(f"⚠️ Error Code: {e}")