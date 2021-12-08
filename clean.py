#!/usr/bin/env python3
import argparse
import csv
import datetime
import pathlib
import re

import bs4
from markdown import markdown


def main(args):
    cleaned_comments = []

    print(f'Opening {args.infile}')

    with args.infile.open('r') as f:
        reader = csv.DictReader(f)

        print('Cleaning Reddit text')

        for row in reader:
            cleaned_text = remove_quote(row['text'])
            cleaned_text = remove_removed_or_deleted(cleaned_text)
            cleaned_text = remove_edit(cleaned_text)
            cleaned_text = remove_zero_width_space(cleaned_text)
            cleaned_text = remove_markdown(cleaned_text)
            cleaned_text = remove_urls(cleaned_text)
            row['body'] = cleaned_text

            cleaned_comments.append(row)

    print(f'Writing results to {args.outfile}')

    with args.outfile.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=cleaned_comments[0].keys())
        writer.writeheader()
        writer.writerows(cleaned_comments)

        print(f'Cleaned text written to {args.outfile}')


def remove_quote(text):
    lines = [l for l in text.splitlines() if not l.startswith('>')]
    cleaned_text = ' '.join(lines)
    
    return cleaned_text


def remove_removed_or_deleted(text):
    return text.replace('[removed]', '').replace('[deleted]', '')


def remove_edit(text):
    return text.replace('Edit:', '')


def remove_zero_width_space(text):
    return text.replace('&#x200B;', '')


def remove_markdown(text):
    soup = bs4.BeautifulSoup(markdown(text), 'html.parser')
    cleaned_text = ' '.join(soup.stripped_strings)
    
    return cleaned_text


def remove_urls(text):
    pattern = r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])'
    cleaned_text = re.sub(pattern, repl='', string=text)

    return cleaned_text


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--infile',
        type=pathlib.Path,
        dest='infile',
        required=True,
        help='Location of the input CSV file containing Reddit comments'
    )
    parser.add_argument(
        '-o', '--outfile',
        type=pathlib.Path,
        dest='outfile',
        default=pathlib.Path.cwd() / f'comments_cleaned_{datetime.date.today()}',
        help='The destination file where cleaned Reddit data will be saved'
    )
    args = parser.parse_args()
    main(args)
