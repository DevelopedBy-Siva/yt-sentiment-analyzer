import pandas as pd
from datetime import datetime, timezone
import altair as alt


SAMPLE_URL = "https://www.youtube.com/watch?v=X3paOmcrTjQ"


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

    st.subheader(f":blue[{info['video_name']}]")
    st.markdown(f"*- {info['channel_title']}*")
    new_line(st, 3)

    info_col1, info_col2, info_col3 = st.columns(3)
    info_col1.metric("Views", format_large_number(info["views"]))
    info_col2.metric("Likes", format_large_number(info["likes"]))
    info_col3.metric("Comments", format_large_number(comments_count))
    new_line(st, 3)


def parse_comments_dataset(st, comments_df):
    """
    :param st: Streamlit object
    :param comments_df: comments dataframe
    """

    st.markdown("##### Dataset to Analyze")
    new_line(st)

    selected_columns = ['comment', 'likes']
    sorted_df = comments_df.sort_values(by='likes', ascending=False)
    st.dataframe(sorted_df[selected_columns], width=2000)


def plot_comments_replies_trend(st, comments_df, replies_df):
    """
    :param st: Streamlit object
    :param comments_df: comments dataframe
    :param replies_df: replies dataframe
    :return: None
    """
    new_line(st)

    # Create a fake dataframe with current timestamp
    fake_data = [{
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }]
    fake_data_df = pd.DataFrame(fake_data)
    fake_data_df["timestamp"] = pd.to_datetime(fake_data_df["timestamp"])

    # Combine comments, replies & fake dataframes
    merged_df = pd.concat([comments_df, replies_df, fake_data_df])
    resampled_df = merged_df.resample('M', on='timestamp').count().reset_index()

    # DataFrame for Altair plotting
    melted_df = pd.melt(resampled_df, id_vars=['timestamp'], value_vars=['comment', 'reply'],
                        var_name='parameter', value_name='count')

    # Plot graph for comments and replies
    chart_comments_replies = alt.Chart(melted_df).mark_line().encode(
        x='timestamp:T',
        y='count:Q',
        color='parameter:N',
    ).interactive()

    # Plot graph for comments alone
    chart_comments_alone = alt.Chart(melted_df[melted_df['parameter'] == 'comment']).mark_line().encode(
        x='timestamp:T',
        y='count:Q',
    ).interactive()

    st.markdown("##### User Interaction Over Time")
    st.caption("This chart visually represents the trend of user interaction, "
               "showcasing the ebb and flow of comments and replies over the selected time period.")
    new_line(st)

    # Create two columns as tabs
    col1, col2 = st.tabs(["Comments & Replies", "Comments"])

    # Display charts based on the selected tab
    with col1:
        new_line(st, 2)
        st.altair_chart(chart_comments_replies, use_container_width=True)
    with col2:
        new_line(st, 2)
        st.altair_chart(chart_comments_alone, use_container_width=True)
    new_line(st, 3)
