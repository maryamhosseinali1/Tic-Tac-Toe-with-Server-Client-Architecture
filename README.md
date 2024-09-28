# Tic-Tac-Toe with Server-Client Architecture

## Overview
This project is a multiplayer Tic-tac-toe game designed with a server-client architecture. It supports three different board sizes (3x3, 4x4, and 5x5), and players are matched based on their selected board size. The server manages the game logic and player coordination, while the client allows players to make moves and view the game state.

### Author:
- Maryam Hosseinali

### Course:
Fundamentals of Operating Systems, School of Computer Science, University of Tehran

## Server
The server acts as the central hub that:
- Handles incoming player connections.
- Manages game states and player turns.
- Matches players for games based on board size.
- Uses threads to allow multiple concurrent games.

The server listens on port 8080 and manages player matchmaking using a waiting list. When two players are matched, the game begins, and the server sends game updates and validations between clients.

## Client
The client program:
- Connects to the server via a socket on port 8080.
- Accepts the player’s move and sends it to the server for validation.
- Receives game updates, including the opponent's moves and the game result.

Players input their moves in "X Y" format, and the game continues until one player wins or the game ends in a draw.

## Game Engine
The game engine:
- Handles the core game logic, including win conditions and board updates.
- Processes player moves and checks for valid moves, win conditions, or a draw.
- Updates the game board based on player inputs.

