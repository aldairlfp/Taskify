from pydantic import (
    BaseModel,
    field_serializer,
    field_validator,
    model_validator,
    EmailStr,
)
from datetime import datetime
from typing import Optional, Any, Dict
import uuid
import re


# Base schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class UserBase(BaseModel):
    username: str
    email: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Comprehensive username validation"""
        if not v or not isinstance(v, str):
            raise ValueError("Username is required and must be a string")

        # Strip whitespace
        v = v.strip()

        if len(v) == 0:
            raise ValueError("Username cannot be empty")

        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")

        if len(v) > 50:
            raise ValueError("Username cannot exceed 50 characters")

        # Check for valid characters (alphanumeric, underscore, hyphen)
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )

        # Must start with letter or number
        if not re.match(r"^[a-zA-Z0-9]", v):
            raise ValueError("Username must start with a letter or number")

        # Cannot end with special characters
        if v.endswith(("_", "-")):
            raise ValueError("Username cannot end with underscore or hyphen")

        # Check for reserved usernames
        reserved_usernames = {
            "admin",
            "administrator",
            "root",
            "user",
            "test",
            "demo",
            "guest",
            "api",
            "www",
            "mail",
            "email",
            "support",
            "help",
            "info",
            "contact",
            "null",
            "undefined",
            "none",
            "system",
            "operator",
        }

        if v.lower() in reserved_usernames:
            raise ValueError(f"Username '{v}' is reserved and cannot be used")

        # Check for excessive repetition
        if len(set(v)) < 2 and len(v) > 3:
            raise ValueError("Username cannot be repetitive characters")

        return v.lower()  # Store usernames in lowercase

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Comprehensive email validation"""
        if not v or not isinstance(v, str):
            raise ValueError("Email is required and must be a string")

        # Strip whitespace
        v = v.strip().lower()

        if len(v) == 0:
            raise ValueError("Email cannot be empty")

        if len(v) > 100:
            raise ValueError("Email cannot exceed 100 characters")

        # Basic email regex pattern
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")

        # Check for common mistakes
        if ".." in v:
            raise ValueError("Email cannot contain consecutive dots")

        if v.startswith(".") or v.startswith("@"):
            raise ValueError("Email cannot start with dot or @ symbol")

        if v.endswith(".") or v.endswith("@"):
            raise ValueError("Email cannot end with dot or @ symbol")

        # Check domain part
        if "@" in v:
            local, domain = v.split("@", 1)

            if len(local) == 0:
                raise ValueError("Email local part cannot be empty")

            if len(local) > 64:
                raise ValueError("Email local part cannot exceed 64 characters")

            if len(domain) == 0:
                raise ValueError("Email domain cannot be empty")

            if len(domain) > 253:
                raise ValueError("Email domain cannot exceed 253 characters")

            # Check for valid domain
            if not re.match(r"^[a-zA-Z0-9.-]+$", domain):
                raise ValueError("Email domain contains invalid characters")

            if domain.startswith("-") or domain.endswith("-"):
                raise ValueError("Email domain cannot start or end with hyphen")

            # Must have at least one dot in domain
            if "." not in domain:
                raise ValueError("Email domain must contain at least one dot")

        return v


# Request schemas (what we receive from the client)
class TaskCreate(TaskBase):
    """Schema for creating a new task"""

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        """Comprehensive title validation"""
        if not v or not isinstance(v, str):
            raise ValueError("Title is required and must be a string")

        # Strip whitespace
        v = v.strip()

        if len(v) == 0:
            raise ValueError("Title cannot be empty or only whitespace")

        if len(v) < 3:
            raise ValueError("Title must be at least 3 characters long")

        if len(v) > 200:
            raise ValueError("Title cannot exceed 200 characters")

        # Check for only special characters
        if re.match(r"^[^\w\s]+$", v):
            raise ValueError("Title cannot contain only special characters")

        # Check for suspicious patterns
        if v.lower() in ["null", "undefined", "none", ""]:
            raise ValueError("Title cannot be a reserved word")

        # Check for excessive repetition
        if len(set(v.replace(" ", ""))) < 2 and len(v) > 5:
            raise ValueError("Title cannot be repetitive characters")

        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """Comprehensive description validation"""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("Description must be a string")

            # Strip whitespace
            v = v.strip()

            if len(v) == 0:
                return None  # Empty description is OK, convert to None

            if len(v) > 1000:
                raise ValueError("Description cannot exceed 1000 characters")

            # Check for only special characters
            if re.match(r"^[^\w\s]+$", v):
                raise ValueError("Description cannot contain only special characters")

        return v if v else None

    @model_validator(mode="before")
    @classmethod
    def validate_input_data(cls, data: Any) -> Any:
        """Pre-process and validate input data structure for task creation"""
        if isinstance(data, dict):
            # Handle null/None values that might come as strings
            for key, value in list(data.items()):
                if isinstance(value, str):
                    # Convert string nulls to actual None
                    if value.lower() in ["null", "none", "undefined"]:
                        data[key] = None
                    # Strip whitespace from all string values
                    elif value.strip() != value:
                        data[key] = value.strip()
                # Handle numeric values that should be strings
                elif isinstance(value, (int, float)) and key in [
                    "title",
                    "description",
                ]:
                    raise ValueError(f"{key.title()} must be a string, not a number")
                # Handle boolean values that should be strings
                elif isinstance(value, bool) and key in ["title", "description"]:
                    raise ValueError(f"{key.title()} must be a string, not a boolean")

            # Check for required fields
            if "title" not in data or data["title"] is None:
                raise ValueError("Title is required for task creation")

            # Reject completely empty requests
            if not data or all(v is None for v in data.values()):
                raise ValueError("Request cannot be empty")

        return data


class TaskUpdate(BaseModel):
    """Schema for updating a task"""

    title: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None  # Accept "done" or "pending"

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        """Enhanced title validation for updates"""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("Title must be a string")

            # Strip whitespace
            v = v.strip()

            if len(v) == 0:
                raise ValueError("Title cannot be empty or only whitespace")

            if len(v) < 3:
                raise ValueError("Title must be at least 3 characters long")

            if len(v) > 200:
                raise ValueError("Title cannot exceed 200 characters")

            # Check for only special characters
            if re.match(r"^[^\w\s]+$", v):
                raise ValueError("Title cannot contain only special characters")

            # Check for suspicious patterns
            if v.lower() in ["null", "undefined", "none", ""]:
                raise ValueError("Title cannot be a reserved word")

            # Check for excessive repetition
            if len(set(v.replace(" ", ""))) < 2 and len(v) > 5:
                raise ValueError("Title cannot be repetitive characters")

        return v if v else None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """Enhanced description validation for updates"""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("Description must be a string")

            # Strip whitespace
            v = v.strip()

            if len(v) == 0:
                return None  # Empty description becomes None

            if len(v) > 1000:
                raise ValueError("Description cannot exceed 1000 characters")

            # Check for only special characters
            if re.match(r"^[^\w\s]+$", v):
                raise ValueError("Description cannot contain only special characters")

            # Check for suspicious patterns
            if v.lower() in ["null", "undefined", "none"]:
                raise ValueError("Description cannot be a reserved word")

        return v if v else None

    @field_validator("state")
    @classmethod
    def validate_state(cls, v):
        """Enhanced state validation"""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("State must be a string")

            # Normalize case and strip whitespace
            v = v.strip().lower()

            if v == "":
                raise ValueError("State cannot be empty")

            # Accept various forms and normalize them
            valid_states = {
                "done": "done",
                "completed": "done",
                "finished": "done",
                "complete": "done",
                "true": "done",
                "1": "done",
                "pending": "pending",
                "todo": "pending",
                "incomplete": "pending",
                "open": "pending",
                "false": "pending",
                "0": "pending",
            }

            if v not in valid_states:
                valid_options = list(set(valid_states.values()))
                raise ValueError(
                    f'State must be one of: {", ".join(valid_options)}. '
                    f'Also accepts: {", ".join(valid_states.keys())}'
                )

            return valid_states[v]

        return v

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data: Any) -> Any:
        """Enhanced validation for allowed fields and data types"""
        if isinstance(data, dict):
            # Check for allowed fields
            allowed_fields = {"title", "description", "state"}
            provided_fields = set(data.keys())
            invalid_fields = provided_fields - allowed_fields

            if invalid_fields:
                raise ValueError(
                    f"Invalid field(s): {', '.join(invalid_fields)}. "
                    f"Allowed fields are: {', '.join(allowed_fields)}"
                )

            # Handle null/None values that might come as strings
            for key, value in list(data.items()):
                if isinstance(value, str):
                    # Convert string nulls to actual None (but preserve empty strings for validation)
                    if value.lower() in ["null", "none", "undefined"]:
                        data[key] = None
                # Handle unexpected data types
                elif isinstance(value, (int, float)) and key in [
                    "title",
                    "description",
                    "state",
                ]:
                    raise ValueError(f"{key.title()} must be a string, not a number")
                elif isinstance(value, bool) and key in [
                    "title",
                    "description",
                    "state",
                ]:
                    raise ValueError(f"{key.title()} must be a string, not a boolean")
                elif isinstance(value, list) and key in [
                    "title",
                    "description",
                    "state",
                ]:
                    raise ValueError(f"{key.title()} must be a string, not a list")
                elif isinstance(value, dict) and key in [
                    "title",
                    "description",
                    "state",
                ]:
                    raise ValueError(f"{key.title()} must be a string, not an object")

            # Check for completely empty request
            if not data:
                raise ValueError("Update request cannot be completely empty")

            # Check if all provided values are None
            if all(v is None for v in data.values()):
                raise ValueError("Cannot update all fields to null/empty")

        return data

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "TaskUpdate":
        """Ensure at least one field is provided for update"""
        if all(
            getattr(self, field) is None for field in ["title", "description", "state"]
        ):
            raise ValueError(
                "At least one field (title, description, or state) must be provided for update"
            )
        return self

    class Config:
        """Pydantic configuration"""

        extra = "forbid"  # Forbid extra fields not defined in the model


class UserCreate(UserBase):
    """Schema for creating a new user"""

    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Comprehensive password validation"""
        if not v or not isinstance(v, str):
            raise ValueError("Password is required and must be a string")

        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if len(v) > 128:
            raise ValueError("Password cannot exceed 128 characters")

        # Check for at least one uppercase letter
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        # Check for at least one lowercase letter
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        # Check for at least one digit
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError(
                'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)'
            )

        # Check for common weak passwords
        weak_passwords = {
            "password",
            "password123",
            "12345678",
            "qwerty123",
            "abc123456",
            "password1",
            "admin123",
            "user123",
            "test123",
            "demo123",
        }

        if v.lower() in weak_passwords:
            raise ValueError("Password is too common and weak")

        # Check for repetitive patterns
        if len(set(v)) < 4:
            raise ValueError("Password cannot be too repetitive")

        # Check for sequential characters
        sequences = ["1234", "abcd", "qwer", "asdf", "zxcv"]
        for seq in sequences:
            if seq in v.lower():
                raise ValueError("Password cannot contain common sequential patterns")

        return v


# Response schemas (what we send back to the client)
class Task(TaskBase):
    """Schema for task responses"""

    id: uuid.UUID
    state: bool  # Internal field (boolean from database)
    created_at: datetime
    updated_at: datetime
    user_id: uuid.UUID

    class Config:
        from_attributes = True  # This allows Pydantic to work with SQLAlchemy models

    @field_serializer("state")
    def serialize_state(self, state: bool) -> str:
        """Convert boolean state to user-friendly string"""
        return "done" if state else "pending"


class User(UserBase):
    """Schema for user responses"""

    id: uuid.UUID
    created_at: datetime
    tasks: list[Task] = []

    class Config:
        from_attributes = True


class TaskResponse(Task):
    """Extended task response with owner information"""

    owner: Optional[User] = None


# Authentication schemas
class Token(BaseModel):
    """JWT Token response"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data"""

    username: Optional[str] = None


class UserLogin(BaseModel):
    """User login credentials"""

    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Login username validation"""
        if not v or not isinstance(v, str):
            raise ValueError("Username is required")

        v = v.strip()
        if len(v) == 0:
            raise ValueError("Username cannot be empty")

        if len(v) > 50:
            raise ValueError("Username too long")

        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Login password validation"""
        if not v or not isinstance(v, str):
            raise ValueError("Password is required")

        if len(v) == 0:
            raise ValueError("Password cannot be empty")

        if len(v) > 128:
            raise ValueError("Password too long")

        return v


class UserRegister(BaseModel):
    """User registration data"""

    username: str
    email: str
    password: str
    confirm_password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Registration username validation"""
        if not v or not isinstance(v, str):
            raise ValueError("Username is required and must be a string")

        v = v.strip()

        if len(v) == 0:
            raise ValueError("Username cannot be empty")

        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")

        if len(v) > 50:
            raise ValueError("Username cannot exceed 50 characters")

        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )

        if not re.match(r"^[a-zA-Z0-9]", v):
            raise ValueError("Username must start with a letter or number")

        if v.endswith(("_", "-")):
            raise ValueError("Username cannot end with underscore or hyphen")

        reserved_usernames = {
            "admin",
            "administrator",
            "root",
            "user",
            "test",
            "demo",
            "guest",
            "api",
            "www",
            "mail",
            "email",
            "support",
            "help",
            "info",
            "contact",
            "null",
            "undefined",
            "none",
            "system",
            "operator",
        }

        if v.lower() in reserved_usernames:
            raise ValueError(f"Username '{v}' is reserved and cannot be used")

        return v.lower()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Registration email validation"""
        if not v or not isinstance(v, str):
            raise ValueError("Email is required and must be a string")

        v = v.strip().lower()

        if len(v) == 0:
            raise ValueError("Email cannot be empty")

        if len(v) > 100:
            raise ValueError("Email cannot exceed 100 characters")

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")

        if ".." in v:
            raise ValueError("Email cannot contain consecutive dots")

        if v.startswith(".") or v.startswith("@"):
            raise ValueError("Email cannot start with dot or @ symbol")

        if v.endswith(".") or v.endswith("@"):
            raise ValueError("Email cannot end with dot or @ symbol")

        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Registration password validation"""
        if not v or not isinstance(v, str):
            raise ValueError("Password is required and must be a string")

        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if len(v) > 128:
            raise ValueError("Password cannot exceed 128 characters")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")

        weak_passwords = {
            "password",
            "password123",
            "12345678",
            "qwerty123",
            "abc123456",
            "password1",
            "admin123",
            "user123",
            "test123",
            "demo123",
        }

        if v.lower() in weak_passwords:
            raise ValueError("Password is too common and weak")

        if len(set(v)) < 4:
            raise ValueError("Password cannot be too repetitive")

        return v

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v):
        """Confirm password validation"""
        if not v or not isinstance(v, str):
            raise ValueError("Password confirmation is required")

        return v

    @model_validator(mode="after")
    def validate_passwords_match(self) -> "UserRegister":
        """Ensure password and confirm_password match"""
        if self.password != self.confirm_password:
            raise ValueError("Password and confirmation password do not match")
        return self
