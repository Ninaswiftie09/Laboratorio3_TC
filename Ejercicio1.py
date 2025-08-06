import os
from graphviz import Digraph
import re  

# Función para tokenizar una expresión regular (infix)
def tokenize(expr):
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        if expr[i] == '\\':  
            if i + 1 < n:
                tokens.append(expr[i:i+2])
                i += 2
            else:
                tokens.append(expr[i])
                i += 1
        else:
            tokens.append(expr[i])
            i += 1
    return tokens

# Determina si un token es un operando válido (no operador)
def is_operand(token):
    if len(token) == 2 and token.startswith('\\'):
        return True
    if len(token) == 1:
        if token not in ['*', '+', '?', '|', '(', ')', '.']:
            return True
    return False

# Inserta operadores de concatenación '.' donde sean necesarios
def insert_concatenation(tokens):
    if not tokens:
        return []
    new_tokens = []
    n = len(tokens)
    for i in range(n - 1):
        t1 = tokens[i]
        t2 = tokens[i+1]
        new_tokens.append(t1)
        cond1 = is_operand(t1) or t1 in ['*', '+', '?'] or t1 == ')'
        cond2 = is_operand(t2) or t2 == '('
        if cond1 and cond2:
            new_tokens.append('.')
    new_tokens.append(tokens[-1])
    return new_tokens

# Diccionario de operadores con su precedencia y asociatividad
OPERATORS = {
    '*': (3, 'right'),
    '+': (3, 'right'),
    '?': (3, 'right'),
    '.': (2, 'left'),
    '|': (1, 'left')
}

# Algoritmo de Shunting Yard para convertir infix a postfix
def shunting_yard(tokens):
    output = []
    stack = []
    steps = []  # Para rastrear cada paso 

    steps.append(("Inicio", output[:], stack[:]))

    for token in tokens:
        if token == '(':
            stack.append(token)
            steps.append((f"Token '{token}': push '(' a pila", output[:], stack[:]))
        elif token == ')':
            popped = False
            while stack and stack[-1] != '(':
                op = stack.pop()
                output.append(op)
                steps.append((f"Token '{token}': pop '{op}' a salida", output[:], stack[:]))
                popped = True
            if stack and stack[-1] == '(':
                stack.pop()
                steps.append((f"Token '{token}': pop '(' de pila", output[:], stack[:]))
            elif not popped:
                steps.append((f"Token '{token}': no se encontro '('", output[:], stack[:]))
        elif token in OPERATORS:
            prec_token, assoc_token = OPERATORS[token]
            while stack and stack[-1] != '(':
                top = stack[-1]
                if top not in OPERATORS:
                    break
                prec_top, assoc_top = OPERATORS[top]
                if (prec_top > prec_token) or (prec_top == prec_token and assoc_token == 'left'):
                    op = stack.pop()
                    output.append(op)
                    steps.append((f"Token '{token}': pop '{op}' a salida", output[:], stack[:]))
                else:
                    break
            stack.append(token)
            steps.append((f"Token '{token}': push a pila", output[:], stack[:]))
        else:
            output.append(token)
            steps.append((f"Token '{token}': push a salida", output[:], stack[:]))

    # Vacía la pila restante
    while stack:
        if stack[-1] == '(':
            steps.append(("Error: '(' sin cerrar", output[:], stack[:]))
            stack.pop()
        else:
            op = stack.pop()
            output.append(op)
            steps.append((f"Fin: pop '{op}' a salida", output[:], stack[:]))

    return output, steps

# Clase nodo del árbol sintáctico
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

# Construye el árbol sintáctico desde la expresión en postfix
def postfix_to_syntax_tree(postfix):
    stack = []
    for token in postfix:
        if token not in OPERATORS:
            stack.append(Node(token))  # Si es operando, lo mete como nodo
        else:
            node = Node(token)
            if token in ['*', '+', '?']:  # Operadores unarios
                node.left = stack.pop()
            else:  # Operadores binarios
                node.right = stack.pop()
                node.left = stack.pop()
            stack.append(node)
    return stack.pop()  # Devuelve la raíz del árbol

# Imprime el árbol sintáctico de manera jerárquica
def print_syntax_tree(node, level=0):
    if node is not None:
        print_syntax_tree(node.right, level + 1)
        print("   " * level + f"-> {node.value}")
        print_syntax_tree(node.left, level + 1)

# Convierte el árbol a formato Graphviz 
def syntax_tree_to_graphviz(node):
    dot = Digraph()
    def add_nodes_edges(node):
        if node is not None:
            dot.node(str(id(node)), node.value)
            if node.left:
                dot.edge(str(id(node)), str(id(node.left)))
                add_nodes_edges(node.left)
            if node.right:
                dot.edge(str(id(node)), str(id(node.right)))
                add_nodes_edges(node.right)
    add_nodes_edges(node)
    return dot

# Función principal del programa
def main():
    input_file = "expresiones.txt"
    
    if not os.path.exists(input_file):
        print(f"Error: El archivo '{input_file}' no existe en la carpeta actual.")
        return

    try:
        with open(input_file, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"XXX Error al leer el archivo: {e}")
        return

    for expr in lines:
        print("\n" + "="*50)
        print(f"<> Procesando Expresion: '{expr}'")
        print("="*50)

        # Paso 1: Tokenización
        tokens = tokenize(expr)
        print("\n> 1. Tokenizacion:")
        print(f"   ➡ Tokens: {tokens}")

        # Paso 2: Inserta los puntos de concatenación
        tokens_concatenated = insert_concatenation(tokens)
        print("\n> 2. Insercion de concatenacion:")
        print(f"   ➡ Tokens con concatenacion: {tokens_concatenated}")

        # Paso 3: Infix a Postfix
        postfix, steps = shunting_yard(tokens_concatenated)
        print("\n> 3. Postfix:")
        print(f"   ➡ Notacion Postfix: {' '.join(postfix)}")

        # Paso 4: Construcción del árbol sintáctico
        print("\n> 4. Sintax Tree:")
        syntax_tree = postfix_to_syntax_tree(postfix)
        print_syntax_tree(syntax_tree)

        # Paso 5: Dibujar árbol usando Graphviz
        dot = syntax_tree_to_graphviz(syntax_tree)

        # Sanitiza el nombre para el archivo .png
        safe_expr = re.sub(r'[\\/*?:"<>|()\s+]', '_', expr)
        filename = f"syntax_tree_{safe_expr}"
        dot.render(filename, format="png", cleanup=True)

        print(f"   ➡ El arbol sintactico se ha guardado como '{filename}.png'.")
        print(f"   ➡ El arbol sintactico se ha guardado como 'syntax_tree_{expr.replace(' ', '_')}.png'.")

        # Paso 6: Mostrar todos los pasos del Shunting Yard
        print("\n> 5. Pasos del Algoritmo Shunting-Yard:")
        for i, (desc, out, stk) in enumerate(steps):
            print(f"   #Paso {i+1}: {desc}")
            print(f"      ➡ Salida: {out}")
            print(f"      ➡ Pila: {stk}")

        # Pregunta si seguir con la siguiente expresión
        while True:
            user_input = input("\n¿Continuar con la siguiente expresion? (s/n): ").strip().lower()
            if user_input == 's':
                break
            elif user_input == 'n':
                print("\n Ejecucion terminada por el usuario.")
                return
            else:
                print("Entrada no valida. Ingresa 's' para continuar o 'n' para terminar.")

# Para ejecutar el programa
if __name__ == "__main__":
    main()
