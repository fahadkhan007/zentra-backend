from app.core.security import hash_password, verify_password

class Hash:
    @staticmethod
    def bcrypt(password: str):
        return hash_password(password)

    @staticmethod
    def verify(hashed: str, plain: str):
        return verify_password(plain, hashed)
