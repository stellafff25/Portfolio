import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

area_names = {
    "1": "Vinnytsia r.",
    "2": "Volyn r.",
    "3": "Dnipro r.",
    "4": "Donetsk r.",
    "5": "Zhytomyr r.",
    "6": "Zakarpattia r.",
    "7": "Zaporizhzhia r.",
    "8": "Ivano-Frankivsk r.",
    "9": "Kyiv r.",
    "10": "Kirovohrad r.",
    "11": "Luhansk r.",
    "12": "Lviv r.",
    "13": "Mykolaiv r.",
    "14": "Odesa r.",
    "15": "Poltava r.",
    "16": "Rivne r.",
    "17": "Sumy r.",
    "18": "Ternopil r.",
    "19": "Kharkiv r.",
    "20": "Kherson r.",
    "21": "Khmelnytshyi r.",
    "22": "Cherkasy r.",
    "23": "Chernivtsi r.",
    "24": "Chernihiv r.",
    "25": "AR Crimea",
    "26": "Kyiv c.",
    "27": "Sevastopol c."
}

# Load data
def load_data():
    data = pd.read_csv('../../data.csv')
    return data

# Filter data
def filter_data(data, area, years, weeks):
    return data[
        (data['area'] == area) &
        (data['Year'].between(years[0], years[1])) &
        (data['Week'].between(weeks[0], weeks[1]))
    ]

# Main application
def main():
    st.title("Analysis of VCI, TCI, and VHI indices")

    # Load data
    data = load_data()
    if data is None:
        st.stop()

    # Replace area codes with region names
    data['area'] = data['area'].astype(str)
    data['area_name'] = data['area'].map(area_names)

    # Default filter values
    default_index = "VCI"
    default_area = list(area_names.values())[6]
    default_year_range = (1988, 2002)
    default_week_range = (9, 10)

    # Initialize values
    st.session_state.selected_index = default_index
    st.session_state.selected_area = default_area
    st.session_state.year_range = default_year_range
    st.session_state.week_range = default_week_range

    # Two columns for filters and graph
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Filters")

        # Reset button
        if st.button("Reset filters"):
            st.session_state.selected_index = default_index
            st.session_state.selected_area = default_area
            st.session_state.year_range = default_year_range
            st.session_state.week_range = default_week_range

        # Filter components
        st.session_state.selected_index = st.selectbox(
            "Select index", ["VCI", "TCI", "VHI"], index=["VCI", "TCI", "VHI"].index(st.session_state.selected_index)
        )
        st.session_state.selected_area = st.selectbox(
            "Select region", options=list(area_names.values()), index=list(area_names.values()).index(st.session_state.selected_area)
        )
        selected_area_code = [k for k, v in area_names.items() if v == st.session_state.selected_area][0]
        st.session_state.year_range = st.slider(
            "Select year range", int(data['Year'].min()), int(data['Year'].max()), st.session_state.year_range
        )
        st.session_state.week_range = st.slider(
            "Select week range", 1, 52, st.session_state.week_range
        )

    # Filtered data
    filtered_data = filter_data(data, selected_area_code, st.session_state.year_range, st.session_state.week_range)

    # Tabs for table and charts
    with col2:
        tab1, tab2, tab3 = st.tabs(["Table", "Chart 1", "Chart 2"])

        with tab1:
            st.header("Table")

            # Select index from dropdown
            selected_index = st.session_state.selected_index

            # Filter data for selected index
            table_data = filtered_data[["Year", "Week", "SMN", "SMT", selected_index]]

            # Initialize sorting state
            if "ascending_order" not in st.session_state:
                st.session_state["ascending_order"] = True
            if "descending_order" not in st.session_state:
                st.session_state["descending_order"] = False

            # Sorting checkboxes
            def toggle_ascending():
                if st.session_state["ascending_order"]:
                    st.session_state["descending_order"] = False

            def toggle_descending():
                if st.session_state["descending_order"]:
                    st.session_state["ascending_order"] = False

            ascending_order = st.checkbox(
                "Sort ascending",
                value=st.session_state["ascending_order"],
                key="ascending_order",
                on_change=toggle_ascending
            )

            descending_order = st.checkbox(
                "Sort descending",
                value=st.session_state["descending_order"],
                key="descending_order",
                on_change=toggle_descending
            )

            # Define sorting order
            order = ascending_order and not descending_order

            # Sort data by selected index
            sorted_table_data = table_data.sort_values(by=selected_index, ascending=order)

            # Display table
            if sorted_table_data.empty:
                st.warning("No data available!")
            else:
                st.dataframe(sorted_table_data)

        with tab2:
            st.header("Chart")
            if filtered_data.empty:
                st.warning("No data available!")
            else:
                fig, ax = plt.subplots()
                ax.plot(filtered_data['Year'] + filtered_data['Week'] / 52, filtered_data[st.session_state.selected_index], color="purple")
                ax.set_title(f"{st.session_state.selected_index} for {st.session_state.selected_area}")
                ax.set_xlabel("Year")
                ax.set_ylabel(st.session_state.selected_index)
                ax.grid(True)
                st.pyplot(fig)

        with tab3:
            st.header("Comparison with other regions")
            comparison_data = data[
                (data['Year'].between(st.session_state.year_range[0], st.session_state.year_range[1])) &
                (data['Week'].between(st.session_state.week_range[0], st.session_state.week_range[1]))
                ]
            if comparison_data.empty:
                st.warning("No data available for comparison!")
            else:
                # Calculate mean values for each region
                mean_values = comparison_data.groupby('area_name')[st.session_state.selected_index].mean().sort_values()

                fig, ax = plt.subplots(figsize=(10, 6))
                mean_values.plot(kind="bar", ax=ax, color="skyblue")
                ax.set_title(f"Average {st.session_state.selected_index} (all regions)")
                ax.set_ylabel(st.session_state.selected_index)
                ax.set_xlabel("Regions")
                ax.axhline(
                    mean_values.loc[st.session_state.selected_area],
                    color="red", linestyle="--",
                    label=f"{st.session_state.selected_area}"
                )
                ax.legend()
                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig)

if __name__ == "__main__":
    main()