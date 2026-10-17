# Kim Duy Vương
# 20237410

from datetime import date, timedelta
from decimal import Decimal
from typing import Callable, List

from enums import DeviceStatus
from exceptions import BorrowingException
from devices import ProjectorRemote, AirConditionerRemote, WirelessMicrophone
from classroom import ClassRoom
from borrowers import Lecturer, TeachingAssistant
from borrowing import BorrowingSlip


def run_exception_test(test_title: str, action: Callable[[], None], slip: BorrowingSlip) -> None:
    """
    Hàm hỗ trợ thực thi kiểm thử ngoại lệ với khối try - except - finally
    và kiểm chứng tính nhất quán của phiếu mượn sau khi thao tác thất bại.
    """
    print(f"\n--- {test_title} ---")
    try:
        action()
    except BorrowingException as ex:
        print(f"[Bắt ngoại lệ thành công - {type(ex).__name__}]: {ex}")
    except Exception as ex:
        print(f"[Lỗi hệ thống khác - {type(ex).__name__}]: {ex}")
    finally:
        print(f"[Finally - Kiểm tra nhất quán] Phiếu '{slip.slip_id}' hiện có {len(slip.items)} thiết bị.")


def main() -> None:
    print("=" * 84)
    print("       HỆ THỐNG QUẢN LÝ THIẾT BỊ GIẢNG DẠY VÀ HỢP ĐỒNG BẢO TRÌ (PYTHON)")
    print("=" * 84 + "\n")

    # =========================================================================
    # 1. KIỂM THỬ MỤC 3: QUẢN LÝ PHÒNG HỌC & CHI PHÍ BẢO TRÌ (KẾT TẬP & ĐA HÌNH)
    # =========================================================================
    print(">>> 1. KIỂM THỬ QUẢN LÝ PHÒNG HỌC & CHI PHÍ BẢO TRÌ (ĐA HÌNH)")
    room_d3 = ClassRoom("D3-201", "Phòng học đa phương tiện D3-201", capacity=80)

    prj_room = ProjectorRemote("PRJ-01", "Điều khiển máy chiếu Sony", 2024, Decimal("500000"))
    ac_room = AirConditionerRemote(
        "AC-01", "Điều khiển điều hòa Daikin", 2019, Decimal("400000"),
        status=DeviceStatus.UNDER_MAINTENANCE
    )
    mic_room = WirelessMicrophone("MIC-01", "Micro không dây Shure", 2020, Decimal("1500000"))

    room_d3.add_device(prj_room)
    room_d3.add_device(ac_room)
    room_d3.add_device(mic_room)

    print(f"Phòng: {room_d3.room_name} ({room_d3.room_id}) - Sức chứa: {room_d3.capacity} SV")
    for dev in room_d3.devices:
        print(f"  + {dev}")

    print(f"=> Tổng chi phí bảo trì dự kiến/năm (Đa hình): {room_d3.calculate_annual_maintenance_cost():,.0f}đ")
    print("=> Danh sách thiết bị cần bảo trì (UnderMaintenance hoặc sử dụng > 5 năm):")
    for dev in room_d3.get_devices_requiring_maintenance():
        print(f"  * [{dev.device_id}] {dev.device_name} (Năm SD: {dev.year_of_use}, Trạng thái: {dev.status.value})")
    print()

    # =========================================================================
    # 2. KIỂM THỬ MỤC 11.1: LUỒNG NGHIỆP VỤ THÀNH CÔNG
    # =========================================================================
    print("=" * 84)
    print(">>> 2. KIỂM THỬ MỤC 11.1: LUỒNG NGHIỆP VỤ THÀNH CÔNG")
    print("=" * 84)

    all_slips: List[BorrowingSlip] = []
    borrow_date = date(2026, 10, 10)

    try:
        # 1. Tạo một giảng viên
        lecturer = Lecturer("GV001", "TS. Nguyễn Văn An")

        # 2. Tạo 1 điều khiển máy chiếu, 1 điều khiển điều hòa và 1 micro không dây
        prj_01 = ProjectorRemote("TB-PRJ01", "Điều khiển máy chiếu Epson", 2024, Decimal("450000"), max_borrow_days=2)
        ac_01 = AirConditionerRemote("TB-AC01", "Điều khiển điều hòa Panasonic", 2023, Decimal("350000"), max_borrow_days=5)
        mic_01 = WirelessMicrophone("TB-MIC01", "Micro không dây Sennheiser", 2025, Decimal("1800000"), max_borrow_days=1)

        # 3. Tạo phiếu mượn cho một phòng dạy
        slip_01 = BorrowingSlip("PM-001", lecturer, "D5-102", borrow_date)
        all_slips.append(slip_01)

        # 4. Thêm điều khiển máy chiếu và micro vào phiếu
        slip_01.add_device(prj_01, borrow_days=2)  # Hạn trả: 12/10/2026
        slip_01.add_device(mic_01, borrow_days=1)  # Hạn trả: 11/10/2026
        print("[Thành công] Đã thêm Điều khiển máy chiếu (TB-PRJ01) và Micro (TB-MIC01) vào phiếu PM-001.")

        # 5. Trả điều khiển máy chiếu đúng hạn (12/10/2026)
        fee_prj = slip_01.return_device("TB-PRJ01", date(2026, 10, 12))
        print(
            f"[Trả đúng hạn] Đã trả TB-PRJ01 ngày 12/10/2026. "
            f"Phí phạt: {fee_prj:,.0f}đ | Trạng thái thiết bị: {prj_01.status.value}"
        )

        # 6. Trả micro muộn 2 ngày (Hạn 11/10/2026 -> Trả ngày 13/10/2026)
        fee_mic = slip_01.return_device("TB-MIC01", date(2026, 10, 13))
        print(
            f"[Trả muộn 2 ngày] Đã trả TB-MIC01 ngày 13/10/2026. "
            f"Phí phạt: {fee_mic:,.0f}đ | Trạng thái thiết bị: {mic_01.status.value}"
        )

        # Tạo thêm 1 phiếu chứa thiết bị chưa trả để minh họa đầy đủ mục 7
        slip_02 = BorrowingSlip("PM-002", lecturer, "D3-304", borrow_date)
        slip_02.add_device(ac_01, borrow_days=3)
        all_slips.append(slip_02)

        # 7. Hiển thị các phiếu trả muộn hoặc chưa trả
        print("\n--- DANH SÁCH CÁC PHIẾU TRẢ MUỘN HOẶC CHƯA TRẢ ---")
        for slip in all_slips:
            if slip.has_late_or_unreturned_items():
                print(slip)
                print("-" * 60)

    except BorrowingException as ex:
        print(f"[Lỗi nghiệp vụ không mong đợi]: {ex}")
    finally:
        print("[Finally] Hoàn tất kiểm thử luồng thành công 11.1.\n")

    # =========================================================================
    # 3. KIỂM THỬ MỤC 11.2: LUỒNG PHÁT SINH NGOẠI LỆ (7 TÌNH HUỐNG)
    # =========================================================================
    print("=" * 84)
    print(">>> 3. KIỂM THỬ MỤC 11.2: 7 TÌNH HUỐNG PHÁT SINH NGOẠI LỆ & TÍNH NHẤT QUÁN")
    print("=" * 84)

    assistant = TeachingAssistant("TG001", "ThS. Trần Thị Bình")  # Tối đa 2 thiết bị
    slip_test = BorrowingSlip("PM-TEST", assistant, "TC-205", borrow_date)

    ac_broken = AirConditionerRemote(
        "TB-AC-ERR", "ĐK Điều hòa Gree", 2022, Decimal("300000"),
        status=DeviceStatus.UNDER_MAINTENANCE
    )
    prj_valid_1 = ProjectorRemote("TB-PRJ-01", "ĐK Máy chiếu BenQ", 2024, Decimal("400000"), max_borrow_days=2)
    ac_valid_2 = AirConditionerRemote("TB-AC-02", "ĐK Điều hòa Casper", 2024, Decimal("350000"), max_borrow_days=5)
    mic_valid_3 = WirelessMicrophone("TB-MIC-03", "Micro không dây AAP", 2024, Decimal("1200000"), max_borrow_days=1)
    prj_outside = ProjectorRemote("TB-PRJ-OUT", "ĐK Máy chiếu ngoài phiếu", 2024, Decimal("400000"))

    # Tình huống 1: Mượn điều khiển điều hòa đang UnderMaintenance
    run_exception_test(
        "Tình huống 1: Mượn ĐK điều hòa đang UnderMaintenance",
        lambda: slip_test.add_device(ac_broken, borrow_days=1),
        slip_test
    )

    # Tình huống 3: Thêm cùng một micro hai lần vào cùng phiếu
    def test_duplicate_mic() -> None:
        slip_test.add_device(mic_valid_3, borrow_days=1)  # Lần 1 thành công (Tổng = 1 thiết bị)
        slip_test.add_device(mic_valid_3, borrow_days=1)  # Lần 2 phát sinh DuplicateDeviceException

    run_exception_test(
        "Tình huống 3: Thêm cùng một micro hai lần vào cùng phiếu",
        test_duplicate_mic,
        slip_test
    )

    # Tình huống 2: Trợ giảng mượn thiết bị thứ ba (Hạn mức trợ giảng = 2 thiết bị)
    def test_assistant_limit() -> None:
        slip_test.add_device(ac_valid_2, borrow_days=2)   # Thiết bị thứ 2 thành công (Tổng = 2 thiết bị)
        slip_test.add_device(prj_valid_1, borrow_days=1)  # Thiết bị thứ 3 phát sinh BorrowLimitExceededException

    run_exception_test(
        "Tình huống 2: Trợ giảng mượn thiết bị thứ ba (vượt hạn mức 2 thiết bị)",
        test_assistant_limit,
        slip_test
    )

    # Tình huống 4: Mượn micro trong 3 ngày dù giới hạn là 1 ngày
    slip_period_test = BorrowingSlip("PM-PERIOD", Lecturer("GV002", "PGS. Lê Hoàng"), "D9-401", borrow_date)
    mic_limit_1day = WirelessMicrophone("TB-MIC-LIM", "Micro giới hạn 1 ngày", 2025, Decimal("1500000"), max_borrow_days=1)
    run_exception_test(
        "Tình huống 4: Mượn micro trong 3 ngày dù giới hạn tối đa là 1 ngày",
        lambda: slip_period_test.add_device(mic_limit_1day, borrow_days=3),
        slip_period_test
    )

    # Tình huống 5: Trả một điều khiển máy chiếu không thuộc phiếu
    run_exception_test(
        "Tình huống 5: Trả một điều khiển máy chiếu không thuộc phiếu",
        lambda: slip_test.return_device(prj_outside.device_id, borrow_date + timedelta(days=1)),
        slip_test
    )

    # Tình huống 6: Trả cùng một thiết bị hai lần
    def test_return_twice() -> None:
        slip_test.return_device(mic_valid_3.device_id, borrow_date + timedelta(days=1))  # Lần 1 thành công
        slip_test.return_device(mic_valid_3.device_id, borrow_date + timedelta(days=1))  # Lần 2 ném ngoại lệ

    run_exception_test(
        "Tình huống 6: Trả cùng một thiết bị hai lần",
        test_return_twice,
        slip_test
    )

    # Tình huống 7: Trả thiết bị với ngày trả trước ngày mượn
    run_exception_test(
        "Tình huống 7: Trả thiết bị với ngày trả trước ngày mượn",
        lambda: slip_test.return_device(ac_valid_2.device_id, borrow_date - timedelta(days=2)),
        slip_test
    )


if __name__ == "__main__":
    main()