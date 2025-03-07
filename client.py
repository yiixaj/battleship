import tkinter as tk
from tkinter import messagebox, simpledialog
import xmlrpc.client
import threading
import time
import pygame


class BattleshipGUI:
    def __init__(self, server):
        pygame.mixer.init()

        try:
            self.hit_sound = pygame.mixer.Sound('hit_sound.mp3')
            self.miss_sound = pygame.mixer.Sound('miss_sound.mp3')
        except Exception as e:
            print(f"Error loading sound files: {e}")
            self.hit_sound = None
            self.miss_sound = None

        self.server = server
        self.player_name = None
        self.selected_ship = None
        self.selected_orientation = None
        self.root = tk.Tk()
        self.root.title("Battleship Naval Battle")
        self.root.geometry("800x900")
        self.root.configure(bg="#2C3E50")

        self.font_title = ("Helvetica", 16, "bold")
        self.font_normal = ("Helvetica", 12)
        self.color_bg = "#2C3E50"
        self.color_text = "#ECF0F1"
        self.color_button = "#3498DB"
        self.color_button_hover = "#2980B9"

        self.ships_remaining = {
            "Acorazado": 1,
            "Destructor": 1,
            "Submarino": 1,
            "Portaviones": 1,
            "Fragata": 1
        }

        self.create_main_window()

    def create_main_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="BATTLESHIP", font=("Helvetica", 24, "bold"), bg=self.color_bg, fg=self.color_text).pack(pady=20)

        button_frame = tk.Frame(self.root, bg=self.color_bg)
        button_frame.pack(expand=True)

        new_game_btn = tk.Button(button_frame, text="Nueva Partida", command=self.start_new_game, font=self.font_normal, bg=self.color_button, fg="white", activebackground=self.color_button_hover)
        new_game_btn.pack(pady=10, padx=20, fill=tk.X)
        new_game_btn.bind("<Enter>", lambda e: e.widget.configure(bg=self.color_button_hover))
        new_game_btn.bind("<Leave>", lambda e: e.widget.configure(bg=self.color_button))

        # Nuevo botón de Más Información
        info_btn = tk.Button(button_frame, text="Más Información", command=self.show_game_info, font=self.font_normal, bg="#2ECC71", fg="white", activebackground="#27AE60")
        info_btn.pack(pady=10, padx=20, fill=tk.X)
        info_btn.bind("<Enter>", lambda e: e.widget.configure(bg="#27AE60"))
        info_btn.bind("<Leave>", lambda e: e.widget.configure(bg="#2ECC71"))

        quit_btn = tk.Button(button_frame, text="Salir", command=self.root.quit, font=self.font_normal, bg="#E74C3C", fg="white", activebackground="#C0392B")
        quit_btn.pack(pady=10, padx=20, fill=tk.X)
        quit_btn.bind("<Enter>", lambda e: e.widget.configure(bg="#C0392B"))
        quit_btn.bind("<Leave>", lambda e: e.widget.configure(bg="#E74C3C"))

    def start_new_game(self):
        self.player_name = simpledialog.askstring("Player Name", "Ingresa tu nombre:")
        if not self.player_name:
            return

        try:
            response = self.server.registrar_jugador(self.player_name)
            print(f"Server response: {response}")
            if response != "Registrado con éxito.":
                messagebox.showerror("Error", response)
                return
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            return

        self.create_ship_placement_window()

    def create_ship_placement_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Coloca tus barcos", font=self.font_title, bg=self.color_bg, fg=self.color_text).pack(pady=10)

        # Contenedor principal para el tablero y los menús
        main_frame = tk.Frame(self.root, bg=self.color_bg)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Crear un frame superior para los menús desplegables
        top_frame = tk.Frame(main_frame, bg=self.color_bg)
        top_frame.pack(side=tk.TOP, pady=10)

        # Menú desplegable para seleccionar el tipo de barco
        tk.Label(top_frame, text="Selecciona un barco:", bg=self.color_bg, fg=self.color_text, font=self.font_normal).pack(side=tk.LEFT, padx=5)
        self.selected_ship = tk.StringVar()
        self.selected_ship.set("Seleccionar barco")
        self.ship_menu = tk.OptionMenu(top_frame, self.selected_ship, *self.ships_remaining.keys())
        self.ship_menu.config(width=15, font=self.font_normal, bg=self.color_button, fg="white")
        self.ship_menu.pack(side=tk.LEFT, padx=5)

        # Menú desplegable para seleccionar la orientación
        tk.Label(top_frame, text="Selecciona la orientación:", bg=self.color_bg, fg=self.color_text, font=self.font_normal).pack(side=tk.LEFT, padx=8)
        self.selected_orientation = tk.StringVar()
        self.selected_orientation.set("Seleccionar orientación")
        self.orientation_menu = tk.OptionMenu(top_frame, self.selected_orientation, "Horizontal", "Vertical")
        self.orientation_menu.config(width=20, font=self.font_normal, bg=self.color_button, fg="white")
        self.orientation_menu.pack(side=tk.LEFT, padx=8)

        # Crear un frame para el tablero centrado
        board_frame = tk.Frame(main_frame, bg=self.color_bg)
        board_frame.pack(side=tk.TOP, pady=20)  # Agregar margen vertical
        board_container = tk.Frame(board_frame, bg=self.color_bg)  # Contenedor centrado
        board_container.pack(expand=True)  # Centrar el tablero horizontalmente

        # Crear botones para el tablero
        self.placement_buttons = []
        for y in range(10):
            row_buttons = []
            for x in range(10):
                btn = tk.Button(
                    board_container,
                    width=4,
                    height=2,
                    bg="#34495E",
                    fg="white",
                    command=lambda x=x, y=y: self.place_ship(x, y)
                )
                btn.grid(row=y, column=x, padx=2, pady=2)
                row_buttons.append(btn)
            self.placement_buttons.append(row_buttons)

        # Crear etiqueta para mostrar barcos restantes
        self.ships_remaining_label = tk.Label(
            self.root,
            text="Barcos por colocar: 5",
            font=self.font_normal,
            bg=self.color_bg,
            fg=self.color_text
        )
        self.ships_remaining_label.pack(pady=10)

        self.update_ship_placement_status()



    def select_ship(self, ship_type):
        self.selected_ship = ship_type
        messagebox.showinfo("Barco seleccionado", f"Usted ha seleccionado {ship_type}. ahora, ubiquelo en el mapa.")

    def select_orientation(self, orientation):
        self.selected_orientation = orientation
        messagebox.showinfo("Orientacion seleccionada", f"usted ha seleccionado {orientation}")

    def place_ship(self, x, y):
        ship_type = self.selected_ship.get()
        orientation = self.selected_orientation.get()

        if ship_type == "Seleccionar barco" or orientation == "Seleccionar orientación":
            messagebox.showwarning("Selección incompleta", "Por favor selecciona un barco y una orientación antes de colocarlo.")
            return

        ship_sizes = {"Acorazado": 5, "Destructor": 4, "Submarino": 3, "Portaviones": 4, "Fragata": 3}
        size = ship_sizes[ship_type]

        # Verificar si ya no quedan barcos de este tipo
        if self.ships_remaining[ship_type] <= 0:
            messagebox.showwarning("Barco ya colocado", f"Ya has colocado el {ship_type}.")
            return

        # Comprobar que el barco cabe en el tablero y no colisiona
        if orientation == "Horizontal":
            if x + size > 10:
                messagebox.showwarning("Placement Error", "El barco no cabe en esa posición horizontal.")
                return
            for i in range(size):
                if self.placement_buttons[y][x + i].cget("bg") == "#2ECC71":
                    messagebox.showwarning("Placement Error", "El barco colisiona con otro.")
                    return
            for i in range(size):
                self.placement_buttons[y][x + i].config(bg="#2ECC71")  # Verde para barcos
        elif orientation == "Vertical":
            if y + size > 10:
                messagebox.showwarning("Placement Error", "El barco no cabe en esa posición vertical.")
                return
            for i in range(size):
                if self.placement_buttons[y + i][x].cget("bg") == "#2ECC71":
                    messagebox.showwarning("Placement Error", "El barco colisiona con otro.")
                    return
            for i in range(size):
                self.placement_buttons[y + i][x].config(bg="#2ECC71")  # Verde para barcos

        # Reducir el conteo de barcos disponibles de este tipo
        self.ships_remaining[ship_type] -= 1

        # Actualizar menú para deshabilitar barcos ya colocados
        self.update_ship_menu()

        # Limpiar selección
        self.selected_ship.set("Seleccionar barco")
        self.selected_orientation.set("Seleccionar orientación")

        # Actualizar estado del juego
        self.update_ship_placement_status()

    def update_ship_menu(self):
        menu = self.ship_menu["menu"]
        menu.delete(0, "end")
        for ship, count in self.ships_remaining.items():
            if count > 0:
                menu.add_command(label=ship, command=lambda value=ship: self.selected_ship.set(value))



    def update_ship_placement_status(self):
        ships_remaining = sum(self.ships_remaining.values())
        self.ships_remaining_label.config(text=f"Barcos por colocar: {ships_remaining}")

        if ships_remaining == 0:
            messagebox.showinfo("Listo", "Todos los barcos colocados, esperando al otro jugador...")
            self.enviar_posiciones_barcos()
            self.send_ready_signal()

    def enviar_posiciones_barcos(self):
        posiciones = {}
        for y, row in enumerate(self.placement_buttons):
            for x, btn in enumerate(row):
                if btn.cget("bg") == "#2ECC71":
                    posiciones[f"{x},{y}"] = 'occupied'

        try:
            response = self.server.enviar_posiciones(self.player_name, posiciones)
            print("Posiciones enviadas:", response)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send ship positions: {type(e).__name__} - {e}")

    def send_ready_signal(self):
        try:
            self.server.jugador_listo(self.player_name)
            print(f"{self.player_name} marked as ready.")  # Debugging
            self.wait_for_game_start()
        except Exception as e:
            messagebox.showerror("Error", f"Error notifying server: {e}")

    def wait_for_game_start(self):
        threading.Thread(target=self.check_game_ready, daemon=True).start()

    def check_game_ready(self):
        while True:
            try:
                estado = self.server.obtener_estado(self.player_name)
                print("Server state:", estado)  # Debugging
                if len(estado['jugadores_listos']) >= 2:
                    self.root.after(0, self.create_battle_window)
                    break
                time.sleep(1)
            
            except Exception as e:
                messagebox.showerror("Error", str(e))
                break

    def create_battle_window(self):
        print("Creating battle window...")  # Debugging
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Battlefield", font=self.font_title, bg=self.color_bg, fg=self.color_text).pack(pady=10)

        main_frame = tk.Frame(self.root, bg=self.color_bg)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        player_frame = tk.Frame(main_frame, bg=self.color_bg)
        player_frame.pack(side=tk.LEFT, expand=True, padx=10)

        tk.Label(player_frame, text="Tu flota", font=self.font_title, bg=self.color_bg, fg=self.color_text).pack()

        self.player_buttons = []
        player_board_frame = tk.Frame(player_frame, bg=self.color_bg)
        player_board_frame.pack()

        for y in range(10):
            row_buttons = []
            for x in range(10):
                btn = tk.Button(player_board_frame, width=4, height=2, bg="#34495E", fg="white", state=tk.DISABLED)
                btn.grid(row=y, column=x, padx=2, pady=2)
                row_buttons.append(btn)
            self.player_buttons.append(row_buttons)

        attack_frame = tk.Frame(main_frame, bg=self.color_bg)
        attack_frame.pack(side=tk.RIGHT, expand=True, padx=10)

        tk.Label(attack_frame, text="Mapa de ataque", font=self.font_title, bg=self.color_bg, fg=self.color_text).pack()

        self.attack_buttons = []
        attack_board_frame = tk.Frame(attack_frame, bg=self.color_bg)
        attack_board_frame.pack()

        for y in range(10):
            row_buttons = []
            for x in range(10):
                btn = tk.Button(attack_board_frame, width=4, height=2, bg="#34495E", fg="white", command=lambda x=x, y=y: self.attack(x, y))
                btn.grid(row=y, column=x, padx=2, pady=2)
                row_buttons.append(btn)
            self.attack_buttons.append(row_buttons)

        self.game_status_label = tk.Label(self.root, text="", font=self.font_normal, bg=self.color_bg, fg=self.color_text)
        self.game_status_label.pack(pady=10)

        # Cargar posiciones de barcos
        self.cargar_posiciones_barcos()
        
        # Iniciar actualización del estado del juego
        self.update_game_state()

    def cargar_posiciones_barcos(self):
        try:
            estado = self.server.obtener_estado(self.player_name)
            print("Contenido completo del estado:", estado)  # Debug completo del estado
        
            # Verificar si existe la clave de posiciones
            posiciones = estado.get('posiciones_barcos', {})
            print("Posiciones de barcos:", posiciones)  # Debugging de posiciones
        
            for coordenada in posiciones:
                print(f"Procesando coordenada: {coordenada}")
                x, y = map(int, coordenada.split(','))
                self.player_buttons[y][x].config(bg="#2ECC71")  # Verde para barcos
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las posiciones de los barcos: {e}")

    def update_game_state(self):
        try:
            estado = self.server.obtener_estado(self.player_name)

            # Check if the battle window is still active
            if not hasattr(self, 'root') or not self.root.winfo_exists():
                return
        
            # Verificar si el juego ha terminado
            if estado.get('ganador'):
                self.handle_game_end(estado)
                return

            # Actualizar tablero propio con ataques recibidos
            if 'ataques' in estado:
                for coordenada, resultado in estado['ataques'].items():
                    x, y = map(int, coordenada.split(','))
                    btn = self.player_buttons[y][x]
                    if resultado == 'hit':
                        btn.config(bg="#E74C3C")  # Rojo para impactos
                    elif resultado == 'miss':
                        btn.config(bg="#3498DB")  # Azul para fallos

            # Manejar turnos
            current_turn = estado.get('turno')
            if current_turn == self.player_name:
                self.enable_attack_grid()
                self.game_status_label.config(
                    text="Es tu turno para atacar.", 
                    fg="green"
                )
            else:
                self.disable_attack_grid()
                self.game_status_label.config(
                    text=f"Turno de {current_turn}", 
                    fg="red"
                )

            # Programar próxima actualización
            self.root.after(2000, self.update_game_state)

        except Exception as e:
            print(f"Error actualizando estado del juego: {e}")
            import traceback
            traceback.print_exc()
        
            # Intentar volver al menú principal si hay un error
            try:
                self.create_main_window()
            except Exception:
                # Si falla la creación del menú principal, reiniciar la aplicación
                self.root.destroy()
        
            

    def handle_game_end(self, estado):
        try:
            #evitar multiples ejecuciones
            if hasattr(self, 'game_ended') and self.game_ended:
                return
            self.game_ended =True

            # Detener actualizaciones de estado
            try:
                self.root.after_cancel(self.update_game_state)
            except Exception as e:
                print(f" error al cancelar actualizaciones pendientes: {e}")

            ganador = estado.get('ganador')
            perdedor = estado.get('perdedor')

            # Obtener el ganador
            ganador = estado.get('ganador')
            if not ganador:
                return

            # Determinar si el jugador actual es el ganador o el perdedor
            if ganador == self.player_name:
                # Mensaje para el ganador
                messagebox.showinfo(
                    "¡Felicidades!", 
                    f"¡Ganaste el juego, {self.player_name}! \n\nHas hundido toda la flota enemiga."
                )
            elif perdedor == self.player_name:
               messagebox.showinfo(
                   "juego terminado",
                   f"losiento, {self.player_name}. \n\nEl ganador es {ganador}.  "
               )
            
                

            # Resetear estado del juego
            self.reset_game_state()

            # Volver a la pantalla inicial
            self.create_main_window()

        except Exception as e:
            print(f"Error en handle_game_end: {e}")
            import traceback
            traceback.print_exc()
        
            # Intento de volver a la pantalla inicial en caso de error
            try:
                self.create_main_window()
            except Exception:
                # Si falla, reiniciar la aplicación
                self.root.destroy()
    
    def reset_game_state(self):
        self.player_name = None
        self.selected_ship = None
        self.game_ended = False
        self.selected_orientation = None
        self.ships_remaining = {
            "Acorazado": 1,
            "Destructor": 1,
            "Submarino": 1,
            "Portaviones": 1,
            "Fragata": 1
        }

    def show_game_result(self, estado):
        # Intentar detener todas las posibles actualizaciones de estado
        try:
            self.root.after_cancel(self.update_game_state)
        except Exception:
            pass

        # Obtener el nombre del ganador
        ganador = estado.get('ganador')

        # Mostrar mensaje de ganador o perdedor
        if ganador == self.player_name:
            messagebox.showinfo("¡Felicidades!", f"¡Ganaste el juego, {self.player_name}! Hundiste toda la flota enemiga.")
        else:
            messagebox.showinfo("Juego Terminado", f"Lo siento, {self.player_name}. {ganador} ha ganado el juego.")

        # Resetear todos los estados del juego
        self.player_name = None
        self.selected_ship = None
        self.selected_orientation = None
        self.ships_remaining = {
            "Acorazado": 1,
            "Destructor": 1,
            "Submarino": 1,
            "Portaviones": 1,
            "Fragata": 1
        }

        # Redirigir al menú principal
        self.create_main_window()



    def enable_attack_grid(self):
        if hasattr(self, 'attack_buttons'):
            for row in self.attack_buttons:
                for btn in row:
                    if btn.winfo_exists():
                        btn.config(state=tk.NORMAL)

    def disable_attack_grid(self):
        if hasattr(self, 'attack_buttons'):
            for row in self.attack_buttons:
                for btn in row:
                    if btn.winfo_exists():
                        btn.config(state=tk.DISABLED)

    def attack(self, x, y):
        try:
            # Disable the attacked button immediately
            self.attack_buttons[y][x].config(state=tk.DISABLED)

            # Perform attack
            resultado = self.server.atacar(self.player_name, x, y)
            print(f"Attack result: {resultado}")

            # Update button color based on result
            if "hit" in resultado.lower():
                self.attack_buttons[y][x].config(bg='red')
                # sound shoot
                if self.hit_sound:
                    self.hit_sound.play()
            elif "miss" in resultado.lower():
                self.attack_buttons[y][x].config(bg='white')
                #soud miss
                if self.miss_sound:
                    self.miss_sound.play()

            # Show attack result
            #messagebox.showinfo("Attack Result", resultado)

            # Check if game is over
            estado = self.server.obtener_estado(self.player_name)
            if estado.get('ganador') or estado.get('perdedor'):
                self.handle_game_end(estado)
                return

            # Update game state
            self.update_game_state()

        except Exception as e:
            messagebox.showerror("Error", f"Could not perform attack: {e}")
            # Re-enable the button if there's an error
            self.attack_buttons[y][x].config(state=tk.NORMAL)

    def show_game_info(self):
        # Ventana de información personalizable
        info_window = tk.Toplevel(self.root)
        info_window.title("Información del Juego")
        info_window.geometry("400x300")
        info_window.configure(bg=self.color_bg)

        # Título
        tk.Label(info_window, text="Información de Battleship", 
                font=("Helvetica", 16, "bold"), 
                bg=self.color_bg, 
                fg=self.color_text).pack(pady=10)

        # Área de texto desplazable para información
        info_text = tk.Text(info_window, 
                            wrap=tk.WORD, 
                            width=50, 
                            height=10, 
                            bg="#34495E", 
                            fg=self.color_text, 
                            font=self.font_normal)
        info_text.pack(padx=20, pady=10)

        # Texto predeterminado que puedes personalizar
        default_info = """Bienvenido a Battleship Naval Battle!

            Reglas del Juego:
            - Coloca tus 5 barcos estratégicamente en tu tablero
            - Cada jugador tiene un tablero de 10x10
            - Turnos alternos para atacar las coordenadas del oponente
            - Gana quien hunda todos los barcos del enemigo primero

            Tipos de Barcos:
            - Acorazado: 5 casillas
            - Portaviones: 4 casillas
            - Destructor: 4 casillas
            - Submarino: 3 casillas
            - Fragata: 3 casillas

            ¡Buena suerte, almirante!"""

        info_text.insert(tk.END, default_info)
        info_text.config(state=tk.DISABLED)  # Hacer el texto de solo lectura

        # Botón de cerrar
        close_btn = tk.Button(info_window, 
                            text="Cerrar", 
                            command=info_window.destroy, 
                            bg=self.color_button, 
                            fg="white")
        close_btn.pack(pady=10)

def main():
    try:
        server = xmlrpc.client.ServerProxy("http://0.0.0.0:8000", allow_none=True) # aqui debemos de colocar la direccion IP del servidor
        app = BattleshipGUI(server)
        app.root.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")

if __name__ == "__main__":
    main()