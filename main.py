
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import database
import auth

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="TradeSim India",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

auth.initialize_auth_db()

# --------------------------------------------------
# MODERN TRADING TERMINAL DESIGN
# --------------------------------------------------



st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background: #080D13 !important;
    color: #FFFFFF !important;
}

/* ALL HEADINGS */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
    font-weight: 800 !important;
}

/* NORMAL TEXT */
.stApp p,
.stApp label,
.stApp li,
.stApp [data-testid="stMarkdownContainer"] {
    color: #F1F5F9 !important;
}

/* TOP NAVIGATION */
div[data-testid="stRadio"] label {
    background: #1B2A3B !important;
    border: 1px solid #465B70 !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
}

/* NAVIGATION TEXT */
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span {
    color: #FFFFFF !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}

/* SELECTED NAVIGATION */
div[data-testid="stRadio"] label:has(input:checked) {
    background: #B8F34A !important;
    border: 2px solid #B8F34A !important;
}

div[data-testid="stRadio"] label:has(input:checked) p,
div[data-testid="stRadio"] label:has(input:checked) span {
    color: #101510 !important;
    font-weight: 900 !important;
}

/* ACCOUNT METRIC CARDS */
[data-testid="stMetric"] {
    background: #172536 !important;
    border: 1px solid #40536A !important;
    border-radius: 18px !important;
    padding: 24px !important;
}

/* METRIC LABELS */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] label {
    color: #FFFFFF !important;
    font-size: 17px !important;
    font-weight: 700 !important;
}

/* ACCOUNT VALUES */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    color: #FFFFFF !important;
    font-size: 32px !important;
    font-weight: 900 !important;
}

/* BUTTONS */
div.stButton > button,
div.stFormSubmitButton > button {
    background: #B8F34A !important;
    color: #101510 !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 900 !important;
    font-size: 16px !important;
    min-height: 46px !important;
}

div.stButton > button *,
div.stFormSubmitButton > button * {
    color: #101510 !important;
}

/* INPUT FIELDS */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background: #172536 !important;
    border: 1px solid #53677D !important;
}

input, textarea {
    color: #FFFFFF !important;
    font-size: 16px !important;
}

/* LOGIN EMAIL */
.brand {
    color: #B8F34A !important;
    font-weight: 900 !important;
}

/* CUSTOM PANELS */
.terminal-panel {
    background: #172536 !important;
    border: 1px solid #40536A !important;
    border-radius: 16px !important;
    padding: 20px !important;
}

.terminal-muted {
    color: #DCE5EF !important;
    font-size: 15px !important;
}

/* TABLES */
[data-testid="stDataFrame"] {
    border: 1px solid #40536A !important;
    border-radius: 12px !important;
}

/* CAPTIONS */
.stCaption,
[data-testid="stCaptionContainer"] {
    color: #C8D3E0 !important;
}

/* DIVIDERS */
hr {
    border-color: #40536A !important;
}

/* MOBILE */
@media (max-width: 768px) {
    h1 {
        font-size: 30px !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {
        font-size: 25px !important;
    }

    div[data-testid="stRadio"] label p {
        font-size: 14px !important;
    }
}

</style>
""", unsafe_allow_html=True)



# --------------------------------------------------
# STOCK LIST
# --------------------------------------------------

COMPANIES = {
    "Reliance Industries": "RELIANCE.NS",
    "Tata Consultancy Services": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "State Bank of India": "SBIN.NS",
    "ITC": "ITC.NS",
    "Wipro": "WIPRO.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Tata Motors": "TATAMOTORS.NS"
}


# --------------------------------------------------
# MARKET DATA
# --------------------------------------------------

@st.cache_data(ttl=20, show_spinner=False)
def fetch_history(ticker, period, interval):
    return yf.Ticker(ticker).history(
        period=period,
        interval=interval
    )


def get_stock_history(ticker, period="1d", interval="1m"):
    hist = fetch_history(ticker, period, interval)

    if hist.empty:
        return hist

    hist = hist.dropna(subset=["Open", "High", "Low", "Close"])

    return hist


def latest_stock_price(ticker):
    hist = get_stock_history(ticker, "1d", "1m")

    if hist.empty:
        hist = get_stock_history(ticker, "5d", "5m")

    if hist.empty:
        raise ValueError("Stock price is currently unavailable.")

    return float(hist["Close"].iloc[-1])


# --------------------------------------------------
# LOGIN AND REGISTRATION
# --------------------------------------------------

def auth_screen():

    st.markdown(
        "<div class='brand'>📈 TradeSim India</div>",
        unsafe_allow_html=True
    )

    st.subheader("Your personal trading terminal")
    st.caption("Learn the Indian stock market with virtual money.")

    login_tab, register_tab = st.tabs(
        ["🔐 Login", "✨ Create account"]
    )

    with login_tab:

        with st.form("login_form"):

            email = st.text_input("Email address")
            password = st.text_input(
                "Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if submitted:

            user = auth.login(email, password)

            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Email or password is incorrect.")

    with register_tab:

        with st.form("register_form"):

            email = st.text_input(
                "Email address",
                key="register_email"
            )

            password = st.text_input(
                "Create password",
                type="password",
                key="register_password"
            )

            confirm = st.text_input(
                "Confirm password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Create account",
                use_container_width=True
            )

        if submitted:

            if password != confirm:
                st.error("Passwords do not match.")

            else:

                try:
                    user = auth.register(email, password)

                    st.session_state.user = user

                    st.success("Account created successfully!")

                    st.rerun()

                except ValueError as exc:
                    st.error(str(exc))


# --------------------------------------------------
# AUTHENTICATION CHECK
# --------------------------------------------------

if "user" not in st.session_state:

    auth_screen()
    st.stop()


user = st.session_state.user

db_file = user["db_filename"]

cash = database.load_account(db_file)

portfolio = database.load_portfolio(db_file)


# --------------------------------------------------
# TOP NAVIGATION
# --------------------------------------------------

nav_left, nav_middle, nav_right = st.columns(
    [2, 7, 1.5],
    vertical_alignment="center"
)

with nav_left:

    st.markdown(
        "<div class='brand'>📈 TradeSim</div>",
        unsafe_allow_html=True
    )

with nav_middle:

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Market & Charts",
            "Virtual Trading",
            "Portfolio",
            "Trade History"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

with nav_right:

    if st.button("Log out", use_container_width=True):

        del st.session_state["user"]

        st.rerun()


# --------------------------------------------------
# AUTOMATIC REFRESH
# --------------------------------------------------

if page in ["Overview", "Market & Charts", "Portfolio"]:

    st_autorefresh(
        interval=30_000,
        key="tradesim_refresh"
    )


# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.markdown("---")

header_left, header_right = st.columns([3, 1])

with header_left:

    st.title("TradeSim India")

    st.caption(
        "Your personal Indian stock market dashboard"
    )

with header_right:

    st.markdown(
        f"<div style='text-align:right;color:#AAB8C5;'>"
        f"Logged in as<br><b style='color:#B8F34A;'>"
        f"{user['email']}</b></div>",
        unsafe_allow_html=True
    )


# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

if page == "Overview":

    st.subheader("📊 Account Overview")

    prices = {}

    for name, qty in portfolio.items():

        if qty > 0 and name in COMPANIES:

            try:
                prices[name] = latest_stock_price(
                    COMPANIES[name]
                )

            except Exception:
                pass

    stock_value = sum(
        prices[n] * q
        for n, q in portfolio.items()
        if n in prices
    )

    total = cash + stock_value

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "💰 Available Cash",
        f"₹{cash:,.2f}"
    )

    c2.metric(
        "📈 Portfolio Value",
        f"₹{stock_value:,.2f}"
    )

    c3.metric(
        "💎 Total Account Value",
        f"₹{total:,.2f}"
    )

    st.markdown("---")

    st.subheader("Your Holdings")

    holding_rows = []

    for name, qty in portfolio.items():

        if qty <= 0:
            continue

        price = prices.get(name)

        holding_rows.append({
            "Company": name,
            "Shares": qty,
            "Latest Price (₹)": (
                round(price, 2) if price is not None else "Unavailable"
            ),
            "Market Value (₹)": (
                round(price * qty, 2)
                if price is not None else "Unavailable"
            )
        })

    if holding_rows:

        st.dataframe(
            pd.DataFrame(holding_rows),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Your portfolio is empty. Visit Virtual Trading to begin."
        )

    st.markdown("---")

    st.subheader("🇮🇳 Market Watch")

    watch_rows = []

    for name, ticker in COMPANIES.items():

        try:

            price = latest_stock_price(ticker)

            watch_rows.append({
                "Company": name,
                "Price (₹)": round(price, 2),
                "Status": "Available"
            })

        except Exception:

            watch_rows.append({
                "Company": name,
                "Price (₹)": "Unavailable",
                "Status": "Unavailable"
            })

    st.dataframe(
        pd.DataFrame(watch_rows),
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# MARKET AND CHARTS
# --------------------------------------------------

elif page == "Market & Charts":

    st.subheader("📈 Indian Stock Market")

    selected = st.selectbox(
        "Select Company",
        list(COMPANIES.keys())
    )

    period_options = {
        "1 Day": ("1d", "1m"),
        "5 Days": ("5d", "5m"),
        "1 Month": ("1mo", "1d"),
        "3 Months": ("3mo", "1d"),
        "6 Months": ("6mo", "1d"),
        "1 Year": ("1y", "1d")
    }

    selected_period = st.selectbox(
        "Chart Period",
        list(period_options.keys()),
        index=0
    )

    period, interval = period_options[selected_period]

    ticker = COMPANIES[selected]

    try:

        hist = get_stock_history(
            ticker,
            period,
            interval
        )

        if hist.empty:

            st.warning("No market data is currently available.")

        else:

            latest = float(hist["Close"].iloc[-1])

            previous = float(hist["Close"].iloc[0])

            change = latest - previous

            change_percent = (
                change / previous * 100
                if previous else 0
            )

            a, b, c = st.columns(3)

            a.metric(
                "Latest Price",
                f"₹{latest:,.2f}",
                f"{change:+.2f}"
            )

            b.metric(
                "Price Change",
                f"{change_percent:+.2f}%"
            )

            c.metric(
                "Trading Volume",
                f"{int(hist['Volume'].iloc[-1]):,}"
            )

            st.markdown("---")

            fig = go.Figure()

            fig.add_trace(
                go.Candlestick(
                    x=hist.index,
                    open=hist["Open"],
                    high=hist["High"],
                    low=hist["Low"],
                    close=hist["Close"],
                    name=selected,
                    increasing_line_color="#B8F34A",
                    decreasing_line_color="#FF5964",
                    increasing_fillcolor="#B8F34A",
                    decreasing_fillcolor="#FF5964"
                )
            )

            fig.update_layout(
                template="plotly_dark",
                title=selected,
                height=550,
                paper_bgcolor="#121C29",
                plot_bgcolor="#121C29",
                font=dict(color="#DCE5EF"),
                xaxis_title="Time",
                yaxis_title="Price (₹)",
                xaxis_rangeslider_visible=False,
                margin=dict(l=20, r=20, t=60, b=20)
            )

            fig.update_xaxes(
                showgrid=True,
                gridcolor="#263648"
            )

            fig.update_yaxes(
                showgrid=True,
                gridcolor="#263648"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    except Exception as exc:

        st.error(f"Could not load market data: {exc}")


# --------------------------------------------------
# VIRTUAL TRADING
# --------------------------------------------------

elif page == "Virtual Trading":

    st.subheader("💹 Virtual Trading Terminal")

    left, right = st.columns([1.2, 1])

    with left:

        st.markdown(
            "<div class='terminal-panel'>"
            "<h3>Execute Virtual Trade</h3>"
            "<p class='terminal-muted'>"
            "Buy and sell shares using your virtual balance."
            "</p></div>",
            unsafe_allow_html=True
        )

        company = st.selectbox(
            "Select Company",
            list(COMPANIES.keys())
        )

        action = st.radio(
            "Order Type",
            ["Buy", "Sell"],
            horizontal=True
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            max_value=1000,
            value=1,
            step=1
        )

    with right:

        try:

            current_price = latest_stock_price(
                COMPANIES[company]
            )

            st.metric(
                "Latest Available Price",
                f"₹{current_price:,.2f}"
            )

            st.metric(
                "Available Virtual Cash",
                f"₹{cash:,.2f}"
            )

            st.metric(
                "Estimated Order Value",
                f"₹{current_price * quantity:,.2f}"
            )

        except Exception as exc:

            current_price = None

            st.warning(str(exc))

    if st.button(
        "🚀 Execute Virtual Trade",
        use_container_width=True
    ):

        try:

            if current_price is None:

                st.error("Stock price unavailable.")

            else:

                new_cash, new_qty = database.execute_trade(
                    db_file,
                    company,
                    action,
                    int(quantity),
                    current_price
                )

                st.success(
                    f"{action} completed: {quantity} "
                    f"{company} share(s) at ₹{current_price:,.2f}"
                )

                st.rerun()

        except Exception as exc:

            st.error(str(exc))


# --------------------------------------------------
# PORTFOLIO AND PROFIT / LOSS
# --------------------------------------------------

elif page == "Portfolio":

    st.subheader("💼 Portfolio Analytics")

    avg_costs = database.load_average_costs(db_file)

    realized = database.calculate_realized_profit_loss(
        db_file
    )

    rows = []

    unrealized = 0.0

    invested = 0.0

    current_value_total = 0.0

    for company, qty in portfolio.items():

        if qty <= 0 or company not in COMPANIES:
            continue

        try:

            price = latest_stock_price(
                COMPANIES[company]
            )

            avg = avg_costs.get(company, 0.0)

            cost = avg * qty

            value = price * qty

            pnl = value - cost

            pnl_percent = (
                pnl / cost * 100 if cost > 0 else 0
            )

            invested += cost

            current_value_total += value

            unrealized += pnl

            rows.append({
                "Company": company,
                "Shares": qty,
                "Invested (₹)": round(cost, 2),
                "Average Cost (₹)": round(avg, 2),
                "Current Price (₹)": round(price, 2),
                "Current Value (₹)": round(value, 2),
                "Profit/Loss (₹)": round(pnl, 2),
                "Profit/Loss (%)": round(pnl_percent, 2)
            })

        except Exception:
            pass

    a, b, c = st.columns(3)

    a.metric(
        "Unrealized P/L",
        f"₹{unrealized:,.2f}",
        delta=f"{unrealized:+,.2f}"
    )

    b.metric(
        "Realized P/L",
        f"₹{realized:,.2f}"
    )

    c.metric(
        "Invested Amount",
        f"₹{invested:,.2f}"
    )

    if rows:

        st.markdown("---")

        st.subheader("Individual Stock Performance")

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )

        total_change = current_value_total - invested

        total_change_pct = (
            total_change / invested * 100
            if invested > 0 else 0
        )

        st.markdown("---")

        x, y, z = st.columns(3)

        x.metric(
            "Total Invested",
            f"₹{invested:,.2f}"
        )

        y.metric(
            "Current Value",
            f"₹{current_value_total:,.2f}"
        )

        z.metric(
            "Total Investment P/L",
            f"₹{total_change:,.2f}",
            delta=f"{total_change_pct:+.2f}%"
        )

    else:

        st.info("No currently priced holdings.")


# --------------------------------------------------
# TRADE HISTORY
# --------------------------------------------------

elif page == "Trade History":

    st.subheader("📋 Transaction History")

    trades = database.load_trades(db_file)

    if trades:

        df = pd.DataFrame(
            trades,
            columns=[
                "Company",
                "Action",
                "Quantity",
                "Price (₹)",
                "Trade Time"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"Total transactions: {len(df)}"
        )

    else:

        st.info("No trades recorded yet.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.caption(
    "📈 TradeSim India | Virtual trading simulator | "
    "Market data provided by Yahoo Finance and may be delayed. "
    "No real exchange orders are placed."
)
