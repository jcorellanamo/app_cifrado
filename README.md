Cifrado Secreto César

Microservicio FastAPI para codificar/decodificar texto usando un Cifrado César con desplazamiento fijo +5 (y −5 al decodificar).
Incluye UI web mínima y API REST. Soporta A–Z, a–z, Ñ/ñ y 0–9 (rotación circular).
Los espacios, tildes (á, é, í, ó, ú, ü) y signos de puntuación se preservan.

⚠️ Nota: El cifrado César es educativo y no es criptografía segura para usos sensibles.

🚀 Características

Alfabeto español con Ñ/ñ en la posición correcta (ABCDEFGHIJKLMNÑOPQRSTUVWXYZ).

Rotación de dígitos 0–9.

UI web lista para usar.

API REST (/encode, /decode) en métodos GET/POST.

Endpoint de salud: /healthz.

Listo para Docker (Dockerfile + docker-compose).

Permite CORS (orígenes * por defecto).

📁 Estructura
cesar-es/
├─ app/
│  └─ main.py
├─ requirements.txt
├─ Dockerfile
└─ docker-compose.yml

🧑‍💻 Correr en local (Windows / Linux / macOS)
Requisitos

Python 3.10+ (recomendado 3.12)

pip

Paso a paso (con entorno virtual)
# 1) Crear entorno
python -m venv .venv
# Windows:
# .\.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate

# 2) Instalar dependencias
pip install -r requirements.txt

# 3) Ejecutar (si main.py está en app/)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8082

Probar

UI: http://127.0.0.1:8082/

Salud: http://127.0.0.1:8082/healthz

API:

GET /encode?text=Hola%20Se%C3%B1or%20123

POST /encode { "text": "Hola Señor 123" }

GET /decode?text=Mtpf%20Xjstw%20678

POST /decode { "text": "Mtpf Xjstw 678" }

🐳 Docker
Build & Run (simple)
# desde la raíz del repo
docker build -t cesar-es:latest .
docker run -d --name cesar-es \
  -p 8082:8000 \
  -e TZ=America/Santiago \
  --restart unless-stopped \
  cesar-es:latest

docker-compose (recomendado)
docker compose up -d --build


Por defecto expone la app en http://<IP>:8082/.

🌐 Endpoints

GET / → UI web

GET /healthz → { "status": "ok" }

GET /encode?text=... → { "result": "..." }

POST /encode → body JSON { "text": "..." }

GET /decode?text=... → { "result": "..." }

POST /decode → body JSON { "text": "..." }

🔧 Configuración

Puerto host: 8082 (puedes cambiarlo)

TZ (opcional): TZ=America/Santiago

🛡️ Producción (opcional)
Healthcheck + Autoheal

Mantiene el contenedor siempre saludable y lo reinicia si falla.

# Relanzar el servicio con healthcheck
docker rm -f cesar-es 2>/dev/null || true
docker run -d --name cesar-es \
  -p 8082:8000 \
  -e TZ=America/Santiago \
  --health-cmd='python -c "import urllib.request,sys,socket; socket.setdefaulttimeout(3); sys.exit(0) if urllib.request.urlopen(\"http://127.0.0.1:8000/healthz\").getcode()==200 else sys.exit(1)"' \
  --health-interval=30s --health-timeout=5s --health-retries=3 --health-start-period=10s \
  --label autoheal=true \
  --restart unless-stopped \
  cesar-es:latest

# Contenedor autoheal
docker rm -f autoheal 2>/dev/null || true
docker run -d --name autoheal \
  -e AUTOHEAL_CONTAINER_LABEL=all \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --restart unless-stopped \
  willfarrell/autoheal

Nginx como reverse proxy (ruta /cesar/)
server {
    listen 80;
    server_name _;

    location /cesar/ {
        proxy_pass         http://127.0.0.1:8082/;
        proxy_http_version 1.1;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 5s;
        proxy_send_timeout 30s;
    }
}

Blue/Green (actualizaciones sin caída)
# construir nueva imagen
docker build -t cesar-es:latest .

# levantar v2 en otro puerto
docker run -d --name cesar-es-v2 \
  -p 8502:8000 \
  --restart unless-stopped \
  cesar-es:latest

# probar en 8502... y luego cambiar
docker rm -f cesar-es
docker rename cesar-es-v2 cesar-es

🧪 Ejemplos

Entrada: Hola Señor 123
Encode (+5) → Mtpf Xjstw 678
Decode (−5) → Hola Señor 123

Las letras con tilde y signos se preservan. Ñ/ñ rota correctamente dentro del alfabeto español.

🆘 Troubleshooting

El contenedor reinicia en bucle y ves:

RuntimeError: Form data requires "python-multipart" to be installed.


➜ Asegúrate de tener python-multipart en requirements.txt y reconstruye la imagen:

echo "python-multipart==0.0.9" >> requirements.txt
docker build --no-cache -t cesar-es:latest .
docker run -d --name cesar-es -p 8082:8000 cesar-es:latest


ERR_CONNECTION_TIMED_OUT desde fuera:

Verifica que el host escucha: ss -ltnp | grep :8082

Prueba local: curl http://127.0.0.1:8082/healthz

Abre firewall (UFW):

ufw status
ufw allow 8082/tcp
ufw reload


Revisa reglas de red del proveedor (Security Groups): permitir TCP 8082 entrante.

Puerto ocupado:

Cambia el mapeo -p 8082:8000 por otro (e.g. -p 8502:8000) o ajusta docker-compose.yml.

Cambiaste el código y no refleja:

En Docker, reconstruye/relanza:

docker build -t cesar-es:latest .
docker rm -f cesar-es
docker run -d --name cesar-es -p 8082:8000 cesar-es:latest

📄 Licencia

MIT (Massachusetts Institute of Technology).
