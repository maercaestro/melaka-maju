import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title='Melaka Maju',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in os.getenv('FRONTEND_ORIGIN','http://localhost:5173').split(',') if x.strip()],allow_methods=['GET','POST'],allow_headers=['Content-Type','Authorization'])
@app.get('/api/health')
def health(): return {'status':'ok'}
from fastapi.responses import JSONResponse
from .data.opendosm import DataUnavailable
from .api import overview,rankings,trends,compare,datasets,labour
@app.exception_handler(DataUnavailable)
async def unavailable(request,exc):
    return JSONResponse(status_code=503,content={'detail':str(exc)})
for module in (overview,rankings,trends,compare,datasets,labour):
    app.include_router(module.router,prefix='/api')
