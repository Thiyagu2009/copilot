import streamlit as st
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import jwt
import datetime
import os


# Assume these are set via environment variables for security
secret_key = st.secrets["SECRET_KEY"]
environment_id = st.secrets['ENVIRONMENT_ID']
organization_id = st.secrets['ORGANIZATION_ID']
conversation_id = st.secrets['CONVERSATION_ID']

# Define the issuer and audience
issuer = "graphlit"
audience = "https://portal.graphlit.io"

# Specify the role (Owner, Contributor, Reader)
role = "Owner"

# Specify the expiration (one hour from now)
expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=10)

# Define the payload
payload = {
    "https://graphlit.io/jwt/claims": {
        "x-graphlit-environment-id": environment_id,
        "x-graphlit-organization-id": organization_id,
        "x-graphlit-role": role,
    },
    "exp": expiration.timestamp(),
    "iss": issuer,
    "aud": audience,
}

# Sign the JWT
token = jwt.encode(payload, secret_key, algorithm="HS256")

print(token)
# Setup GraphQL client with AIOHTTPTransport
def get_graphql_client():
    transport = AIOHTTPTransport(
        url="https://data-scus.graphlit.io/api/v1/graphql",
        headers={"Authorization": f"Bearer {token}"}
    )
    return Client(transport=transport, fetch_schema_from_transport=True)


def chatbot():
    st.title("Knowldge Chatbot")

    tab1, tab2 = st.tabs(["Chat", "Ingest"])

    with tab1:
        user_input = st.text_input("User Input", "")

        if user_input:
            client = get_graphql_client()
            response = generate_response(client, user_input)
            st.text_area("Chatbot Response", value=response, height=200)

    with tab2:
        scrap_url = st.text_input("Enter URL to ingest", "")
        if scrap_url:
            client = get_graphql_client()
            response = ingest_url(client, scrap_url)
            st.info("Ingested successfully & vector embeddings created ")


def generate_response(client, user_input):
    # Your GraphQL query or mutation
    query = gql('''
    mutation promptconversation($prompt: String!, $promptConversationId: ID){
        promptConversation(prompt: $prompt, id: $promptConversationId) {
            message {
                message
            }
        }
    }
    ''')

    variables = {"prompt": user_input, "promptConversationId": st.secrets['CONVERSATION_ID']}

    response = client.execute(query, variable_values=variables)
    return response["promptConversation"]["message"]["message"]


def ingest_url(client, user_input):
    # Your GraphQL query or mutation
    query = gql('''
    mutation IngestPage($ingestPageUri2: URL!) {
    ingestPage(uri: $ingestPageUri2) {
        id
        uri
        state
        }
    }
    ''')

    variables = {"ingestPageUri2": user_input}

    response = client.execute(query, variable_values=variables)
    return response["ingestPage"]["id"]

if __name__ == "__main__":
    chatbot()
