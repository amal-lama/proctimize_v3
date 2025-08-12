import streamlit as st
import pandas as pd
import polars as pl

st.set_page_config(page_title= "ProcTimize", layout = "wide")
st.title("DATA INGESTION")

st.markdown(
    """
    <style>

     /* Sidebar with deep blue gradient */
    section[data-testid="stSidebar"] {
        background-color: #001E96 !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #001E96 !important;
        filter: brightness(1.1);
    }
    </style>
    """, unsafe_allow_html=True)


# Define steps and current step (0-based index)
steps = ["Upload", "Standardize", "Merge", "Filter", "Pivot", "Save"]

if "current_step" not in st.session_state:
    st.session_state["current_step"] = 0

# Calculate progress percentage
progress_percent = int((st.session_state["current_step"] / (len(steps) - 1)) * 100)

# background: linear-gradient(to right, #4f91ff, #007aff);
# Display the progress bar using HTML and CSS
st.markdown(f"""
<style>
.progress-container {{
    width: 100%;
    margin-top: 20px;
}}

.progress-bar {{
    height: 10px;
    background: linear-gradient(to right, #001E96, #007aff);
    border-radius: 10px;
    width: {progress_percent}%;
    transition: width 0.4s ease-in-out;
}}

.track {{
    background-color: #e0e0e0;
    height: 10px;
    width: 100%;
    border-radius: 10px;
    margin-bottom: 10px;
}}

.step-labels {{
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    color: #333;
    font-weight: 600;
    letter-spacing: 0.5px;
}}
</style>

<div class="progress-container">
    <div class="track">
        <div class="progress-bar"></div>
    </div>
    <div class="step-labels">
        {''.join([f"<span>{step}</span>" for step in steps])}
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

col1, col2  = st.columns(2)

with col1:
    st.markdown("Add description of the functionality of this page later")

with col2:

    with st.expander("Upload CSV Files"):
        uploaded_files = st.file_uploader(
            "Select CSV file(s) to upload:",
            type="csv",
            accept_multiple_files=True
        )

    with st.expander("Connect to Azure Blob Storage"):
        st.markdown("This section will allow you to securely connect to " \
        "an Azure Blob Storage account and load files directly.")

        st.subheader("Azure Credentials")
        blob_account_name = st.text_input("Azure Storage Account Name", 
                                          disabled=True, 
                                          placeholder="e.g., mystorageaccount")
        blob_container_name = st.text_input("Container Name",
                                            disabled=True,
                                            placeholder="e.g., marketing-data")
        blob_sas_token = st.text_input("SAS Token", 
                                       type="password", 
                                       disabled=True, 
                                       placeholder="Your secure token")

        st.subheader("File Selection")
        st.selectbox("Browse files in container",
                     options=["-- Coming soon --"], 
                     disabled=True)
        st.button("Refresh File List", disabled=True)

        st.markdown("---")
        st.info("You will be able to load files directly from your " \
        "Azure Blob Storage container using the credentials above.")

        # TO IMPLEMENT LATER:
        # from azure.storage.blob import ContainerClient
        
        # container_url = f"https://{blob_account_name}.blob.core.windows.net/{blob_container_name}?{blob_sas_token}"
        # container_client = ContainerClient.from_container_url(container_url)
        # blobs = [blob.name for blob in container_client.list_blobs()]
        # blob_client = container_client.get_blob_client(blob_name)
        # stream = blob_client.download_blob().readall()
        # df_final = pd.read_csv(io.BytesIO(stream))

    df_final = None
        
tab1, tab2 = st.tabs(["Data Mapping", "Data Profiling"])

# --- DATA MAPPING PAGE ---
with tab1:
    if uploaded_files:
        st.session_state["current_step"] = 1
        st.write(st.session_state["current_step"])
        if len(uploaded_files) == 1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Standardize columns for a single file")
                file = uploaded_files[0]
                df = pd.read_csv(file)
                st.write(f"**Currently editing:** `{file.name}`")
                st.dataframe(df[:3], hide_index=True)

                # Step 1: Column Selection
                selected_cols = st.multiselect(
                    f"Select columns from `{file.name}`:",
                    df.columns.tolist(),
                    default=df.columns.tolist(),
                    key="select_cols_0"
                )
                df = df[selected_cols]

                # Step 2a: Column Renaming
                rename_columns = pd.DataFrame({
                    "Rename columns if necessary": df.columns
                })
                column_config = {
                    "Rename columns if necessary": st.column_config.TextColumn()
                }

                edited_renamed_df = st.data_editor(
                    rename_columns,
                    column_config=column_config,
                    num_rows="fixed",
                    use_container_width=True,
                    key="rename_editor_0",
                    hide_index=True
                )
                rename_dict = dict(zip(
                    df.columns,
                    edited_renamed_df["Rename columns if necessary"]
                ))
                df = df.rename(columns=rename_dict)

                # Step 2b: Date Standardization
                date_cols = st.multiselect(
                    "Select Date Columns (if any):",
                    df.columns.tolist(),
                    key="date_cols_0"
                )
                for date_col in date_cols:
                    date_format = st.selectbox(
                        f"Select current date format for `{date_col}`:",
                        ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"],
                        index=None,
                        key=f"date_format_0_{date_col}"
                    )
                    if date_format:
                        try:
                            df[date_col] = pd.to_datetime(
                                df[date_col],
                                format=date_format,
                                errors='coerce'
                            )
                            st.success(f"Date column `{date_col}` standardized!")
                        except Exception as e:
                            st.error(f"Failed to parse `{date_col}`: {e}")

                # Final clean-up
                str_cols = df.select_dtypes(include=["object", "string"]).columns
                df[str_cols] = df[str_cols].fillna("")

                st.session_state["df_final"] = df
                st.session_state["current_step"] = 3

            with col2:
                st.markdown("### Final Preview")
                st.dataframe(df, hide_index=True)

        else:
            st.markdown("### Standardize columns for multiple files")
            renamed_columns_list = []

            for i, file in enumerate(uploaded_files):
                col1, col2 = st.columns([2, 3])
                with col1:
                    with st.expander(f"**Currently editing:** `{file.name}`"):
                        df = pd.read_csv(file)
                        st.dataframe(df[:3], hide_index=True)

                        selected_cols = st.multiselect(
                            f"Select columns from `{file.name}`:",
                            df.columns.tolist(),
                            default=df.columns.tolist(),
                            key=f"select_cols_{i}"
                        )
                        df = df[selected_cols]

                        rename_columns = pd.DataFrame({
                            "Rename columns if necessary": df.columns
                        })
                        column_config = {
                            "Rename columns if necessary": st.column_config.TextColumn()
                        }

                        edited_renamed_df = st.data_editor(
                            rename_columns,
                            column_config=column_config,
                            num_rows="fixed",
                            use_container_width=True,
                            key=f"rename_editor_{i}",
                            hide_index=True
                        )
                        rename_dict = dict(zip(
                            df.columns,
                            edited_renamed_df["Rename columns if necessary"]
                        ))
                        df = df.rename(columns=rename_dict)
                        renamed_columns_list.append(set(df.columns))

                        date_cols = st.multiselect(
                            f"Select Date Columns (if any) for `{file.name}`:",
                            df.columns.tolist(),
                            key=f"date_cols_{i}"
                        )
                        for date_col in date_cols:
                            date_format = st.selectbox(
                                f"Select format for `{date_col}`:",
                                ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"],
                                index=None,
                                key=f"date_format_{i}_{date_col}"
                            )
                            if date_format:
                                try:
                                    df[date_col] = pd.to_datetime(
                                        df[date_col],
                                        format=date_format,
                                        errors='coerce'
                                    )
                                    st.success(f"Standardized `{date_col}`!")
                                except Exception as e:
                                    st.error(f"Could not parse `{date_col}`: {e}")

                        str_cols = df.select_dtypes(include=["object", "string"]).columns
                        df[str_cols] = df[str_cols].fillna("")
                        
                        if "df_final_list" not in st.session_state:
                            st.session_state["df_final_list"] = []

                        if len(st.session_state["df_final_list"]) <= i:
                            st.session_state["df_final_list"].append(df)
                        else:
                            st.session_state["df_final_list"][i] = df
                
                st.session_state["current_step"] = 2    

                with col2:
                    st.markdown(f"**Data Frame Preview**: `{file.name}`")
                    st.dataframe(df, hide_index=True)
                # col1, col2, col3, col4 = st.columns(4)

                # with col1:
                #     st.markdown(f"#### `{file.name}` Preview")
                #     df = pd.read_csv(file)
                #     st.dataframe(df.head(3), hide_index=True)

                # with col2:
                #     selected_cols = st.multiselect(
                #         f"Select columns from `{file.name}`:",
                #         df.columns.tolist(),
                #         default=df.columns.tolist(),
                #         key=f"select_cols_{i}"
                #     )
                #     df = df[selected_cols]

                #     rename_columns = pd.DataFrame({
                #         "Rename columns if necessary": df.columns
                #     })
                #     column_config = {
                #         "Rename columns if necessary": st.column_config.TextColumn()
                #     }

                #     edited_renamed_df = st.data_editor(
                #         rename_columns,
                #         column_config=column_config,
                #         num_rows="fixed",
                #         use_container_width=True,
                #         key=f"rename_editor_{i}",
                #         hide_index=True
                #     )
                #     rename_dict = dict(zip(
                #         df.columns,
                #         edited_renamed_df["Rename columns if necessary"]
                #     ))
                #     df = df.rename(columns=rename_dict)
                #     renamed_columns_list.append(set(df.columns))

                # with col3:
                #     date_cols = st.multiselect(
                #         f"Select Date Columns (if any) for `{file.name}`:",
                #         df.columns.tolist(),
                #         key=f"date_cols_{i}"
                #     )
                #     for date_col in date_cols:
                #         date_format = st.selectbox(
                #             f"Format for `{date_col}`:",
                #             ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"],
                #             index=None,
                #             key=f"date_format_{i}_{date_col}"
                #         )
                #         if date_format:
                #             try:
                #                 df[date_col] = pd.to_datetime(df[date_col], format=date_format, errors='coerce')
                #                 st.success(f"Standardized `{date_col}`")
                #             except Exception as e:
                #                 st.error(f"Could not parse `{date_col}`: {e}")

                # with col4:
                #     str_cols = df.select_dtypes(include=["object", "string"]).columns
                #     df[str_cols] = df[str_cols].fillna("")
                    
                #     if "df_final_list" not in st.session_state:
                #         st.session_state["df_final_list"] = []

                #     if len(st.session_state["df_final_list"]) <= i:
                #         st.session_state["df_final_list"].append(df)
                #     else:
                #         st.session_state["df_final_list"][i] = df

                #     st.markdown(f"**Final Preview:** `{file.name}`")
                #     st.dataframe(df, hide_index=True)



            with st.expander("Merge Files"):
                st.subheader("Select Merge Strategy")

                common_columns = set.intersection(*renamed_columns_list)
                merge_strategy = st.radio("Merge type:", ["Vertical Stack", "Horizontal Join"])
                
                if merge_strategy == "Horizontal Join":
                    join_keys = st.multiselect("Select join key(s):", list(common_columns))
                    join_type = st.selectbox("Join type:", ["inner", "left", "right", "outer"])
                else:
                    join_keys = join_type = None

                if st.button("Merge"):
                    if merge_strategy in ["vertical", "Vertical Stack"]:
                        df_final = pd.concat(st.session_state["df_final_list"], ignore_index=True, sort=False)

                    elif merge_strategy in ["horizontal", "Horizontal Join"]:
                        if not join_keys:
                            st.warning("Join key must be provided for horizontal joins.")
                            st.stop()
                        df_final = st.session_state["df_final_list"][0]
                        for df in st.session_state["df_final_list"][1:]:
                            df_final = pd.merge(df_final, df, on=join_keys, how=join_type)
                    else:
                        st.error("Invalid merge strategy. Choose 'vertical' or 'horizontal'.")
                        st.stop()

                    # Post-processing: cleanup and standardize date columns
                    if join_keys:
                        for col_name in join_keys:
                            if col_name in df_final.columns:
                                df_final = df_final[df_final[col_name].notnull()]
                    else:
                        print("No join_keys provided — skipping null identifier filtering.")

                    for col in df_final.select_dtypes(include="object").columns:
                        if "date" in col.lower():
                            try:
                                df_final[col] = pd.to_datetime(df_final[col], errors='coerce')
                            except:
                                pass

                    df_final = pl.from_pandas(df_final)
                    df_final = df_final.with_columns([
                        pl.col(col).cast(pl.Date)
                        for col, dtype in zip(df_final.columns, df_final.dtypes)
                        if dtype == pl.Datetime
                    ])

                    st.session_state["df_final"] = df_final
                    st.markdown("### Final Data Frame")
                    st.dataframe(df_final)
                st.session_state["current_step"] = 3
                    