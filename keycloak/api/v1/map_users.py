import frappe
from frappe import _

@frappe.whitelist()
def map_users_in_frappe(kwargs):
	# print(kwargs)
	if kwargs["operation"] == "create":
		create_user_in_frappe(kwargs)
	elif kwargs["operation"] == "update":
		update_user_in_frappe(kwargs)
	elif kwargs["operation"] == "delete":
		delete_user_in_frappe(kwargs)

def create_user_in_frappe(kwargs):
	doc = frappe.new_doc("User")
	set_data_in_erpnext_user_doctype(kwargs,doc)

	# Map user and user-id
	create_frappe_keycloak_user_map(kwargs)

def create_frappe_keycloak_user_map(kwargs):
	doc = frappe.new_doc("Erpnext Keycloak User Mapping")
	doc.erpnext_username = kwargs.get("email")
	doc.keycloak_id = kwargs.get("id")
	doc.save(ignore_permissions=True)

def update_user_in_frappe(kwargs):
	doc = frappe.get_doc("User",kwargs.get("email"))
	set_data_in_erpnext_user_doctype(kwargs,doc)

def delete_user_in_frappe(kwargs):
	erp_username = frappe.db.get_value("Erpnext Keycloak User Mapping",{"keycloak_id": kwargs["id"]},"erpnext_username")
	if erp_username is not None:
			frappe.delete_doc("User",erp_username)
			frappe.delete_doc("Erpnext Keycloak User Mapping",erp_username)
	else:
		frappe.log_error("Username not found in frappe")

def map_fieldnames_of_erp_and_keycloak():
    parameters_map = {
        "firstName": "first_name",
        "lastName": "last_name",
        "userName": "username",
		# "userType": "role_profile_name",
        "email": "email",
		"enableUser": "enabled"
    }
    return parameters_map

def set_data_in_erpnext_user_doctype(kwargs,doc):
	parameters_map = map_fieldnames_of_erp_and_keycloak()
	for field,value in kwargs.items():
		if field in parameters_map.keys():
			if field == "lastName" and value == "null":
				doc.set(parameters_map[field],None)
			else:
				doc.set(parameters_map[field],value)
	doc.save(ignore_permissions=True)