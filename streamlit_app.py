import numpy as np
import streamlit as st

from percolation import PercolationSimulation



def render_streamlit():


    # Streamlit sidebar vars can be updated at any time by user.
    # u_ prefix for these.
    u_Nx = st.sidebar.number_input(
        "Nx (Sites on X axis)",
        min_value=3,
        value=20,
        max_value=400)

    u_Ny = st.sidebar.number_input(
        "Ny (Sites on Y axis)",
        min_value=3,
        value=20,
        max_value=400)

    u_p = st.sidebar.number_input(
        "p (Site occupation fraction)",
        min_value=0.0,
        value=0.593,
        max_value=1.0
        )


    # Initialize one simulation per user session
    if 'sim' not in st.session_state:
        st.session_state['sim'] = PercolationSimulation(u_Nx, u_Ny, u_p)

    # Header
    st.title("Site Percolation on the Square Lattice")

    st.write(
        r'''
        Site percolation on square lattice better write up some documentation here.
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

        if sim.Nx != u_Nx or sim.Ny != u_Ny or sim.p != u_p:
            sim.reinitialize(u_Nx,u_Ny,u_p)
        sim.trial()

        if not hasattr(stss, 'first_render'):
            stss.first_render=True
        # Draw chart
        with chartholder.container():
            st.altair_chart(sim.get_chart(),use_container_width=True)

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

    render_streamlit()
