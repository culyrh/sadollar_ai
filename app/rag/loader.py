
import json
from langchain_core.documents import Document



def load_menu():
    
    # 데이터 가져오기
    with open("data/menu.json", "r", encoding="utf-8") as f:
        menus = json.load(f)
    # return menus 
    
    # 형태 변환   
    document = []
    
    for menu in menus:
        text = f"""
        {menu['name']}는 {menu['category']} 메뉴입니다.
        가격은 {menu['price']}원이고,
        맵기 수준은 {menu['spicy_level']} 단계입니다.
        {menu['description']}
        추천 상황: {', '.join(menu['tags'])}
        """.strip()
        
        doc = Document(
            page_content=text,
            metadata={
                "id": menu["id"],
                "name": menu["name"],
                "price": menu["price"],
                "spicy_level": menu["spicy_level"],
                "category": menu["category"],
            }
        )    
        
        document.append(doc)
    return document    


    
    
    

