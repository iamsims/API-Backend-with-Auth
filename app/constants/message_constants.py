# String constants that are used as messages in api
unauthorized_403 = "You are not authorized to perform this action."
jwt_error = "Bad Request Error while working with token. Malformed token or token is not present."
forbidden_error = "FORBIDDEN You are not authorized to access this resource."
authorization_error = "UNAUTHORIZED You are not authorized to access this resource."
login_success = "Login successful."
logout_success = "Logout successful."
bad_request = "Bad request"
user_not_allowed_error = "Error You are not allowed to perform action on this response {response_id}"
get_form_responses_error = "No any form responses found. Either this form isn't " \
                           "created by you or you are not a processor of this form."
linked_form_without_login_error = "Error You must be logged in to submit" \
                                  " a response that is linked to another form response."
invalid_action_ids = "Error these actions are not found {action_ids}"

api_key_success_message = "This api key is shown only once. You need to save it in a secure location. " \
                          "If you lost it you have to regenerate new api key and use it."
invalid_api_key_error = "Error Invalid api key."
revoke_api_key_success = "Api key is revoked successfully."
ping_message = "Server is up."

action_code_and_file_both_exists = "Error action code and file both exist. Use only one of them."
update_failed_message = "Failed to update resource with given details. Server error occurred."
action_code_required = "Error one of action code or action code file is required."

response_locked_error = "FORBIDDEN Cannot update response. Response is locked for modifying."
response_not_found_error = "Error response id is not present on query parameters for non admin users.."
email_success = "Email sent successfully."
user_not_found = "Error user not found."
otp_code_expired = "Error Verification code is expired. Please request for new code."
invalid_otp_code = "Error Invalid Verification code."
no_refresh_token_error = "Error Refresh token is not present in request."
duplicate_field_ids = "Error form contains duplicate field ids."
