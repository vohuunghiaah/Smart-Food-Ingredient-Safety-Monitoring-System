class AllergenResultDTO:
    """
    DTO chua ket qua kiem tra di ung cua mot san pham doi voi mot nguoi dung.

    Attributes:
        product_id          : Ma san pham
        product_name        : Ten san pham
        product_group       : Nhom san pham
        product_ingredients : Danh sach tat ca thanh phan cua san pham
                              [{ "id": ..., "name": ..., "aliases": [...] }]
        user_allergies      : Danh sach thanh phan di ung cua nguoi dung
                              [{ "id": ..., "name": ... }]
        matched_allergens   : Danh sach thanh phan trung khop (co di ung)
                              [{ "id": ..., "name": ..., "matched_by": "direct" | "alias" }]
        warning_level       : Muc canh bao: "SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL"
        warning_message     : Thong bao canh bao chi tiet
    """

    # --- Hang so muc canh bao ---
    LEVEL_SAFE = "SAFE"          # An toan - khong co thanh phan di ung
    LEVEL_LOW = "LOW"            # Thap - co thanh phan lien quan qua ten goi khac
    LEVEL_MEDIUM = "MEDIUM"      # Trung binh - co 1 thanh phan di ung truc tiep
    LEVEL_HIGH = "HIGH"          # Cao - co 2 thanh phan di ung truc tiep
    LEVEL_CRITICAL = "CRITICAL"  # Nghiem trong - co >= 3 thanh phan di ung truc tiep

    def __init__(self):
        self.product_id = None
        self.product_name = None
        self.product_group = None
        self.product_ingredients = []   # [{"id", "name", "aliases": [...]}]
        self.user_allergies = []        # [{"id", "name"}]
        self.matched_allergens = []     # [{"id", "name", "matched_by"}]
        self.warning_level = self.LEVEL_SAFE
        self.warning_message = ""
