# 🕵️ Análisis de Seguridad: U.S. Dept of Defense (HackerOne VDP)

## 1. Perfil del Programa
- **Plataforma:** HackerOne (https://hackerone.com/deptofdefense)
- **Tiempos de Respuesta:** Muy rápidos. El triaje suele realizarse en menos de 48 horas.
- **Recompensas:** **NO** (Es un programa VDP, no paga recompensas en dinero).
- **Valor para el Laboratorio:** Es excelente para practicar, ganar puntos de reputación en HackerOne y mejorar el "Signal Rate", lo cual abre puertas a programas privados y exclusivos que sí pagan bounties altos.

## 2. Alcance Principal (In-Scope)
El alcance de este programa incluye prácticamente toda la presencia web del Departamento de Defensa de los EE. UU. que sea accesible públicamente:
- `*.mil` (Todo subdominio público bajo esta extensión).

## 3. Reglas Críticas e Identificación de Tráfico
El DoD es sumamente estricto respecto al comportamiento ético. Sigue estas reglas:
- **Cabecera de Identificación:** Agrega en todas tus peticiones:
  ```http
  X-HackerOne-Research: tomas244
  ```
- **Prohibición de Explotación Profunda:** Si encuentras un fallo (ej: una inyección SQL o una lectura de archivos), **detente inmediatamente**. No intentes exfiltrar bases de datos ni escalar privilegios. Reporta únicamente la demostración mínima.
- **Escaneos automáticos:** Están prohibidos los escaneos masivos ruidosos (ej. escaneos agresivos de Nmap o Acunetix). Todo el análisis debe ser pasivo o manual dirigido.

## 4. Vectores de Ataque Prioritarios para nuestro Laboratorio
1. **Exposición de Archivos Sensibles:**
   - Dado el enorme volumen de servidores legacy de la red militar, es muy común encontrar configuraciones incorrectas que exponen archivos `.git`, archivos de log, carpetas `/backup` o instaladores de software expuestos.
2. **Bypasses de Autenticación:**
   - Portales web internos o consolas de administración mal configuradas que permiten omitir la autenticación básica.

## 5. Próximos Pasos de Integración
1. Aceptar los términos del programa del DoD en HackerOne.
2. Añadir `mil` al archivo `config/objetivos.txt` en el servidor OCI para que comience el monitoreo pasivo diario de subdominios `.mil`.
