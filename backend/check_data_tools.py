import pandas as pd
try:
    df = pd.read_csv(r'd:\projects\StudioFlowAI\backend\app\ml\data\Social Media Engagement Dataset.csv')
    print(df.columns)
    print(df[['timestamp', 'likes_count', 'impressions']].head())
except Exception as e:
    print(e)
