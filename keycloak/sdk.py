import frappe
from keycloak.utils.utils import success_response, error_response
from keycloak.api.V1 import V1
import time
@frappe.whitelist(allow_guest=True)
def api(**kwargs):
    try:
        st = time.time()
        version = kwargs.get('version') 
        if version == "v1":
            api = V1()
        elif version =="v2":
            api = V2()
        response = api.class_map(kwargs)
        et = time.time()
        if type(response) == dict:
            response['exec_time'] = f"{round(et - st, 4)} seconds"
        return response
    except Exception as e:
        frappe.log_error("API", frappe.get_traceback(with_context=True))
        frappe.throw(e)
