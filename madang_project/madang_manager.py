
import streamlit as st
import duckdb
import pandas as pd
import time

# DuckDB 연결
con = duckdb.connect(database="data/madang.duckdb", read_only=False)

def query(sql, params=None):
    if params:
        return con.execute(sql, params).fetchdf()
    return con.execute(sql).fetchdf()

# 책 목록
books_df = query("SELECT bookid, bookname FROM Book")
books = ["선택하세요"] + [f"{row.bookid}, {row.bookname}" for _, row in books_df.iterrows()]

tab1, tab2 = st.tabs(["고객조회", "거래 입력"])

# 고객 조회
name = tab1.text_input("고객명")
if name:
    sql = """
        SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice
        FROM Customer c
        JOIN Orders o ON c.custid = o.custid
        JOIN Book b ON b.bookid = o.bookid
        WHERE c.name = ?
    """
    result = query(sql, [name])

    if len(result) == 0:
        tab1.warning("해당 고객이 없습니다.")
    else:
        tab1.write(result)
        custid = result.iloc[0]["custid"]

        tab2.write(f"고객번호: {custid}")
        tab2.write(f"고객명: {name}")

        select_book = tab2.selectbox("구매 서적:", books)

        if select_book != "선택하세요":
            bookid = int(select_book.split(",")[0])
            dt = time.strftime('%Y-%m-%d')
            price = tab2.text_input("금액", key="price")

            if tab2.button("거래 입력"):
                new_id = query("SELECT COALESCE(MAX(orderid), 0) + 1 AS id FROM Orders")["id"][0]

                con.execute(
                    """
                    INSERT INTO Orders (orderid, custid, bookid, saleprice, orderdate)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [new_id, custid, bookid, int(price), dt]
                )
                con.commit()
                tab2.success("거래가 입력되었습니다.")




