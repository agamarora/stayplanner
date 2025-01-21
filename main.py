import os
import json
import streamlit as st

# Set environment variables if not already set
env_vars = {"GROQ_API_KEY", "TAVILY_API_KEY"}
for var in env_vars:
    if var not in os.environ:
        os.environ[var] = st.secrets[var]

from agents import create_workflow

# Load hotel data from JSON file
hotel_data_path = "hotel-data/the_park-new_delhi_india.json"
try:
    with open(hotel_data_path, "r") as f:
        hotel_data = json.load(f)
except FileNotFoundError:
    st.error(f"Hotel data file not found at path: {hotel_data_path}")
    hotel_data = {}
except json.JSONDecodeError:
    st.error(f"Error decoding JSON file at path: {hotel_data_path}")
    hotel_data = {}

# Create workflow
app = create_workflow()

# Sidebar UI for user input
st.sidebar.header("Guest Details")
group = st.sidebar.selectbox(
    "Group type:",
    ["solo", "couple", "friends - male", "friends - female", "family"],
    index=0,
)

num_people = st.sidebar.number_input(
    "Number of Travelers:", min_value=1, value=1, step=1
)

# Add a text box for interests input
interests = st.sidebar.text_area(
    "What are your interests? (Enter as a comma-separated list)",
    placeholder="e.g., sightseeing, adventure, food"
)

# Validate group and number of travelers
if group == "solo" and num_people > 1:
    st.sidebar.error("For a solo group, the number of travelers cannot exceed 1.")

if st.sidebar.button("Plan my stay!"):
    with st.spinner("Planning your trip..."):
        try:
            # Define the initial state with hotel data and interests
            initial_state = {
                "name": "Bob",
                "hotel": "The Park, New Delhi",
                "city": "New Delhi",
                "group": group,
                "num_people": num_people,
                "interests": [interest.strip() for interest in interests.split(",") if interest.strip()],
                "agent_output": {"hotel_info": hotel_data},  # Include hotel data here
                "is_last_step": False,  # Required by state schema
            }

            # Invoke the workflow
            output = app.invoke(initial_state)

            # Display results in Streamlit
            st.title("Your Travel Plan")

            # Display state details
            st.subheader("State")
            st.markdown(
                f"**Hotel:** {output.get('hotel', 'N/A')}\n\n"
                f"**City:** {output.get('city', 'N/A')}\n\n"
                f"**Guest Name:** {output.get('name', 'N/A')}\n\n"
                f"**Group:** {output.get('group', 'N/A')}\n\n"
                f"**Number of People:** {output.get('num_people', 'N/A')}\n\n"
                f"**Interests:** {', '.join(output.get('interests', [])) if output.get('interests') else 'N/A'}"
            )

            # Display agent outputs
            st.subheader("Agents Outputs")
            for key, value in output.get("agent_output", {}).items():
                with st.expander(key.capitalize()):
                    if key == "hotel_info":
                        st.write(f"**Hotel Name:** {value.get('name', 'N/A')}")
                        st.write(f"**Website:** {value.get('website', 'N/A')}")
                        st.write(f"**Address:** {value.get('address', 'N/A')}")
                        st.write(f"**Phone:** {value.get('phone', 'N/A')}")
                        st.write(f"**Email:** {value.get('email', 'N/A')}")

                        st.subheader("Rooms")
                        for room in value.get("rooms", []):
                            st.markdown(
                                f"- **Type:** {room.get('type', 'N/A')}\n"
                                f"  - **Size:** {room.get('size', 'N/A')}\n"
                                f"  - **View:** {room.get('view', 'N/A')}\n"
                                f"  - **Bed Type:** {', '.join(room.get('bed', []))}\n"
                                f"  - **Amenities:** {', '.join(room.get('amenities', []))}"
                            )

                        st.subheader("Dining Options")
                        for dining in value.get("dining", []):
                            st.markdown(
                                f"- **Name:** {dining.get('name', 'N/A')}\n"
                                f"  - **Cuisine:** {dining.get('cuisine', 'N/A')}\n"
                                f"  - **Type:** {dining.get('type', 'N/A')}\n"
                                f"  - **Hours:** {dining.get('hours', 'N/A')}"
                            )

                        st.subheader("Facilities")
                        for facility in value.get("facilities", []):
                            st.markdown(
                                f"- **Name:** {facility.get('name', 'N/A')}\n"
                                f"  - **Hours:** {facility.get('hours', 'N/A')}\n"
                                f"  - **Services:** {', '.join(facility.get('services', []))}"
                            )
                    else:
                        st.write(value)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
