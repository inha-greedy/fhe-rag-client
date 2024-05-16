from fastapi import APIRouter, Form


from ..services.chat import send_query_and_receive_encrypted_similarity
from ..services.generate import generate_answer
from ..services.storage import set_content, get_content

chat_router = APIRouter()


@chat_router.post("/chat")
async def chat(query: str = Form(...), step: int = Form(...)):

    if step == 1:
        # send embed query to storage-server, and... receive encrypted similarity

        encrypted_similarity = send_query_and_receive_encrypted_similarity(query=query)
        set_content("c1", encrypted_similarity)

        return encrypted_similarity

    elif step == 2:

        encrypted_similarity = get_content("c1")

        # decrypt similarity

        similarity = ""

        set_content("c2", similarity)

    elif step == 3:

        similarity = get_content("c2")

        # send similarity, and... receive pure context

        context = None
        set_content("c3", context)

    elif step == 4:
        # make RAG prompt, request generation, and... get answer

        context = get_content("c3")
        if context is None:
            context = """주간예보 도움말최저  최고 기준
오늘
5.16.
오전
10%
 구름많음 오후
0%
 맑음	
최저기온10° / 최고기온18°


내일
5.17.
0%
 맑음 
0%
 맑음	
최저기온13° / 최고기온22°


토
5.18.
0%
 맑음 
0%
 맑음	
최저기온15° / 최고기온23°
일
5.19.
10%
 맑음 
10%
 맑음	
최저기온15° / 최고기온24°
월
5.20.
10%
 맑음 
10%
 맑음	
최저기온16° / 최고기온24°
화
5.21.
10%
 맑음 
10%
 맑음	
최저기온15° / 최고기온25°
수
5.22.
10%
 맑음 
10%
 맑음	
최저기온16° / 최고기온24°
목
5.23.
10%
 맑음 
10%
 맑음	
최저기온16° / 최고기온23°
금
5.24.
30%
 구름많음 
30%
 구름많음	
최저기온16° / 최고기온23°
토
5.25.
30%
 구름많음 
30%
 구름많음	
최저기온16° / 최고기온23°"""

        answer = generate_answer(query, context)

        return {"answer": answer}

    return "OK"
