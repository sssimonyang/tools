#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
@author: SSSimon Yang
@contact: yangjingkang@126.com
@file: image_arrangement.py
@time: 2020/6/28 13:45
@desc:
"""
import argparse
import json
import os
import shutil
import time

import exifread

file_category = ['img', 'video', 'other', 'video/big', 'video/small', 'img/big_withtime', 'img/big_withouttime',
                 'img/small']
time_dir = 'img/big_withtime'


def makedirs(file_category):
    for category in file_category:
        directory = os.path.join(*category.split('/'))
        if not os.path.exists(directory):
            os.mkdir(directory)


def timedir_prepare(timedir):
    timedir = os.path.join(*timedir.split('/'))
    for i in range(1998, time.localtime().tm_year + 1):
        directory = os.path.join(timedir, f'{i}')
        if not os.path.exists(directory):
            os.mkdir(directory)

        for j in range(1, 13):
            directory = os.path.join(timedir, f'{i}', f'{j:02}')
            if not os.path.exists(directory):
                os.mkdir(directory)


def timedir_end(timedir):
    # os.removedirs区别
    timedir = os.path.join(*timedir.split('/'))
    for i in range(1998, time.localtime().tm_year + 1):
        for j in range(1, 13):
            directory = os.path.join(timedir, f'{i}', f'{j:02}')
            if not os.listdir(directory):
                os.rmdir(directory)
    for i in range(1998, time.localtime().tm_year + 1):
        directory = os.path.join(timedir, f'{i}')
        if not os.listdir(directory):
            os.rmdir(directory)


def get_photo_time(file):
    f = open(file, 'rb')
    tags = exifread.process_file(f)
    if tags and 'Image DateTime' in tags:
        photo_time = tags.get('Image DateTime').values
        if photo_time:
            print(f'{file} {photo_time}')
            return time.strftime('%Y/%m', time.strptime(photo_time[:19], '%Y:%m:%d %H:%M:%S'))

    print(f'{file} without time')
    return None


def move(to_where, file_path, ext, remove=False, photo_time=None):
    if to_where.endswith('withtime') and photo_time:
        to_file_path = os.path.join(*to_where.split('/'), *photo_time.split('/'))
    else:
        to_file_path = os.path.join(*to_where.split('/'))
    if remove:
        shutil.move(file_path,
                    os.path.join(f'{to_file_path}', f'{len(os.listdir(to_file_path)) + 1:03}') + '.' + ext)
    else:
        shutil.copyfile(file_path,
                        os.path.join(f'{to_file_path}', f'{len(os.listdir(to_file_path)) + 1:03}') + '.' + ext)


def process_files(root, files, remove):
    for file in files:
        file_path = os.path.join(root, file)
        ext = os.path.splitext(file_path)[1][1:].lower()
        if ext not in format_map.keys():
            file_type = input(f"{ext}属于何种类型：")
            while file_type not in ['img', 'video', 'other']:
                print(f"请输入img或video或other")
                file_type = input(f"{ext}属于何种类型：")
            format_map[ext] = file_type
        photo_time = None
        to_where = ''
        if format_map[ext] == 'img':
            if os.path.getsize(file_path) >= 1024 ** 2:
                photo_time = get_photo_time(file_path)
                if photo_time:
                    to_where = 'img/big_withtime'
                else:
                    to_where = 'img/big_withouttime'
            else:
                to_where = 'img/small'
        if format_map[ext] == 'video':
            if os.path.getsize(file_path) >= 1024 ** 2:
                to_where = 'video/big'
            else:
                to_where = 'video/small'
        if format_map[ext] == 'other':
            to_where = 'other'
        move(to_where, file_path, ext, remove, photo_time)


def main(process_directory, to_directory, remove=False):
    curdir = os.path.abspath(os.curdir)
    os.chdir(to_directory)
    makedirs(file_category)
    timedir_prepare(time_dir)
    for root, dirs, files in os.walk(process_directory):
        process_files(root, files, remove)
    timedir_end(time_dir)
    os.chdir(curdir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="specify the image directory you want to process")
    parser.add_argument("-o", "--out", help="specify the directory to store file, empty is recommended")
    parser.add_argument("-remove", "--remove", help="remove the raw file or false", action="store_true")
    args = parser.parse_args()
    with open('format.json', 'r') as f:
        format_map = json.load(f)
    main(args.dir, args.out, args.remove)
    with open('format.json', 'w') as f:
        json.dump(format_map, f, indent=2)
