from fastapi import FastAPI
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
import os 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all frontends
    allow_credentials=True,
    allow_methods=["*"], # GET, POST, PUT, DELETE
    allow_headers=["*"]
)

con = mysql.connector.connect(
    host=os.getenv("db_host"),
    user=os.getenv("db_user"),
    password=os.getenv("db_password"),
    database=os.getenv("db_name"),
    port=os.getenv("db_port")
)

cursor_obj = con.cursor(dictionary=True)

cursor_obj.execute(""" 
create table if not exists expenses(
    expense_id int primary key auto_increment,
    title varchar(200),
    amount float,
    category varchar(100),
    payment_method varchar(100),
    expense_date DATE,
    description text
)
""")

con.commit()

@app.post("/add_expense")
def add_expense(playload: dict):
    
    query = """ 
    insert into expenses
    (title,amount,category,payment_method,expense_date,description)
    values(%s,%s,%s,%s,%s,%s)
    """
    
    values = (
        playload["title"],
        playload["amount"],
        playload["category"],
        playload["payment_method"],
        playload["expense_date"],
        playload["description"]
    )
    
    cursor_obj.execute(query,values)
    con.commit()
    
    return{
        "message": "Expense Added Successfully"
    }
    
@app.get("/get_expenses")
def get_expenses():
    query = """ 
    select * 
    from expenses
    order by expense_id desc
    """
    
    cursor_obj.execute(query)
    data = cursor_obj.fetchall()
    return {
        "expenses": data
}
    
@app.get("/get_single_expense/{expense_id}")
def get_single_expense(expense_id: int):

    query = """
    SELECT *
    FROM expenses
    WHERE expense_id = %s
    """

    cursor_obj.execute(query, (expense_id,))
    data = cursor_obj.fetchone()
    if data:
        return {
            "expense": data
        }

    return {
        "message": "Expense Not Found"
    }
        
@app.put("/update_expense/{expense_id}")
def update_expense(expense_id: int, payload: dict):

    query = """
    UPDATE expenses
    SET
        title=%s,
        amount=%s,
        category=%s,
        payment_method=%s,
        expense_date=%s,
        description=%s
    WHERE expense_id=%s
    """

    values = (
        payload["title"],
        payload["amount"],
        payload["category"],
        payload["payment_method"],
        payload["expense_date"],
        payload["description"],
        expense_id
    )

    cursor_obj.execute(query, values)
    con.commit()

    return {
        "message": "Expense Updated Successfully"
    }
    
@app.delete("/delete_expense/{expense_id,}")
def delete_expense(expense_id: int):
    query = """ 
    delete from expenses
    where expense_id = %s
    """
    
    cursor_obj.execute(query, (expense_id,))
    con.commit()
    
    return {
        "message": "Expense deleted Successfilly"
    }
    
@app.get("/expense_summary")
def expense_summary():

    query = """
    SELECT
        category,
        SUM(amount) as total_amount
    FROM expenses
    GROUP BY category
    """

    cursor_obj.execute(query)

    data = cursor_obj.fetchall()

    return {
        "summary": data
    }

