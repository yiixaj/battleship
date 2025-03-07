import xmlrpc.server
import random
from xmlrpc.server import SimpleXMLRPCServer


class BattleshipServer:
    def __init__(self):
        self.jugadores = {}
        self.estado_juego = {
            'jugadores_listos': [],
            'posiciones_barcos': {},
            'ataques': {},
            'turno': None
        }
        self.tablero_size = 10

    def registrar_jugador(self, nombre_jugador):
        if nombre_jugador in self.jugadores:
            return "El jugador ya está registrado."
        
        if len(self.jugadores) >= 2:
            return "Ya hay suficientes jugadores."
        
        self.jugadores[nombre_jugador] = {
            'barcos': [],
            'tablero': [[0 for _ in range(self.tablero_size)] for _ in range(self.tablero_size)]
        }
        
        return "Registrado con éxito."

    def enviar_posiciones(self, nombre_jugador, posiciones):
        if nombre_jugador not in self.jugadores:
            return "Jugador no registrado."
        
        self.estado_juego['posiciones_barcos'][nombre_jugador] = posiciones
        
        # Marcar barcos en el tablero del jugador
        for coordenada in posiciones:
            x, y = map(int, coordenada.split(','))
            self.jugadores[nombre_jugador]['tablero'][y][x] = 1
        
        return "Posiciones recibidas correctamente."

    def jugador_listo(self, nombre_jugador):
        if nombre_jugador not in self.estado_juego['jugadores_listos']:
            self.estado_juego['jugadores_listos'].append(nombre_jugador)
        
        # Iniciar juego si hay 2 jugadores
        if len(self.estado_juego['jugadores_listos']) == 2:
            self._iniciar_juego()
        
        return "Jugador marcado como listo."

    def _iniciar_juego(self):
        # Seleccionar primer turno aleatoriamente
        jugadores = list(self.jugadores.keys())
        self.estado_juego['turno'] = random.choice(jugadores)

    def obtener_estado(self, nombre_jugador):
        # Clonar el estado para evitar modificaciones directas
        estado = {
            'jugadores_listos': self.estado_juego['jugadores_listos'].copy(),
            'turno': self.estado_juego['turno'],
            'posiciones_barcos': self.estado_juego['posiciones_barcos'].get(nombre_jugador, {}),
            'ataques': self.estado_juego['ataques'].get(nombre_jugador, {}),
            'ganador': self.estado_juego.get('ganador'),
            'perdedor': self.estado_juego.get('perdedor')
        }
        return estado

    def atacar(self, nombre_jugador, x, y):
        print(f"--- Detailed Attack Debugging ---")
        print(f"Attacker: {nombre_jugador}")
        print(f"Current registered players: {list(self.jugadores.keys())}")
        print(f"Current turn BEFORE attack: {self.estado_juego['turno']}")

        # Verificar turno
        if self.estado_juego['turno'] != nombre_jugador:
            print(f"ERROR: Not {nombre_jugador}'s turn.")
            return f"No es tu turno de atacar. Turno actual: {self.estado_juego['turno']}"

        # Obtener oponente
        oponentes = [j for j in self.jugadores.keys() if j != nombre_jugador]
        if not oponentes:
            print("ERROR: No opponents found")
            return "No hay oponente para atacar."

        oponente = oponentes[0]
        print(f"Opponent identified: {oponente}")

        # Verificar si la coordenada ya fue atacada
        if f"{x},{y}" in self.estado_juego['ataques'].get(oponente, {}):
            return "Esta coordenada ya ha sido atacada."

        # Verificar si hay un barco en la coordenada
        if self.jugadores[oponente]['tablero'][y][x] == 1:
            resultado = "¡HIT! Has alcanzado un barco."
            tipo_resultado = 'hit'
            self.jugadores[oponente]['tablero'][y][x] = 2  # Marcar como tocado

            # Verificar si este hit hunde completamente un barco
            if self._verificar_barco_hundido(oponente, x, y):
                resultado = "¡Barco hundido! Pero continúas tu turno."

        else:
            resultado = "¡MISS! No hay barco en esta coordenada."
            tipo_resultado = 'miss'
            # Cambiar turno solo si es un miss
            self.estado_juego['turno'] = oponente

        # Registrar ataque
        if oponente not in self.estado_juego['ataques']:
            self.estado_juego['ataques'][oponente] = {}
        self.estado_juego['ataques'][oponente][f"{x},{y}"] = tipo_resultado

        # Verificar si todos los barcos han sido hundidos
        if self._verificar_victoria(oponente):
            resultado = f"¡VICTORIA! Has hundido todos los barcos de {oponente}"
            self.estado_juego['ganador'] = nombre_jugador
            self.estado_juego['perdedor'] = oponente 

        print(f"Turn after attack: {self.estado_juego['turno']}")

        return resultado

    def _verificar_barco_hundido(self, oponente, x, y):
    
        # Buscar todas las partes del barco
        for dy in range(-3, 4):  # Rango suficiente para cubrir barcos de hasta 4 cuadros
            for dx in range(-3, 4):
                new_x, new_y = x + dx, y + dy
            
                # Verificar límites del tablero
                if 0 <= new_x < 10 and 0 <= new_y < 10:
                    if self.jugadores[oponente]['tablero'][new_y][new_x] == 1:
                        # Aún hay parte del barco sin tocar
                        return False
    
        # Si llegamos aquí, el barco está completamente hundido
        return True

    def _verificar_victoria(self, nombre_jugador):
        # Verificar si todos los barcos del jugador han sido hundidos
        tablero = self.jugadores[nombre_jugador]['tablero']
        for fila in tablero:
            if 1 in fila:  # Si queda algún barco sin tocar
                return False
        return True

def run_server():
    server = SimpleXMLRPCServer(("0.0.0.0", 8000), allow_none=True) #aqui debemos de colocar la direccion IP del servidor
    print("Servidor Battleship iniciado en  0.0.0.0:8000")
    
    battleship_server = BattleshipServer()
    
    # Registrar métodos
    server.register_instance(battleship_server)
    
    # Iniciar servidor
    server.serve_forever()

if __name__ == "__main__":
    run_server()
