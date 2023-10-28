SAMPLE_URL = "https://www.youtube.com/watch?v=G7d5RTMcTV4"


def new_line(st=None, count=1):
    """
    :param st: Streamlit object
    :param count: new line count
    """
    if not st:
        return
    for _ in range(count):
        st.write("\n")


def format_large_number(number):
    """
    Format a large number to display in terms of 'K' or 'M'.
    """
    if abs(number) >= 1.0e6:
        return f"{number / 1.0e6:.1f} M"
    elif abs(number) >= 1.0e3:
        return f"{number / 1.0e3:.1f} K"
    else:
        return str(number)


def parse_info(st, info, comments_count=0):
    """
    :param st: Streamlit object
    :param info: Video details
    :param comments_count: length of comments
    """
    if not st or not info:
        return

    st.subheader(f":green[{info['video_name']}]")
    new_line(st)

    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    info_col1.metric("Channel", info["channel_title"])
    info_col2.metric("Views", format_large_number(info["views"]))
    info_col3.metric("Likes", format_large_number(info["likes"]))
    info_col4.metric("Comments", format_large_number(comments_count))
    new_line(st, 3)


def parse_comments_dataset(st, comments_df):
    """
    :param st: Streamlit object
    :param comments_df: comments dataframe
    """

    st.markdown("#### Sample Dataset")
    new_line(st)

    st.dataframe(comments_df.head(100))

