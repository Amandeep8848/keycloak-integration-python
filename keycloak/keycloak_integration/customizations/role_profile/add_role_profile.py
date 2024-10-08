import frappe
from frappe import _
import requests
# from frappe.utils import get_site_path()

def add_role_profile_in_keycloak(doc, method):
    if doc.is_new():
        token = get_access_token()
        if token:
            create_new_role_profile(doc, token)

def get_access_token():
    if frappe.db.exists("Social Login Key","keycloak"):
        doc = frappe.get_doc("Social Login Key", "keycloak")
        if doc.enable_keycloak:
            if "/" == doc.base_url[-1]:
                url = doc.base_url+doc.access_token_url
            else:
                url = doc.base_url + "/" + doc.access_token_url
            payload = {
                'client_id': doc.client_id,
                'client_secret': doc.get_password("client_secret"),
                'grant_type': 'client_credentials'
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            response = requests.post(url, headers=headers, data=payload)
            data = response.json()
            return data["access_token"]
    return None

def create_new_role_profile(doc,access_token):
    url,headers = get_url_and_headers(access_token)
    role_profile_name = {
        "name": doc.role_profile
    }

    site_url = frappe.utils.get_url()
    if site_url:
        role_profile_name["attributes"] = {"site_url":[f"{site_url}"]}
    response = requests.post(url, headers=headers, json=role_profile_name)
    
    if response.status_code == 201:
        frappe.msgprint(_("Role Profile added successfully."))
    else:
        frappe.throw(_(response.text))

def get_url_and_headers(access_token):
    doc = frappe.get_value("Social Login Key", "keycloak", ["root_url", "realm_name"], as_dict = 1)
    if "/" == doc.root_url[-1]:
        url = f"{doc.root_url}admin/realms/{doc.realm_name}/roles"
    else:
        url = f"{doc.root_url}/admin/realms/{doc.realm_name}/roles"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    return url,headers


def delete_role_profile_in_keycloak(doc,method):
    access_token = get_access_token()
    if access_token:
        url,headers = get_url_and_headers(access_token)
        mapped_doc = frappe.get_doc("Erpnext Keycloak Role Profile Mapping",doc.role_profile)

        delete_url = f"{url}/{mapped_doc.keycloak_realm_role_name}"
        response = requests.delete(delete_url, headers=headers)
        if response.status_code == 204:
            frappe.msgprint(_("Role deleted successfully."))
            delete_role_profile_map(doc.role_profile)
        else:
            frappe.throw(_(response.text)) 

def delete_role_profile_map(role_profile_name):
    if frappe.db.exists("Erpnext Keycloak Role Profile Mapping", role_profile_name):
        frappe.delete_doc("Erpnext Keycloak Role Profile Mapping", role_profile_name)
    else:
        frappe.log_error("Role Profile Map not found in frappe")