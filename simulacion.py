import random
from statistics import mean
import matplotlib.pyplot as plt
from mastermind import COLORES, NUM_FICHAS, obtener_retroalimentacion, MastermindSolver

def simular_juego_automatico(secreta):
    """
    Simula un juego automático con la combinación secreta dada.
    Retorna:
      - intentos: número de intentos realizados.
      - historial: lista con el tamaño del espacio de búsqueda después de cada intento.
    """
    # Se pasan los parámetros necesarios al constructor
    solver = MastermindSolver(COLORES, NUM_FICHAS)
    intentos = 0
    historial = []
    
    while True:
        jugada = solver.proponer_jugada()
        intentos += 1
        
        # Guarda el tamaño actual del espacio antes de actualizarlo.
        historial.append(len(solver.soluciones_posibles))
        
        feedback = obtener_retroalimentacion(secreta, jugada)
        if feedback[0] == NUM_FICHAS:
            break
        solver.actualizar_soluciones(jugada, feedback)
    
    return intentos, historial

def simular_varios_juegos(num_juegos=200):
    """Simula num_juegos y retorna las estadísticas necesarias."""
    resultados_intentos = []  # Lista de intentos por juego.
    historiales = []          # Lista de historiales de cada juego.

    for _ in range(num_juegos):
        # Se genera la combinación secreta aleatoria.
        secreta = tuple(random.choice(COLORES) for _ in range(NUM_FICHAS))
        intentos, historial = simular_juego_automatico(secreta)
        resultados_intentos.append(intentos)
        historiales.append(historial)
    
    return resultados_intentos, historiales

def procesar_y_graficar(resultados_intentos, historiales):
    """Calcula promedios y genera el gráfico del tamaño del espacio de búsqueda."""
    num_juegos = len(resultados_intentos)
    promedio_intentos = mean(resultados_intentos)
    print(f"Promedio de intentos necesarios: {promedio_intentos:.2f}")

    # Determina el número máximo de intentos en todos los juegos.
    max_intentos = max(len(hist) for hist in historiales)
    
    promedios_por_intento = []
    for i in range(max_intentos):
        espacios = [hist[i] for hist in historiales if i < len(hist)]
        promedios_por_intento.append(mean(espacios))
    
    # Gráfico: eje X = número de intento, eje Y = promedio del tamaño del espacio.
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, max_intentos+1), promedios_por_intento, marker='o', linestyle='-')
    plt.title("Promedio del tamaño del espacio de búsqueda por intento")
    plt.xlabel("Número de intento")
    plt.ylabel("Tamaño del espacio de búsqueda")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    num_juegos = 200
    resultados_intentos, historiales = simular_varios_juegos(num_juegos)
    procesar_y_graficar(resultados_intentos, historiales)
