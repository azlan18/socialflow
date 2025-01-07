import requests
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import streamlit.components.v1 as components

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = st.secrets["LANGFLOW_ID"]
FLOW_ID = st.secrets["FLOW_ID"]
APPLICATION_TOKEN = st.secrets["APP_TOKEN"]
ENDPOINT = "socialmedia-1"

def run_flow(message: str) -> dict:
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{ENDPOINT}"
    
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }
    
    headers = {"Authorization": "Bearer " + APPLICATION_TOKEN, "Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

def load_data():
    data = {
        'post_id': range(101, 121),
        'post_type': ['reel', 'video', 'carousel', 'video', 'carousel', 'carousel', 'reel', 'reel', 
                     'carousel', 'reel', 'carousel', 'static_image', 'static_image', 'video', 'video',
                     'reel', 'video', 'carousel', 'carousel', 'reel'],
        'topic': ['fashion', 'technology', 'fashion', 'technology', 'technology', 'memes', 'sports',
                 'memes', 'fashion', 'dance', 'technology', 'technology', 'technology', 'dance',
                 'dance', 'memes', 'fashion', 'memes', 'memes', 'technology'],
        'likes': [2614, 5274, 7593, 7852, 1718, 730, 9928, 10288, 1218, 5304, 3198, 2206, 4365,
                 3086, 7508, 8472, 3065, 4154, 1211, 8764],
        'comments': [4743, 5729, 2044, 852, 453, 1115, 4095, 3224, 1406, 930, 783, 520, 1057,
                    5185, 1116, 887, 1838, 1220, 362, 941],
        'shares': [2688, 322, 97, 576, 369, 405, 1612, 2824, 501, 1575, 1085, 313, 67, 3815,
                  690, 2248, 1589, 1015, 418, 3677],
        'saves': [1443, 548, 588, 952, 282, 273, 1748, 2353, 741, 573, 495, 358, 86, 1086,
                 457, 1006, 395, 612, 278, 1751],
        'reach': [6108, 29954, 50988, 20765, 16666, 3073, 91857, 45656, 1843, 33798, 31571,
                 17030, 19326, 16349, 11993, 74735, 20911, 7335, 4680, 20255],
        'engagement_rate': [8.8808, 0.3964, 0.2024, 0.4928, 0.1693, 2.821, 3.1892, 0.4093,
                          2.0977, 0.248, 0.1761, 0.1995, 0.2885, 0.8057, 0.8147, 1.1688,
                          0.3293, 0.9545, 0.4848, 0.7471]
    }
    return pd.DataFrame(data)

def create_visualizations(df):
    # 1. Bar chart for engagement metrics by post type
    engagement_by_type = df.groupby('post_type')[['likes', 'comments', 'shares']].mean().reset_index()
    fig_engagement = px.bar(engagement_by_type, x='post_type', y=['likes', 'comments', 'shares'],
                          title='Average Engagement Metrics by Post Type',
                          barmode='group')
    
    # 2. Scatter plot of engagement rate vs reach
    fig_scatter = px.scatter(df, x='reach', y='engagement_rate', color='post_type',
                           title='Engagement Rate vs Reach by Post Type',
                           hover_data=['post_id'])
    
    # 3. Pie chart of post type distribution
    post_type_dist = df['post_type'].value_counts()
    fig_pie = px.pie(values=post_type_dist.values, names=post_type_dist.index,
                    title='Distribution of Post Types')
    
    # 4. Topic-based average engagement rates
    topic_engagement = df.groupby('topic')['engagement_rate'].mean().reset_index()
    fig_topic = px.bar(topic_engagement, x='topic', y='engagement_rate',
                      title='Average Engagement Rate by Topic')
    
    return fig_engagement, fig_scatter, fig_pie, fig_topic

def main():
    st.set_page_config(layout="wide")
    
    # Center-aligned title using markdown
    st.markdown("<h1 style='text-align: center;'>📊Social Flow Chat Dashbaord</h1>", unsafe_allow_html=True)
    
    # Add Lottie animation using HTML component
    # Updated Lottie animation using HTML component
    lottie_html = """
    <script src="https://unpkg.com/@dotlottie/player-component@2.7.12/dist/dotlottie-player.mjs" type="module"></script>
    <div style="display: flex; justify-content: center; gap: 20px;">
        <dotlottie-player 
            src="https://lottie.host/a04ffede-c907-4887-9465-a2d7bf40728b/fisXVd47zw.lottie" 
            background="transparent" 
            speed="1" 
            style="width: 300px; height: 300px" 
            loop 
            autoplay>
        </dotlottie-player>
        <dotlottie-player 
            src="https://lottie.host/2b20015a-75eb-4ada-8998-074917d3227f/gGQ1hoWAy0.lottie" 
            background="transparent" 
            speed="1" 
            style="width: 300px; height: 300px" 
            loop 
            autoplay>
        </dotlottie-player>
    </div>
    """
    components.html(lottie_html, height=320)

    
    if 'streaming' not in st.session_state:
        st.session_state.streaming = False
    
    message = st.text_area("Ask me anything about your social media performance:", 
                          placeholder="E.g., What type of content performs best?")
    
    if st.button("Analyze"):
        if not message.strip():
            st.error("Please enter a question")
            return
        
        try:
            stream_container = st.empty()
            
            with st.spinner("Getting AI analysis... Please wait, could take up to 30 seconds"):
                response = run_flow(message)
                response_text = response["outputs"][0]["outputs"][0]["results"]["message"]["text"]
            
            with stream_container.container():
                st.markdown("### AI Analysis")
                message_placeholder = st.empty()
                for i in range(len(response_text) + 1):
                    message_placeholder.markdown(response_text[:i] + "▌")
                    time.sleep(0.004)
                message_placeholder.markdown(response_text)
                
                st.markdown("---")
                
                df = load_data()
                
                st.markdown("### Key Metrics")
                metrics_container = st.container()
                with metrics_container:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    time.sleep(0.5)
                    with col1:
                        st.metric("Total Posts", len(df))
                    time.sleep(0.3)
                    with col2:
                        st.metric("Avg. Likes", int(df['likes'].mean()))
                    time.sleep(0.3)
                    with col3:
                        st.metric("Avg. Engagement Rate", f"{df['engagement_rate'].mean():.2f}%")
                    time.sleep(0.3)
                    with col4:
                        st.metric("Total Reach", df['reach'].sum())
                
                st.markdown("### Performance Visualizations")
                fig_engagement, fig_scatter, fig_pie, fig_topic = create_visualizations(df)
                
                time.sleep(0.5)
                st.plotly_chart(fig_engagement, use_container_width=True)
                time.sleep(0.3)
                st.plotly_chart(fig_scatter, use_container_width=True)
                
                col1, col2 = st.columns(2)
                time.sleep(0.3)
                with col1:
                    st.plotly_chart(fig_pie, use_container_width=True)
                time.sleep(0.3)
                with col2:
                    st.plotly_chart(fig_topic, use_container_width=True)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
