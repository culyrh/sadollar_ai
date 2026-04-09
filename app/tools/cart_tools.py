
import re
import sqlite3
from langchain.tools import tool
from app.session_context import current_session_id

DB_PATH = "data/ria_menu.db"


def _build_search_terms(normalized: str, clean_name: str) -> list[str]:
    """공백 기준 토큰 분리 + 접두어 분해로 검색어 목록을 생성한다.

    - 공백 분리: "더블 새우 버거" → ["더블", "새우", "버거"] (단어 순서 무관 검색)
    - 접두어 분해: "불고기버거" → ["불고기버거", "불고기버", "불고기"] (복합어 처리)
    - 최소 2글자 ("새우", "더블" 같은 2글자 단어 포함)
    """
    tokens = [t for t in clean_name.split() if t] or [normalized]

    terms = []
    for tok in tokens:
        terms.append(tok)
        for trim in range(1, len(tok)):
            prefix = tok[:-trim]
            if len(prefix) >= 2:
                terms.append(prefix)

    seen = set()
    return [t for t in terms if not (t in seen or seen.add(t))]

@tool
def add_to_cart(item_name: str, quantity: int = 1) -> str:
    """장바구니에 메뉴를 추가한다.

    item_name: 손님이 말한 메뉴명. 정확하지 않아도 자동으로 유사 메뉴를 찾아준다.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.create_function("REPLACE_SPACE", 1, lambda s: s.replace(" ", "") if s else s)
    cur = conn.cursor()

    # [BEST], [NEW] 등 badge 태그 제거 후 공백 정규화
    clean_name = re.sub(r'\[.*?\]', '', item_name).strip()
    normalized = clean_name.replace(" ", "")
    # 1차: 완전 일치
    cur.execute(
        "SELECT id, price, name FROM menu WHERE REPLACE_SPACE(name) = ?",
        (normalized,)
    )
    exact_row = cur.fetchone()

    if exact_row:
        rows = [exact_row]
    else:
        # 2차: 복합어 접두어 분해 후 OR LIKE 검색
        terms = _build_search_terms(normalized, clean_name)
        placeholders = " OR ".join(["REPLACE_SPACE(name) LIKE ?" for _ in terms])
        cur.execute(
            f"SELECT id, price, name FROM menu WHERE {placeholders}",
            [f"%{t}%" for t in terms],
        )
        rows = cur.fetchall()

    if not rows:
        conn.close()
        return f"'{item_name}' 메뉴를 찾을 수 없습니다."

    # 여러 메뉴가 매칭되면 선택지 반환
    if len(rows) > 1:
        conn.close()
        options = "\n".join([f"- {name} ({price}원)" for _, price, name in rows])
        return f"'{item_name}'에 해당하는 메뉴가 여러 개 있습니다. 어떤 메뉴를 원하시나요?\n{options}"

    menu_id, price_str, actual_name = rows[0]
    try:
        unit_price = int(str(price_str).replace(",", "").replace("원", "").strip())
    except ValueError:
        unit_price = 0

    cur.execute(
        "INSERT INTO cart (session_id, menu_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        (current_session_id.get(), menu_id, quantity, unit_price),
    )
    conn.commit()
    conn.close()

    return f"{actual_name} {quantity}개를 장바구니에 추가했습니다."


@tool
def view_cart() -> str:
    """장바구니에 담긴 메뉴 목록과 총 금액을 반환한다.
    손님이 "장바구니 확인", "뭐 담았어", "총 얼마야" 등을 물을 때 사용하라.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT m.name, c.quantity, c.unit_price
        FROM cart c
        JOIN menu m ON c.menu_id = m.id
        WHERE c.session_id = ?
    """, (current_session_id.get(),))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "장바구니가 비어 있습니다."

    lines = []
    total = 0
    for name, qty, unit_price in rows:
        subtotal = qty * unit_price
        total += subtotal
        lines.append(f"{name} x {qty} = {subtotal:,}원")

    lines.append(f"합계: {total:,}원")
    return "\n".join(lines)


@tool
def remove_from_cart(item_name: str) -> str:
    """장바구니에서 메뉴를 제거한다"""

    conn = sqlite3.connect(DB_PATH)
    conn.create_function("REPLACE_SPACE", 1, lambda s: s.replace(" ", "") if s else s)
    cur = conn.cursor()

    clean_name = re.sub(r'\[.*?\]', '', item_name).strip()
    normalized = clean_name.replace(" ", "")
    # 1차: 완전 일치
    cur.execute("SELECT id, name FROM menu WHERE REPLACE_SPACE(name) = ?", (normalized,))
    exact_row = cur.fetchone()

    if exact_row:
        rows = [exact_row]
    else:
        # 2차: 복합어 접두어 분해 후 OR LIKE 검색
        terms = _build_search_terms(normalized, clean_name)
        placeholders = " OR ".join(["REPLACE_SPACE(name) LIKE ?" for _ in terms])
        cur.execute(
            f"SELECT id, name FROM menu WHERE {placeholders}",
            [f"%{t}%" for t in terms],
        )
        rows = cur.fetchall()

    if not rows:
        conn.close()
        return f"'{item_name}' 메뉴를 찾을 수 없습니다."

    # 여러 메뉴가 매칭되면 선택지 반환
    if len(rows) > 1:
        conn.close()
        options = "\n".join([f"- {name}" for _, name in rows])
        return f"'{item_name}'에 해당하는 메뉴가 여러 개 있습니다. 어떤 메뉴를 취소하시겠어요?\n{options}"

    menu_id = rows[0][0]
    cur.execute("DELETE FROM cart WHERE session_id = ? AND menu_id = ?", (current_session_id.get(), menu_id))
    affected = cur.rowcount
    conn.commit()
    conn.close()

    if affected == 0:
        return f"{item_name}이 장바구니에 없습니다."
    return f"{item_name}을 장바구니에서 제거했습니다."


@tool
def confirm_order(payment_method: str = "카드") -> str:
    """장바구니를 주문 완료 처리한다.
    손님이 "주문할게요", "결제할게요", "이걸로 할게요" 등을 말할 때 사용하라.
    payment_method: 결제 수단. 기본값 카드. 카드/모바일 중 하나.
    """
    session_id = current_session_id.get()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 장바구니 조회
    cur.execute("""
        SELECT m.name, c.quantity, c.unit_price
        FROM cart c
        JOIN menu m ON c.menu_id = m.id
        WHERE c.session_id = ?
    """, (session_id,))
    rows = cur.fetchall()

    if not rows:
        conn.close()
        return "장바구니가 비어 있습니다. 먼저 메뉴를 담아주세요."

    # 총 금액 계산
    total_price = sum(qty * unit_price for _, qty, unit_price in rows)

    # orders 테이블에 저장
    cur.execute(
        "INSERT INTO orders (session_id, total_price, payment_method, status) VALUES (?, ?, ?, 'done')",
        (session_id, total_price, payment_method)
    )

    # 장바구니 비우기
    cur.execute("DELETE FROM cart WHERE session_id = ?", (session_id,))

    conn.commit()
    conn.close()

    lines = [f"{name} x{qty} = {qty * unit_price:,}원" for name, qty, unit_price in rows]
    lines.append(f"총 결제 금액: {total_price:,}원")
    lines.append("주문이 완료되었습니다. 감사합니다!")
    return "\n".join(lines)


@tool
def clear_cart() -> str:
    """장바구니를 전부 비운다.
    손님이 "다 취소해줘", "처음부터 다시 할게" 등을 말할 때 사용하라.
    """
    session_id = current_session_id.get()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM cart WHERE session_id = ?", (session_id,))
    affected = cur.rowcount
    conn.commit()
    conn.close()

    if affected == 0:
        return "장바구니가 이미 비어 있습니다."
    return "장바구니를 비웠습니다."
