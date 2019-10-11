from flask import Flask, g, request
from Dbcontroller import Dbcontroller

def main():
	database = Dbcontroller('database1')
	print(database.get_file())

if __name__ == "__main__":
	main()