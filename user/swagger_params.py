from drf_yasg import openapi

groups = [
    "public",
    "ward viewer",
    "ward editor",
    "municipal viewer",
    "municipal editor",
    "municipal admin",
    "super admin",
]

signin_parameters = [
    openapi.Parameter(
        name="email",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        required=True,
    ),
    openapi.Parameter(
        name="password",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        required=True,
    ),
]

changepassword_parameters = [
    openapi.Parameter(
        name="old_password",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        required=True,
        description="The old password of the user.",
    ),
    openapi.Parameter(
        name="new_password",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        required=True,
        description="The new password of the user.",
    ),
    openapi.Parameter(
        name="confirm_password",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        required=True,
        description="The new password of the user.",
    ),
]

forgotpassword_parameters = [
    openapi.Parameter(
        name="email",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        required=True,
        description="The email of the user.",
    ),
]

userlist_parameters = [
    openapi.Parameter(
        name="search",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Search query string for filtering user data",
        required=False,
    ),
    openapi.Parameter(
        name="ordering",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Query string for ordering the user data",
        required=False,
    ),
]

userpatch_parameters = [
    # openapi.Parameter(
    #     name="ward",
    #     in_=openapi.IN_QUERY,  # Use 'query' to pass parameters in the query string
    #     type=openapi.TYPE_ARRAY,
    #     items=openapi.Items(type=openapi.TYPE_INTEGER),  # Specify items as integer
    #     required=False,
    #     description="The list of wards.",
    # ),
    openapi.Parameter(
        name="role_type",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        enum=[group for group in groups],
        required=False,
        description="The type of user role (e.g., Super Admin, IT Officer, Public User,etc.).",
        # default="public",
    ),
    openapi.Parameter(
        name="designation",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        required=False,
        description="Designation of the user.",
    ),
    openapi.Parameter(
        name="is_deleted",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_BOOLEAN,
        required=False,
        description="deletion status",
    ),
]

userprofile_parameters = [
    # openapi.Parameter(
    #     name="gender",
    #     in_=openapi.IN_FORM,
    #     type=openapi.TYPE_STRING,
    #     enum=[choice[0] for choice in GENDER_CHOICES],
    #     default="Male",
    #     required=False,
    #     description="The gender of the user (male, female, other).",
    # ),
    openapi.Parameter(
        name="role_type",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        enum=[group for group in groups],
        required=True,
        description="The type of user role (e.g., Super Admin, IT Officer, Public User,etc.).",
    ),
    # openapi.Parameter(
    #     name="ward",
    #     in_=openapi.IN_FORM,
    #     type=openapi.TYPE_ARRAY,
    #     items=openapi.TYPE_INTEGER,
    #     required=True,
    #     description="ward",
    # ),
]

userlogs_parameters = [
    openapi.Parameter(
        name="search",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Search query string for filtering user logs",
        required=False,
    ),
    openapi.Parameter(
        name="ordering",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Query string for ordering the user logs",
        required=False,
    ),
]
