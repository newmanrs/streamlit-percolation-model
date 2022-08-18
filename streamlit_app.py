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
    u_N = st.sidebar.number_input(
        "N (Number of sites on X and Y axes)",
        min_value=5,
        value=20,
        max_value=30)

    u_p = st.sidebar.number_input(
        "p (Site occupation fraction)",
        min_value=0.0,
        value=0.593,
        step=0.01,
        format="%0.3f",
        max_value=1.0
        )

    # Kludge to force Nx = Ny
    return u_N, u_N, u_p


def altair_percolation_heatmap(df, u_Nx, u_Ny):

    # May need to scale with u_Nx, u_Ny variables
    chart_rect_width = 500 // max(u_Nx, u_Ny)
    if chart_rect_width == 0:
        chart_rect_width = 1  # min width 1 px

    # chart_title = f"Site lattice percolation Nx = {self.Nx}, " \
    #    f"Ny = {self.Ny}"
    chart_title = ""

    # mark_rect <--> heatmap
    chart = alt.Chart(df).mark_rect().encode(
        x='i:O',
        y='j:O',
        color=alt.Color(
            'cluster site fraction:Q',
            scale=alt.Scale(
                range=['purple', 'yellow', 'white', 'white'],
                domain=[1.0, 0.0001, 0.0001, 0.0]
                )
            ),
        tooltip=['i', 'j', 'cluster site fraction',
                 'cluster size', 'cluster id']

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
        Site percolation simulator on the square lattice.
        '''
        )

    # Reset button ontop of the place where the chart lives
    u_reset = st.button('Reset')

    # This anchors chart to this position
    chartholder = st.empty()  # TODO: try to init to size of fig

    # Alias long names
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
            sim.reinitialize(u_Nx, u_Ny, u_p)
            df = sim.get_chart_df()
            stss.chart = altair_percolation_heatmap(df, u_Nx, u_Ny)

        sim.trial()

        if not hasattr(stss, 'first_render'):
            stss.first_render = True

        # Draw chart
        with chartholder.container():
            df = sim.get_chart_df()
            col = 'cluster site fraction'  # Alias long name
            # pandas round seems to not work on np.float32...
            # so we cast to native float type
            df[col] = df[col].astype(float).round(3)
            stss.chart.data = df

            st.altair_chart(stss.chart, use_container_width=True)

            st.write(f'''
                Largest cluster size is {sim.max_cluster_size},
                spanning {sim.heat_cluster_frac.max().max()*100:.2f}% of
                all sites.
                ''')

    # Text after chart
    st.write(
        r'''

        ## Description

        Lattice positions on the grid are occupied with a given 
        site occupation probability $p$.
        Neighboring sites are considered connected for
        the purposes of clustering if they are both occupied.  Neighboring sites
        are those above, below, left and right (with periodic boundary
        conditions).

        For low values of $p$ the system contains many small clusters,
        and for large values of $p$ the system is dominated by one cluster.
        The main question of interest in these simulations is the 
        phase transition between isolated clusters and a single 
        spanning cluster which occurs near $p=0.593$ 
        ([Ziff 2000](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.85.4104)).

        Hitting the reset button on the simulation at different 
        probabilities in this demo lets you look for the transition 
        between these states.  Spanning 
        clusters are those that possess more than half 
        the sites in the system.  We then look for a $p$ where we expect to observe
        a spanning cluster half of the time and call this the phase transition

        Plotting the probability of finding a spanning cluster for various $p$
        from several trials will reveal a sigmoid curve reaching 50% around 0.593.
        The width of the transition is dependent on the grid size, and narrows
        as N is increased.  In the limit of $N \to \infty$ it should narrow into
        a step function.

        TODO: Precompute and render this graph for N=10, 20, 30 etc. for p = 0.4 to 0.7 by 0.01,
        with at least ten or a hundred replicas per point.

        ''') # noqa : E501


if __name__ == '__main__':

    st.set_page_config(
        page_title='Percolation',
        page_icon='favicon.ico'
        )

    initialize_session_state()
    main_streamlit_page()
