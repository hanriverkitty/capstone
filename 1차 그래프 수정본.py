import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


df = pd.read_csv('./result_.csv')


language_counts = df.groupby(['detected_source_language_name']).size().reset_index(name='counts')


sentiment_counts = df.groupby(['sentiment']).size().reset_index(name='counts')


sns.set(style='whitegrid')
sns.set_context("talk", rc={"lines.linewidth": 4.0})
fig, axes = plt.subplots(1, 2, figsize=(15,6))
sns.barplot(x='detected_source_language_name', y='counts', data=language_counts, ax=axes[0])
sns.barplot(x='sentiment', y='counts', data=sentiment_counts, ax=axes[1])


axes[0].set_title('detected_source_language_name별 댓글 수')
axes[1].set_title('sentiment별 댓글 수')


plt.show()

