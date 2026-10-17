# Kim Duy Vương
# 20237410

from enum import Enum


class DeviceStatus(Enum):
    """
    Trạng thái hoạt động và mượn trả của thiết bị.
    Kết hợp đầy đủ các trạng thái mượn trả và vòng đời bảo trì.
    """
    AVAILABLE = "Available"                  # Sẵn sàng cho mượn / Đang hoạt động tốt
    BORROWED = "Borrowed"                    # Đang được mượn
    UNDER_MAINTENANCE = "UnderMaintenance"  # Đang bảo trì, sửa chữa
    RETIRED = "Retired"                      # Ngừng sử dụng / Đã thanh lý

    def __str__(self) -> str:
        return self.value