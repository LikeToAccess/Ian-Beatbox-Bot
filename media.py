# -*- coding: utf-8 -*-
# filename          : media.py
# description       : Holds important functions for the project
# author            : LikeToAccess
# email             : liketoaccess@protonmail.com
# date              : 05-04-2021
# version           : v1.0
# usage             : python main.py
# notes             :
# license           : MIT
# py version        : 3.8.2 (must run on 3.6 or higher)
#==============================================================================
import os


def log(msg):
	append_file("log.txt", msg)

def credit(author, filename, resolution, file_size):
	msg = f"{filename}|{resolution}|{file_size}"
	append_file(f"{author}.txt", msg)

def format_title(filename):
	if "/" in filename: filename = filename.split("/")[::-1][0]
	filename = " ".join([word.capitalize() for word in filename.split(".")[0].split()])
	return filename

def remove_file(filename):
	try:
		os.remove(filename)
		return True
	except OSError:
		return False

def rename(filename_old, filename_new):
	filename = filename_new.split(".")
	filename_new = f"{filename[0].strip()}.{filename[1]}"
	try: os.rename(filename_old, filename_new)
	except FileExistsError:
		remove_file(filename_new)
		msg = f"Removed old version of show to be replaced with new version, {filename_new}"
		print(msg)
		log(msg)
		rename(filename_old, filename_new)
	return f"RENAME: {filename_old} -> {filename_new}"

def read_file(filename, directory=None, filter=False):
	if directory:
		os.chdir(f"{os.getcwd()}/{directory}")
	with open(filename, "r") as file:
		lines = file.read().split("\n")
	if filter:
		lines = filter_list(lines)
	return lines

def write_file(filename, msg):
	with open(filename, "w") as file:
		file.write(msg)

def append_file(filename, msg):
	with open(filename, "a") as file:
		file.write(f"{msg}\n")

def filter_list(lines, filename=False):
	if filename:
		lines = read_file(filename)
	data = []
	for line in lines:
		if line[:1] != "#" and line != "":
			data.append(line)
	return data
