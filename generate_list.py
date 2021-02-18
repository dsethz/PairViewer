#######################################################################################################################
# This script constructs a .csv file to load into PairViewer.                                                         #
# Author:               Daniel Schirmacher                                                                            #
#                       PhD Student, Cell Systems Dynamics Group, D-BSSE, ETH Zurich                                  #
# Python Version:       3.8.6                                                                                         # 
# PyTorch Version:      1.7.0                                                                                         #
#######################################################################################################################
import re
import glob
import argparse

import pandas as pd


def arg_parse():
    '''
        Catch user input.


        Parameter
        ---------
        
        -


        Return
        ------

        Returns a namespace from `argparse.parse_args()`.
    '''
    desc = "Program to train a segmentation model."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--movie',
                        type=str,
                        default='T:/TimelapseData/201124SK30/',
                        help='Path to movie directory.')

    parser.add_argument('--left',
                        type=str,
                        default='w00.png',
                        help='Identifier of .png files used for the left frame.')

    parser.add_argument('--right',
                        type=str,
                        default='w02.png',
                        help='Identifier of .png files used for the right frame.')

    parser.add_argument('--out',
                        type=str,
                        default='C:/Users/schidani/Desktop/',
                        help='Path to output directory.')

    return parser.parse_args()


def main():
    args = arg_parse()

    movie_path = args.movie
    left = args.left
    right = args.right
    out_path = args.out

    pattern = re.compile(r'[0-9]{6}[A-Z]{2}[0-9]{2}')
    movie = pattern.search(movie_path)[0]

    files_l = glob.glob(movie_path + '*/*' + left)
    files_l.sort()
    files_r = glob.glob(movie_path + '*/*' + right)
    files_r.sort()

    df = pd.DataFrame({'left': files_l, 'right': files_r})
    df.to_csv(out_path + movie + '_paths.csv', header=None, index=None)


if __name__ == '__main__':
    main()


