#!/usr/bin/env python3
"""
scrape.py

Collect submission and comment data from the top submissions of a Subreddit.

Eddie Chapman
2021-10-14

"""
import argparse
import csv
import datetime
import os
import pathlib

import dotenv
import praw


def main(args):
    dotenv.load_dotenv()

    print('Authenticating with Reddit API...')
    reddit = praw.Reddit(
        client_id=os.environ.get('CLIENT_ID'), 
        client_secret=os.environ.get('CLIENT_SECRET'),
        user_agent=os.environ.get('USER_AGENT')
    )
    
    print(f'Fetching submission {args.submission}...')
    submission = reddit.submission(id=args.submission)

    reddit_data = []

    print(f'Unpacking comments for submission {submission.id}...')
    print(f'This may take a while. Total comments: {submission.num_comments}')
    submission.comments.replace_more(limit=None)
    comments = submission.comments.list()

    for comment in comments:
        reddit_data.append({
            'subreddit': comment.subreddit.display_name,
            'submission_id': submission.id,
            'comment_id': comment.id,
            'comment_name': comment.name,
            'depth': comment.depth,
            'author': comment.author.name if comment.author else None,
            'timestamp': datetime.datetime.utcfromtimestamp(comment.created_utc),
            'score': comment.score,
            'title': None,
            'text': comment.body,
            'is_submitter': comment.is_submitter,
            'reply_to': comment.parent_id,
            'url': comment.permalink
        })
        
    column_names = [
        'subreddit', 'submission_id', 'comment_id', 'comment_name', 'depth', 'author', 
        'timestamp', 'score', 'title', 'text', 'is_submitter', 'reply_to', 'url'
    ]

    if args.outfile.exists():
        print(f'Caution: Overwriting output file: {args.outfile}')

    with args.outfile.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=column_names)
        writer.writeheader()
        writer.writerows(reddit_data)
        print(f'Data written to output file: {args.outfile}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o', '--outfile', 
        type=pathlib.Path, 
        default=pathlib.Path.cwd() / f'comments_{datetime.date.today()}.csv', 
        dest='outfile',
        help='The destination of the output file'
    )
    parser.add_argument(
        '-s', '--submission', 
        type=str, 
        dest='submission', 
        required=True,
        help='ID of submission you would like to scrape (found at end of URL ie. `2gmzqe`)'
    )
    args = parser.parse_args()
    main(args)
