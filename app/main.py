from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import html  # para escapar el resultado en la UI

app = FastAPI(title="Cifrado Secreto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALPHA_UP = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
ALPHA_LO = "abcdefghijklmnñopqrstuvwxyz"
DIGITS   = "0123456789"
SHIFT    = 5

def _shift_char(ch: str, k: int) -> str:
    if ch in ALPHA_UP:
        i = ALPHA_UP.index(ch)
        return ALPHA_UP[(i + k) % len(ALPHA_UP)]
    if ch in ALPHA_LO:
        i = ALPHA_LO.index(ch)
        return ALPHA_LO[(i + k) % len(ALPHA_LO)]
    if ch in DIGITS:
        i = DIGITS.index(ch)
        return DIGITS[(i + k) % len(DIGITS)]
    return ch

def _transform(text: str, k: int) -> str:
    return "".join(_shift_char(c, k) for c in text)

def encode(text: str) -> str:
    return _transform(text, SHIFT)

def decode(text: str) -> str:
    return _transform(text, -SHIFT)

class TextIn(BaseModel):
    text: str

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/encode")
def encode_get(text: str):
    return JSONResponse({"result": encode(text)})

@app.post("/encode")
def encode_post(body: TextIn):
    return JSONResponse({"result": encode(body.text)})

@app.get("/decode")
def decode_get(text: str):
    return JSONResponse({"result": decode(text)})

@app.post("/decode")
def decode_post(body: TextIn):
    return JSONResponse({"result": decode(body.text)})

# ---------- UI ----------
INDEX_HTML = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Cifrado Secreto</title>
<style>
  body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Helvetica,Arial,sans-serif;background:#0b1220;color:#e8eef8;margin:0}
  .wrap{max-width:820px;margin:0 auto;padding:24px}
  .card{background:#121a2b;border:1px solid #1f2a44;border-radius:16px;padding:20px;box-shadow:0 10px 30px rgba(0,0,0,.25)}
  h1{margin:0 0 8px;font-size:24px}
  p{opacity:.9}
  label{display:block;margin:12px 0 6px}
  textarea,input[type=text]{width:100%;padding:12px;border-radius:12px;border:1px solid #2a3a5e;background:#0e1626;color:#e8eef8}
  .row{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px;align-items:center}
  .btn{background:#2563eb;border:none;color:#fff;padding:10px 14px;border-radius:10px;cursor:pointer;font-weight:600}
  .btn.secondary{background:#334155}
  .result{margin-top:16px;padding:12px;border-radius:12px;background:#0e1626;border:1px solid #2a3a5e;display:flex;gap:10px;align-items:center}
  .label{user-select:none;opacity:.9} /* visible, pero NO se copia */
  #resultText{white-space:pre-wrap}
  .footer{opacity:.7;margin-top:16px;font-size:12px}
  .badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
  .badge{font-size:12px;background:#1f2a44;border:1px solid #2a3a5e;padding:4px 8px;border-radius:999px}
</style>
</head>
<body>
<div class="wrap">
  <div class="card">
    <h1>🔐 Cifrado Secreto</h1>
    <form method="post" action="/process">
      <label for="text">Ingrese Texto</label>
      <textarea id="text" name="text" rows="5" placeholder="Escribe aquí...">{{TEXT_VALUE}}</textarea>
      <div class="row">
        <label><input type="radio" name="mode" value="encode" {{CHECK_ENCODE}}> Codificar</label>
        <label><input type="radio" name="mode" value="decode" {{CHECK_DECODE}}> Decodificar</label>
        <button class="btn" type="submit">Procesar</button>
      </div>
    </form>

    {{RESULT_BLOCK}}

    <div class="footer">
      <div class="badges">
        <div class="badge">Incluye Ñ</div>
        <div class="badge">Incluye dígitos</div>
        <div class="badge">API REST</div>
        <div class="badge">Docker Ready</div>
      </div>
    </div>
  </div>
</div>
<script>
function ejemplo(){
  const t = document.getElementById('text'); 
  t.value = '';
  t.focus();
}
function copyResult(){
  const el = document.getElementById('resultText');
  if(!el) return;
  navigator.clipboard.writeText(el.innerText).then(()=>{}).catch(()=>{});
}
</script>
</body>
</html>
"""

def render_page(text_value: str, mode: str, result: str | None):
    # Rellena placeholders del HTML de forma segura
    page = INDEX_HTML
    page = page.replace("{{TEXT_VALUE}}", html.escape(text_value))
    page = page.replace("{{CHECK_ENCODE}}", "checked" if mode == "encode" else "")
    page = page.replace("{{CHECK_DECODE}}", "checked" if mode == "decode" else "")

    if result is None:
        page = page.replace("{{RESULT_BLOCK}}", "")
    else:
        # Resultado visible y copiable SIN el rótulo
        result_block = (
            '<div id="result" class="result">'
            '<span class="label" aria-hidden="true">Resultado:</span>'
            f'<span id="resultText">{html.escape(result)}</span>'
            '<button class="btn secondary" type="button" onclick="copyResult()">Copiar</button>'
            '</div>'
        )
        page = page.replace("{{RESULT_BLOCK}}", result_block)
    return page

@app.get("/", response_class=HTMLResponse)
def index(_: Request):
    return HTMLResponse(render_page("", "encode", None))

@app.post("/process", response_class=HTMLResponse)
async def process(_: Request, text: str = Form(...), mode: str = Form("encode")):
    out = encode(text) if mode == "encode" else decode(text)
    return HTMLResponse(render_page(text, mode, out))
