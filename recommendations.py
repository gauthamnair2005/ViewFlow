from models import Video, ViewHistory, User
from sqlalchemy import func, desc
from collections import Counter, defaultdict
import random
import math

def get_user_profile_vector(user_id):
    """
    Builds a weighted feature vector for the user based on watch history.
    Features: Categories, Tags, Channels.
    Weights: Recency (Decay), Frequency (Replays), Context (Last 2 videos).
    """
    # Get last 50 views for long-term profile
    history = ViewHistory.query.filter_by(user_id=user_id).order_by(ViewHistory.timestamp.desc()).limit(50).all()
    
    if not history:
        return None

    # 1. Analyze Replays (Frequency)
    video_counts = Counter([h.video_id for h in history])
    
    # 2. Build User Profile Vector
    user_vector = defaultdict(float)
    
    # Hyperparameters
    WEIGHT_CATEGORY = 3.0
    WEIGHT_TAG = 1.0
    WEIGHT_CHANNEL = 2.0
    DECAY_FACTOR = 0.95  # 5% decay per step back in history
    
    # Short-term context (Last 2 videos) - "Current Mood"
    last_2_ids = [h.video_id for h in history[:2]]
    
    for idx, h in enumerate(history):
        if not h.video:
            continue
            
        # Time Decay: Recent views have higher weight
        recency_weight = pow(DECAY_FACTOR, idx)
        
        # Replay Multiplier: Boost if watched multiple times
        # Logarithmic scaling to prevent spamming from dominating
        replay_count = video_counts[h.video_id]
        replay_mult = 1.0 + math.log(replay_count) if replay_count > 1 else 1.0
        
        # Short-term Context Boost: Massive boost for the immediate previous videos
        context_boost = 2.5 if h.video_id in last_2_ids else 1.0
        
        # Final Event Weight
        final_weight = recency_weight * replay_mult * context_boost
        
        # Feature Extraction & Weighting
        if h.video.category:
            user_vector[f"cat:{h.video.category}"] += WEIGHT_CATEGORY * final_weight
        
        if h.video.tags:
            # tags are comma separated
            t_list = [t.strip().lower() for t in h.video.tags.split(',') if t.strip()]
            for tag in t_list:
                user_vector[f"tag:{tag}"] += WEIGHT_TAG * final_weight
                
        user_vector[f"chan:{h.video.user_id}"] += WEIGHT_CHANNEL * final_weight

    return user_vector

def get_recommendations(user_id, limit=4, exclude_video_ids=None):
    if not user_id:
        return []
    
    user_vector = get_user_profile_vector(user_id)
    
    if not user_vector:
        return []

    # Fetch candidate videos (public videos)
    query = Video.query.filter_by(is_public=True)
    
    if exclude_video_ids:
        query = query.filter(~Video.id.in_(exclude_video_ids))
    
    candidates = query.all()
    
    scored_videos = []
    for vid in candidates:
        score = 0
        
        # Dot Product: User Vector • Video Feature Vector
        
        # Category Match
        if vid.category:
            score += user_vector.get(f"cat:{vid.category}", 0)
        
        # Tag Match
        if vid.tags:
            v_tags = [t.strip().lower() for t in vid.tags.split(',') if t.strip()]
            for t in v_tags:
                score += user_vector.get(f"tag:{t}", 0)
        
        # Channel Match
        score += user_vector.get(f"chan:{vid.user_id}", 0)
        
        if score > 0:
            # Add a tiny random noise to break ties and add serendipity
            score += random.uniform(0, 0.5)
            scored_videos.append((score, vid))
            
    # Sort by score desc
    scored_videos.sort(key=lambda x: x[0], reverse=True)
    
    return [v for s, v in scored_videos[:limit]]

def get_channel_recommendation(user_id):
    user_vector = get_user_profile_vector(user_id)
    if not user_vector:
        return None, []
        
    # Extract channel scores from the vector
    channel_scores = {}
    for key, score in user_vector.items():
        if key.startswith("chan:"):
            chan_id = int(key.split(":")[1])
            channel_scores[chan_id] = score
            
    if not channel_scores:
        return None, []
        
    # Get top channel by score
    top_channel_id = max(channel_scores, key=channel_scores.get)
    channel = User.query.get(top_channel_id)
    
    if not channel:
        return None, []
    
    # Get videos from this channel
    videos = Video.query.filter_by(user_id=top_channel_id, is_public=True).order_by(Video.upload_date.desc()).limit(4).all()
    
    return channel, videos
