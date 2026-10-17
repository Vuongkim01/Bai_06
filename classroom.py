# Kim Duy Vương
# 20237410

from datetime import date
from decimal import Decimal
from typing import List, Optional
from enums import DeviceStatus
from devices import Device


class ClassRoom:
    """
    Biểu diễn một phòng học trong trường đại học.
    Kết tập (Aggregation) danh sách các thiết bị được trang bị trong phòng.
    """

    def __init__(self, room_id: str, room_name: str, capacity: int) -> None:
        if not room_id or not room_id.strip():
            raise ValueError("Mã phòng học không được để trống.")
        if not room_name or not room_name.strip():
            raise ValueError("Tên phòng học không được để trống.")
        if capacity <= 0:
            raise ValueError("Sức chứa của phòng học phải lớn hơn 0.")

        self._room_id = room_id.strip()
        self.room_name = room_name.strip()
        self.capacity = capacity
        self._devices: List[Device] = []

    @property
    def room_id(self) -> str:
        """Mã phòng học."""
        return self._room_id

    @property
    def devices(self) -> List[Device]:
        """Trả về bản sao danh sách thiết bị để bảo vệ tính đóng gói."""
        return list(self._devices)

    def add_device(self, device: Device) -> None:
        """
        Thêm một thiết bị vào phòng học.
        Quy tắc:
        1. Không chấp nhận đối tượng thiết bị None.
        2. Không thêm hai thiết bị có cùng mã vào một phòng.
        """
        if device is None:
            raise ValueError("Không chấp nhận đối tượng thiết bị None (null).")

        if self.find_device(device.device_id) is not None:
            raise ValueError(f"Thiết bị có mã '{device.device_id}' đã tồn tại trong phòng '{self.room_id}'.")

        self._devices.append(device)

    def remove_device(self, device_id: str) -> bool:
        """
        Xóa thiết bị khỏi phòng học theo mã thiết bị.
        Trả về True nếu xóa thành công, False nếu không tìm thấy.
        """
        target = self.find_device(device_id)
        if target is not None:
            self._devices.remove(target)
            return True
        return False

    def find_device(self, device_id: str) -> Optional[Device]:
        """
        Tìm kiếm thiết bị trong phòng theo mã (không phân biệt hoa thường).
        Trả về đối tượng Device hoặc None nếu không tồn tại.
        """
        if not device_id or not device_id.strip():
            return None

        normalized_id = device_id.strip().lower()
        for device in self._devices:
            if device.device_id.lower() == normalized_id:
                return device
        return None

    def calculate_annual_maintenance_cost(self) -> Decimal:
        """
        Tính tổng chi phí bảo trì hằng năm của toàn bộ thiết bị trong phòng.
        Sử dụng tính đa hình (Polymorphism): gọi trực tiếp phương thức trên từng đối tượng
        mà không dùng if/switch hay isinstance để kiểm tra lớp cụ thể.
        """
        return sum(
            (device.calculate_annual_maintenance_cost() for device in self._devices),
            start=Decimal("0")
        )

    def get_devices_requiring_maintenance(self) -> List[Device]:
        """
        Lấy danh sách các thiết bị cần bảo trì trong phòng học.
        Điều kiện:
        - Đang ở trạng thái UnderMaintenance; HOẶC
        - Có thời gian sử dụng trên 5 năm tính đến năm hiện tại.
        """
        current_year = date.today().year
        return [
            device for device in self._devices
            if device.status == DeviceStatus.UNDER_MAINTENANCE
            or (current_year - device.year_of_use) > 5
        ]