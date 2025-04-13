import streamlit as st
import datetime
from main import run_eod, run_sprint_review
import logging
import io
from streamlit.runtime.scriptrunner import StopException
from contextlib import redirect_stdout

# Configure page settings
st.set_page_config(
    page_title="EOD & Sprint Review Generator",
    page_icon="📝",
    layout="centered"
)

def capture_logs_and_output(func, *args, **kwargs):
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    stdout_stream = io.StringIO()

    try:
        with redirect_stdout(stdout_stream):
            result = func(*args, **kwargs)

        logs = log_stream.getvalue()
        output = stdout_stream.getvalue()

        return logs, output, result
    finally:
        root_logger.removeHandler(handler)

# Initialize session states safely
def initialize_session_states():
    if 'app_initialized' not in st.session_state:
        logging.info("First time initialization of session states")
        defaults = {
            'sprint_step': 1,
            'start_date': (datetime.datetime.now() - datetime.timedelta(days=14)).date(),
            'end_date': datetime.datetime.now().date(),
            'tickets_text': "",
            'form_submitted': False,
            'app_initialized': True
        }
        for key, val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = val
    else:
        logging.info("Session already initialized")

# Reset all session states
def reset_states():
    keys_to_reset = [
        'sprint_step',
        'start_date',
        'end_date',
        'tickets_text',
        'form_submitted',
        'app_initialized'
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    logging.info("All session states reset")

# Main Application

def main():
    initialize_session_states()

    st.title("EOD & Sprint Review Generator")
    st.write("Choose an option below to generate your report.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        eod_button = st.button("Generate End of Day Report", key="eod_btn", use_container_width=True)
        sprint_button = st.button("Generate Sprint Review", key="sprint_btn", use_container_width=True)
        st.write("")
        quit_button = st.button("Exit Application", key="quit_btn", type="primary", use_container_width=True)

    if eod_button:
        st.divider()
        st.subheader("Generating End of Day Report")
        with st.spinner("Generating EOD report..."):
            logs, output, result = capture_logs_and_output(run_eod)

            with st.expander("View Logs", expanded=False):
                st.text_area("Execution Logs", value=logs, height=200)

            if result:
                st.markdown("### Generated Report")
                st.code(result, language="text")
                st.download_button(
                    "📥 Download Report",
                    result,
                    file_name=f"eod_report_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )

    elif sprint_button:
        st.divider()
        st.subheader("Generate Sprint Review")

        col_home, _ = st.columns([6, 1])
        with _:
            if st.button("🏠 Home", key="home_btn"):
                logging.info("Home button clicked - resetting states")
                reset_states()
                st.session_state.initialized = False  # Reset initialization
                st.rerun()

        step = st.session_state.sprint_step

        if step == 1:
            logging.info("Rendering Step 1")
            logging.info(f"Current step: {step}")
            st.write("### Step 1: Select Sprint Start Date")
            
            # Create a container for the date selection UI
            date_container = st.container()
            logging.info(f"Current step: {step}")
            with date_container:
                with st.form(key="sprint_start_form", clear_on_submit=False):
                    # Store current date for comparison
                    logging.info(f"Current step: {step}")
                    current_date = st.session_state.start_date
                    
                    # Date input
                    start_date = st.date_input(
                        "Sprint Start Date",
                        value=current_date,
                        max_value=datetime.datetime.now().date(),
                        key="start_date_input"
                    )
                    logging.info(f"Current step: {step}")
                    # Form submit button
                    submitted = st.form_submit_button("Next Step")
                    
                    if submitted:
                        try:
                            logging.info(f"Current step: {step}")
                            logging.info(f"Form submitted - Date selected: {start_date}")
                            st.session_state.start_date = start_date
                            st.session_state.form_submitted = True
                            
                            # Only update end date if needed
                            if st.session_state.end_date < start_date:
                                st.session_state.end_date = start_date
                                
                            st.session_state.sprint_step = 2
                            logging.info(f"Current step: {step}")
                            logging.info("Moving to step 2")
                            st.experimental_rerun()
                            
                        except Exception as e:
                            logging.error(f"Error processing form: {str(e)}")
                            st.error("Failed to proceed to next step")

        elif step == 2:
            logging.info(f"Current step: {step}")
            st.write("### Step 2: Select Sprint End Date")
            st.info(f"Selected Start Date: {st.session_state.start_date}")
            end_date = st.date_input("Sprint End Date", st.session_state.end_date, min_value=st.session_state.start_date, max_value=datetime.datetime.now().date())

            col_back, col_next = st.columns([1, 2])
            with col_back:
                if st.button("← Back"):
                    st.session_state.sprint_step = 1
                    st.rerun()

            with col_next:
                if st.button("Next →"):
                    st.session_state.end_date = end_date
                    st.session_state.sprint_step = 3
                    st.rerun()

        elif step == 3:
            st.write("### Step 3: Enter Ticket Information")
            st.info(f"Sprint Period: {st.session_state.start_date} to {st.session_state.end_date}")

            tickets_text = st.text_area("Enter your ticket information below (one per line):", value=st.session_state.tickets_text, height=150)
            st.session_state.tickets_text = tickets_text

            col_back, col_generate = st.columns([1, 2])
            with col_back:
                if st.button("← Back"):
                    st.session_state.sprint_step = 2
                    st.rerun()

            with col_generate:
                if st.button("Generate Sprint Review"):
                    if not tickets_text.strip():
                        st.error("Please enter at least one ticket.")
                        return
                    tickets = [ticket.strip() for ticket in tickets_text.split('\n') if ticket.strip()]
                    
                    # Log the processed input data
                    logging.info(f"Processing sprint review with:")
                    logging.info(f"Start date: {st.session_state.start_date.strftime('%Y-%m-%d')}")
                    logging.info(f"End date: {st.session_state.end_date.strftime('%Y-%m-%d')}")
                    logging.info(f"Number of tickets: {len(tickets)}")
                    logging.info(f"Tickets: {tickets}")

                    with st.spinner("Generating Sprint Review..."):
                        try:
                            logs, output, result = capture_logs_and_output(
                                run_sprint_review,
                                st.session_state.start_date.strftime("%Y-%m-%d"),
                                st.session_state.end_date.strftime("%Y-%m-%d"),
                                tickets
                            )
                            logging.info("Sprint review generation completed successfully")
                        except Exception as e:
                            logging.error(f"Error generating sprint review: {str(e)}")
                            st.error(f"Failed to generate sprint review: {str(e)}")
                            return

                        with st.expander("View Logs"):
                            st.text_area("Execution Logs", value=logs, height=200)

                        if result:
                            st.markdown("### Generated Report")
                            st.code(result, language="text")
                            st.download_button("📥 Download Report", result, file_name=f"sprint_review_{st.session_state.start_date}_{st.session_state.end_date}.txt", mime="text/plain")

    if quit_button:
        st.success("Thank you for using EOD & Sprint Review Generator!")
        raise StopException()

if __name__ == "__main__":
    main()