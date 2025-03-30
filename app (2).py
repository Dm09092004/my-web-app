from typing                 import Any, Dict, List, Optional
from fastapi                import FastAPI, HTTPException, Request, Body
from fastapi.responses      import JSONResponse
from fastapi.openapi.models import Response
from pydantic               import BaseModel, Field, field_validator
from typing                 import List, Optional
from datetime               import datetime    
from concurrent.futures              import ThreadPoolExecutor
from nltk.corpus                     import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise        import cosine_similarity
from sklearn.cluster                 import KMeans
from sklearn.metrics.pairwise        import cosine_similarity

import requests
import vk_api
import re
import time
import uvicorn
import logging
import nltk
import pymorphy2

app = FastAPI(
    title="Search for competitors",
    description="Сервис для поиска конкурентов",
    version="1.0.0",
)

@app.exception_handler(404)
async def not_found(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found"},
    )

@app.post("/find_competitors")
def find_competitors(request: dict = Body(..., example={
    "link": "http://instagram.com/mtc",
    "segment": "телекоммуникации"
})):
    try:
        group_url = request['link']
        query = request['segment']
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка валидации данных: отсутствует ключ {str(e)}")

    try:
        links = [group_url] + search_vk_groups(query, count=10)

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(get_group_data, links))

        processed_text = [res for res in results if res]
        
        if not processed_text:
            raise HTTPException(status_code=404, detail="Нет доступных данных для анализа")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения данных из ВК: {str(e)}")

    try:
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(processed_text)
        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(X)

        similarities = cosine_similarity(X[0], X).flatten()
        similar_indices = similarities.argsort()[-5:][::-1]
        result = [links[i] for i in similar_indices]
        
        return JSONResponse({"result": result})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при кластеризации или расчете сходства: {str(e)}")

def get_vk_group_id(group_url, access_token):
    group_name = group_url.split('/')[-1]
    api_url = f"https://api.vk.com/method/groups.getById?group_id={group_name}&access_token={access_token}&v=5.131"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        if 'response' in data:
            return data['response'][0]['id']
        else:
            raise Exception("Сообщество не найдено")
    else:
        raise Exception("Не удалось выполнить запрос")

def search_vk_groups(query, count=10):
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    groups = vk.groups.search(q=query, count=count)

    links = []
    for group in groups["items"]:
        group_id = group['id']
        group_link = f"https://vk.com/club{group_id}"
        links.append(group_link)
    return links

def get_group_data(link):
    try:
        group_id = get_vk_group_id(link, API_KEY)
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        group_info = vk.groups.getById(group_id=group_id, fields=['description'])[0]['description']
        time.sleep(0.1)

        posts = vk.wall.get(owner_id=-group_id, count=10)
        hashtags = []
        for post in posts["items"]:
            hashtags += re.findall(r"#\w+", post["text"])
        hashtags = list(set(hashtags))
        description = group_info + " " + ", ".join(hashtags)
        return preprocess_text(description)

    except Exception as e:
        print(f"Ошибка с {link}: {e}")
        return None

def preprocess_text(text):
    text = re.sub(r'\W+', ' ', text.lower())
    words = text.split()
    words = [morph.parse(word)[0].normal_form for word in words if word not in stop_words]
    result = ' '.join(words)
    
    return result


# Обработка недоступных страниц
@app.exception_handler(404)
async def not_found(request: Request, exc: HTTPException):
    return JSONResponse(
                            status_code=404,
                            content={"error": "Not found"},
                        )


@app.post("/find_competitors")
def find_competitors(request: dict = Body(..., example={
                                                        "link"   : "https://vk.com/mts",
                                                        "segment": "телекоммуникации"
                                                    })):

    try:
        """Получаем список данных для каждого MemberID"""
        input_json   = request
        # request      = BaseRequest(**request)   # проверка входных данных
        group_url         = request['link'] # распаковка данных
        query      = request['segment']         # распаковка данных

    except Exception as e:
    
        raise HTTPException(status_code=400, detail=f"Error № 0 Ошибка валидации данных: {str(e)}")

    try:
        links      = [group_url] + search_vk_groups(query, count=10)

        # Обработаем описание группы
        processed_text = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:  # 5 потоков
            results = list(executor.map(get_group_data, links))
        
        # Очищаем результаты от None
        processed_text = [res for res in results if res]
    except Exception as e:
    
        raise HTTPException(status_code=500, detail=f"Error № 1 Проблемы с получение данных из вк: {str(e)}")
    try:
        # Пример с описаниями нескольких групп
        vectorizer = TfidfVectorizer()
        model = vectorizer.fit_transform(processed_text)
        return JSONResponse( {"result": X} )
        kmeans = KMeans(n_clusters=5, random_state=42)
        labels = kmeans.fit_predict(X)

    except Exception as e:
    
        raise HTTPException(status_code=500, detail=f"Error № 2 Проблемы с кластеризацией: {str(e)}")
    try:    
        # Вычисляем схожесть с первым сообществом
        similarities = cosine_similarity(model[0], model).flatten()
        similar_indices = similarities.argsort()[-5:][::-1]  # Топ-5 похожих
        result = []
        for i in similar_indices:
            result.append(links[i])
        return JSONResponse( {"result": result} )
    
    except Exception as e:
    
        raise HTTPException(status_code=500, detail=f"Error № 3 Проблемы с рассчтеом расстояний: {str(e)}")


if __name__ == "__main__":
    API_KEY = 'd5c4f4b2d5c4f4b2d5c4f4b29cd6eafbecdd5c4d5c4f4b2b22316f4f109a2c5e8405368'
    token  ='vk1.a.fcQFAedQdiLTZZSpZCrhxn6cB2Efle5HM7OOWQXktiJf4PucaolNbwC9t9ZemBFce28tbFeSEKkVwnHxk_FtPlj3kkT5UrXXEv12SvMFNA6Av3zHGhboJxUVXrKf1DiS4OY8HBq96N__s69UP0DoF78E6wDT6FhoIRLZBbq3OmnnidRzCemvY3UD1ijnDao1fx9P2WSoQPDNbr0-d9z28Q'
    nltk.download('stopwords')
    morph = pymorphy2.MorphAnalyzer()
    stop_words = set(stopwords.words('russian'))

    uvicorn.run(app, host = '0.0.0.0', port=8000)
