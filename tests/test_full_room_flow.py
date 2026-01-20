import unittest
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options

# Import Pages
from pages.login_page import LoginPage
from pages.hotel_list_page import HotelListPage
from pages.room_update import RoomUpdatePage

class TestFullRoomFlow(unittest.TestCase):

    def setUp(self):
        options = Options()
        self.driver = webdriver.Edge(options=options)
        self.driver.maximize_window()
        # Vào thẳng trang Hotel List
        self.base_url = "https://qa-tms.bizihub.vn/dashboard/hotel-management/list"
        self.driver.get(self.base_url)

    def test_full_flow(self):
        # Init Pages
        login_page = LoginPage(self.driver)
        hotel_page = HotelListPage(self.driver)
        room_page = RoomUpdatePage(self.driver)

        # 1. Login
        print("--- LOGIN ---")
        login_page.login_flow("tmssuperadmin", "tmssuperadmin123")

        # 2. Danh sách ID (Cập nhật từ ảnh của bạn)
        hotel_ids = [
            "bizi42193636", "bizi42193643", "bizi42193678", "bizi42193645",
            "bizi42193670", "bizi42193662", "bizi42193656", "bizi42193652",
            "bizi42193637", "bizi42193666"
        ]

        print(f"--- BẮT ĐẦU CHẠY {len(hotel_ids)} IDs ---")

        for i, hotel_id in enumerate(hotel_ids):
            print(f"\n=== [{i+1}/{len(hotel_ids)}] ID: {hotel_id} ===")
            try:
                # A. Tìm & Mở Form
                hotel_page.search_hotel(hotel_id)
                hotel_page.open_update_form()

                # B. Vào Tab Room
                room_page.click_room_tab()

                # C. CẤU HÌNH CHUNG (Tick Surcharge)
                room_page.tick_surcharge_option(surcharge_name="weekend")

                # D. NHẬP LIỆU (Thứ tự: Price -> Surcharge -> Market)
                
                # 1. Nhập Period & Giá Base
                print("      -> Nhập Giá Base...")
                room_page.input_period_and_price(
                    start_date="20/01/2026", 
                    end_date="25/01/2026", 
                    price="1500000"
                )

                # 2. Nhập Giá Surcharge (Vì đã tick ở trên nên ô này mới hiện ra)
                print("      -> Nhập Giá Surcharge...")
                room_page.input_surcharge_price(sat_price="200000", sun_price="300000")

                # 3. Market Price (Nằm dưới cùng -> Cần scroll)
                print("      -> Thêm & Nhập Market Price...")
                room_page.add_market_price(region="South East Asia", price="1800000")

                # E. LƯU & HOÀN TẤT
                room_page.save_changes()
                
                # Check thông báo
                msg = room_page.get_toast_msg()
                if msg: print(f"         Msg: {msg}")

                # Đóng form
                hotel_page.close_update_form()

            except Exception as e:
                print(f"   -> ❌ LỖI ID {hotel_id}: {e}")
                # HỒI PHỤC: Load lại trang chủ để chạy ID tiếp theo
                try:
                    # Đóng popup nếu còn mở
                    hotel_page.close_update_form()
                    # Quay về danh sách
                    hotel_page.go_to_hotel_list_menu()
                except:
                    self.driver.get(self.base_url)
                    time.sleep(3)

    def tearDown(self):
        print("Done.")
        # self.driver.quit()

if __name__ == "__main__":
    unittest.main()