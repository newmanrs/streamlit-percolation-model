import numpy as np
import streamlit as st
import altair as alt

from percolation import PercolationSimulation


def initialize_session_state():

    # Initialize one simulation per user session
    if 'sim' not in st.session_state:
        st.session_state['sim'] = PercolationSimulation()

def config_streamlit_sidebar():

    # Streamlit sidebar vars can be updated at any time by user.
    # u_ prefix these variables
    u_Nx = st.sidebar.number_input(
        "Nx (Sites on X axis)",
        min_value=5,
        value=20,
        max_value=30)

    u_Ny = st.sidebar.number_input(
        "Ny (Sites on Y axis)",
        min_value=5,
        value=20,
        max_value=30)

    u_p = st.sidebar.number_input(
        "p (Site occupation fraction)",
        min_value=0.0,
        value=0.593,
        max_value=1.0
        )

    return u_Nx, u_Ny, u_p

def altair_percolation_heatmap(df, u_Nx, u_Ny):

    # May need to scale with u_Nx, u_Ny variables
    chart_rect_width = 500 // max(u_Nx, u_Ny)
    if chart_rect_width == 0:
        chart_rect_width = 1 # min width 1 px


    #chart_title = f"Site lattice percolation Nx = {self.Nx}, " \
    #    f"Ny = {self.Ny}"
    chart_title = ""

    # mark_rect <--> heatmap
    chart = alt.Chart(df).mark_rect().encode(
        x='i:O',
        y='j:O',
        color=alt.Color('cluster site fraction:Q',
            scale=alt.Scale(
                range=['purple','yellow', 'white','white'],
                domain=[1.0, 0.0001, 0.0001, 0.0]
                )
            ),
        tooltip=['i', 'j', 'cluster site fraction', 'cluster size', 'cluster id']
    ).properties(
        height={'step': chart_rect_width},
        width={'step': chart_rect_width},
        title=chart_title
    ).configure_scale(
        # Gap between rectangles
        bandPaddingInner=0.1
    ).configure_title(
        fontSize=16,
        anchor='start'
    )

    return chart

def main_streamlit_page():

    u_Nx, u_Ny, u_p = config_streamlit_sidebar()

    # Header
    st.title("Site Percolation")

    st.write(
        r'''
        Site percolation demo simulator on the square lattice.
        '''
        )

    u_reset = st.button('Reset')

    # This anchors chart to this position
    chartholder = st.empty()

    stss = st.session_state
    sim = st.session_state.sim

    # redraw chart on load, or on ui changes
    if u_reset \
        or not hasattr(stss, 'first_render') \
        or sim.Nx != u_Nx \
        or sim.Ny != u_Ny \
        or sim.p != u_p:

        # Reinitialize simulation on user state change
        if sim.Nx != u_Nx or sim.Ny != u_Ny or sim.p != u_p:
            sim.reinitialize(u_Nx,u_Ny,u_p)
            df = sim.get_chart_df()
            stss.chart = altair_percolation_heatmap(df,u_Nx, u_Ny)

        sim.trial()

        if not hasattr(stss, 'first_render'):
            stss.first_render=True

        # Draw chart
        with chartholder.container():
            df = sim.get_chart_df()

            df['cluster site fraction'] = df['cluster site fraction'].astype(float).round(3)
            stss.chart.data = df

            st.altair_chart(stss.chart,use_container_width=True)

    # Text after chart
    st.write(
        r'''
        Post text
        ''') # noqa : E501

    st.write(f'''
        Largest cluster size is {sim.max_cluster_size}
        ''')

    for _ in range(100):
        st.write(" ")

if __name__ == '__main__':

    initialize_session_state()
    main_streamlit_page()
