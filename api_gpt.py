import difflib
import openai
import re
from src.config import settings

openai_api_key = settings.GPT_KEY

def define_category_from_specialties(categories_list: list[str], category_services_list: dict, services_text: str, about: str):

    prompt = f"""
    У тебя есть список услуг специалиста:
    <\"{services_text}\"> 
    и описание специалиста: 
    <\"{about}\">

    В database есть список доступных категорий:
    {categories_list}
    
    В database есть список услуг и к какой категории они относятся:
    {category_services_list} 
    
    В списке услуг может быть: название типа работ и название услуги, название категории.
    В опсании специалиста может быть: название типа работ и название услуги, название категории.
    
    1.Определи, к какой одной из этих категорий относится специалист.
    Если ни одна не подходит — предложи новую.
    Верни только название категории из списка или новую одним словосочетанием.
    Категория может быть только одна.
    
    2. На основе списка услуг и информации о специалисте определи список услуг специалиста
       (Например: сантехник, электрик, курьер, медсестра, визажист), т.е. список услуг для категории
       исправь грамматические ошибки, если они есть. приведи к нижнему регистру.

    3. На основе списка услуг и информации о специалисте определи список видов работ
       исправь граматтические ошибки, если они есть. приведи к нижнему регистру
       
       
    Выведи результат в виде словаря:
        "category": "category_name",
        "services": ["specialty1", "specialty2"],
        "work_types": ["work_type1", "work_type2"]
    """


    # return prompt

    return {
      "category": "Красота",
      "services": ["визаж", "макияж"],
      "work_types": ["укладка волос", "локоны", "прическа", "выезд на дом"]
    }



    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return resp.choices[0].message["content"].strip()
