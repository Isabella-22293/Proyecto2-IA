import itertools

class Sentence:
    def evaluate(self, model):
        raise NotImplementedError("Debe implementarse en la subclase.")

    def formula(self):
        # Retorna una representación en forma de fórmula.
        return ""

    def symbols(self):
        # Retorna el conjunto de símbolos presentes en la oración.
        return set()

    @classmethod
    def validate(cls, sentence):
        if not isinstance(sentence, Sentence):
            raise TypeError("Debe ser una oración lógica (instancia de Sentence).")

    @classmethod
    def parenthesize(cls, s):
        def balanced(s):
            count = 0
            for c in s:
                if c == "(":
                    count += 1
                elif c == ")":
                    if count <= 0:
                        return False
                    count -= 1
            return count == 0
        if not s or s.isalpha() or (s[0] == "(" and s[-1] == ")" and balanced(s[1:-1])):
            return s
        else:
            return f"({s})"

class Symbol(Sentence):
    def __init__(self, name):
        self.name = name  # Guarda el nombre del símbolo

    def evaluate(self, model):
        """
        Evalúa el símbolo devolviendo el valor booleano asociado en el modelo.
        Si el símbolo no está en el modelo, se lanza una excepción.
        """
        try:
            return bool(model[self.name])
        except KeyError:
            raise Exception(f"Variable {self.name} no asignada en el modelo.")

    def formula(self):
        # Devuelve el nombre del símbolo como representación de la fórmula.
        return self.name

    def symbols(self):
        # Retorna un conjunto que contiene este símbolo.
        return {self.name}

    def __repr__(self):
        # Representación en cadena del símbolo.
        return self.name

class Not(Sentence):
    def __init__(self, operand):
        # Valida que el operando sea una oración lógica.
        Sentence.validate(operand)
        self.operand = operand

    def evaluate(self, model):
        # Devuelve el valor negado de la evaluación del operando.
        return not self.operand.evaluate(model)

    def formula(self):
        # Devuelve la representación de la fórmula con el operador de negación.
        return "¬" + Sentence.parenthesize(self.operand.formula())

    def symbols(self):
        # Retorna los símbolos presentes en el operando.
        return self.operand.symbols()

    def __repr__(self):
        # Representación en cadena de la negación.
        return f"Not({self.operand})"

class And(Sentence):
    def __init__(self, *conjuncts):
        # Valida que cada operando sea una oración lógica.
        for conjunct in conjuncts:
            Sentence.validate(conjunct)
        self.conjuncts = list(conjuncts)

    def evaluate(self, model):
        # Evalúa la conjunción. Devuelve True solo si TODOS los operandos son verdaderos.
        for conjunct in self.conjuncts:
            if not conjunct.evaluate(model):
                return False
        return True

    def formula(self):
        """
        Devuelve una cadena que representa la fórmula de la conjunción, 
        uniendo cada operando con el símbolo ∧.
        """
        if len(self.conjuncts) == 1:
            return self.conjuncts[0].formula()
        return " ∧ ".join([Sentence.parenthesize(c.formula()) for c in self.conjuncts])

    def symbols(self):
        # Retorna el conjunto de todos los símbolos presentes en cada operando.
        s = set()
        for c in self.conjuncts:
            s = s.union(c.symbols())
        return s

    def __repr__(self):
        # Representación en cadena de la conjunción.
        return "And(" + ", ".join([str(c) for c in self.conjuncts]) + ")"

class Or(Sentence):
    def __init__(self, *disjuncts):
        # Valida que cada operando sea una oración lógica.
        for disjunct in disjuncts:
            Sentence.validate(disjunct)
        self.disjuncts = list(disjuncts)

    def evaluate(self, model):
        # Evalúa la disyunción. Devuelve True si al menos uno de los operandos es verdadero.
        for disjunct in self.disjuncts:
            if disjunct.evaluate(model):
                return True
        return False

    def formula(self):
        # Devuelve la representación en forma de fórmula, uniendo los operandos con el símbolo ∨.
        if len(self.disjuncts) == 1:
            return self.disjuncts[0].formula()
        return " ∨ ".join([Sentence.parenthesize(d.formula()) for d in self.disjuncts])

    def symbols(self):
        # Retorna el conjunto de todos los símbolos presentes en cada operando.
        s = set()
        for d in self.disjuncts:
            s = s.union(d.symbols())
        return s

    def __repr__(self):
        # Representación en cadena de la disyunción.
        return "Or(" + ", ".join([str(d) for d in self.disjuncts]) + ")"

class Implication(Sentence):
    def __init__(self, antecedent, consequent):
        # Valida que tanto el antecedente como el consecuente sean oraciones lógicas.
        Sentence.validate(antecedent)
        Sentence.validate(consequent)
        self.antecedent = antecedent
        self.consequent = consequent

    def evaluate(self, model):
        # Evalúa la implicación. Es falsa únicamente cuando el antecedente es True y el consecuente es False.
        return (not self.antecedent.evaluate(model)) or self.consequent.evaluate(model)

    def formula(self):
        # Devuelve la representación en fórmula de la implicación, utilizando "=>" para separar.
        ant = Sentence.parenthesize(self.antecedent.formula())
        cons = Sentence.parenthesize(self.consequent.formula())
        return f"{ant} => {cons}"

    def symbols(self):
        # Retorna el conjunto de símbolos presentes en el antecedente y consecuente.
        return self.antecedent.symbols().union(self.consequent.symbols())

    def __repr__(self):
        # Representación en cadena de la implicación.
        return f"Implication({self.antecedent}, {self.consequent})"

class Biconditional(Sentence):
    def __init__(self, left, right):
        # Valida que ambos operandos sean oraciones lógicas.
        Sentence.validate(left)
        Sentence.validate(right)
        self.left = left
        self.right = right

    def evaluate(self, model):
        # Evalúa el bicondicional. Devuelve True si ambos lados tienen el mismo valor.
        return self.left.evaluate(model) == self.right.evaluate(model)

    def formula(self):
        # Devuelve la fórmula del bicondicional, utilizando "<=>" para indicar equivalencia.
        left_str = Sentence.parenthesize(self.left.formula())
        right_str = Sentence.parenthesize(self.right.formula())
        return f"{left_str} <=> {right_str}"

    def symbols(self):
        # Retorna el conjunto de símbolos presentes en ambos lados.
        return self.left.symbols().union(self.right.symbols())

    def __repr__(self):
        # Representación en cadena del bicondicional.
        return f"Biconditional({self.left}, {self.right})"

def model_check(knowledge, query):
    """
    Verifica recursivamente si la base de conocimiento (knowledge) implica la consulta (query).
    
    Lógica:
      1. Se obtienen los símbolos presentes en knowledge y query.
      2. La función recursiva check_all:
         a. Si ya no hay símbolos por asignar, evalúa el modelo:
            - Si knowledge es True, retorna el valor de query.
            - Si knowledge es False, la implicación se cumple vacíamente.
         b. Si quedan símbolos, selecciona uno, asigna True y False y verifica recursivamente.
      
    Se incorpora memoización para evitar cálculos repetitivos.
    """
    symbols = knowledge.symbols().union(query.symbols())
    cache = {}
    
    def check_all(remaining_symbols, model):
        key = (frozenset(remaining_symbols), frozenset(model.items()))
        if key in cache:
            return cache[key]

        if not remaining_symbols:
            result = query.evaluate(model) if knowledge.evaluate(model) else True
            cache[key] = result
            return result

        remaining = remaining_symbols.copy()
        symbol = remaining.pop()

        model_true = model.copy()
        model_true[symbol] = True
        model_false = model.copy()
        model_false[symbol] = False

        result = check_all(remaining, model_true) and check_all(remaining, model_false)
        cache[key] = result
        return result
    
    return check_all(symbols, {})

COLORES = ["Azul", "Rojo", "Blanco", "Negro", "Verde", "Purpura"]
NUM_FICHAS = 4

def obtener_retroalimentacion(secreta, propuesta):
    """
    Calcula la retroalimentación comparando la combinación secreta con la propuesta.
    
    Retorna una tupla:
      - aciertos: cantidad de fichas en la posición correcta.
      - color_correcto: cantidad de fichas con el color correcto en posición incorrecta.
    """
    secreta = list(secreta)
    propuesta = list(propuesta)
    
    aciertos = sum(s == p for s, p in zip(secreta, propuesta))
    
    secreta_temp, propuesta_temp = [], []
    for s, p in zip(secreta, propuesta):
        if s != p:
            secreta_temp.append(s)
            propuesta_temp.append(p)
    
    color_correcto = 0
    for color in COLORES:
        color_correcto += min(secreta_temp.count(color), propuesta_temp.count(color))
    
    return aciertos, color_correcto

class MastermindSolver:
    def __init__(self, colores, num_fichas):
        self.colores = colores
        self.num_fichas = num_fichas
        self.soluciones_posibles = list(itertools.product(colores, repeat=num_fichas))
        self.intentos = []
        self.historial_soluciones = []  # Para registrar la evolución del tamaño del espacio.

    def proponer_jugada(self):
        """
        Propone la jugada óptima usando una heurística minimax simplificada:
          - Para cada posible jugada, se simula la partición de las soluciones posibles
            según la retroalimentación que se obtendría.
          - Se selecciona la jugada cuyo peor caso (el mayor grupo de soluciones) sea el mínimo.
        """
        if not self.soluciones_posibles:
            raise Exception("No quedan soluciones posibles.")
        
        if len(self.soluciones_posibles) == len(list(itertools.product(self.colores, repeat=self.num_fichas))):
            return self.soluciones_posibles[0]
        
        best_choice = None
        min_worst_case = float('inf')

        for jugada in self.soluciones_posibles:
            partitions = {}
            for sol in self.soluciones_posibles:
                feedback = obtener_retroalimentacion(sol, jugada)
                partitions[feedback] = partitions.get(feedback, 0) + 1
            worst = max(partitions.values())
            if worst < min_worst_case:
                min_worst_case = worst
                best_choice = jugada
        
        return best_choice if best_choice is not None else self.soluciones_posibles[0]

    def actualizar_soluciones(self, jugada, retroalimentacion):
        """
        Filtra las soluciones posibles manteniendo aquellas que producirían la misma retroalimentación
        si se comparara con la jugada propuesta.
        """
        nuevas_soluciones = [sol for sol in self.soluciones_posibles if obtener_retroalimentacion(sol, jugada) == retroalimentacion]
        self.soluciones_posibles = nuevas_soluciones
        self.historial_soluciones.append(len(self.soluciones_posibles))

def modo_automatico(secreta):
    """
    Modo Automático:
      - Recibe la combinación secreta.
      - Resuelve el juego de forma autónoma utilizando la heurística para elegir jugadas.
      - Muestra en cada intento la jugada propuesta, la retroalimentación y el número de soluciones restantes.
      - Al finalizar, muestra la evolución del espacio de búsqueda.
    """
    solver = MastermindSolver(COLORES, NUM_FICHAS)
    intentos = 0
    print("Modo Automático iniciado.")
    print("Combinación secreta:", secreta)
    
    while True:
        jugada = solver.proponer_jugada()
        intentos += 1
        feedback = obtener_retroalimentacion(secreta, jugada)
        print(f"Intento {intentos}: Propuesta: {jugada} -> Retroalimentación: {feedback}, soluciones restantes: {len(solver.soluciones_posibles)}")
        if feedback[0] == NUM_FICHAS:
            print(f"¡Solución encontrada en {intentos} intentos!")
            break
        solver.actualizar_soluciones(jugada, feedback)
    
    print("\nEvolución del número de soluciones posibles:")
    print(solver.historial_soluciones)

def modo_interactivo():
    """
    Modo Interactivo:
      - El agente propone una jugada.
      - El usuario ingresa la retroalimentación (dos números separados por espacio).
      - Se repite el proceso hasta que se encuentre la solución.
    """
    solver = MastermindSolver(COLORES, NUM_FICHAS)
    intentos = 0
    print("Modo Interactivo iniciado.")
    print("Responde con dos números separados por espacio: [aciertos exactos] [color correcto en posición equivocada].")
    print("Para salir, ingresa 'salir'.")
    
    while True:
        jugada = solver.proponer_jugada()
        intentos += 1
        print(f"Intento {intentos}: Propuesta: {jugada}")
        entrada = input("Ingresa la retroalimentación (ejemplo '2 1'): ").strip()
        if entrada.lower() == "salir":
            print("Terminando el juego...")
            break
        try:
            aciertos, color_correcto = map(int, entrada.split())
        except ValueError:
            print("Formato incorrecto. Asegúrate de ingresar dos números separados por espacio.")
            continue
        
        feedback = (aciertos, color_correcto)
        if aciertos == NUM_FICHAS:
            print(f"¡Solución encontrada en {intentos} intentos!")
            break
        solver.actualizar_soluciones(jugada, feedback)
        print(f"Soluciones restantes: {len(solver.soluciones_posibles)}\n")

if __name__ == "__main__":
    print("Seleccione el modo de ejecución:")
    print("1. Modo Automático")
    print("2. Modo Interactivo")
    opcion = input("Ingrese 1 o 2: ").strip()
    
    if opcion == "1":
        print("\nModo Automático")
        print("Ingrese la combinación secreta. Separe los colores con espacio (opciones: " + ", ".join(COLORES) + ").")
        entrada = input("Ejemplo: Rojo Azul Blanco Negro: ").strip().split()
        if len(entrada) != NUM_FICHAS:
            print(f"Error: Debe ingresar {NUM_FICHAS} colores.")
        else:
            secreta = tuple(entrada)
            modo_automatico(secreta)
    elif opcion == "2":
        print("\nModo Interactivo")
        modo_interactivo()
    else:
        print("Opción no válida. Terminando el programa.")
