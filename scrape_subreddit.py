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
    
    print(f'Fetching subreddit {args.subreddit}...')
    subreddit = reddit.subreddit(args.subreddit)

    if args.top:
        print(f'Fetching {args.max_submissions} top submissions...')
        submissions = subreddit.top(limit=args.max_submissions)
    elif args.hot:
        print(f'Fetching {args.max_submissions} hot submissions...')
        submisisons = subreddit.hot(limit=args.max_submissions)
    elif args.controversial:
        print(f'Fetching {args.max_submissions} controversial submissions...')
        submissions = subreddit.controversial(limit=args.max_submissions)
    
    reddit_data = []

    for submission in submissions:
        print(f'Collecting data from submission {submission.id}...')

        if submission.num_comments > args.max_comments:
            print(f'Skipping {submission.id}  because it contains too many comments ({submission.num_comments} > {args.max_comments})')
            continue

        reddit_data.append({
            'subreddit': submission.subreddit.display_name,
            'submission_id': submission.id,
            'comment_id': None,
            'type': 'submission',
            'author': submission.author.name if submission.author else None,
            'timestamp': datetime.datetime.utcfromtimestamp(submission.created_utc),
            'score': submission.score,
            'title': submission.title,
            'text': submission.selftext,
            'is_submitter': True,
            'reply_to': None,
            'url': submission.url,
            
        })

        print(f'Unpacking comments for submission {submission.id}...')
        print(f'This may take a while. Total comments: {submission.num_comments}')
        submission.comments.replace_more(limit=None)
        comments = submission.comments.list()

        for comment in comments:
            reddit_data.append({
                'subreddit': comment.subreddit.display_name,
                'submission_id': submission.id,
                'comment_id': comment.id,
                'type': 'comment',
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
        'subreddit', 'submission_id', 'comment_id', 'type', 'author', 'timestamp', 
        'score', 'title', 'text', 'is_submitter', 'reply_to', 'url'
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
        '-n', '--n_submissions', 
        type=int, 
        default=10, 
        dest='max_submissions',
        help='The number of submissions (posts) to collect from the subreddit'
    )
    parser.add_argument(
        '-s', '--subreddit', 
        type=str, 
        dest='subreddit', 
        required=True,
        help='Name of subreddit you would like to scrape (do not include prefix "r/")'
    )
    parser.add_argument(
        '--max_comments',
        type=int,
        dest='max_comments',
        default=25_000,
        help='Skip submissions with comment count exceeding this number'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--top',
        dest='top',
        default=True,
        action='store_true',
        help='Return "top" submissions from a given subreddit'
    )
    group.add_argument(
        '--hot',
        dest='hot',
        default=False,
        action='store_true',
        help='Return "hot" submissions from a given subreddit'
    )
    group.add_argument(
        '--controversial',
        dest='controversial',
        default=False,
        action='store_true',
        help='Return "controversial" submissions from a given subreddit'
    )
    args = parser.parse_args()
    main(args)
