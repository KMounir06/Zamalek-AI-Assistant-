from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "zamalek.dataset.csv")

try:
    df = pd.read_csv(CSV_PATH)
    df["Ticket_Revenue"] = (
        df["Ticket_Revenue"].astype(str)
        .str.replace("EGP", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df["Ticket_Revenue"]     = pd.to_numeric(df["Ticket_Revenue"], errors="coerce").fillna(0)
    df["Merch_Revenue"]      = pd.to_numeric(df["Merch_Revenue"],  errors="coerce").fillna(0)
    df["Sponsor_Revenue"]    = pd.to_numeric(df["Sponsor_Revenue"],errors="coerce").fillna(0)
    df["Broadcast_Revenue"]  = pd.to_numeric(df["Broadcast_Revenue"],errors="coerce").fillna(0)
    df["Membership_Revenue"] = pd.to_numeric(df["Membership_Revenue"],errors="coerce").fillna(0)
    df["Total_Revenue"]      = pd.to_numeric(df["Total_Revenue"],  errors="coerce").fillna(0)
    df["Profit"]             = pd.to_numeric(df["Profit"],         errors="coerce").fillna(0)
    df["Attendance"]         = pd.to_numeric(df["Attendance"],     errors="coerce").fillna(0)
    df["Goals_Scored"]       = pd.to_numeric(df["Goals_Scored"],   errors="coerce").fillna(0)
    df["Goals_Conceded"]     = pd.to_numeric(df["Goals_Conceded"], errors="coerce").fillna(0)
    df["Win"]                = pd.to_numeric(df["Win"],            errors="coerce").fillna(0)
    df["Match_Date"]         = pd.to_datetime(df["Match_Date"],    errors="coerce")
    DATASET_LOADED = True
    print(f"✅ Dataset loaded: {len(df)} matches")
except Exception as e:
    df = None
    DATASET_LOADED = False
    print(f"❌ Dataset error: {e}")

# ── Conversation Memory ───────────────────────────────────────
conversation_history = []

# ── Core AI Logic ─────────────────────────────────────────────
def ask_agent(user_message: str) -> str:
    msg = user_message.lower()
    conversation_history.append(f"User: {msg}")

    if not DATASET_LOADED:
        result = "⚠️ Dataset not loaded. Please add zamalek.dataset.csv to the project folder."

    elif "win rate" in msg:
        result = f"Win Rate: {df['Win'].mean() * 100:.2f}%"

    elif "attendance" in msg and not any(w in msg for w in ["increase", "improve"]):
        avg = df['Attendance'].mean()
        mx  = df['Attendance'].max()
        result = f"Average Attendance: {avg:,.0f} fans\nHighest Attendance: {mx:,.0f} fans"

    elif "total revenue" in msg:
        total = (
            df["Ticket_Revenue"].sum() + df["Merch_Revenue"].sum()
            + df["Sponsor_Revenue"].sum() + df["Broadcast_Revenue"].sum()
            + df["Membership_Revenue"].sum()
        )
        result = f"Total Revenue: {total:,.0f} EGP"

    elif "highest revenue" in msg or "which revenue" in msg or "revenue stream" in msg:
        streams = {
            "Ticket":     df["Ticket_Revenue"].sum(),
            "Merch":      df["Merch_Revenue"].sum(),
            "Sponsor":    df["Sponsor_Revenue"].sum(),
            "Broadcast":  df["Broadcast_Revenue"].sum(),
            "Membership": df["Membership_Revenue"].sum(),
        }
        top = max(streams, key=streams.get)
        lines = "\n".join([f"• {k}: {v:,.0f} EGP" for k, v in sorted(streams.items(), key=lambda x: -x[1])])
        result = f"Revenue Streams:\n{lines}\n\n🏆 Highest: {top}"

    elif "goals" in msg:
        scored   = df['Goals_Scored'].mean()
        conceded = df['Goals_Conceded'].mean()
        total_s  = df['Goals_Scored'].sum()
        result   = (f"Avg Goals Scored: {scored:.2f} | Avg Conceded: {conceded:.2f}\n"
                    f"Total Goals Scored: {total_s:.0f}")

    elif "profit" in msg and not any(w in msg for w in ["increase", "improve"]):
        avg = df['Profit'].mean()
        total = df['Profit'].sum()
        result = f"Average Profit: {avg:,.0f} EGP\nTotal Profit: {total:,.0f} EGP"

    elif "total cost" in msg or "cost" in msg:
        result = f"Total Cost: {df['Total_Cost'].sum():,.0f} EGP\nAverage Cost per Match: {df['Total_Cost'].mean():,.0f} EGP"

    elif "matches" in msg or "how many matches" in msg:
        total  = len(df)
        wins   = int(df['Win'].sum())
        losses = total - wins
        result = f"Total Matches: {total}\nWins: {wins} | Losses/Draws: {losses}"

    elif "idea" in msg:
        result = "Zamalek AI analyzes football performance, revenue, attendance, and KPIs for smarter decision making."

    elif any(w in msg for w in ["stadium", "venue", "where does zamalek play"]):
        result = "Zamalek plays at Cairo International Stadium."

    elif any(w in msg for w in ["country", "where is zamalek based", "where is zamalek located"]):
        result = "Zamalek SC is based in Egypt 🇪🇬"

    elif any(w in msg for w in ["season", "current season"]):
        result = "Current Season: 2025/2026"

    elif any(w in msg for w in ["recommend", "recommendation", "improve profitability",
                                  "increase profit", "business advice"]):
        avg_att = df['Attendance'].mean()
        avg_pr  = df['Profit'].mean()
        recs = ["📊 Business Recommendations for Zamalek SC:\n"]
        if avg_att < 25000:
            recs.append("• Low attendance: Launch fan campaigns & ticket discounts")
        else:
            recs.append("• Good attendance: Strengthen loyalty & season ticket programs")
        if avg_pr > 0:
            recs.append("• Club is profitable: Invest in merch, stadium experience & brand expansion")
        else:
            recs.append("• Profit is low: Review costs and diversify revenue streams")
        recs.append("• Use high-attendance matches for premium sponsorship deals")
        recs.append("• Expand digital merchandising & social media revenue")
        result = "\n".join(recs)

    elif any(w in msg for w in ["founded", "founding", "when was zamalek founded"]):
        result = "Zamalek SC was founded in 1911 🏆"

    elif any(w in msg for w in ["increase revenue", "improve revenue"]):
        result = (
            "Zamalek can increase revenue through:\n"
            "• Sponsorship expansion\n"
            "• Higher match attendance\n"
            "• Merchandising growth\n"
            "• Fan engagement campaigns\n"
            "• Premium broadcast deals"
        )

    elif any(w in msg for w in ["increase it", "improve it", "increase attendance", "improve attendance"]):
        last_context = conversation_history[-2].lower() if len(conversation_history) >= 2 else ""
        if "attendance" in last_context:
            result = (
                "Zamalek can increase attendance through:\n"
                "• Fan engagement campaigns\n"
                "• Discounted tickets\n"
                "• Social media marketing\n"
                "• Better match-day experience\n"
                "• Winning more matches"
            )
        elif "revenue" in last_context:
            result = (
                "Revenue can be improved through:\n"
                "• Sponsorship expansion\n"
                "• Merchandising growth\n"
                "• Premium ticket pricing"
            )
        else:
            result = "Please specify what you want to improve."

    elif "summary" in msg or "overview" in msg:
        total_rev = df["Total_Revenue"].sum()
        total_pr  = df["Profit"].sum()
        win_rate  = df['Win'].mean() * 100
        avg_att   = df['Attendance'].mean()
        result = (
            f"📋 Zamalek SC Overview ({len(df)} matches)\n"
            f"• Win Rate: {win_rate:.1f}%\n"
            f"• Total Revenue: {total_rev:,.0f} EGP\n"
            f"• Total Profit: {total_pr:,.0f} EGP\n"
            f"• Avg Attendance: {avg_att:,.0f} fans\n"
            f"• Avg Goals/Match: {df['Goals_Scored'].mean():.2f}"
        )

    else:
        result = "I can answer questions about Zamalek KPIs, revenue, attendance, goals, profits, and performance. Try asking about 'total revenue', 'win rate', or 'recommendations'."

    conversation_history.append(f"Assistant: {result}")
    return result

# ── HTML Template Context ─────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Zamalek AI Assistant</title>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --red:      #CC0000;
      --red-dark: #990000;
      --white:    #FFFFFF;
      --off-white:#F5F0E8;
      --bg:       #0a0a0a;
      --surface:  #141414;
      --surface2: #1e1e1e;
      --border:   #2a2a2a;
      --muted:    #666;
      --text:     #f0f0f0;
      --radius:   12px;
    }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    body::before {
      content: '';
      position: fixed; inset: 0;
      background: repeating-linear-gradient(
        -55deg, transparent, transparent 40px,
        rgba(204,0,0,.018) 40px, rgba(204,0,0,.018) 41px
      );
      pointer-events: none; z-index: 0;
    }
    header {
      position: relative; z-index: 10;
      background: var(--red);
      padding: 0 24px; height: 64px;
      display: flex; align-items: center; gap: 16px;
      box-shadow: 0 2px 24px rgba(204,0,0,.4);
    }
    .club-badge {
      width: 42px; height: 42px; background: white; border-radius: 50%;
      display: grid; place-items: center; font-size: 22px; flex-shrink: 0;
      box-shadow: 0 0 0 2px rgba(255,255,255,.3);
    }
    .header-info h1 {
      font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem;
      letter-spacing: .08em; color: white; line-height: 1;
    }
    .header-info p {
      font-size: .68rem; color: rgba(255,255,255,.7);
      font-family: 'DM Mono', monospace; margin-top: 2px;
    }
    .header-right {
      margin-left: auto; display: flex; align-items: center; gap: 8px;
      font-size: .72rem; color: rgba(255,255,255,.8); font-family: 'DM Mono', monospace;
    }
    .dot {
      width: 7px; height: 7px; background: #7fff7f; border-radius: 50%;
      box-shadow: 0 0 8px #7fff7f; animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
    #messages {
      flex: 1; overflow-y: auto; padding: 24px 20px;
      display: flex; flex-direction: column; gap: 18px;
      position: relative; z-index: 1; scroll-behavior: smooth;
    }
    #messages::-webkit-scrollbar { width: 4px; }
    #messages::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
    .message { display: flex; gap: 12px; max-width: 820px; animation: fadein .22s ease both; }
    @keyframes fadein { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
    .message.user { align-self: flex-end; flex-direction: row-reverse; }
    .message.ai   { align-self: flex-start; }
    .avatar { width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center; font-size: 16px; flex-shrink: 0; margin-top: 2px; }
    .message.user .avatar { background: var(--red); color: white; font-weight: 700; font-size: .8rem; font-family:'Bebas Neue',sans-serif; letter-spacing:.05em; }
    .message.ai   .avatar { background: white; }
    .bubble { padding: 12px 16px; border-radius: var(--radius); font-size: .9rem; line-height: 1.7; max-width: 65ch; word-break: break-word; white-space: pre-line; }
    .message.user .bubble { background: var(--red); color: white; border-top-right-radius: 3px; }
    .message.ai .bubble { background: var(--surface2); border: 1px solid var(--border); border-top-left-radius: 3px; color: var(--text); }
    .typing-dots span { display: inline-block; width: 6px; height: 6px; background: var(--muted); border-radius: 50%; margin: 0 2px; animation: blink 1.2s ease-in-out infinite; }
    .typing-dots span:nth-child(2){animation-delay:.2s}
    .typing-dots span:nth-child(3){animation-delay:.4s}
    @keyframes blink{0%,80%,100%{opacity:.2;transform:scale(.8)}40%{opacity:1;transform:scale(1)}}
    #empty-state { margin: auto; text-align: center; opacity: .5; pointer-events: none; }
    #empty-state .crest { font-size: 4rem; margin-bottom: 16px; }
    #empty-state h2 { font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; letter-spacing: .1em; color: var(--red); margin-bottom: 6px; }
    #empty-state p { font-size: .8rem; color: var(--muted); font-family: 'DM Mono', monospace; }
    .suggestions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 16px; }
    .suggestion-btn { background: var(--surface2); border: 1px solid var(--border); color: var(--text); font-family: 'Inter', sans-serif; font-size: .78rem; padding: 6px 14px; border-radius: 20px; cursor: pointer; transition: border-color .2s, background .2s; pointer-events: all; }
    .suggestion-btn:hover { border-color: var(--red); background: rgba(204,0,0,.1); }
    footer { position: relative; z-index: 10; padding: 14px 20px; border-top: 1px solid var(--border); background: rgba(10,10,10,.95); backdrop-filter: blur(10px); }
    .input-row { display: flex; align-items: flex-end; gap: 10px; max-width: 860px; margin: 0 auto; background: var(--surface2); border: 1px solid var(--border); border-radius: var(--radius); padding: 10px 14px; transition: border-color .2s; }
    .input-row:focus-within { border-color: var(--red); box-shadow: 0 0 0 3px rgba(204,0,0,.12); }
    #user-input { flex: 1; background: transparent; border: none; outline: none; color: var(--text); font-family: 'Inter', sans-serif; font-size: .9rem; line-height: 1.5; resize: none; max-height: 120px; overflow-y: auto; }
    #user-input::placeholder { color: var(--muted); }
    #send-btn { width: 36px; height: 36px; background: var(--red); color: white; border: none; border-radius: 9px; cursor: pointer; display: grid; place-items: center; font-size: 15px; flex-shrink: 0; transition: transform .15s, box-shadow .15s, opacity .2s; }
    #send-btn:hover  { transform: scale(1.08); box-shadow: 0 0 16px rgba(204,0,0,.5); }
    #send-btn:active { transform: scale(.94); }
    #send-btn:disabled { opacity: .3; cursor: not-allowed; transform: none; box-shadow: none; }
    .hint { text-align: center; margin-top: 7px; font-size: .67rem; color: var(--muted); font-family: 'DM Mono', monospace; }
  </style>
</head>
<body>
<header>
  <div class="club-badge">⚽</div>
  <div class="header-info">
    <h1>Zamalek AI Assistant</h1>
    <p>Powered by Zamalek Dataset · localhost:5000</p>
  </div>
  <div class="header-right"><span class="dot"></span> online</div>
</header>
<div id="messages">
  <div id="empty-state">
    <div class="crest">🤍❤️</div>
    <h2>Zamalek AI Assistant</h2>
    <p>Ask anything about Zamalek SC — stats, revenue, performance & more</p>
    <div class="suggestions">
      <button class="suggestion-btn" onclick="quickAsk('What is the total revenue?')">Total Revenue</button>
      <button class="suggestion-btn" onclick="quickAsk('What is Zamalek win rate?')">Win Rate</button>
      <button class="suggestion-btn" onclick="quickAsk('What is the average attendance?')">Attendance</button>
      <button class="suggestion-btn" onclick="quickAsk('What is the average profit?')">Avg Profit</button>
      <button class="suggestion-btn" onclick="quickAsk('Give me business recommendations')">Recommendations</button>
      <button class="suggestion-btn" onclick="quickAsk('Average goals scored?')">Goals</button>
    </div>
  </div>
</div>
<footer>
  <div class="input-row">
    <textarea id="user-input" rows="1" placeholder="Ask about Zamalek…"></textarea>
    <button id="send-btn" title="Send">➤</button>
  </div>
  <p class="hint">Enter to send &nbsp;·&nbsp; Shift+Enter for new line</p>
</footer>
<script>
  const messagesEl = document.getElementById('messages');
  const inputEl    = document.getElementById('user-input');
  const sendBtn    = document.getElementById('send-btn');
  const emptyState = document.getElementById('empty-state');

  inputEl.addEventListener('input', () => {
    inputEl.style.height = 'auto';
    inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + 'px';
  });
  inputEl.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });
  sendBtn.addEventListener('click', sendMessage);

  function quickAsk(text) { inputEl.value = text; sendMessage(); }
  function addMessage(role, text) {
    emptyState.style.display = 'none';
    const wrap = document.createElement('div'); wrap.className = `message ${role}`;
    const avatar = document.createElement('div'); avatar.className = 'avatar';
    avatar.textContent = role === 'user' ? 'YOU' : '⚽';
    const bubble = document.createElement('div'); bubble.className = 'bubble';
    bubble.textContent = text;
    wrap.appendChild(avatar); wrap.appendChild(bubble); messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }
  function addTyping() {
    emptyState.style.display = 'none';
    const wrap = document.createElement('div'); wrap.className = 'message ai'; wrap.id = 'typing-indicator';
    const avatar = document.createElement('div'); avatar.className = 'avatar'; avatar.textContent = '⚽';
    const bubble = document.createElement('div'); bubble.className = 'bubble';
    bubble.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    wrap.appendChild(avatar); wrap.appendChild(bubble); messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }
  function removeTyping() { const el = document.getElementById('typing-indicator'); if (el) el.remove(); }
  async function sendMessage() {
    const text = inputEl.value.trim(); if (!text) return;
    addMessage('user', text); inputEl.value = ''; inputEl.style.height = 'auto'; sendBtn.disabled = true; addTyping();
    try {
      const res  = await fetch('/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json(); removeTyping();
      if (data.error) addMessage('ai', '⚠️ Error: ' + data.error);
      else            addMessage('ai', data.reply);
    } catch (err) {
      removeTyping(); addMessage('ai', '⚠️ Cannot reach server. Make sure the server is running.');
    } finally { sendBtn.disabled = false; inputEl.focus(); }
  }
</script>
</body>
</html>"""

# ── Routes ─────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    try:
        reply = ask_agent(user_message)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/status")
def status():
    return jsonify({
        "dataset_loaded": DATASET_LOADED,
        "rows": len(df) if DATASET_LOADED else 0,
        "columns": df.columns.tolist() if DATASET_LOADED else []
    })

if __name__ == "__main__":
    print("=" * 50)
    print("🤍❤️  Zamalek AI Assistant")
    print("🌐  http://localhost:5000")
    print(f"📊  Dataset: {'✅ Loaded — ' + str(len(df)) + ' matches' if DATASET_LOADED else '❌ Not Found'}")
    print("=" * 50)
    app.run(debug=True, port=5000)