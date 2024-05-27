import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RectangleSelector

recipient = False
def build_graph(db_name):
    SORT_BY = 'blockNumber'

    def fetch_all_nonce_zero_transactions():
        # Connect to the db_name
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        # Fetch all transactions with nonce = 0, including additional fields and the hash
        query = """
            SELECT hash, address, MIN(blockNumber) as min_block, value, methodId, timeStamp, sender, recipient
            FROM transactions WHERE nonce = 0
        """
        params = ()
        if recipient:
            query += " AND recipient = ?"
            params = (recipient,)
        query += " GROUP BY address"
        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()
        return data

    all_nonce_zero_transactions = fetch_all_nonce_zero_transactions()
    df = pd.DataFrame(all_nonce_zero_transactions,
                      columns=['hash', 'address', 'blockNumber', 'value', 'methodId', 'timeStamp', 'sender',
                               'recipient'])
    # Sort the DataFrame by timestamp
    df = df.sort_values(by=SORT_BY)

    chunk_size = 100000  # Adjust the chunk size as needed
    num_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size != 0 else 0)

    fig, ax = plt.subplots(figsize=(15, 10))
    sc = None

    # Define the current_chunk variable as global
    global current_chunk
    current_chunk = 0

    def plot_chunk(chunk_index):
        nonlocal sc
        start_index = chunk_index * chunk_size
        end_index = min((chunk_index + 1) * chunk_size, len(df))
        chunk_df = df.iloc[start_index:end_index]

        ax.clear()
        sc = ax.scatter(chunk_df[SORT_BY], range(len(chunk_df['address'])), picker=True)
        ax.set_ylabel('Address index')
        ax.set_xlabel('past <TIME> future')
        ax.set_title(f'Very first txn of each address sorted by time (Chunk {chunk_index + 1}/{num_chunks})')
        fig.canvas.draw()

    def on_prev_click(event):
        global current_chunk
        if current_chunk > 0:
            current_chunk -= 1
            plot_chunk(current_chunk)

    def on_next_click(event):
        global current_chunk
        if current_chunk < num_chunks - 1:
            current_chunk += 1
            plot_chunk(current_chunk)

    # Create navigation buttons
    ax_prev = plt.axes((0.7, 0.01, 0.1, 0.075))
    ax_next = plt.axes((0.81, 0.01, 0.1, 0.075))
    btn_prev = Button(ax_prev, 'Previous')
    btn_next = Button(ax_next, 'Next')

    # Connect the button click events
    btn_prev.on_clicked(on_prev_click)
    btn_next.on_clicked(on_next_click)

    # Rectangle Selector for selecting points
    # Rectangle Selector for selecting points
    def onselect(eclick, erelease):
        """eclick and erelease are matplotlib events at press and release."""
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata

        # Find points within the selected rectangle
        start_index = current_chunk * chunk_size
        end_index = min((current_chunk + 1) * chunk_size, len(df))
        chunk_df = df.iloc[start_index:end_index]

        mask = (chunk_df[SORT_BY] >= min(x1, x2)) & (chunk_df[SORT_BY] <= max(x1, x2))
        selected_data = chunk_df[mask]

        # Print each element from the selected data with a prefix in Markdown format
        for index, row in selected_data.iterrows():
            # Convert the timestamp to human-readable UTC format
            utc_time = datetime.utcfromtimestamp(int(row['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S')

            # Format each field with a fixed width
            hash_field = f"[link-to-txn](https://arbiscan.io/tx/{row['hash']})"
            profile_field = f"[debank-profile](https://debank.com/profile/{row['address']})"
            utc_time_field = f"{utc_time} UTC"
            sender_field = f"{row['sender']:<42}"
            recipient_field = f"{row['recipient']:<42}"
            value_field = f"{float(row['value']):.12f}"
            block_number_field = f"{row['blockNumber']:<10}"
            method_id_field = f"{row['methodId']:<10}"

            # Print the formatted output in a single row
            print(f"{hash_field:<40} | "
                  f"{profile_field:<40} | {utc_time_field:<20} | value : {value_field} | {sender_field} > {recipient_field} | "
                  f"blockNumber : {block_number_field} | methodId: {method_id_field}<br>")

    rect_selector = RectangleSelector(ax, onselect, useblit=True, button=[1], minspanx=5, minspany=5,
                                      spancoords='pixels', interactive=True)


    # Plot the first chunk
    plot_chunk(current_chunk)

    plt.tight_layout()
    plt.show()


# Example usage
build_graph('transactions_ARB_light.db')
