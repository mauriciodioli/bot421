<<<<<<< HEAD
async function calculateResult() {
    const display = document.getElementById('display').value;
    
    // Parsear la expresión matemática para obtener los números y la operación
    const match = display.match(/^([0-9\.]+)([+\-*/])([0-9\.]+)$/);
    
    if (!match) {
        document.getElementById('display').value = 'Expresión inválida';
        return;
    }

    const num1 = match[1];
    const operacion = match[2];
    const num2 = match[3];

    try {
        const response = await fetch('/calculadora_standar_calcular', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                operacion: operacion,
                numeros: [num1, num2] // Mandamos los dos números
            })
        });

        const result = await response.json();
        document.getElementById('display').value = result.resultado || result.error;
    } catch (error) {
        document.getElementById('display').value = 'Error';
    }
}

function appendCharacter(char) {
    document.getElementById('display').value += char;
}

function clearDisplay() {
    document.getElementById('display').value = '';
}






// Función que se ejecuta cuando se presionan las teclas del teclado
document.addEventListener('keydown', function(event) {
    const display = document.getElementById('display');
    const key = event.key;

    // Verifica si la tecla presionada es un número o una operación válida
    if (key >= '0' && key <= '9') {
        appendCharacter(key); // Añadir el número al display
    } else if (key === '.') {
        appendCharacter('.'); // Añadir punto al display
    } else if (key === '+' || key === '-' || key === '*' || key === '/') {
        appendCharacter(key); // Añadir operador
    } else if (key === 'Enter') {
        calculateResult(); // Ejecutar el cálculo cuando se presiona Enter
    } else if (key === 'Backspace') {
        clearDisplay(); // Limpiar la pantalla cuando se presiona Backspace
    }
});

// Función para agregar un carácter al display
function appendCharacter(char) {
    document.getElementById('display').value += char;
}

// Función para limpiar la pantalla
function clearDisplay() {
    document.getElementById('display').value = '';
}

// Función para calcular el resultado
async function calculateResult() {
    const display = document.getElementById('display').value;
    try {
        const response = await fetch('/calculadora_standar_calcular', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ operacion: getOperation(display), numeros: getNumbers(display) })
        });

        const result = await response.json();
        document.getElementById('display').value = result.resultado || result.error;
    } catch (error) {
        document.getElementById('display').value = 'Error';
    }
}

// Función para obtener la operación de la expresión
function getOperation(expression) {
    // Buscar el primer operador en la expresión
    if (expression.includes('+')) return '+';
    if (expression.includes('-')) return '-';
    if (expression.includes('*')) return '*';
    if (expression.includes('/')) return '/';
    return '';
}

// Función para obtener los números de la expresión
function getNumbers(expression) {
    // Separar la expresión por el operador y convertir los números a tipo float
    return expression.split(/[\+\-\*\/]/).map(num => parseFloat(num));
}


















let dragArea = document.getElementById("dragArea");
let calculator = document.getElementById("calculator");

dragArea.onmousedown = function(e) {
    e.preventDefault(); // Prevenir el comportamiento predeterminado

    // Obtener la posición inicial del ratón con respecto a la calculadora
    let shiftX = e.clientX - calculator.getBoundingClientRect().left;
    let shiftY = e.clientY - calculator.getBoundingClientRect().top;

    // Función para mover la calculadora
    function moveAt(pageX, pageY) {
        calculator.style.left = pageX - shiftX + 'px';
        calculator.style.top = pageY - shiftY + 'px';
    }

    // Mover la calculadora mientras se arrastra
    document.onmousemove = function(e) {
        moveAt(e.pageX, e.pageY);
    }

    // Al soltar el botón del ratón, detener el movimiento
    document.onmouseup = function() {
        document.onmousemove = null;
        document.onmouseup = null;
    }
=======
async function calculateResult() {
    const display = document.getElementById('display').value;
    
    // Parsear la expresión matemática para obtener los números y la operación
    const match = display.match(/^([0-9\.]+)([+\-*/])([0-9\.]+)$/);
    
    if (!match) {
        document.getElementById('display').value = 'Expresión inválida';
        return;
    }

    const num1 = match[1];
    const operacion = match[2];
    const num2 = match[3];

    try {
        const response = await fetch('/calculadora_standar_calcular', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                operacion: operacion,
                numeros: [num1, num2] // Mandamos los dos números
            })
        });

        const result = await response.json();
        document.getElementById('display').value = result.resultado || result.error;
    } catch (error) {
        document.getElementById('display').value = 'Error';
    }
}

function appendCharacter(char) {
    document.getElementById('display').value += char;
}

function clearDisplay() {
    document.getElementById('display').value = '';
}






// Función que se ejecuta cuando se presionan las teclas del teclado
document.addEventListener('keydown', function(event) {
    const display = document.getElementById('display');
    const key = event.key;

    // Verifica si la tecla presionada es un número o una operación válida
    if (key >= '0' && key <= '9') {
        appendCharacter(key); // Añadir el número al display
    } else if (key === '.') {
        appendCharacter('.'); // Añadir punto al display
    } else if (key === '+' || key === '-' || key === '*' || key === '/') {
        appendCharacter(key); // Añadir operador
    } else if (key === 'Enter') {
        calculateResult(); // Ejecutar el cálculo cuando se presiona Enter
    } else if (key === 'Backspace') {
        clearDisplay(); // Limpiar la pantalla cuando se presiona Backspace
    }
});

// Función para agregar un carácter al display
function appendCharacter(char) {
    document.getElementById('display').value += char;
}

// Función para limpiar la pantalla
function clearDisplay() {
    document.getElementById('display').value = '';
}

// Función para calcular el resultado
async function calculateResult() {
    const display = document.getElementById('display').value;
    try {
        const response = await fetch('/calculadora_standar_calcular', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ operacion: getOperation(display), numeros: getNumbers(display) })
        });

        const result = await response.json();
        document.getElementById('display').value = result.resultado || result.error;
    } catch (error) {
        document.getElementById('display').value = 'Error';
    }
}

// Función para obtener la operación de la expresión
function getOperation(expression) {
    // Buscar el primer operador en la expresión
    if (expression.includes('+')) return '+';
    if (expression.includes('-')) return '-';
    if (expression.includes('*')) return '*';
    if (expression.includes('/')) return '/';
    return '';
}

// Función para obtener los números de la expresión
function getNumbers(expression) {
    // Separar la expresión por el operador y convertir los números a tipo float
    return expression.split(/[\+\-\*\/]/).map(num => parseFloat(num));
}


















let dragArea = document.getElementById("dragArea");
let calculator = document.getElementById("calculator");

dragArea.onmousedown = function(e) {
    e.preventDefault(); // Prevenir el comportamiento predeterminado

    // Obtener la posición inicial del ratón con respecto a la calculadora
    let shiftX = e.clientX - calculator.getBoundingClientRect().left;
    let shiftY = e.clientY - calculator.getBoundingClientRect().top;

    // Función para mover la calculadora
    function moveAt(pageX, pageY) {
        calculator.style.left = pageX - shiftX + 'px';
        calculator.style.top = pageY - shiftY + 'px';
    }

    // Mover la calculadora mientras se arrastra
    document.onmousemove = function(e) {
        moveAt(e.pageX, e.pageY);
    }

    // Al soltar el botón del ratón, detener el movimiento
    document.onmouseup = function() {
        document.onmousemove = null;
        document.onmouseup = null;
    }
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
};