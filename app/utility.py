def new_line(st=None, count=1):
    """
    :param st: Streamlit object
    :param count: new line count
    """
    if not st:
        return
    for _ in range(count):
        st.write("\n")
