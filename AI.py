import pandas as pd
import requests
#import libarchive

from langchain_core.tools import Tool
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.agents import initialize_agent, AgentType
from langchain_core.prompts import ChatPromptTemplate

import pandas as pd
df = pd.read_csv("zamalek.dataset.csv")
#print(df)

df["Ticket_Revenue"] = (
    df["Ticket_Revenue"]
    .astype(str)
    .str.replace("EGP", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.strip()
)
df["Ticket_Revenue"] = pd.to_numeric(df["Ticket_Revenue"], errors="coerce")

df["Match_Date"] = pd.to_datetime(df["Match_Date"], errors="coerce")

df["Match_Date"] = df["Match_Date"].fillna(pd.NaT)  
df["Ticket_Revenue"] = df["Ticket_Revenue"].fillna(0)  

#df.info()

system_prompt = """
You are Zamalek AI Assistant.

Your role is to help users analyze Zamalek Sporting Club using only:
- datasets
- APIs
- provided tools
- conversation memory

You must focus ONLY on Zamalek SC.

You can answer questions about:
- Zamalek squad and players
- match statistics
- performance analysis
- club history
- tactical insights
- fan engagement
- ticketing and merchandise
- sponsorship and marketing
- business KPIs
- digital transformation of the club

---

## TOOL USAGE RULES

Always choose the correct tool:

### Dataset / Pandas Tools
Use for:
- statistics
- averages
- comparisons
- historical matches
- KPIs
- calculations

### API Tools
Use for:
- live football data
- external team information
- stadium, league, fixtures

### KPI Tools
Use for:
- revenue
- profit
- attendance
- business performance

### Memory
Use for:
- follow-up questions
- previous context

---

## IMPORTANT RULES

- Do NOT provide information outside Zamalek SC.
- Do NOT invent numbers or statistics.
- Only use tools, datasets, APIs, or memory.
- If data is not available, respond exactly:
"The information is not available."

---

## RESPONSE STYLE

- Be concise and data-driven
- Act like a professional sports data analyst for Zamalek SC
- Always prioritize accuracy over explanation
"""

#print(system_prompt)


def analyze_kpis(question):
    question = question.lower()

    if "profit" in question:
        return f"Average Profit: {df['Profit'].mean():,.2f} EGP"

    elif "attendance" in question:
        return f"Average Attendance: {df['Attendance'].mean():,.0f} fans"

    elif "revenue" in question:
        return f"Total Revenue: {df['Total_Revenue'].sum():,.2f} EGP"

    elif "wins" in question:
        wins = df["Win"].sum()
        return f"Total Wins: {wins}"

    return "KPI not found in dataset."

analyze_kpis("total revenue")


def pandas_analysis(question):
    question = question.lower()

    if "profit" in question and "highest" in question:
        row = df.loc[df["Profit"].idxmax()]
        return f"Highest profit match generated {row['Profit']:,.2f} EGP."

    elif "attendance" in question and "highest" in question:
        row = df.loc[df["Attendance"].idxmax()]
        return f"Highest attendance was {row['Attendance']} fans."

    elif "average" in question and "goals" in question:
        return f"Average goals scored: {df['Goals_Scored'].mean():.2f}"

    return "Analysis not available."

pandas_analysis("which match had highest attendance")

import requests
from datetime import datetime

API_Key = "47acce8b094d7fff2fb97a0b0db62634"

def football_api_tool(team_name):
    try:
        url = f"https://v3.football.api-sports.io/teams?search={team_name}"

        headers = {
            "x-apisports-key": API_Key
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return "API request failed."

        data = response.json()

        if not data.get("response"):
            return "No data found from API."

        team = data["response"][0]["team"]


        current_year = datetime.now().year
        season = f"{current_year - 1}/{current_year}"

        stadium = "Cairo International Stadium"
        

        return f"Team: {team.get('name')} | Country: {team.get('country')} | Venue: {stadium} | Founded: {team.get('founded')} | Current Season: {season}"

    except Exception as e:
        return f"API Error: {e}"
    
#print(football_api_tool("Zamalek"))

def business_recommendation(question):
    avg_attendance = df["Attendance"].dropna().mean()
    avg_profit = df["Profit"].dropna().mean()

    recommendations = []

    if avg_attendance < 25000:
        recommendations.append(
            "Low attendance detected: Launch marketing campaigns, discounts, and fan engagement activities."
        )
    else:
        recommendations.append(
            "Attendance levels are good: Maintain current engagement strategies and improve fan loyalty programs."
        )

    if avg_profit > 0:
        recommendations.append(
            "The club is profitable: Invest in merchandising, stadium experience, and brand expansion."
        )
    else:
        recommendations.append(
            "Profit is low or negative: Optimize costs and review revenue streams."
        )

    recommendations.append(
        "Use high-attendance matches for premium sponsorship opportunities."
    )

    return "\n".join(recommendations)
result = business_recommendation("any question here")
#print(result)


conversation_history = []
 
def ask_agent(user_message):
    user_message = user_message.lower()
    conversation_history.append(f"User: {user_message}")
 
    if "win rate" in user_message:
        result = f"Win Rate: {df['Win'].mean() * 100:.2f}%"
 
    elif "attendance" in user_message and not any(w in user_message for w in ["increase", "improve"]):
        result = f"Average Attendance: {df['Attendance'].mean():,.0f}"
 
    elif "total revenue" in user_message:
        total = (
            df["Ticket_Revenue"].sum() + df["Merch_Revenue"].sum()
            + df["Sponsor_Revenue"].sum() + df["Broadcast_Revenue"].sum()
            + df["Membership_Revenue"].sum()
        )
        result = f"Total Revenue: {total:,.0f} EGP"
 
    elif "highest revenue" in user_message or "which revenue" in user_message:
        streams = {
            "Ticket":     df["Ticket_Revenue"].sum(),
            "Merch":      df["Merch_Revenue"].sum(),
            "Sponsor":    df["Sponsor_Revenue"].sum(),
            "Broadcast":  df["Broadcast_Revenue"].sum(),
            "Membership": df["Membership_Revenue"].sum(),
        }
        result = f"Highest Revenue Stream: {max(streams, key=streams.get)}"
 
    elif "goals" in user_message:
        result = f"Avg Goals Scored: {df['Goals_Scored'].mean():.2f} | Avg Conceded: {df['Goals_Conceded'].mean():.2f}"
 
    elif "profit" in user_message and not any(w in user_message for w in ["increase", "improve"]):
        result = f"Average Profit: {df['Profit'].mean():,.0f} EGP"
 
    elif "idea" in user_message:
        result = "Zamalek AI analyzes football performance, revenue, attendance, and KPIs for decision making."
 
    elif any(w in user_message for w in ["stadium", "venue", "where does zamalek play"]):
        result = "Zamalek plays at Cairo International Stadium."
 
    elif any(w in user_message for w in ["country", "where is zamalek based", "where is zamalek located"]):
        result = "Egypt"
 
    elif any(w in user_message for w in ["season", "what season", "what is the current season"]):
        result = "2025/2026"
 
    elif any(w in user_message for w in ["recommend", "recommendation", "improve profitability", "increase profit", "business advice"]):
        result = (
            "Recommendations:\n"
            "- Increase sponsorship partnerships\n"
            "- Improve merchandising sales\n"
            "- Increase fan attendance through marketing campaigns\n"
            "- Improve match performance to attract more supporters\n"
            "- Use high-attendance matches for premium ticket pricing"
        )
 
    elif any(w in user_message for w in ["founded", "founding", "when was zamalek founded"]):
        result = "Zamalek SC was founded in 1911."
 
    elif any(w in user_message for w in ["increase revenue", "improve revenue", "how can zamalek increase revenue"]):
        result = (
            "Zamalek can increase revenue through sponsorship expansion, "
            "higher attendance, merchandising growth, and fan engagement campaigns."
        )
 
    elif any(w in user_message for w in ["increase it", "improve it", "increase attendance", "improve attendance"]):
        last_context = conversation_history[-2].lower() if len(conversation_history) >= 2 else ""
        if "attendance" in last_context:
            result = (
                "Zamalek can increase attendance through:\n"
                "- Fan engagement campaigns\n"
                "- Discounted tickets\n"
                "- Social media marketing\n"
                "- Better match-day experience\n"
                "- Winning more matches"
            )
        elif "revenue" in last_context:
            result = (
                "Revenue can be improved through:\n"
                "- Sponsorship expansion\n"
                "- Merchandising growth\n"
                "- Premium ticket pricing"
            )
        else:
            result = "Please specify what you want to improve."
 
    else:
        result = "I can answer only Zamalek KPIs, revenue, attendance, goals, and performance."
 
    conversation_history.append(f"Assistant: {result}")
    print(result)
    
print("Hello I'm your Zamalek Ai Assistant, How can i help you?")
while True:
    user_input = input("You: ")
    if user_input.lower() in {"exit", "quit"}:
        break
    ask_agent(user_input)
    print()
    
