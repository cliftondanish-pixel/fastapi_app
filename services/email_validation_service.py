PERSONAL_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "icloud.com"
}


def is_personal_email(email: str) -> bool:

    domain = email.split("@")[-1].lower()

    return domain in PERSONAL_EMAIL_DOMAINS


def is_business_email(email: str) -> bool:

    return not is_personal_email(email)