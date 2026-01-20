import unittest
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options

from pages.login_page import LoginPage
from pages.hotel_list_page import HotelListPage
from pages.room_update import RoomUpdatePage

class TestRoomUpdate(unittest.TestCase):

    def setUp(self):
        options = Options()
        self.driver = webdriver.Edge(options=options)
        self.driver.maximize_window()
        self.driver.get("https://qa-tms.bizihub.vn/dashboard/hotel-management/list")

    def test_update_and_create_room(self):
        login_page = LoginPage(self.driver)
        hotel_list_page = HotelListPage(self.driver)
        room_page = RoomUpdatePage(self.driver)

        print("\n--- 1. ĐĂNG NHẬP ---")
        login_page.login_flow("tmssuperadmin", "tmssuperadmin123")

        hotel_ids = [
            "bizi1756240234", "bizi42193643"
        ]

        print(f"--- 2. BẮT ĐẦU XỬ LÝ {len(hotel_ids)} KHÁCH SẠN ---")

        for index, hotel_id in enumerate(hotel_ids):
            print(f"\n[{index + 1}/{len(hotel_ids)}] Đang xử lý ID: {hotel_id}")
            try:
                # A. Tìm & Mở Form
                hotel_list_page.search_hotel(hotel_id)
                hotel_list_page.open_update_form()

                # B. Vào Tab Room
                room_page.click_room_management_tab()

                # C. Xử lý Phòng 1: Area + Amenities (o) + View (o)
                room_page.fill_first_room_basic(area="28")
                
                # D. UPDATE (Lưu lần 1)
                room_page.submit_update()
                
                # E. ADD ROOM
                room_page.add_new_room()
                
                # F. Xử lý Phòng Mới: Full info + Bed Type (p)
                room_page.fill_last_new_room(
                    name_vi="Phòng Gia Đình VIP",
                    name_en="VIP Family Room",
                    area="45",
                    max_occ="3",
                    adult="2",
                    child="2"
                )

                # G. UPDATE (Lưu lần 2)
                room_page.submit_update()

                msg = room_page.get_toast_message()
                if msg: print(f"         Thông báo: {msg}")

                hotel_list_page.close_update_form()

            except Exception as e:
                print(f"   -> ❌ Lỗi ID {hotel_id}: {e}")
                try:
                    hotel_list_page.close_update_form()
                    hotel_list_page.go_to_hotel_list_menu()
                except:
                    self.driver.get("https://qa-tms.bizihub.vn/dashboard/hotel-management/list")
                    time.sleep(3)

    def tearDown(self):
        print("Hoàn thành test.")
        # self.driver.quit()

if __name__ == "__main__":
    unittest.main()