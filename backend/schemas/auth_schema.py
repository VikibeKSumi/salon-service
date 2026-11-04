from schemas.io_model_config import InputModel

class LoginInput(InputModel):
    email: str
    password: str

