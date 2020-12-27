import logging
import argparse
import json

from timetable_bot import run_bot

logging.basicConfig(level=logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='Path to configuration file',
                        required=True, type=str)
    return parser.parse_args()


def load_config(path_to_config):
    with open(path_to_config, 'r') as fo:
        config = json.load(fo)
    return config


if __name__ == '__main__':
    args = parse_args()
    config = load_config(args.config)
    run_bot(config)

