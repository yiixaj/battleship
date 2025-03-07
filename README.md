# Battleship Naval Battle Game

![Battleship Game](https://img.shields.io/badge/Game-Battleship-blue)
![Python](https://img.shields.io/badge/Python-3.x-green)
![RPC](https://img.shields.io/badge/Technology-XML--RPC-orange)

A multiplayer naval battle game implemented in Python using XML-RPC for client-server communication.

## Description

This project is a digital implementation of the classic Battleship board game where players strategically place ships on a grid and take turns firing at their opponent's grid to sink all their ships. The game features:

- Client-server architecture using XML-RPC
- Graphical user interface built with Tkinter
- Sound effects for hit and miss events
- Turn-based gameplay
- Real-time game state updates

## Game Rules

- Each player has a 10x10 grid
- Players place 5 different ships on their grid:
  - Acorazado (Battleship): 5 cells
  - Portaviones (Aircraft Carrier): 4 cells
  - Destructor (Destroyer): 4 cells
  - Submarino (Submarine): 3 cells
  - Fragata (Frigate): 3 cells
- Players take alternating turns to attack coordinates on the opponent's grid
- The game ends when one player sinks all of the opponent's ships

## Requirements

- Python 3.x
- Tkinter (included in standard Python installation)
- Pygame (for sound effects)
- XML-RPC (included in standard Python library)

## Installation

1. Clone the repository or download the source code

2. Install required dependencies:
   ```bash
   pip install pygame
   ```

3. Place sound effect files in the same directory as the client:
   - `hit_sound.mp3` - Sound played when a ship is hit
   - `miss_sound.mp3` - Sound played when an attack misses

## Usage

### Starting the Server

1. Open a terminal and navigate to the project directory
2. Edit the server.py file to set the desired IP address (default is 0.0.0.0)
3. Run the server:
   ```bash
   python server.py
   ```
4. The server will start and display a message: "Servidor Battleship iniciado en 0.0.0.0:8000"

### Starting the Client

1. Open a terminal and navigate to the project directory
2. Edit the client.py file to set the server IP address in the following line:
   ```python
   server = xmlrpc.client.ServerProxy("http://0.0.0.0:8000", allow_none=True)
   ```
   Replace "0.0.0.0" with the actual IP address of the server
3. Run the client:
   ```bash
   python client.py
   ```
4. The game interface will open

### Playing the Game

1. Click "Nueva Partida" to start a new game
2. Enter your player name when prompted
3. Place your ships on your grid:
   - Select a ship type from the dropdown menu
   - Select an orientation (Horizontal or Vertical)
   - Click on the grid to place the ship
4. After placing all ships, wait for another player to join
5. Take turns attacking the opponent's grid by clicking on cells in the attack map
6. The game ends when one player sinks all of the opponent's ships

## Project Structure

- `server.py` - Server-side code for game logic and state management
- `client.py` - Client-side code and user interface

## Key Features

- Real-time game state updates
- Ship placement with collision detection
- Color-coded visual feedback (green for ships, red for hits, blue for misses)
- Sound effects for gameplay actions
- Informative game status messages

## Known Issues

- If the server crashes, clients need to be restarted
- Connection errors may occur if incorrect IP addresses are specified

## Future Enhancements

- Persistent player statistics
- Multiple concurrent games
- More ship types and grid sizes
- Chat functionality between players
- Custom game options

## License

This project is for educational purposes.

## Credits

- Sound effects: [Update with appropriate credit if needed]
- Game concept: Based on the classic Battleship board game
