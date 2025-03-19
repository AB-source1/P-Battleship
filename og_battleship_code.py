import random

def create_board(size):
    return [['O' for _ in range(size)] for _ in range(size)]

def print_board(board):
    for row in board:
        print(' '.join(row))
    print()

def place_ship(board, ship_size):
    size = len(board)
    while True:
        orientation = random.choice(['horizontal', 'vertical'])
        if orientation == 'horizontal':
            row = random.randint(0, size - 1)
            col = random.randint(0, size - ship_size)
            if all(board[row][col+i] == 'O' for i in range(ship_size)):
                for i in range(ship_size):
                    board[row][col+i] = 'S'
                return
        else:
            row = random.randint(0, size - ship_size)
            col = random.randint(0, size - 1)
            if all(board[row+i][col] == 'O' for i in range(ship_size)):
                for i in range(ship_size):
                    board[row+i][col] = 'S'
                return

def play_battleship():
    size = 10
    num_ships = 3
    ship_sizes = [3, 4, 5]
    
    player_board = create_board(size)
    computer_board = create_board(size)
    computer_view = create_board(size)
    
    for ship_size in ship_sizes:
        place_ship(player_board, ship_size)
        place_ship(computer_board, ship_size)
    
    player_ships = sum(row.count('S') for row in player_board)
    computer_ships = sum(row.count('S') for row in computer_board)
    
    while player_ships > 0 and computer_ships > 0:
        print("Your board:")
        print_board(player_board)
        print("Your guesses:")
        print_board(computer_view)
        
        # Player's turn
        while True:
            try:
                row = int(input("Enter row (0-9): "))
                col = int(input("Enter column (0-9): "))
                if 0 <= row < size and 0 <= col < size and computer_view[row][col] == 'O':
                    break
                print("Invalid input. Try again.")
            except ValueError:
                print("Invalid input. Try again.")
        
        if computer_board[row][col] == 'S':
            print("Hit!")
            computer_view[row][col] = 'X'
            computer_board[row][col] = 'X'
            computer_ships -= 1
        else:
            print("Miss!")
            computer_view[row][col] = 'M'
        
        # Computer's turn
        while True:
            row, col = random.randint(0, size-1), random.randint(0, size-1)
            if player_board[row][col] != 'X' and player_board[row][col] != 'M':
                break
        
        print(f"\nComputer guesses: {row}, {col}")
        if player_board[row][col] == 'S':
            print("Computer hit your ship!")
            player_board[row][col] = 'X'
            player_ships -= 1
        else:
            print("Computer missed!")
            player_board[row][col] = 'M'
        
        print(f"\nYour ships remaining: {player_ships}")
        print(f"Computer ships remaining: {computer_ships}\n")
    
    if player_ships == 0:
        print("Game over! The computer won.")
    else:
        print("Congratulations! You won!")

play_battleship()
