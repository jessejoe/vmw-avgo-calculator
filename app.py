import requests
import streamlit as st
import pandas as pd


@st.cache_data
def get_current_price(stock):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock}"
    headers = {"User-Agent": "testing"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    current_price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
    print(f'Fetched price for {stock}: {current_price}')
    return current_price


# Hide the Streamlit menu - https://docs.streamlit.io/knowledge-base/using-streamlit/how-hide-hamburger-menu-app
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Initalize dynamic variables
if "total_vmw_shares" not in st.session_state:
    st.session_state.total_vmw_shares = 165
if "vmw_cur_price" not in st.session_state:
    st.session_state.vmw_cur_price = get_current_price("VMW")
if "avgo_cur_price" not in st.session_state:
    st.session_state.avgo_cur_price = get_current_price("AVGO")
if "percent_cash" not in st.session_state:
    st.session_state.percent_cash = 50
if "percent_stock" not in st.session_state:
    st.session_state.percent_stock = 50
if "vmw_fall_price" not in st.session_state:
    st.session_state.vmw_fall_price = 115.0

# Calculate the rest of the variables
vmw_fall_url = "https://seekingalpha.com/news/3957771-vmware-potential-deal-price-break-raised-to-115-from-100-at-ubs"
current_value = st.session_state.total_vmw_shares * st.session_state.vmw_cur_price
potential_value = (st.session_state.total_vmw_shares *
                   (st.session_state.percent_cash * .01) *
                   142.5) + (st.session_state.total_vmw_shares *
                             (st.session_state.percent_stock * .01) *
                             (st.session_state.avgo_cur_price * 0.252))
potential_gain = potential_value - current_value
potential_gain_percent = potential_gain / current_value
avgo_break_even_price = (current_value -
                         (st.session_state.total_vmw_shares *
                          (st.session_state.percent_cash * .01) * 142.5)) / (
                              st.session_state.total_vmw_shares *
                              (st.session_state.percent_stock * .01) * 0.252)
deal_fails_value = st.session_state.total_vmw_shares * st.session_state.vmw_fall_price
loss_vs_current = current_value - deal_fails_value
loss_vs_current_percent = loss_vs_current / current_value

## Layout and display elements
col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

with col2:
    with st.form(key="my_form"):
        st.number_input(
            "Total VMW shares:",
            key="total_vmw_shares",
            min_value=1,
        )
        st.number_input(
            "Current VMW price:",
            key="vmw_cur_price",
            min_value=0.01,
            step=1.0,
        )
        st.number_input(
            "Current AVGO price:",
            key="avgo_cur_price",
            min_value=0.01,
            step=1.0,
        )
        st.divider()
        # st.warning("These probably won't change")
        percent_cash_input = st.number_input("% cash:",
                                             key="percent_cash",
                                             min_value=1,
                                             max_value=100,
                                             format='%d')
        percent_stock_input = st.number_input(
            "% stock:",
            key="percent_stock",
            min_value=1,
            max_value=100,
        )
        st.number_input(
            f"[VMW price if deal falls through]({vmw_fall_url}):",
            key="vmw_fall_price",
            min_value=0.01,
            step=1.0,
        )
        submitted = st.form_submit_button(label="Submit")
        if submitted:
            if (percent_cash_input + percent_stock_input) != 100:
                st.error('% stock and % cash must equal 100')
                st.stop()

with col3:
    # Prefer tabular layout, but no real way to get rid of headers and can't use tooltips
    #     st.write(f'''<table>
    # <tr><td>Total current value</td><td><code>${current_value:,.2f}</code></td></tr>
    # <tr><td>Total potential value</td><td><code>${potential_value:,.2f}</code></td></tr>
    # <tr><td>Gain by waiting</td><td><code>${potential_gain:,.2f} ({potential_gain_percent:.2%})</code></td></tr>
    # <tr><td>AVGO break even price</td><td><code>${avgo_break_even_price:.2f}</code></td></tr>
    # <tr><td>Value if deal fails</td><td><code>${deal_fails_value:,.2f}</code></td></tr>
    # <tr><td>Loss vs. current</td><td><code>${loss_vs_current:,.2f} ({loss_vs_current_percent:.2%})</code></td></tr>
    # </table>''', unsafe_allow_html=True)
    st.markdown(f"""Total current value:  
`${current_value:,.2f}`""",
                help='Current value if you sold all your VMW shares today')
    st.markdown(
        f"""Total potential value:  
`${potential_value:,.2f}`""",
        help='Value of a split of AVGO and VMW if the deal closed today')
    st.markdown(f"""Gain by waiting:  
`${potential_gain:,.2f}` (`{potential_gain_percent:.2%}`)""",
                help='Gain (or loss) if you waited and the deal closed today')
    st.markdown(
        f"""AVGO break even price:  
`${avgo_break_even_price:.2f}`""",
        help=
        'Price AVGO would need to fall to to make it beneficial to sell before the deal closes'
    )
    st.markdown(f"""Value if deal fails:  
`${deal_fails_value:,.2f}`""",
                help='Value of stock if deal falls through')
    st.markdown(f"""Loss vs. current:  
`${loss_vs_current:,.2f}` (`{loss_vs_current_percent:.2%}`)""",
                help="Difference between current value and value if deal fails")

# Doesn't seem to be an easy way to center things, so use HTML
st.write(
    '<p style="text-align: center;"><a href="https://github.com/jessejoe/vmw-avgo-calculator">Source</a></p>',
    unsafe_allow_html=True)
