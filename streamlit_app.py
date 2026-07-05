#to import libraries
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import datetime as dt
import seaborn as sns

# wealth goals
st.title("Wealth Goals Projection")
st.markdown("""
Welcome to this page! Here you can calculate how much annual returns % you require to achieve your desired retirement goals.

Few key notes:

1. Please enter all values in whole numbers, e.g. 22, 45, and avoid decimal points.
2. Do not input commas whilst inputting numbers in thousands, e.g. use 1000 instead of 1,000.
3. Currency is not defined here. Whatever currency you use as inputs, the final output will be based in the same currency.
""")


st.header("Tell me more about your financial goals")
current_age = int(st.number_input("Enter your current age (Input Whole Number e.g. 22): ", min_value = 0 , value = 0 , step = 1 , format = "%d"))
try:
    if current_age < 0:
        st.error("Please enter a valid age.")
except ValueError:
    st.error("Please enter a valid number.")

retirement_age = int(st.number_input("Enter your desired retirement age (Input Whole Number e.g. 45): " , min_value = 0 , value = 0 , step = 1 , format = "%d"))
try:
    if retirement_age < current_age:
        st.error("Retirement age must be greater than your current age.")
    working_years = retirement_age - current_age
except ValueError:
    st.error("Please enter a valid number.")

current_assets = float(st.number_input("Enter your current assets (including bank savings, investments, assets etc): "))
try:
    if current_assets < 0:
        st.error("Please enter a valid assets amount.")
except ValueError:
    st.error("Please enter a valid number.")

monthly_income = float(st.number_input("Enter your monthly salary (assuming gross salary i.e. pre-contribution to CPF, tax etc): "))
try:
    if monthly_income < 0:
        st.error("Please enter a valid income amount.")
except ValueError:
    st.error("Please enter a valid number.")

savings_rate = float(st.number_input("Enter your monthly savings percentage rate (input in forms of XX e.g. 20): ", min_value=0, max_value=100) / 100)
try:
    if savings_rate < 0 or savings_rate > 1:
        st.error("Please enter a valid percentage between 0 and 100.")
except ValueError:
    st.error("Please enter a valid number.")
monthly_savings = monthly_income * savings_rate

monthly_expenses = float(st.number_input("At current prices, how much monthly expenses do you need during retirement?"))
try:
    if monthly_expenses < 0:
        st.error("Please enter a positive expense amount.")
except ValueError:
    st.error("Please enter a valid number.")

st.header("Our Key Assumptions")
st.markdown("""
1. According to Straits Times, average annual salary increment is around 3% in Singapore.
2. The global average life expentancy is around 73 years old, we assume a conservative age of 99 years old for our calculations.
3. We assume the average inflation is around 3% annually.
""")

annual_income = monthly_income * 12
annual_savings = annual_income * savings_rate
annual_expenses = monthly_expenses * 12
retirement_years = 99 - retirement_age
inflation_assumption = 0.03
annual_salary_increment = 0.03

def build_financial_table(current_age, retirement_age, current_assets, annual_income, annual_salary_increment,savings_rate, annual_expenses , required_return):

    rows = []
    total_assets = current_assets
    portfolio_return = float(required_return) / 100
    for age in range(current_age, life_expectancy +1):
        row = {}
        row["Age"] = age
        if age < retirement_age:
            annual_savings = annual_income * savings_rate
            row["Annual Income"] = annual_income
            row["Annual Savings"] = annual_savings
            total_assets = (total_assets + annual_savings) * (1 + portfolio_return)
            row["Annual Retirement Expenses"] = np.nan
            annual_income = annual_income * (1 + annual_salary_increment)
        else:
            annual_savings = 0
            row["Annual Income"] = np.nan
            row["Annual Savings"] = np.nan
            retirement_expenses = annual_expenses * (1 + inflation_assumption) ** (age - current_age)
            row["Annual Retirement Expenses"] = retirement_expenses
            total_assets = (total_assets * (1 + portfolio_return)) - retirement_expenses

        row["Assets"] = total_assets
        rows.append(row)
        
    df = pd.DataFrame(rows)
    return df

def calculate_required_return(current_age, retirement_age, current_assets, annual_income, annual_salary_increment, savings_rate, annual_expenses):
    low = 0.0
    high = 100.0
    tolerance = 0.000001
    required_return = None

    while high - low > tolerance:
        mid = (low + high) / 2
        portfolio_return = mid
        df = build_financial_table(current_age, retirement_age, current_assets, annual_income, annual_salary_increment, savings_rate, annual_expenses, mid)
        final_assets = df.iloc[-1]["Assets"]

        if final_assets < 0:
            low = mid
        else:
            high = mid

    required_return = (low + high) / 2
    return required_return  # Convert to percentage

life_expectancy = 99

required_return = calculate_required_return(current_age, retirement_age, current_assets, annual_income, annual_salary_increment, savings_rate, annual_expenses)

st.metric("Required Annual Return:" , f"{required_return:.2f}%")
st.header("Basic Financial Table Without Big Purchases")
df = build_financial_table(current_age, retirement_age, current_assets, annual_income, annual_salary_increment, savings_rate, annual_expenses, required_return)
st.dataframe(df, width = "stretch" , height = "auto" , hide_index = "None" ,
             column_config = {"Age" : st.column_config.NumberColumn("Age",format = "%d"),
                              "Annual Income" : st.column_config.NumberColumn("Annual Income",format = "$%,.2f"),
                              "Annual Savings" : st.column_config.NumberColumn("Annual Savings",format = "$%,.2f"),
                              "Annual Retirement Expenses" : st.column_config.NumberColumn("Annual Retirement Expenses",format = "$%,.2f"),
                              "Assets" : st.column_config.NumberColumn("Assets",format = "$%,.2f")})

st.line_chart(df.set_index("Age")["Assets"] , x_label = "Age" , y_label = "Assets" , width = "stretch")
st.markdown("""
            1. The above chart shows your projected assets over your lifetime.
            2. We assume assets to be 0 by age 99 to fund your retirement expenses.
            """)

st.header("Adding Big Purchases")
st.markdown("""
            If you plan to make big purchases before retirement (e.g. buying a house, car etc), you can input the amount + age of purchase + intended loan period.
            """)
add_purchases = st.checkbox ("Do you want to add big purchases to your plan?")
big_purchases = []
if add_purchases:
    num_purchases = st.number_input("How many big purchases do you want to add? (Please input between range of 1 to 10): " , min_value = 1 , max_value = 10)
    for i in range(num_purchases):
        st.subheader(f"Big Purchase {i+1}")
        purchase_name = st.text_input(f"Enter the name of purchase {i + 1}: " , key = f"name_{i}")
        purchase_value = st.number_input(f"Enter the value of purchase {i + 1} (Input Whole Number e.g. 100000): " , min_value = 0 , key = f"value_{i}")
        purchase_age = st.number_input(f"Enter the age at which you plan to make purchase {i+1}" , min_value = current_age , max_value = life_expectancy , key = f"age_{i}")
        loan_interest = st.number_input(f"Loan interest rate % for purchase {i + 1}", min_value=0.0, key=f"interest_{i}") / 100
        loan_years = st.number_input(f"Loan length in years {i + 1}", min_value=1, max_value=50, key=f"loan_{i}")

        big_purchases.append({
            "Name": purchase_name,
            "Value": purchase_value,
            "Purchase Age": purchase_age,
            "Interest Rate": loan_interest,
            "Loan Years": loan_years
        })

def calculate_loan_payment(principal , annual_interest_rate , loan_years):
    if annual_interest_rate == 0:
        return principal / loan_years
    
    payment = principal * (annual_interest_rate * (1 + annual_interest_rate) ** loan_years) / ((1 + annual_interest_rate) ** loan_years - 1)
    return payment

def financial_table_with_purchases(current_age, retirement_age, current_assets, annual_income, annual_salary_increment,savings_rate, annual_expenses , required_return , big_purchases=None):
    rows = []
    total_assets = current_assets
    portfolio_return = float(required_return) / 100
    if big_purchases is None:
        big_purchases = []
    for age in range(current_age, life_expectancy + 1):
        row = {}
        row["Age"] = age
        annual_big_purchase_payment = 0
        for purchase in big_purchases:
            purchase_age = purchase["Purchase Age"]
            loan_years = purchase["Loan Years"]
            
            if purchase_age <= age < purchase_age + loan_years:
                annual_payment = calculate_loan_payment(purchase["Value"] , purchase["Interest Rate"] , loan_years)
                annual_big_purchase_payment += annual_payment
        row["Big Purchase Loan Payment"] = annual_big_purchase_payment
        if age < retirement_age:
            annual_savings = annual_income * savings_rate
            row["Annual Income"] = annual_income
            row["Annual Savings"] = annual_savings
            row["Annual Retirement Expenses"] = np.nan
            total_assets = (total_assets + annual_savings) * (1 + portfolio_return)
            total_assets = total_assets - annual_big_purchase_payment
            annual_income = annual_income * (1 + annual_salary_increment)
        else:
            row["Annual Income"] = np.nan
            row["Annual Savings"] = np.nan
            retirement_expenses = annual_expenses * (1 + inflation_assumption) ** (age - current_age)
            row["Annual Retirement Expenses"] = retirement_expenses
            total_assets = (total_assets * (1 + portfolio_return)) - retirement_expenses - annual_big_purchase_payment
        row["Assets"] = total_assets
        rows.append(row)
    df = pd.DataFrame(rows)
    return df

def calculate_required_return_with_big_purchase(current_age, retirement_age, current_assets, annual_income, annual_salary_increment, savings_rate, annual_expenses , big_purchases = None):
    low = 0.0
    high = 100.0
    tolerance = 0.000001
    required_return = None

    while high - low > tolerance:
        mid = (low + high) / 2
        portfolio_return = mid
        df = financial_table_with_purchases(current_age, retirement_age, current_assets, annual_income, annual_salary_increment, savings_rate, annual_expenses, mid , big_purchases)
        final_assets = df.iloc[-1]["Assets"]

        if final_assets < 0:
            low = mid
        else:
            high = mid

    required_return = (low + high) / 2
    return required_return  # Convert to percentage

required_return_with_big_purchase = calculate_required_return_with_big_purchase(current_age, retirement_age, current_assets, annual_income, annual_salary_increment, savings_rate, annual_expenses , big_purchases)
df_with_big_purchases = financial_table_with_purchases(current_age, retirement_age, current_assets, annual_income, annual_salary_increment,savings_rate, annual_expenses , required_return_with_big_purchase , big_purchases)
st.dataframe(df_with_big_purchases, width = "stretch" , height = "auto" , hide_index = "None" ,
             column_config = {"Age" : st.column_config.NumberColumn("Age",format = "%d"),
                              "Big Purchase Loan Payment" : st.column_config.NumberColumn("Big Purchase Loan Payment" , format = "$%,.2f"),
                              "Annual Income" : st.column_config.NumberColumn("Annual Income",format = "$%,.2f"),
                              "Annual Savings" : st.column_config.NumberColumn("Annual Savings",format = "$%,.2f"),
                              "Annual Retirement Expenses" : st.column_config.NumberColumn("Annual Retirement Expenses",format = "$%,.2f"),
                              "Assets" : st.column_config.NumberColumn("Assets",format = "$%,.2f")} ,
                column_order = ("Age" , "Annual Income" , "Annual Savings" , "Big Purchase Loan Payment" , "Annual Retirement Expenses" , "Assets"))
st.metric("Required Annual Return With Big Purchases:" , f"{required_return_with_big_purchase:.2f}%")
st.line_chart(df_with_big_purchases.set_index("Age")["Assets"] , x_label = "Age" , y_label = "Assets" , width = "stretch")
