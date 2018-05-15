#!/usr/bin/env python

"""
Script for extracting species from a CSV taxonomy file.
The species are output one per line to a 'species.txt' file.
"""
import csv
import sys


def process_csv_data(csv_path):
    with open(csv_path, 'r') as csv_file, open('species.txt', 'w') as species_file:
        print(f'Extracting species from {csv_path}')
        reader = csv.DictReader(csv_file, delimiter=';')
        processed = 0
        for row in reader:
            species_file.write(f'{row["Scientific Name"]}\n')
            processed += 1

    return processed


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print('processed={}'.format(process_csv_data(sys.argv[1])))
