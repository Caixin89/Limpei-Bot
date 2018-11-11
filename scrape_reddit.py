# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import praw, csv, re

reddit = praw.Reddit(client_id=<client-id>,
                     client_secret=<client-secret>,
                     user_agent=<name of application>,
                     username=<username>,
                     password=<password>)
                     
subreddit = reddit.subreddit('Jokes')            
top_subreddit = subreddit.top(limit=1000)         
jokes_dict = { "title":[],
                "score":[],
                "id":[], "url":[],
                "comms_num": [],
                "created": [],
                "body":[]}
                
for submission in top_subreddit:
    jokes_dict["title"].append(submission.title)
    jokes_dict["score"].append(submission.score)
    jokes_dict["id"].append(submission.id)
    jokes_dict["url"].append(submission.url)
    jokes_dict["comms_num"].append(submission.num_comments)
    jokes_dict["created"].append(submission.created)
    jokes_dict["body"].append(submission.selftext)                
        
with open("jokes2.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerow(["Joke"])
        
    for title, body in zip(jokes_dict["title"], jokes_dict["body"])[1:]:
        title = re.sub(r"\s+", " ", title)
        #If title does not end in puctuation, add full stop.
        if not re.match(r"[!.,?]$", title):
            title += "."
        body = re.sub(r"\s+", " ", body)        
        writer.writerow([title.encode("utf-8") + " " + body.encode("utf-8")])
    
    