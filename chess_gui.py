import random
from tkinter import *
from tkinter import ttk
from gpt import get_completion_from_messages
import chess
from start import start_menu

piece_positions = {
    'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K', 'f1': 'B', 'g1': 'N', 'h1': 'R',
    'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e4': 'P', 'f2': 'P', 'g2': 'P', 'h2': 'P',
    'a7': 'p', 'b7': 'p', 'c7': 'p', 'd7': 'p', 'e7': 'p', 'f7': 'p', 'g7': 'p', 'h7': 'p',
    'a8': 'r', 'b8': 'n', 'c8': 'b', 'd8': 'q', 'e8': 'k', 'f8': 'b', 'g8': 'n', 'h8': 'r'
}

move_color = "red"
list_of_wrong_moves = []
countdown = 0
start = False
notation = ["e2e4"]
now = True
crash_count = 0
logic = "Check which pieces white has. Chose one then consider how it moves. Think of all possible moves. Respond with one of them."
robot_prompt = [
    {'role': 'system', 'content': f"You are playing white in this chess game. What move will you play next? Ensure the move is valid. Here are the piece positions to help you visualize the board: {piece_positions}. Provide the UCI without supporting text or spaces. Remember, UCI includes both the starting and ending squares of the move in small letters.Even for captures do not use the format dxe7 just do uci with befor and after."},
    {"role": "user", "content": "Take your time."}, {"role": "user", "content": "Never ever deviate from uci format.Do not add supporting text under circumstance.Here is an example of uci g8h6, every single response should look like this."},
        {"role": "user", "content": logic}]
move_played = ""
color = True
positions = []
piece_shapes = ['♔','♕','♖','♗','♘','♙','♚','♛','♜','♝','♞','♟']

def is_valid_uci_move(move: str) -> bool:
    """Check whether a given string is a valid UCI move."""
    if len(move) != 4:
        return False

    # Check if the first and third characters are lowercase letters
    if not (move[0].islower() and move[2].islower()):
        return False

    # Check if the second and fourth characters are digits
    if not (move[1].isdigit() and move[3].isdigit()):
        return False

    # Check if the second and fourth characters are valid chessboard ranks (1-8)
    if not (1 <= int(move[1]) <= 8 and 1 <= int(move[3]) <= 8):
        return False

    return True
def can_castle_kingside(board):
    # Ensure the king and rook are in their starting positions and have not moved
    if not board.has_kingside_castling_rights(chess.BLACK):
        print("No kingside castling rights")
        return False
    # Ensure the squares between the king and rook are empty
    if board.piece_at(chess.F8) or board.piece_at(chess.G8):
        print("Squares between king and rook are not empty")
        return False
    # Ensure the king is not in check, does not pass through check, and does not end in check
    if board.is_check() or board.is_attacked_by(chess.WHITE, chess.F8) or board.is_attacked_by(chess.WHITE, chess.G8):
        print("King in check, passes through check, or ends in check")
        return False
    return True

def generate_legal_moves(positions, fro, to):
    # Create a new chess board
    board = chess.Board()
    board.clear()

    # Apply the provided piece positions to the board
    for square, piece in positions.items():
        board.set_piece_at(chess.SQUARE_NAMES.index(square), chess.Piece.from_symbol(piece))

    # Set castling rights explicitly
    board.set_castling_fen('KQkq')  # Both sides can castle both ways

    # Set the board turn to Black to simulate Black's move
    board.turn = chess.BLACK
    print(board)

    # Generate all legal moves in UCI format
    legal_moves_uci = [move.uci() for move in board.legal_moves]

    # Print all legal moves for debugging
    print("Legal moves:", legal_moves_uci)

    # Convert from and to squares to UCI format
    from_square_uci = fro
    to_square_uci = to
    move_to_check = f"{from_square_uci}{to_square_uci}"

    # Check if the move_to_check is in legal_moves_uci
    if move_to_check in legal_moves_uci:
        return True

    # Special handling for castling moves
    if (fro, to) == ('e8', 'g8') and can_castle_kingside(board):
        return True

    return False




def robot_turn():
    global notation, robot_prompt

    robot_response = get_completion_from_messages(robot_prompt, temperature=1)

    notation.append(robot_response)
    print(f"Response: {robot_response}")
    return robot_response


for c in range(0,7,6):
    for i in range(16):
        a = i % 8
        b = int(i/8) + c
        positions.append([b, a])

def check_if_capture(piece):
    if [piece.x, piece.y] in positions:
        return True
    else:
        return False

def grid_to_chess(x, y):
    index_to_letter = {0: 'h', 1: 'g', 2: 'f', 3: 'e',
                       4: 'd', 5: 'c', 6: 'b', 7: 'a'}

    # Convert x, y coordinates to chess notation
    letter = index_to_letter[x]
    number = y + 1  # Increment y-coordinate to match chess notation

    return letter + str(number)
def chess_to_grid(chess_notation):
    letter_to_index = {'h': 0, 'g': 1, 'f': 2, 'e': 3,
                       'd': 4, 'c': 5, 'b': 6, 'a': 7}

    # Extract the letter and number from the chess notation
    letter = chess_notation[0]
    number = int(chess_notation[1])

    # Convert chess notation to grid coordinates
    x = letter_to_index[letter]
    y = number - 1  # Decrement the number to match grid coordinates

    return (x, y)

window = Tk()
window.title("Can language model play chess?")
window.minsize(width=640, height=640)
window.config(padx= 0, pady = 0)


def end(game, msg):
    global run
    print("run")
    run = True
    for widget in window.winfo_children():
        widget.destroy()
    p = 0
    window.update()
    # Create a frame to hold the grid
    frame = ttk.Frame(window, padding="10")
    frame.grid(row=0, column=0)

    # Configure the grid
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_rowconfigure(9, weight=1)
    for col in range(8):
        frame.grid_columnconfigure(col, weight=1)

    # Create the first large cell spanning all columns
    first_cell = Label(frame, text=f"{msg}, do you want to play again.", borderwidth=1, relief="solid",
                       font=("Helvetica", 30))
    first_cell.grid(row=0, column=0, columnspan=8, sticky="nsew")

    game = game.replace(" ", "")

    # Remove newline characters
    game = game.replace("\n", "")
    # Create the grid cells for the middle rows
    for row in range(1, 9):
        for col in range(8):
            cell = Label(frame, text=game[p], borderwidth=1, relief="solid", font=("Helvetica", 24))
            cell.grid(row=row, column=col, sticky="nsew")
            p += 1
            print(p)

    # Create the last large cell spanning all columns
    last_cell = Button(frame, text="Play again!", command=lambda: start_menu(window, play_chess))
    last_cell.grid(row=9, column=0, columnspan=8, sticky="nsew")


class Piece(Label):
    def __init__(self,master):
        super().__init__(master)
        self.x, self.y = (4, 6)
        self.box = 'white'
        self.config(bg=self.box, padx=0, pady=0, text="♖", font=("Arial", 40, "normal"), fg='blue')
        self.grid(column=self.x, row=self.y)
        self.identifier = ""

    def identify(self):
        id = self.identifier
        if id == "♖":
            return "R"
        elif id == "♔":
            return "K"
        elif id == "♘":
            return "N"
        elif id == "♙":
            return "P"
        elif id == "♕":
            return "Q"
        elif id == "♗":
            return "B"

    def here(self, pos, pos_two):
        global countdown, crash_count
        prev_x, prev_y = pos_two
        self.x, self.y = pos
        print(f"X: {self.x}, Y: {self.y}")
        print("I have moved")
        if not start:
            self.grid(column=self.x, row=self.y)
            if self.x % 2 ==  self.y % 2:
                self.box = "black"
            else:
                self.box = "white"
            self.config(bg=self.box)

        else:
            current = grid_to_chess(self.x,self.y)
            prev = grid_to_chess(prev_x, prev_y)
            crash_count += 1
            print(f"Crashcount: {crash_count}")
            ram = chess.Board()
            ram.clear()
            temp_positions = piece_positions.copy()
            # Apply the provided piece positions to the ram
            temp_positions[current] = self.identify()
            print(f"Prev: {prev}, {prev_y, prev_x}")
            del temp_positions[prev]
            for square, piece in temp_positions.items():
                ram.set_piece_at(chess.SQUARE_NAMES.index(square), chess.Piece.from_symbol(piece))

            # Set the ram turn to Black to simulate Black's move
            ram.turn = chess.WHITE
            print(ram)
            if ram.is_checkmate():
                print("mate")
                end(str(ram), msg="You win")

                return True

            if crash_count > 13:
                end(str(ram), msg="Your logic crashed.")
                return True

            if ram.is_check():
                countdown += 1
                if countdown > 1:
                    p = random.choice(list(piece_positions.keys()))
                    y, z = chess_to_grid(p)
                    countdown = 0
                    print(f"y, z: {y, z}")
                    king = dictionary_of_gpt_pieces[3]
                    print(king.identifier)
                    king.grid(column=y, row=z)
                    piece_positions[p] = "K"
                    chess_to_delete = grid_to_chess(king.x, king.y)
                    print(f"Delete {chess_to_delete}")
                    if chess_to_delete in piece_positions:
                        del piece_positions[chess_to_delete]
                    if [y,z] in positions:
                        piece_to_delete_index = positions.index([y, z])
                        piece_to_delete = list(dictionary_of_gpt_pieces.keys())[piece_to_delete_index]
                        dictionary_of_gpt_pieces[piece_to_delete].destroy()
                        positions[piece_to_delete_index] = []


                    else:
                        update_player_pieces(dictionary_of_players_pieces, [y, z])
                    positions[3] = [y, z]
                    king.prev_x = king.x
                    king.prev_y = king.y
                    king.x = y
                    king.y = z
                    if king.x % 2 == king.y % 2:
                        king.box = "black"
                    else:
                        king.box = "white"
                    king.config(bg=king.box)


                else:
                    global list_of_wrong_moves
                    print("Check")
                    list_of_wrong_moves.append(f'{prev}{current}')
                    robot_prompt[1] = ({"role": "user", "content": f"you are in check. Here are axamples of moves that wont work {list_of_wrong_moves}"})
                    return False

            else:
                robot_prompt[1] = {"role": "user", "content": "Take your time."}
                list_of_wrong_moves = []
                piece_positions[current] = self.identify()
                del piece_positions[prev]
                self.grid(column=self.x, row=self.y)
                if self.x % 2 == self.y % 2:
                    self.box = "black"
                else:
                    self.box = "white"
                self.config(bg=self.box)
                notation.append(move_played)
                current_pos = [self.x, self.y]
                crash_count = 0
                update_player_pieces(dictionary_of_players_pieces, current_pos)
                print(f"Updtd: {piece_positions}")
                return True




class Rook(Label):
    def __init__(self,master):
        super().__init__(master)
        self.x, self.y = (0, 7)
        self.config(text='♜')
        self.box = 'white'
        self.bind("<Button-1>", self.move)
        self.config(bg=self.box, padx=0, pady=0, text="♜", font=("Arial", 40, "normal"), fg='blue')
        self.grid(column=self.x, row=self.y)
        self.buttons =[]
        self.previous_x, self.previous_y = (self.x, self.y)
        self.clicked = False

    def here(self, pos):
        global move_played, start, now
        self.previous_x = self.x
        self.previous_y = self.y
        self.x = pos[0]
        self.y = pos[1]
        prev = grid_to_chess(self.previous_x, self.previous_y)
        current = grid_to_chess(self.x, self.y)
        if start:
            move_played = f"{prev}{current}"
            now = generate_legal_moves(positions=piece_positions, fro=prev, to=current)
        else:
            pass

        if now:
            if start:
                piece_positions[current] = "r"
                del piece_positions[prev]
                notation.append(move_played)
            self.grid(column=self.x, row=self.y)
            for x in self.buttons:
                x.destroy()
            self.buttons = []
            if self.x % 2 == self.y % 2:
                self.box = "black"
            else:
                self.box = "white"
            self.config(bg=self.box)
            if check_if_capture(self):
                number = positions.index([self.x, self.y])
                dictionary_of_gpt_pieces[number].destroy()
                del dictionary_of_gpt_pieces[number]
                positions[number] = [-1, -1]
            if start:
                run = False
                while not run:
                    uci = robot_turn()
                    if is_valid_uci_move(uci):
                        current = chess_to_grid(uci[:2])
                        next = chess_to_grid(uci[-2:])
                        print(current, next)
                        a, b = current
                        if [a, b] in positions:
                            num = positions.index([a, b])

                            run = dictionary_of_gpt_pieces[num].here(pos=next, pos_two=current)
                            a, b = next
                            print(f"Run : {run}")
                            if run:
                                if [a, b] in positions:
                                    n = positions.index([a, b])
                                    positions[n] = []
                                    dictionary_of_gpt_pieces[n].destroy()
                                positions[num] = [a, b]
                                break

        else:
            self.x = self.previous_x
            self.y = self.previous_y
    def move(self, event):
        if self.clicked:
            for button in self.buttons:
                button.destroy()
            self.buttons = []
            self.clicked = False
        else:
            for i in range(8):
                button = Button(text=' ', bg=move_color,command=lambda pos=(self.x,i): self.here(pos))
                if i != self.y:
                    button.grid(column=self.x, row=i)
                    self.buttons.append(button)
                if i != self.x:
                    button_y = Button(text=' ',bg=move_color, command=lambda pos=(i,self.y): self.here(pos))
                    button_y.grid(column=i, row=self.y)
                    self.buttons.append(button_y)
            self.clicked = True

class Knight(Label):
    def __init__(self,master):
        super().__init__(master)
        self.x, self.y = (1, 7)
        self.box = 'black'
        self.config(bg=self.box, padx=0, pady=0, text="♞", font=("Arial", 40, "normal"), fg='blue')
        self.grid(column=self.x, row=self.y)
        self.bind("<Button-1>", self.move)
        self.buttons = []
        self.previous_x, self.previous_y = (self.x, self.y)
        self.clicked = False

    def here(self, pos):
        global move_played, start, now
        self.previous_x = self.x
        self.previous_y = self.y
        self.x = pos[0]
        self.y = pos[1]
        prev = grid_to_chess(self.previous_x, self.previous_y)
        current = grid_to_chess(self.x, self.y)
        if start:
            move_played = f"{prev}{current}"
            now = generate_legal_moves(positions=piece_positions, fro=prev, to=current)

        if now:
            if start:
                piece_positions[current] = "n"
                del piece_positions[prev]
                notation.append(move_played)
            self.grid(column=self.x, row=self.y)
            for x in self.buttons:
                x.destroy()
            self.buttons = []
            if self.x % 2 == self.y % 2:
                self.box = "black"
            else:
                self.box = "white"
            self.config(bg=self.box)
            if check_if_capture(self):
                number = positions.index([self.x, self.y])
                dictionary_of_gpt_pieces[number].destroy()
                del dictionary_of_gpt_pieces[number]
                positions[number] = [-1, -1]
            if start:
                run = False
                while not run:
                    uci = robot_turn()
                    if is_valid_uci_move(uci):
                        current = chess_to_grid(uci[:2])
                        next = chess_to_grid(uci[-2:])
                        print(current, next)
                        a, b = current
                        if [a, b] in positions:
                            num = positions.index([a, b])

                            run = dictionary_of_gpt_pieces[num].here(pos=next, pos_two=current)
                            a, b = next
                            print(f"Run : {run}")
                            if run:
                                if [a, b] in positions:
                                    n = positions.index([a, b])
                                    positions[n] = []
                                    dictionary_of_gpt_pieces[n].destroy()
                                positions[num] = [a, b]
                                break

        else:
            self.x = self.previous_x
            self.y = self.previous_y

    def move(self, event):
        if self.clicked:
            for button in self.buttons:
                button.destroy()
            self.buttons = []
            self.clicked = False
        else:
            avail_moves = [[1,2],[-1,2],[-1,-2],[1,-2]]
            for i in avail_moves:
                x = self.x + i[0]
                y = self.y + i[1]
                if x > -1 and y > -1 and x < 8 and y < 8:
                    button = Button(text=' ',bg=move_color, command=lambda pos=(x,y): self.here(pos))
                    button.grid(column=x,row=y)
                    self.buttons.append(button)
            for i in avail_moves:
                x = self.x + i[1]
                y = self.y + i[0]
                if x > -1 and y > -1 and x < 8 and y < 8:
                    button = Button(text=' ',bg=move_color, command=lambda pos=(x,y): self.here(pos))
                    button.grid(column=x,row=y)
                    self.buttons.append(button)
            self.clicked = True
class Bishop(Label):
    def __init__(self,master):
        super().__init__(master)
        self.x, self.y = (2, 7)
        self.box = 'white'
        self.config(bg=self.box, padx=0, pady=0, text="♝", font=("Arial", 40, "normal"), fg='blue')
        self.grid(column=self.x, row=self.y)
        self.bind("<Button-1>", self.move)
        self.buttons = []
        self.previous_x, self.previous_y = (self.x, self.y)
        self.clicked = False

    def here(self, pos):
        global move_played, start, now
        self.previous_x = self.x
        self.previous_y = self.y
        self.x = pos[0]
        self.y = pos[1]
        prev = grid_to_chess(self.previous_x, self.previous_y)
        current = grid_to_chess(self.x, self.y)
        if start:
            move_played = f"{prev}{current}"
            now = generate_legal_moves(positions=piece_positions, fro=prev, to=current)


        if now:
            if start:
                piece_positions[current] = "b"
                del piece_positions[prev]
                notation.append(move_played)
            self.grid(column=self.x, row=self.y)
            for x in self.buttons:
                x.destroy()
            self.buttons = []
            if self.x % 2 == self.y % 2:
                self.box = "black"
            else:
                self.box = "white"
            self.config(bg=self.box)
            if check_if_capture(self):
                number = positions.index([self.x, self.y])
                dictionary_of_gpt_pieces[number].destroy()
                del dictionary_of_gpt_pieces[number]
                positions[number] = [-1, -1]
            if start:
                run = False
                while not run:
                    uci = robot_turn()
                    if is_valid_uci_move(uci):
                        current = chess_to_grid(uci[:2])
                        next = chess_to_grid(uci[-2:])
                        print(current, next)
                        a, b = current
                        if [a, b] in positions:
                            num = positions.index([a, b])

                            run = dictionary_of_gpt_pieces[num].here(pos=next, pos_two=current)
                            a, b = next
                            print(f"Run : {run}")
                            if run:
                                if [a, b] in positions:
                                    n = positions.index([a, b])
                                    positions[n] = []
                                    dictionary_of_gpt_pieces[n].destroy()
                                positions[num] = [a, b]
                                break

        else:
            self.x = self.previous_x
            self.y = self.previous_y
    def move(self, event):
        if self.clicked:
            for button in self.buttons:
                button.destroy()
            self.buttons = []
            self.clicked = False
        else:
            x = self.x
            y = self.y
            a = 1
            def add_button(x, y):
                if x > -1 and y > -1 and x < 8 and y < 8:
                    button = Button(text=' ',bg=move_color, command=lambda pos=(x, y): self.here(pos))
                    if x != self.x:
                        button.grid(column=x, row=y)
                        self.buttons.append(button)
            def place_buttons(x, y, a, b):
                for i in range(9):
                    if x>-1 and y >-1:
                        x -= a * b
                        y -= a
                        add_button(x, y)
                    else:
                        x = self.x
                        y = self.y
                        a = -1
                        add_button(x, y)
            place_buttons(x,y,a, 1)
            place_buttons(x,y,a, -1)
            self.clicked = True

class King(Label):
    def __init__(self,master):
        super().__init__(master)
        self.x, self.y = (3, 7)
        self.box = 'black'
        self.config(bg=self.box, padx=0, pady=0, text="♚", font=("Arial", 40, "normal"), fg='blue')
        self.grid(column=self.x, row=self.y)
        self.bind("<Button-1>", self.move)
        self.buttons = []
        self.previous_x, self.previous_y = (self.x, self.y)
        self.clicked = False
        self.castle = False

    def castled(self, pos):
        self.castle = True
        print(f"Castle: {self.castle}")
        self.here(pos)
    def move(self, event):
        if self.clicked:
            for button in self.buttons:
                button.destroy()
            self.buttons = []
            self.clicked = False
        else:
            nums = [1, -1]
            def row_set(a):
                for i in range(-1, 2):
                    x = self.x + i * a
                    y = self.y + 1 * a
                    if x > -1 and y < 8 and y > -1 and x < 8:
                        button = Button(text=' ',bg=move_color, command=lambda pos=(x, y): self.here(pos))
                        button.grid(row=y,column=x)
                        self.buttons.append(button)
            def set_sides(a):
                x =self.x + a
                y =self.y
                if x > -1 and y < 8 and y > -1 and x < 8:
                    button = Button(text=' ',bg=move_color, command=lambda pos=(x , y): self.here(pos))
                    button.grid(row=y, column=x)
                    self.buttons.append(button)
            for num in nums:
                row_set(num)
                set_sides(num)

            if self.x == 3 and self.y == 7:
                for x in [1, 5]:
                    button = Button(text=' ',bg=move_color, command=lambda pos=(x, 7): self.castled(pos))
                    button.grid(row=7, column=x)
                    self.buttons.append(button)
            self.clicked = True

    def here(self, pos):
        global move_played, start, now
        self.previous_x = self.x
        self.previous_y = self.y
        self.x = pos[0]
        self.y = pos[1]
        prev = grid_to_chess(self.previous_x, self.previous_y)
        current = grid_to_chess(self.x, self.y)
        if start:
            move_played = f"{prev}{current}"
            now = generate_legal_moves(positions=piece_positions, fro=prev, to=current)
        print(f"Now: {now}")

        if now:
            if start:
                piece_positions[current] = "k"
                del piece_positions[prev]
                notation.append(move_played)
            self.grid(column=self.x, row=self.y)
            for x in self.buttons:
                x.destroy()
            self.buttons = []
            if self.x % 2 == self.y % 2:
                self.box = "black"
            else:
                self.box = "white"
            self.config(bg=self.box)
            print(f"Reaches her{self.castle}")

            if self.castle:
                dic = dictionary_of_players_pieces["rooks"]
                if self.x == 1:
                    print(f"X: {self.x}")
                    print(dic)
                    for rook in dic:
                        print(rook.x)
                        if rook.x == 0:
                            piece_positions["f8"] = "r"
                            del piece_positions["h8"]
                            rook.grid(column=2, row=7)
                            rook.x = 2
                            rook.y = 7

                if self.x == 5:
                    print(f"X: {self.x}")
                    print(dic)
                    for rook in dic:
                        print(rook.x)
                        if rook.x == 7:
                            piece_positions["d8"] = "r"
                            del piece_positions["a8"]
                            rook.grid(column=4, row=7)
                            rook.x = 4
                            rook.y = 7
                            rook.box = "white"
                            rook.config(bg="white")
                self.castle = False
            else:
                print(f"Not castle {self.castle}")


            if check_if_capture(self):
                number = positions.index([self.x, self.y])
                dictionary_of_gpt_pieces[number].destroy()
                del dictionary_of_gpt_pieces[number]
                positions[number] = [-1, -1]
            if start:
                run = False
                while not run:
                    uci = robot_turn()
                    if is_valid_uci_move(uci):
                        current = chess_to_grid(uci[:2])
                        next = chess_to_grid(uci[-2:])
                        print(current, next)
                        a, b = current
                        if [a, b] in positions:
                            num = positions.index([a, b])

                            run = dictionary_of_gpt_pieces[num].here(pos=next, pos_two=current)
                            a, b = next
                            print(f"Run : {run}")
                            if run:
                                if [a, b] in positions:
                                    n = positions.index([a, b])
                                    positions[n] = []
                                    dictionary_of_gpt_pieces[n].destroy()
                                positions[num] = [a, b]
                                break

        else:
            self.x = self.previous_x
            self.y = self.previous_y









class Queen(Label):
    def __init__(self,master):
        super().__init__(master)
        self.x, self.y = (4, 7)
        self.box = 'white'
        self.config(bg=self.box, padx=0, pady=0, text="♛", font=("Arial", 40, "normal"), fg='blue')
        self.grid(column=self.x, row=self.y)
        self.bind("<Button-1>", self.move)
        self.buttons = []
        self.previous_x, self.previous_y = (self.x, self.y)
        self.clicked = False

    def here(self, pos):
        global move_played, start, now
        self.previous_x = self.x
        self.previous_y = self.y
        self.x = pos[0]
        self.y = pos[1]
        prev = grid_to_chess(self.previous_x, self.previous_y)
        current = grid_to_chess(self.x, self.y)
        if start:
            move_played = f"{prev}{current}"
            now = generate_legal_moves(positions=piece_positions, fro=prev, to=current)


        if now:
            if start:
                piece_positions[current] = "q"
                del piece_positions[prev]
                notation.append(move_played)
            self.grid(column=self.x, row=self.y)
            for x in self.buttons:
                x.destroy()
            self.buttons = []
            if self.x % 2 == self.y % 2:
                self.box = "black"
            else:
                self.box = "white"
            self.config(bg=self.box)
            if check_if_capture(self):
                number = positions.index([self.x, self.y])
                dictionary_of_gpt_pieces[number].destroy()
                del dictionary_of_gpt_pieces[number]
                positions[number] = [-1, -1]
            if start:
                run = False
                while not run:
                    uci = robot_turn()
                    if is_valid_uci_move(uci):
                        current = chess_to_grid(uci[:2])
                        next = chess_to_grid(uci[-2:])
                        print(current, next)
                        a, b = current
                        if [a, b] in positions:
                            num = positions.index([a, b])

                            try:
                                run = dictionary_of_gpt_pieces[num].here(pos=next, pos_two=current)
                            except:
                                run = False
                            finally:
                                a, b = next
                            print(f"Run : {run}")
                            if run:
                                if [a, b] in positions:
                                    n = positions.index([a, b])
                                    positions[n] = []
                                    dictionary_of_gpt_pieces[n].destroy()
                                positions[num] = [a, b]

                                break

                    else:
                        list_of_wrong_moves.append(uci)
                        robot_prompt[1] = {"role": "user", "content": f"These are examples of moves that dont work please do not use them.{list_of_wrong_moves}"}

        else:
            self.x = self.previous_x
            self.y = self.previous_y
    def move(self, event):
        if self.clicked:
            for button in self.buttons:
                button.destroy()
            self.buttons = []
            self.clicked = False
        else:
            x =self.x
            y =self.y
            diagonal = [-1, 1]
            for i in range(1,8):
                if (y + i) < 8:
                    button_up = Button(text=' ',bg=move_color, command=lambda pos=(x, y + i): self.here(pos))
                    button_up.grid(row=y + i, column=x)
                    self.buttons.append(button_up)
                if y - i > -1:
                    button_down = Button(text=' ',bg=move_color, command=lambda pos=(x, y -i): self.here(pos))
                    button_down.grid(row=y - i, column=x)
                    self.buttons.append(button_down)

                if x + i < 8:
                    button_left = Button(text=' ',bg=move_color, command=lambda pos=(x + i, y): self.here(pos))
                    button_left.grid(row=y, column=x + i)
                    self.buttons.append(button_left)

                if x - i > -1:
                    button_right = Button(text=' ',bg=move_color, command=lambda pos=(x - i, y): self.here(pos))
                    button_right.grid(row=y, column=x - i)
                    self.buttons.append(button_right)

                for num in diagonal:
                    for a in diagonal:
                        if y+ (i * num) > -1 and x + (i * a) > -1 and y+ (i * num) < 8 and x + (i * a) < 8:
                            button = Button(text=' ',bg=move_color, command=lambda pos=(x + (i * a), y+ (i * num)): self.here(pos))
                            button.grid(row=y+ (i * num), column=x + (i * a))
                            self.buttons.append(button)
            self.clicked = True

class Pawn(Label):
    def __init__(self,master):
        super().__init__(master)
        self.x, self.y = (5, 6)
        self.box = 'white'
        self.config(bg=self.box, padx=0, pady=0, text="♟", font=("Arial", 40, "normal"), fg='blue')
        self.grid(column=self.x, row=self.y)
        self.bind("<Button-1>", self.move)
        self.buttons = []
        self.previous_x, self.previous_y = (self.x, self.y)
        self.clicked = False

    def here(self, pos):
        global move_played, start, now, countdown
        self.previous_x = self.x
        self.previous_y = self.y
        self.x = pos[0]
        self.y = pos[1]
        prev = grid_to_chess(self.previous_x, self.previous_y)
        current = grid_to_chess(self.x, self.y)
        if start:
            move_played = f"{prev}{current}"
            now = generate_legal_moves(positions=piece_positions, fro=prev, to=current)


        if now:
            if start:
                piece_positions[current] = "p"
                del piece_positions[prev]
                notation.append(move_played)
            self.grid(column=self.x, row=self.y)
            for x in self.buttons:
                x.destroy()
            self.buttons = []
            if self.x % 2 == self.y % 2:
                self.box = "black"
            else:
                self.box = "white"
            self.config(bg=self.box)
            if check_if_capture(self):
                number = positions.index([self.x, self.y])
                dictionary_of_gpt_pieces[number].destroy()
                del dictionary_of_gpt_pieces[number]
                positions[number] = [-1, -1]
            if start:
                run = False
                while not run:
                    uci = robot_turn()
                    if is_valid_uci_move(uci):
                        current = chess_to_grid(uci[:2])
                        next = chess_to_grid(uci[-2:])
                        print(current, next)
                        a, b = current
                        if [a, b] in positions:
                            num = positions.index([a, b])
                            print(dictionary_of_gpt_pieces)
                            run = dictionary_of_gpt_pieces[num].here(pos=next, pos_two=current)
                            a, b = next
                            print(f"Run : {run}")
                            if run:
                                if [a, b] in positions:
                                    n = positions.index([a, b])
                                    positions[n] = []
                                    dictionary_of_gpt_pieces[n].destroy()
                                positions[num] = [a, b]
                                break

        else:
            self.x = self.previous_x
            self.y = self.previous_y

    def move(self, event):
        if self.clicked:
            for button in self.buttons:
                button.destroy()
            self.buttons = []
            self.clicked = False
        else:
            for i in range(-1, 2):
                x = self.x + (-i)
                y = self.y + (-1)
                if x > -1 and y > -1 and x < 8 and y < 8:
                    button = Button(text=' ',bg=move_color, command=lambda pos=(x, y): self.here(pos))
                    button.grid(row=y,column=x)
                    self.buttons.append(button)
            y = self.y -2
            if y > -1 and y < 8:
                button = Button(text=' ',bg=move_color, command=lambda pos=(self.x, y): self.here(pos))
                button.grid(row=y, column=self.x)
                self.buttons.append(button)
            self.clicked = True


colors= ['', 'white', 'black']

dictionary_of_gpt_pieces = {}


dictionary_of_players_pieces = {}

starting_positions = {}

def update_player_pieces(dict, pos):
    for key in dict:
        l = dict[key]
        for piece in l:
            if pos == [piece.x, piece.y]:
                piece.destroy()
                l.remove(piece)

start = True

def play_chess(brain):
    print("reach")
    global notation,logic, start,countdown,now, list_of_wrong_moves, move_played, robot_prompt,color, positions,king, colors,piece_positions, dictionary_of_gpt_pieces, dictionary_of_players_pieces, starting_positions
    for widget in window.winfo_children():
        widget.destroy()
    piece_positions = {
        'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K', 'f1': 'B', 'g1': 'N', 'h1': 'R',
        'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e4': 'P', 'f2': 'P', 'g2': 'P', 'h2': 'P',
        'a7': 'p', 'b7': 'p', 'c7': 'p', 'd7': 'p', 'e7': 'p', 'f7': 'p', 'g7': 'p', 'h7': 'p',
        'a8': 'r', 'b8': 'n', 'c8': 'b', 'd8': 'q', 'e8': 'k', 'f8': 'b', 'g8': 'n', 'h8': 'r'
    }

    list_of_wrong_moves = []
    countdown = 0
    start = False
    notation = ["e2e4"]
    now = True
    logic = brain
    robot_prompt = [
        {'role': 'system',
         'content': f"You are playing white in this chess game. What move will you play next? Ensure the move is valid. Here are the piece positions to help you visualize the board: {piece_positions}. Provide the UCI without supporting text or spaces. Remember, UCI includes both the starting and ending squares of the move in small letters.Even for captures do not use the format dxe7 just do uci with befor and after."},
        {"role": "user", "content": "Take your time."}, {"role": "user",
                                                         "content": "Never ever deviate from uci format.Do not add supporting text under circumstance.Here is an example of uci g8h6, every single response should look like this."},
        {"role": "user", "content": brain}]
    move_played = ""
    color = True
    positions = []

    for i in range(8):
        window.grid_columnconfigure(i, weight=1)  # Make columns expandable
        window.grid_rowconfigure(i, weight=1)
    for key in dictionary_of_players_pieces:
        if key != "queens":
            for i in range(len(dictionary_of_players_pieces[key])):
                piece = dictionary_of_players_pieces[key][i]
                if piece.winfo_exists():  # Check if the piece widget exists

                    piece.here((starting_positions[key][i], piece.y))
    a = 1
    for i in range(8):
        for j in range(8):
            a *= -1
            frame = Frame(window, bg=colors[a], borderwidth=1, relief=SOLID)
            frame.grid(row=i, column=j, sticky="nsew")  # Use sticky to fill the cell
            if j == 7:
                a *= -1
    for i in range(8):
        window.grid_columnconfigure(i, weight=1)
    for i in range(8):
        my_label = Label(text="♖", font=("Arial", 40, "bold"), bg="white", fg='white')
        my_label.grid(column=i, row=7 - i)
        my_label.config(highlightthickness=0)
        my_label.config(padx=0, pady=0)

    positions = []

    for a in range(2):
        for i in range(8):
            positions.append([i, a])

    dictionary_of_gpt_pieces.clear()
    print(dictionary_of_gpt_pieces)
    dictionary_of_gpt_pieces = {i: Piece(window) for i in range(16)}
    list_of_gpt_shapes = ['♖', '♘', '♗', '♔', '♕', '♗', '♘', '♖', '♙', '♙', '♙', '♙', '♙', '♙', '♙', '♙']
    positions[11] = [3, 3]

    for i in range(16):
        value = dictionary_of_gpt_pieces[i]
        value.config(text=list_of_gpt_shapes[i])
        value.identifier = list_of_gpt_shapes[i]
        a, b = positions[i]
        value.here((a, b), (a, b))
    piece_info = {
        "pawns": (Pawn, 8),
        "rooks": (Rook, 2),
        "knights": (Knight, 2),
        "bishops": (Bishop, 2),
        "queens": (Queen, 1)
    }

    # Create an empty dictionary to store the pieces

    dictionary_of_players_pieces = {}

    # Loop through the piece_info dictionary to create pieces
    for piece_type, (piece_class, quantity) in piece_info.items():
        dictionary_of_players_pieces[piece_type] = [piece_class(window) for _ in range(quantity)]

    starting_positions = {"pawns": [0, 1, 2, 3, 4, 5, 6, 7], "rooks": [0, 7], "knights": [1, 6], "bishops": [2, 5]}

    for key in dictionary_of_players_pieces:
        if key != "queens":
            for i in range(len(dictionary_of_players_pieces[key])):
                piece = dictionary_of_players_pieces[key][i]
                piece.here((starting_positions[key][i], piece.y))

    king = King(window)
    start = True
    print([p.y for p in dictionary_of_gpt_pieces.values()])
    print([p.y for p in dictionary_of_players_pieces["pawns"]])

start_menu(window, play_chess)

window.mainloop()