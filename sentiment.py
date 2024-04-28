import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sid = SentimentIntensityAnalyzer()

def get_sentiment_label(score):
    if score >= 0.5:
        return "Very Positive"
    elif score >= 0.2:
        return "Positive"
    elif score >= -0.2:
        return "Neutral"
    elif score >= -0.5:
        return "Negative"
    else:
        return "Very Negative"

def get_tonality_sentiment(transcript):
    sentences = nltk.sent_tokenize(transcript)
    
    tonality_score = 0
    
    for sentence in sentences:
        sentiment = sid.polarity_scores(sentence)
        tonality_score += sentiment['compound']
    
    num_sentences = len(sentences)
    tonality_score /= num_sentences
    
    sentiment_label = get_sentiment_label(tonality_score)
    
    return sentiment_label