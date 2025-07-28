# app.py ---------------------------------------------------------------
import contextlib
from fastapi import FastAPI
from fastmcp import FastMCP

# ────────────────── 1.  Servidores MCP ────────────────────────────────
sum_mcp = FastMCP("SumMCP")

@sum_mcp.tool(description="Suma dos enteros")
def sum_two_numbers(a: int, b: int) -> int:
    return a + b

sub_mcp = FastMCP("SubMCP")

@sub_mcp.tool(description="Resta b de a")
def sub_two_numbers(a: int, b: int) -> int:
    return a - b

# ────────────────── 2.  Apps ASGI para Streamable‑HTTP ────────────────
#   http_app()   = sucesor de streamable_http_app()
#   path="/"     = evita el sufijo /mcp extra.
sum_app = sum_mcp.http_app(path="/")
sub_app = sub_mcp.http_app(path="/")

# ────────────────── 3.  Lifespan combinado ────────────────────────────
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with sum_app.lifespan(app):
        async with sub_app.lifespan(app):
            yield

# ────────────────── 4.  FastAPI raíz y montaje ────────────────────────
app = FastAPI(
    title="Math MCP API",
    description="Suma y resta vía MCP Streamable HTTP",
    lifespan=lifespan,
)

app.mount("/sum", sum_app)   # → http://localhost:8002/sum
app.mount("/sub", sub_app)   # → http://localhost:8002/sub

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ────────────────── 5.  Arranque ──────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
