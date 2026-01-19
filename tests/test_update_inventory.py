import unittest
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
# Import Page Objects
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

class TestInventoryUpdate(unittest.TestCase):

    def setUp(self):
        # Cấu hình Driver
        options = Options()
        # options.add_argument("user-data-dir=...") # Bỏ comment nếu dùng User Data
        self.driver = webdriver.Edge(options=options)
        self.driver.maximize_window()
        self.driver.get("https://qa-tms.bizihub.vn/dashboard/room-inventory-management")

    def test_run_inventory_update(self):
        # 1. Khởi tạo Pages
        login_page = LoginPage(self.driver)
        inventory_page = InventoryPage(self.driver)

        # 2. Login (Nếu cần)
        login_page.login_flow("tmssuperadmin", "tmssuperadmin123")

        # 3. Vào menu chính
        inventory_page.go_to_inventory_menu()

        # 3.1 Vào Trang Inventory
        # Gọi hàm click menu đã viết trong inventory_page.py
        inventory_page.go_to_inventory_menu()

        # 4. Danh sách ID (Dữ liệu tách biệt logic)
        hotel_ids = [
            "bizi42193636", "bizi42193643", "bizi42193678", "bizi42193645",
            "bizi42193670", "bizi42193662", "bizi42193656", "bizi42193652",
            "bizi42193637", "bizi42193666"
        ]

        print(f"--- BẮT ĐẦU XỬ LÝ {len(hotel_ids)} KHÁCH SẠN ---")

        for index, hotel_id in enumerate(hotel_ids):
            print(f"\n[{index + 1}/{len(hotel_ids)}] Đang xử lý ID: {hotel_id}")
            try:
                # Các bước nghiệp vụ rõ ràng:
                inventory_page.search_hotel(hotel_id)
                inventory_page.open_update_form()
                inventory_page.change_all_request_to_available()
                inventory_page.close_update_form()
                
            except Exception as e:
                print(f"   -> ❌ Lỗi ID {hotel_id}: {e}")
                # Nếu lỗi, click lại menu để reset trang
                inventory_page.go_to_inventory_menu()

    def tearDown(self):
        print("Hoàn thành bài test.")
        # self.driver.quit()

if __name__ == "__main__":
    unittest.main()