import tkinter as tk

# Set number of rows and columns
ROWS = 7
COLS = 24
BORDER_WIDTH = 0
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
days = ['M', 'Tu', 'W', 'Th', 'F', 'Sa', 'Su']

# Create a grid of None to store the references to the tiles
tiles = [[None for _ in range(COLS)] for _ in range(ROWS)]

def callback(event):
# Get rectangle diameters
	col_width = c.winfo_width()/COLS
	row_height = c.winfo_height()/ROWS

	# Calculate column and row number
	col = int(event.x // col_width)
	row = int(event.y // row_height)

	# If the tile is not filled, create a rectangle
	if not tiles[row][col]:
		tiles[row][col] = c.create_rectangle(	col*col_width, 		#Top Left Corner X
												row*row_height,		#Top Left Corner Y
												(col+1)*col_width, 	#Bottom Right Corner X
												(row+1)*row_height,	#Bottom Right Corner Y
												fill="#ff4079",		#Fill of the rectangle
												outline = "white",	#Border of the Rectangle 
												width = 5)			#Width of the border

	# If the tile is filled, delete the rectangle and clear the reference
	else:
		c.delete(tiles[row][col])
		tiles[row][col] = None

# Create the window, a canvas and the mouse click event binding
root = tk.Tk()
root.resizable(height = None, width = None)
c = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, borderwidth=BORDER_WIDTH, background='white')
c.pack()
c.bind("<Button-1>", callback)
root.mainloop()