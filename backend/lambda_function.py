import json
import boto3
import urllib.parse
import urllib.request
import urllib.error
import uuid

SECRET_NAME = "customer-dataverse-api/dev/dataverse"
REGION_NAME = "ap-southeast-2"


def get_dataverse_secret():
    client = boto3.client(
        "secretsmanager",
        region_name=REGION_NAME
    )

    response = client.get_secret_value(
        SecretId=SECRET_NAME
    )

    return json.loads(response["SecretString"])


def get_access_token(secret):
    tenant_id = secret["TENANT_ID"]
    client_id = secret["CLIENT_ID"]
    client_secret = secret["CLIENT_SECRET"]
    dataverse_url = secret["DATAVERSE_URL"].rstrip("/")

    token_url = (
        f"https://login.microsoftonline.com/"
        f"{tenant_id}/oauth2/v2.0/token"
    )

    form_data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": f"{dataverse_url}/.default"
    }).encode("utf-8")

    request = urllib.request.Request(
        token_url,
        data=form_data,
        method="POST"
    )

    request.add_header(
        "Content-Type",
        "application/x-www-form-urlencoded"
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        token_response = json.loads(
            response.read().decode("utf-8")
        )

    return token_response["access_token"]


def add_dataverse_headers(request, access_token):
    request.add_header(
        "Authorization",
        f"Bearer {access_token}"
    )

    request.add_header(
        "Accept",
        "application/json"
    )

    request.add_header(
        "OData-Version",
        "4.0"
    )

    request.add_header(
        "OData-MaxVersion",
        "4.0"
    )


def get_contacts(secret, access_token):
    dataverse_url = secret["DATAVERSE_URL"].rstrip("/")

    api_url = (
        f"{dataverse_url}/api/data/v9.2/contacts"
        "?$select=contactid,firstname,lastname,"
        "emailaddress1,telephone1"
    )

    request = urllib.request.Request(
        api_url,
        method="GET"
    )

    add_dataverse_headers(request, access_token)

    with urllib.request.urlopen(request, timeout=20) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

    return result.get("value", [])


def get_contact_by_id(secret, access_token, contact_id):
    dataverse_url = secret["DATAVERSE_URL"].rstrip("/")

    api_url = (
        f"{dataverse_url}/api/data/v9.2/"
        f"contacts({contact_id})"
        "?$select=contactid,firstname,lastname,"
        "emailaddress1,telephone1"
    )

    request = urllib.request.Request(
        api_url,
        method="GET"
    )

    add_dataverse_headers(request, access_token)

    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def create_contact(secret, access_token, customer):
    dataverse_url = secret["DATAVERSE_URL"].rstrip("/")

    api_url = (
        f"{dataverse_url}/api/data/v9.2/contacts"
    )

    dataverse_contact = {
        "firstname": customer["firstName"],
        "lastname": customer["lastName"]
    }

    if customer.get("email"):
        dataverse_contact["emailaddress1"] = customer["email"]

    if customer.get("phone"):
        dataverse_contact["telephone1"] = customer["phone"]

    request_body = json.dumps(
        dataverse_contact
    ).encode("utf-8")

    request = urllib.request.Request(
        api_url,
        data=request_body,
        method="POST"
    )

    add_dataverse_headers(request, access_token)

    request.add_header(
        "Content-Type",
        "application/json"
    )

    # Ask Dataverse to return the newly-created record.
    request.add_header(
        "Prefer",
        "return=representation"
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        response_body = response.read().decode("utf-8")

        if response_body:
            return json.loads(response_body)

        return {}

def update_contact(secret, access_token, contact_id, customer):
    dataverse_url = secret["DATAVERSE_URL"].rstrip("/")

    api_url = (
        f"{dataverse_url}/api/data/v9.2/"
        f"contacts({contact_id})"
    )

    dataverse_contact = {}

    if "firstName" in customer:
        dataverse_contact["firstname"] = customer["firstName"]

    if "lastName" in customer:
        dataverse_contact["lastname"] = customer["lastName"]

    if "email" in customer:
        dataverse_contact["emailaddress1"] = customer["email"]

    if "phone" in customer:
        dataverse_contact["telephone1"] = customer["phone"]

    request_body = json.dumps(
        dataverse_contact
    ).encode("utf-8")

    request = urllib.request.Request(
        api_url,
        data=request_body,
        method="PATCH"
    )

    add_dataverse_headers(
        request,
        access_token
    )

    request.add_header(
        "Content-Type",
        "application/json"
    )

    with urllib.request.urlopen(
        request,
        timeout=20
    ) as response:
        return response.status
def delete_contact(secret, access_token, contact_id):
    dataverse_url = secret["DATAVERSE_URL"].rstrip("/")

    api_url = (
        f"{dataverse_url}/api/data/v9.2/"
        f"contacts({contact_id})"
    )

    request = urllib.request.Request(
        api_url,
        method="DELETE"
    )

    add_dataverse_headers(
        request,
        access_token
    )

    with urllib.request.urlopen(
        request,
        timeout=20
    ) as response:
        return response.status

def map_contact_to_customer(contact):
    return {
        "id": contact.get("contactid"),
        "firstName": contact.get("firstname"),
        "lastName": contact.get("lastname"),
        "email": contact.get("emailaddress1"),
        "phone": contact.get("telephone1")
    }


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    try:
        route_key = event.get("routeKey", "")
        path_parameters = event.get("pathParameters") or {}

        # -------------------------------------------
        # Validate POST body before calling Dataverse
        # -------------------------------------------
        if route_key == "POST /customers":

            try:
                request_body = json.loads(
                    event.get("body") or "{}"
                )
            except json.JSONDecodeError:
                return response(
                    400,
                    {
                        "message": "Request body must be valid JSON"
                    }
                )

            first_name = str(
                request_body.get("firstName", "")
            ).strip()

            last_name = str(
                request_body.get("lastName", "")
            ).strip()

            email = str(
                request_body.get("email", "")
            ).strip()

            phone = str(
                request_body.get("phone", "")
            ).strip()

            if not first_name:
                return response(
                    400,
                    {
                        "message": "firstName is required"
                    }
                )

            if not last_name:
                return response(
                    400,
                    {
                        "message": "lastName is required"
                    }
                )

            customer_input = {
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "phone": phone
            }

            secret = get_dataverse_secret()
            access_token = get_access_token(secret)

            created_contact = create_contact(
                secret,
                access_token,
                customer_input
            )

            created_customer = map_contact_to_customer(
                created_contact
            )

            return response(
                201,
                {
                    "message": "Customer created successfully",
                    "customer": created_customer
                }
            )

        # Authentication/configuration needed for GET/PUT routes
        secret = get_dataverse_secret()
        access_token = get_access_token(secret)

        # -------------------------------------------
        # PUT /customers/{id}
        # -------------------------------------------
        if route_key == "PUT /customers/{id}":

            contact_id = path_parameters.get("id")

            if not contact_id:
                return response(
                    400,
                    {
                        "message": "Customer ID is required"
                    }
                )

            try:
                uuid.UUID(contact_id)
            except ValueError:
                return response(
                    400,
                    {
                        "message": "Invalid customer ID"
                    }
                )

            try:
                request_body = json.loads(
                    event.get("body") or "{}"
                )
            except json.JSONDecodeError:
                return response(
                    400,
                    {
                        "message": "Request body must be valid JSON"
                    }
                )

            allowed_fields = {
                "firstName",
                "lastName",
                "email",
                "phone"
            }

            customer_input = {
                key: value
                for key, value in request_body.items()
                if key in allowed_fields
            }

            if not customer_input:
                return response(
                    400,
                    {
                        "message":
                            "At least one customer field is required"
                    }
                )

            try:
                update_contact(
                    secret,
                    access_token,
                    contact_id,
                    customer_input
                )

                updated_contact = get_contact_by_id(
                    secret,
                    access_token,
                    contact_id
                )

            except urllib.error.HTTPError as e:

                if e.code == 404:
                    return response(
                        404,
                        {
                            "message": "Customer not found"
                        }
                    )

                raise

            return response(
                200,
                {
                    "message": "Customer updated successfully",
                    "customer":
                        map_contact_to_customer(
                            updated_contact
                        )
                }
            )

        # -------------------------------------------    
        # DELETE /customers/{id}
        # -------------------------------------------
        if route_key == "DELETE /customers/{id}":

            contact_id = path_parameters.get("id")

            if not contact_id:
                return response(
                    400,
                    {"message": "Customer ID is required"}
                )

            try:
                uuid.UUID(contact_id)
            except ValueError:
                return response(
                    400,
                    {"message": "Invalid customer ID"}
                )

            try:
                delete_contact(
                    secret,
                    access_token,
                    contact_id
                )
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return response(
                        404,
                        {"message": "Customer not found"}
                    )
                raise

            return response(
                200,
                {
                    "message": "Customer deleted successfully",
                    "id": contact_id
                }
            )

        # -------------------------------------------
        # GET /customers/{id}
        # -------------------------------------------
        if route_key == "GET /customers/{id}":

            contact_id = path_parameters.get("id")

            if not contact_id:
                return response(
                    400,
                    {
                        "message": "Customer ID is required"
                    }
                )

            try:
                uuid.UUID(contact_id)
            except ValueError:
                return response(
                    400,
                    {
                        "message": "Invalid customer ID"
                    }
                )

            try:
                contact = get_contact_by_id(
                    secret,
                    access_token,
                    contact_id
                )

            except urllib.error.HTTPError as e:

                if e.code == 404:
                    return response(
                        404,
                        {
                            "message": "Customer not found"
                        }
                    )

                raise

            return response(
                200,
                {
                    "customer":
                        map_contact_to_customer(contact)
                }
            )

        # -------------------------------------------
        # GET /customers
        # -------------------------------------------
        if route_key == "GET /customers":

            contacts = get_contacts(
                secret,
                access_token
            )

            customers = [
                map_contact_to_customer(contact)
                for contact in contacts
            ]

            return response(
                200,
                {
                    "customers": customers
                }
            )

        return response(
            404,
            {
                "message": "Route not found"
            }
        )

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")

        print(f"Dataverse HTTP error: {e.code}")
        print(f"Dataverse error body: {error_body}")

        return response(
            500,
            {
              "message": "Dataverse request failed",
              "httpStatus": e.code
             }
        )

    except Exception as e:
        print(
            f"Application error: {type(e).__name__}: {str(e)}"
        )

        return response(
            500,
            {
                "message": "Application error",
                "errorType": type(e).__name__
            }
        )