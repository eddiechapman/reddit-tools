#!/usr/bin/env python3
import argparse
import csv
from dataclasses import dataclass, asdict
import pathlib
from pprint import pprint

from more_itertools.recipes import sliding_window
from treelib import Tree
from treelib.exceptions import NodeIDAbsentError

INFILE = pathlib.Path('gore_comments.csv')


@dataclass
class Comment:
    id: str
    parent: str
    depth: int


class CommentPath:
    
    def __init__(self, comments):
        self.id = f'{comments[0]}-{comments[-1]}'
        self.length = len(comments)
        self.comments = comments
        self.comment0 = self.get_comment(0)
        self.comment1 = self.get_comment(1)
        self.comment2 = self.get_comment(2)
        self.comment3 = self.get_comment(3)
    
    def get_comment(self, n):
        try:
            return self.comments[n]
        except IndexError:
            return None

    def to_dict(self):
        return {
            'id': self.id,
            'length': self.length,
            'comment0': self.comment0,
            'comment1': self.comment1,
            'comment2': self.comment2,
            'comment3': self.comment3
        }


def read_comments(infile):
    with infile.open('r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield Comment(
                id=row['comment_id'], 
                parent=row['reply_to'].replace('t3_', '').replace('t1_', ''), 
                depth=row['depth']
            )

def main(args):
    tree = Tree()
    orphans = []
    comments = [comment for comment in read_comments(args.infile)]
    comments.sort(key=lambda x: x.depth)

    # create root node (submission post not included in input data)
    tree.create_node(identifier=comments[0].parent, parent=None)

    for comment in comments:
        try:
            tree.create_node(identifier=comment.id, parent=comment.parent)
        except NodeIDAbsentError:
            orphans.append(comment)

    paths = [path[2:] for path in tree.paths_to_leaves() if len(path) > 3]
    
    sub_paths = []
    for path in paths:
        for i in [2, 3, 4]:
            for sub_path in sliding_window(path, i):
                comment_path = CommentPath(sub_path)
                sub_paths.append(comment_path)

    sub_paths = [p.to_dict() for p in sub_paths]
    fieldnames = sub_paths[0].keys()

    with args.outfile.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sub_paths)
    
    print(f'Results written to {args.outfile}')
    print(f'Orphan comments: {len(orphans)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--infile',
        type=pathlib.Path,
        dest='infile',
        help='The path to a CSV file containing Reddit data scraped using PRAW.'
    )
    parser.add_argument(
        '-o', '--outfile',
        type=pathlib.Path,
        dest='outfile',
        help='The path where CSV results will be written'
    )
    args = parser.parse_args()
    main(args)
