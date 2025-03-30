from typing                 import Any, Dict, List, Optional
from fastapi                import FastAPI, HTTPException, Request, Body
from fastapi.responses      import JSONResponse
from fastapi.openapi.models import Response
from pydantic               import BaseModel, Field, field_validator
from typing                 import List, Optional
from datetime               import datetime     
from bs4                    import BeautifulSoup
import uvicorn
import logging
import pickle 
import time
import pandas as pd
import numpy  as np



app     = FastAPI(
                    title       = "Search for competitors",
                    description = f"Сервис для поиска конкурентов ",
                    version     = "1.0.0",
                 )

    
# Обработка недоступных страниц
@app.exception_handler(404)
async def not_found(request: Request, exc: HTTPException):
    return JSONResponse(
                            status_code=404,
                            content={"error": "Not found"},
                        )


@app.get("/find_competitors")
def find_competitors(request: dict = Body(..., example={
                                                        "link"   : "http://instagram.com/mtc",
                                                        "segment": "телекоммуникации"
                                                    })):

    try:
        """Получаем список данных для каждого MemberID"""
        input_json   = request
        # request      = BaseRequest(**request)   # проверка входных данных
        link         = request['link'] # распаковка данных
        segment      = request['segment']         # распаковка данных

    except Exception as e:
    
        raise HTTPException(status_code=400, detail=f"Error № 0 Ошибка валидации данных: {str(e)}")
  
    try:      
        
        return JSONResponse( {"result": "Все ок"} )
    
    except Exception as e:
        
        return JSONResponse({'result' : 'Ошибка'})
    

if __name__ == "__main__":

    uvicorn.run(app, host = '0.0.0.0', port=8000)
