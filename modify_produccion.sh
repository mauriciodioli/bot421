#!/bin/bash

# Modificar app.py
sed -i '/^app.run(host='\''0\.0\.0\.0'\'', port=5001, debug=True)/s/^/# /' src/app.py


echo "Configuraciones aplicadas con éxito."
