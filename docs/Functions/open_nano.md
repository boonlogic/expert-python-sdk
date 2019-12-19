# **open_nano()**
<br/>

#### authenticates the connection
##### input
>`label`
>>*label for the nano instance to open*
>
>`user`
>>*user credentials to use for authentication*
>
>`authentication_path`
>>*defaulted to the base directory, this points to the file containing the authorization key(s)*

##### output
>*True,`nano_handle` if the nano was loaded*

or
>*False,`nano_handle` if the user was not found but `nano_handle` still contains whatever parameters it could successfully load*

<br/>

[back to list](./Index.md)
