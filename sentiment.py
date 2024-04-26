import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Load the VADER sentiment analyzer
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
    # Tokenize the transcript into sentences
    sentences = nltk.sent_tokenize(transcript)
    
    # Initialize tonality score
    tonality_score = 0
    
    # Calculate sentiment score for each sentence and aggregate
    for sentence in sentences:
        sentiment = sid.polarity_scores(sentence)
        tonality_score += sentiment['compound']
    
    # Calculate average tonality score
    num_sentences = len(sentences)
    tonality_score /= num_sentences
    
    # Get sentiment label
    sentiment_label = get_sentiment_label(tonality_score)
    
    return sentiment_label