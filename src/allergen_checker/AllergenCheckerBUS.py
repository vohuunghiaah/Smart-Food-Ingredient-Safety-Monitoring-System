from allergen_checker.AllergenCheckerDAO import AllergenCheckerDAO
from allergen_checker.AllergenCheckerDTO import AllergenResultDTO


class AllergenCheckerBUS:
    """
    BUS xu ly logic nghiep vu:
    - Tra cuu thanh phan san pham
    - So khop voi thanh phan di ung cua nguoi dung (truc tiep + qua ten goi khac)
    - Phan loai muc canh bao: SAFE / LOW / MEDIUM / HIGH / CRITICAL
    """

    def __init__(self):
        self.dao = AllergenCheckerDAO()

    # ===================================================================
    # HAM CHINH: Kiem tra di ung cua nguoi dung voi mot san pham
    # ===================================================================
    def check_allergens_by_barcode(self, user_id, barcode):
        """
        Kiem tra di ung khi quet ma vach san pham.

        Tham so:
            user_id  : Ma nguoi dung (VD: 'U01')
            barcode  : Ma vach san pham (VD: '8934563123456')

        Tra ve:
            AllergenResultDTO chua ket qua kiem tra
        """
        # Buoc 1: Tim san pham theo ma vach
        product = self.dao.get_product_by_barcode(barcode)
        if product is None:
            result = AllergenResultDTO()
            result.warning_level = AllergenResultDTO.LEVEL_SAFE
            result.warning_message = f"Khong tim thay san pham voi ma vach: {barcode}"
            return result

        # Goi ham kiem tra chung
        return self._check_allergens(user_id, product)

    def check_allergens_by_product_id(self, user_id, product_id):
        """
        Kiem tra di ung theo ma san pham.

        Tham so:
            user_id    : Ma nguoi dung (VD: 'U01')
            product_id : Ma san pham (VD: 'SP01')

        Tra ve:
            AllergenResultDTO chua ket qua kiem tra
        """
        # Buoc 1: Tim san pham theo ID
        product = self.dao.get_product_by_id(product_id)
        if product is None:
            result = AllergenResultDTO()
            result.warning_level = AllergenResultDTO.LEVEL_SAFE
            result.warning_message = f"Khong tim thay san pham voi ma: {product_id}"
            return result

        # Goi ham kiem tra chung
        return self._check_allergens(user_id, product)

    # ===================================================================
    # HAM XU LY NOI BO
    # ===================================================================
    def _check_allergens(self, user_id, product):
        """
        Logic kiem tra di ung chinh:
        1. Lay danh sach thanh phan cua san pham
        2. Lay danh sach ten goi khac cho moi thanh phan
        3. Lay danh sach thanh phan di ung cua nguoi dung
        4. So khop truc tiep + so khop qua ten goi khac
        5. Phan loai muc canh bao
        """
        result = AllergenResultDTO()

        # --- Gan thong tin san pham ---
        result.product_id = product["id"]
        result.product_name = product["name"]
        result.product_group = product["group"]

        # --- Buoc 1: Lay danh sach thanh phan san pham + ten goi khac ---
        raw_ingredients = self.dao.get_product_ingredients(product["id"])
        for ing in raw_ingredients:
            aliases = self.dao.get_ingredient_aliases(ing["id"])
            result.product_ingredients.append({
                "id": ing["id"],
                "name": ing["name"],
                "aliases": aliases
            })

        # --- Buoc 2: Lay danh sach thanh phan di ung cua user ---
        result.user_allergies = self.dao.get_user_allergies(user_id)

        # --- Buoc 3: So khop ---
        # Tao set cac ma thanh phan di ung de tra cuu nhanh
        allergy_ids = set(a["id"] for a in result.user_allergies)
        # Tao dict: ten_goi_khac (lowercase) -> ma_thanh_phan goc
        allergy_names = {}
        for a in result.user_allergies:
            allergy_names[a["name"].lower()] = a["id"]

        # Danh dau cac thanh phan da duoc match de tranh trung lap
        matched_ids = set()

        for ing in result.product_ingredients:
            # --- So khop truc tiep: ma thanh phan co trong danh sach di ung ---
            if ing["id"] in allergy_ids and ing["id"] not in matched_ids:
                result.matched_allergens.append({
                    "id": ing["id"],
                    "name": ing["name"],
                    "matched_by": "direct"
                })
                matched_ids.add(ing["id"])
                continue

            # --- So khop qua ten goi khac ---
            # Kiem tra ten goi khac cua thanh phan san pham
            # co trung voi ten thanh phan di ung khong
            if ing["id"] not in matched_ids:
                for alias in ing["aliases"]:
                    if alias.lower() in allergy_names:
                        matched_allergy_id = allergy_names[alias.lower()]
                        if matched_allergy_id not in matched_ids:
                            result.matched_allergens.append({
                                "id": ing["id"],
                                "name": ing["name"],
                                "matched_by": f"alias ({alias})"
                            })
                            matched_ids.add(ing["id"])
                            break

        # --- Buoc 4: Phan loai muc canh bao ---
        result.warning_level, result.warning_message = self._classify_warning(result)

        return result

    def _classify_warning(self, result):
        """
        Phan loai muc canh bao.
        
        Quy tac da cap nhat (Nhi phan):
        - SAFE:     Khong co thanh phan di ung nao trung khop
        - CRITICAL: Phat hien it nhat 1 thanh phan di ung (bat ke truc tiep hay gian tiep)
        """
        # Truong hop 1: Khong match bat ky chat nao -> An toan tuyet doi
        if len(result.matched_allergens) == 0:
            return (
                AllergenResultDTO.LEVEL_SAFE,
                "AN TOAN - San pham khong chua thanh phan di ung cua ban."
            )

        # Truong hop 2: Phat hien co chat di ung -> Nguy hiem tuc thi
        # Ghi nhan toan bo ten chat (bao gom ca match truc tiep va qua alias)
        all_names = ", ".join(
            f"{m['name']} ({m['matched_by']})" if m["matched_by"] != "direct" else m['name'] 
            for m in result.matched_allergens
        )
        
        return (
            AllergenResultDTO.LEVEL_CRITICAL,
            f"NGUY HIEM - Phat hien thanh phan di ung: {all_names}. TUYET DOI KHONG SU DUNG!"
        )

    # ===================================================================
    # HAM TIEN ICH: Kiem tra tat ca san pham cho 1 user
    # ===================================================================
    def check_all_products_for_user(self, user_id):
        """
        Kiem tra toan bo san pham trong he thong voi 1 nguoi dung.
        Tra ve list[AllergenResultDTO] da sap xep theo muc canh bao giam dan.
        """
        all_products = self.dao.get_all_products()
        results = []

        for product in all_products:
            result = self._check_allergens(user_id, product)
            results.append(result)

        # Sap xep theo muc canh bao giam dan (Nhi phan: CRITICAL truoc, SAFE sau)
        level_order = {
            AllergenResultDTO.LEVEL_CRITICAL: 0,
            AllergenResultDTO.LEVEL_SAFE: 1,
        }
        results.sort(key=lambda r: level_order.get(r.warning_level, 99))

        return results

    # ===================================================================
    # HAM HIEN THI KET QUA (tien ich in ra console)
    # ===================================================================
    @staticmethod
    def print_result(result):
        """
        In ket qua kiem tra di ung ra console voi dinh dang dep.
        """
        sep = "=" * 60
        sub = "-" * 60

        print(f"\n{sep}")
        print(f"  KET QUA KIEM TRA DI UNG")
        print(sep)

        # Thong tin san pham
        print(f"  San pham  : {result.product_name} ({result.product_id})")
        print(f"  Nhom      : {result.product_group}")

        # Thanh phan san pham
        print(f"\n{sub}")
        print(f"  THANH PHAN SAN PHAM:")
        print(sub)
        if result.product_ingredients:
            for ing in result.product_ingredients:
                alias_str = ""
                if ing["aliases"]:
                    alias_str = f" (con goi: {', '.join(ing['aliases'])})"
                print(f"    - {ing['name']}{alias_str}")
        else:
            print("    (Khong co du lieu thanh phan)")

        # Thanh phan di ung cua user
        print(f"\n{sub}")
        print(f"  THANH PHAN DI UNG CUA BAN:")
        print(sub)
        if result.user_allergies:
            for a in result.user_allergies:
                print(f"    - {a['name']} ({a['id']})")
        else:
            print("    (Ban chua dang ky thanh phan di ung nao)")

        # Ket qua so khop
        print(f"\n{sub}")
        print(f"  KET QUA SO KHOP:")
        print(sub)
        if result.matched_allergens:
            for m in result.matched_allergens:
                print(f"    [X] {m['name']} - phat hien qua: {m['matched_by']}")
        else:
            print("    Khong phat hien thanh phan di ung trong san pham nay.")

        # Muc canh bao
        print(f"\n{sub}")
        level_icon = {
            "SAFE": "[OK]",
            "LOW": "[!]",
            "MEDIUM": "[!!]",
            "HIGH": "[!!!]",
            "CRITICAL": "[XXXX]"
        }
        icon = level_icon.get(result.warning_level, "[?]")
        print(f"  {icon} MUC CANH BAO: {result.warning_level}")
        print(f"  {result.warning_message}")
        print(sep)
