from openpyxl import load_workbook

workbook = load_workbook(filename='Parse Event Metadata.xlsm', read_only=True)

genre_table = workbook['Genre Table']

genres = set()

for row in genre_table.rows:
	#for cell in row:
	genres_split = [genre.split('/') for genre in row[1].value.split(', ')]
	genres_split = set([genre for sublist in genres_split for genre in sublist])
	genres.update(genres_split)

