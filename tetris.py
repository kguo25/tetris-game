from tkinter import font
import tkinter as tk
import random

pieces = [
            [
                [(1,-1), (1,0), (0,-1), (0,0)]
            ],
            [
                [(0, -2), (0,-1), (0,0), (0,1)], 
                [(1, 0), (0,0), (-1,0), (-2,0)]
            ],
            [
                [(1,0), (1,1), (0,-1), (0,0)],
                [(2,0), (1,0), (1,1), (0,1)]
            ],
            [
                [(1,-1), (1,0), (0,0), (0,1)],
                [(2,1), (1,0), (1,1), (0,0)]
            ],
            [
                [(1,1), (0,-1), (0,0), (0,1)],
                [(1,0), (0,0), (-1,0), (-1,1)],
                [(0,-1), (0,0), (0,1), (-1,-1)],
                [(1,0), (1,-1), (0,0), (-1,0)]
            ],
            [
                [(1,-1), (0,-1), (0,0), (0,1)],
                [(1,0), (1,1), (0,0), (-1,0)],
                [(0,-1), (0,0), (0,1),(-1,1)],
                [(1,0), (0,0), (-1,0), (-1,-1)]
            ],
            [
                [(1,0), (0,-1), (0,0), (0,1)],
                [(1,0), (0,0), (0,1), (-1,0)],
                [(0,-1), (0,0), (0,1), (-1,0)],
                [(1,0), (0,0), (0,-1), (-1,0)]
            ]
          ]
piece_colors = {0: "LightGoldenrod1", 1: "cyan", 2: "SeaGreen1", 3: "IndianRed1", 4: "coral", 5: "cornflower blue", 6: "MediumPurple1"}
rows = 20
columns = 10
size = 20

class TetrisBoard(tk.Frame):
    def __init__(self, parent, game, controller):
        self.game = game
        self.controller = controller

        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0,
                                width=(columns+9)*size, height=rows*size, background="gainsboro")
        self.canvas.pack(side="top", fill="both", expand=False, padx=2, pady=2)
        self.pack(side="top", fill="both", expand="True", padx=4, pady=4)

    def get_rectangle_coordinate(self, x, y):
        x1, y1 = (x+4) * size, y * size
        x2, y2 = x1 + size, y1 + size
        return (x1, y1, x2, y2)
    
    def show_move(self, tag):
        self.canvas.delete("falling")
        self.draw_piece(self.game.piece_ind, self.game.rot_ind, self.game.center, tag)

    def draw_board(self):
        self.canvas.delete("secured","info")
        for x in range(columns):
            for y in range(rows):
                x1, y1, x2, y2 = self.get_rectangle_coordinate(x, y)
                if self.game.b[y][x] > 0:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="gray10", fill=piece_colors[self.game.b[y][x]-1], tags="secured")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="gray10", fill="gray", tags="square")

    def update_next_pieces(self):
        self.canvas.delete("next_pieces")
        for i, piece_ind in enumerate(self.game.piece_queue.get_queue()):
            center = (columns + 2, 1+4*i)
            self.draw_piece(piece_ind, 0, center, "next_pieces")

    def update_hold_piece(self):
        self.canvas.delete("hold_piece")
        center = (-2,1)
        self.draw_piece(self.game.hold, 0, center, "hold_piece")

    def draw_piece(self, piece_ind, rot_ind, center, tag):
        for point in pieces[piece_ind][rot_ind]:
            x = point[1] + center[0]
            y = -point[0] + center[1]
            x1, y1, x2, y2 = self.get_rectangle_coordinate(x,y)
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="gray10", fill=piece_colors[piece_ind], tags=tag)

    def game_over(self):
        f = font.Font(size=20, weight="bold")
        self.canvas.create_rectangle(80,150, 280, 250, outline="black", fill="black", tags="info")
        self.canvas.create_text((int)(columns/2*size)+80, (int)(rows/2*size)-20, 
            anchor=tk.CENTER, text="Game Over", state=tk.DISABLED, fill="white", font=f, tags="info")
        new_game_button = tk.Button(self.game.root, text="New Game", command=self.controller.new_game)
        button_window = self.canvas.create_window((int)(columns/2*size)+80, (int)(rows/2*size)+20, 
            anchor=tk.CENTER, window=new_game_button, tag="info")

class TetrisGame():
    class PieceQueue():
        def __init__(self):
            self.queue = list()
            for i in range(4):
                self.queue.append(random.randint(0,6))
        
        def pop(self):
            self.queue.append(random.randint(0,6))
            return self.queue.pop(0)

        def get_queue(self):
            return self.queue

    def __init__(self):
        self.root = tk.Tk()
        self.controller = TetrisController(self.root, self)
        self.board = TetrisBoard(self.root, self, self.controller)

        self.start_game()
        self.root.mainloop()

    def start_game(self):
        self.b = [[0 for x in range (columns)] 
                        for y in range (rows)]
        self.game_over = False
        self.board.draw_board()
        self.piece_queue = self.PieceQueue()
        self.hold = None
        self.already_held = False
        self.add_new_piece()

    def add_new_piece(self, from_hold=False):
        if not from_hold:
            self.piece_ind = self.piece_queue.pop()
        else:
            self.piece_ind = self.hold
        self.rot_ind = 0
        self.center = ((int)(columns/2), 0)
        if self.collides(self.center, self.rot_ind):
            self.set_game_over()
        else:
            self.board.show_move("falling")
            self.current_job = self.root.after(1000, self.auto_fall)
        self.board.update_next_pieces()

    def collides(self, new_pos, new_rot_ind):
        for point in pieces[self.piece_ind][new_rot_ind]:
            x = point[1] + new_pos[0]
            y = -point[0] + new_pos[1]
            if y >= rows or x >= columns or x < 0 or (y >= 0 and self.b[y][x] != 0):
                return True
        return False

    def delete_rows(self, y):
        for row in y:
            self.b.remove(self.b[row])
            self.b.insert(0, [0 for x in range(columns)])

    def move_piece(self, y_shift, x_shift): 
        if self.game_over: return
        new_center = (self.center[0] + x_shift, self.center[1] + y_shift)
        if not self.collides(new_center, self.rot_ind):
            self.center = new_center 
            self.board.show_move("falling")
            if y_shift == 1:
                self.root.after_cancel(self.current_job)
                self.current_job = self.root.after(1000, self.auto_fall)
            return True
        return False

    def auto_fall(self):
        if self.game_over: return
        if not self.move_piece(1, 0):
            self.secure_piece()

    def rotate(self):
        if self.game_over: return
        new_ind = self.rot_ind + 1
        new_ind = new_ind % len(pieces[self.piece_ind]) 
        if not self.collides(self.center, new_ind):
            self.rot_ind = new_ind
            self.board.show_move("falling")

    def drop(self):
        if self.game_over: return
        self.center = self.find_piece_shadow() 
        self.secure_piece()

    def find_piece_shadow(self):
        new_center = (self.center[0], self.center[1]+1)
        while not self.collides(new_center, self.rot_ind):
            new_center = (new_center[0], new_center[1] + 1)
        return (new_center[0], new_center[1] - 1)   

    def hold_piece(self):
        if self.already_held or self.game_over: return
        if self.hold == None:
            self.hold = self.piece_ind
            self.add_new_piece()
        else:
            to_hold = self.piece_ind
            self.add_new_piece(True)
            self.hold = to_hold
        self.already_held = True
        self.board.update_hold_piece()

    def secure_piece(self):
        self.already_held = False
        self.root.after_cancel(self.current_job)
        to_delete = list()      
        for point in pieces[self.piece_ind][self.rot_ind]:
            x = point[1] + self.center[0]
            y = -point[0] + self.center[1]
            self.b[y][x] = self.piece_ind+1
            if sum(val > 0 for val in self.b[y]) == columns:
                to_delete.append(y)
        if len(to_delete) > 0:
            self.delete_rows(to_delete)
            self.board.draw_board()
        else:
            self.board.show_move("secured")
        self.add_new_piece()
        self.board.update_next_pieces()

    def set_game_over(self):
        self.game_over = True
        self.board.game_over()

class TetrisController():
    def __init__(self, root, game):
        self.game = game
        root.bind('<Left>', self.left_key)
        root.bind('<Right>', self.right_key)
        root.bind('<Down>', self.down_key)
        root.bind('<Up>', self.up_key)
        root.bind('<space>', self.space_key)
        root.bind('<Shift_L>', self.shift_key)

    def left_key(self, event):
        self.game.move_piece(0, -1)

    def right_key(self, event):
        self.game.move_piece(0, 1)

    def down_key(self, event):
        self.game.move_piece(1, 0)

    def up_key(self, event):
        self.game.rotate()

    def space_key(self, event):
        self.game.drop()

    def shift_key(self, event):
        self.game.hold_piece()

    def new_game(self):
        self.game.start_game()

if __name__ == "__main__":
    TetrisGame()
