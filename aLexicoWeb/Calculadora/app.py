from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Crear la carpeta static si no existe
if not os.path.exists('static'):
    os.makedirs('static')

last_result = None  # Variable para almacenar el último resultado

# Función para construir un árbol sintáctico 
def build_syntax_tree(expression):
    def parse_expr(expr):
        tokens = expr.replace('(', ' ( ').replace(')', ' ) ').split()
        return parse(tokens)

    def parse(tokens):
        if len(tokens) == 0:
            raise SyntaxError("Unexpected end of input")

        token = tokens.pop(0)
        if token == '(':
            sub_expr = []
            while tokens[0] != ')':
                sub_expr.append(parse(tokens))
            tokens.pop(0)  # Elimina ')'
            return {'operator': 'group', 'children': sub_expr}
        elif token == ')':
            raise SyntaxError("Unexpected )")
        elif token in ('+', '-', '*', '/'):
            left = parse(tokens)
            right = parse(tokens)
            return {
                'operator': token,
                'left': left,
                'right': right,
                'expression': f"({left['expression']} {token} {right['expression']})"
            }
        else:
            return {'operator': 'number', 'value': token, 'expression': token}

    return parse_expr(expression)

# Función para generar el árbol en formato JSON
def generate_tree_json(node):
    if 'left' in node and 'right' in node:
        return {
            'name': node['operator'],  # Mostrar la operación
            'children': [
                generate_tree_json(node['left']),
                generate_tree_json(node['right'])
            ]
        }
    else:
        return {'name': node['value']}  # Mostrar el valor del número

@app.route('/')
def index():
    return render_template('index.html', result='', tokens=[], syntax_tree='', last_result=last_result)

@app.route('/calculate', methods=['POST'])
def calculate():
    global last_result
    expression = request.form['expression']

    # Reemplazar "ans" por el último resultado
    if last_result is not None:
        expression = expression.replace('ans', str(last_result))

    tokens = get_tokens(expression)

    try:
        result = eval(expression)
        if isinstance(result, float) and result.is_integer():
            result = int(result)  # Convertir a entero si es un número entero
        last_result = result  # Guardar el último resultado
    except Exception as e:
        return render_template('index.html', result='Error: ' + str(e), tokens=tokens, syntax_tree='', last_result=last_result)

    return render_template('index.html', result=str(result), tokens=tokens, syntax_tree=expression, last_result=last_result)

@app.route('/tree_data', methods=['POST'])
def tree_data():
    expression = request.form['expression']
    syntax_tree = build_syntax_tree(expression)
    tree_json = generate_tree_json(syntax_tree)
    
    return jsonify(tree_json)

def get_tokens(expression):
    tokens = []
    operator_descriptions = {
        '+': 'Operador de suma',
        '-': 'Operador de resta',
        '*': 'Operador de multiplicación',
        '/': 'Operador de división',
        'tree': 'Crea un árbol sintáctico',
        'ans': 'Resultado anterior'  # Agregar descripción para 'ans'
    }

    for char in expression:
        if char.isdigit():
            tokens.append((char, 'Número'))
        elif char in operator_descriptions:
            tokens.append((char, operator_descriptions[char]))
        elif char == '.':
            tokens.append((char, 'Punto'))  
        elif char == '(':
            tokens.append((char, 'Paréntesis izquierdo'))
        elif char == ')':
            tokens.append((char, 'Paréntesis derecho'))
        else:
            tokens.append((char, 'Desconocido'))

    # Añadir 'ans' si es parte de la expresión
    if 'ans' in expression:
        tokens.append(('ans', 'Resultado anterior'))

    return tokens

if __name__ == '__main__':
    app.run(debug=True)
