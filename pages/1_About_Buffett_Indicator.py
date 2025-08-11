# pages/1_About_Buffett_Indicator.py
import streamlit as st

st.set_page_config(page_title="About Buffett Indicator", layout="wide")

st.title("ℹ️ About the Buffett Indicator")

st.markdown("""
## **Definition**
The **Buffett Indicator** is a stock market valuation metric that compares a country's total stock market capitalization to its gross domestic product (GDP).

**Formula**:
Buffett Indicator (%) = (Total Market Capitalization ÷ GDP) × 100
            
- **Market Capitalization**: Combined value of all publicly traded companies in the country.
- **GDP**: Annual economic output in current prices.

---
""")

# ====== Interactive Calculator ======
st.header("📊 Buffett Indicator Calculator")

with st.expander("Try it yourself — Enter values below:"):
    market_cap = st.number_input("Total Market Capitalization (in trillions)", min_value=0.0, format="%.2f")
    gdp = st.number_input("GDP (in trillions)", min_value=0.0, format="%.2f")

    if gdp > 0:
        buffett_indicator = (market_cap / gdp) * 100
        st.markdown(f"**Buffett Indicator:** `{buffett_indicator:.2f}%`")

        # Interpretation logic
        if buffett_indicator < 50:
            status = "Significantly Undervalued 📉"
        elif 50 <= buffett_indicator < 75:
            status = "Moderately Undervalued"
        elif 75 <= buffett_indicator < 90:
            status = "Fair Value ⚖️"
        elif 90 <= buffett_indicator < 115:
            status = "Moderately Overvalued"
        else:
            status = "Significantly Overvalued 📈"

        st.markdown(f"**Interpretation:** {status}")
    else:
        st.info("Enter GDP to calculate the Buffett Indicator.")

# ====== Interpretation Table ======
st.markdown("""
## **Interpretation Guide**
| Buffett Indicator Ratio | Market Valuation Status   |
|-------------------------|---------------------------|
| **< 50%**               | Significantly Undervalued |
| **50% – 75%**           | Moderately Undervalued    |
| **75% – 90%**           | Fair Value                |
| **90% – 115%**          | Moderately Overvalued     |
| **> 115%**              | Significantly Overvalued  |

> These ranges were suggested by Warren Buffett for the US, but thresholds vary across countries depending on interest rates, economic growth, and market structure.
""")

# ====== Why it works ======
st.markdown("""
---
## **Why It Works**
- **GDP** measures the size of the real economy.
- **Market Cap** reflects investors’ expectations.
- When **Market Cap is far above GDP**, it suggests stocks are overpriced relative to the economy's size.
- When **far below GDP**, it may indicate undervaluation.

---
## **Limitations**
1. **Globalization effect** – Many companies earn large revenue abroad.
2. **Interest rate environment** – Low rates can sustain higher valuations.
3. **Data delays** – GDP is updated quarterly/yearly; market cap moves daily.
4. **Country-specific structures** – Emerging markets may have smaller public markets relative to GDP.

---
## **Historical Examples**
- **US Dot-Com Bubble (1999–2000)**: Buffett Indicator >150%, followed by a crash.
- **2008 Financial Crisis**: Fell to ~60%.
- **Post-COVID (2021)**: US ratio exceeded 200%, historically very high.

---
## **Example Calculation**

For example: If
- Market Cap = ₹350 trillion
- GDP = ₹270 trillion

Then:
Buffett Indicator = (350 / 270) × 100 = 129.6%
            
Interpretation: Market is significantly overvalued by traditional standards.

---
## **Practical Usage**
The Buffett Indicator is a *macro valuation gauge*.  
It is **not** a short-term timing tool, but can help assess overall market froth or opportunity.

---
## **References**
- [World Bank — Market Cap Data](https://data.worldbank.org/indicator/CM.MKT.LCAP.CD)  
- [World Bank — GDP Data](https://data.worldbank.org/indicator/NY.GDP.MKTP.CD)  
- Buffett, W. (2001). *Fortune Magazine* interview.
---
""")
