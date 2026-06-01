class AccountDTO:
    def __init__(self, user_id, user_name, phone_number, password):
        self.user_id = user_id
        self.user_name = user_name
        self.phone_number = phone_number
        self.password = password


        self.allergies = []