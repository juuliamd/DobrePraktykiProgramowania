import bcrypt

# Store users as dicts with hashed password and roles list.
# This makes it easy to include roles in JWT payloads and check permissions.
hashed_user1 = bcrypt.hashpw(b"secure_password", bcrypt.gensalt())
hashed_admin = bcrypt.hashpw(b"admin123", bcrypt.gensalt())

USERS_DB = {
    # regular user
    "user1": {
        "password": hashed_user1,
        "roles": ["ROLE_USER"],
    },
    # admin user - has admin privileges
    "admin": {
        "password": hashed_admin,
        "roles": ["ROLE_ADMIN", "ROLE_USER"],
    },
}