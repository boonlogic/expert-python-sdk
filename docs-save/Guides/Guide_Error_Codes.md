# Guide: Error Codes

### 200 Success
A 200 code is not returned because that means the call was successful and the result is just returned (if applicable)

### 400 Bad request

### 401 Unauthorized
When a 401 code gets returned, there is a problem with the 32 digit token supplied in relation to the call.

Responses:
- check your token to make sure you entered it correctly
- make sure the call you are accessing is part of your package

### 404 The specified resource was not found
The rest call that you are trying to access does not exist or the variable spec

### 500 Server error
