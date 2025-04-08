from simulacion import simular_varios_juegos, procesar_y_graficar

if __name__ == "__main__":
    num_juegos = 200
    resultados_intentos, historiales = simular_varios_juegos(num_juegos)
    procesar_y_graficar(resultados_intentos, historiales)
