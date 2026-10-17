# Kim Duy Vương
# 20237410

from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional
from enums import DeviceStatus
from devices import TeachingDevice
from borrowers import IBorrower
from exceptions import (
    DeviceUnavailableException,
    BorrowLimitExceededException,
    InvalidBorrowPeriodException,
    DuplicateDeviceException,
    DeviceNotInSlipException,
    DeviceAlreadyReturnedException,
    InvalidReturnDateException,
)


class BorrowItem:
    """
    Biểu diễn một mục thiết bị được mượn trong phiếu mượn.
    Chỉ tham chiếu đến TeachingDevice; xóa phiếu không làm mất thiết bị khỏi hệ thống.
    """

    def __init__(
        self,
        device: TeachingDevice,
        borrowed_date: date,
        due_date: date,
        from_period: int = 1,
        to_period: int = 3
    ) -> None:
        if device is None:
            raise ValueError("Thiết bị mượn (device) không được None.")
        if due_date < borrowed_date:
            raise ValueError("Hạn trả (due_date) phải sau hoặc bằng ngày mượn (borrowed_date).")
        if from_period <= 0 or to_period < from_period:
            raise ValueError("Tiết kết thúc (to_period) phải lớn hơn hoặc bằng tiết bắt đầu (from_period).")

        self._device: TeachingDevice = device
        self._borrowed_date: date = borrowed_date
        self._due_date: date = due_date
        self.from_period: int = from_period
        self.to_period: int = to_period
        self._returned_date: Optional[date] = None  # Ban đầu là None

    @property
    def device(self) -> TeachingDevice:
        """Thiết bị giảng dạy được mượn."""
        return self._device

    @property
    def borrowed_date(self) -> date:
        """Ngày bắt đầu mượn."""
        return self._borrowed_date

    @property
    def due_date(self) -> date:
        """Hạn phải trả thiết bị."""
        return self._due_date

    @property
    def returned_date(self) -> Optional[date]:
        """Ngày trả thực tế (None nếu chưa trả)."""
        return self._returned_date

    @property
    def is_returned(self) -> bool:
        """Trạng thái đã trả thiết bị hay chưa."""
        return self._returned_date is not None

    @property
    def is_returned_late(self) -> bool:
        """Kiểm tra mục mượn có bị trả muộn so với hạn trả hay không."""
        return self.is_returned and self._returned_date > self._due_date  # type: ignore

    def return_item(self, returned_date: date) -> None:
        """
        Ghi nhận hoàn trả thiết bị.
        Quy tắc:
        - Không được trả một BorrowItem hai lần.
        - Ngày trả không được trước ngày mượn.
        """
        if self.is_returned:
            raise DeviceAlreadyReturnedException(self._device.device_id, self._returned_date)

        if returned_date < self._borrowed_date:
            raise InvalidReturnDateException(self._device.device_id, self._borrowed_date, returned_date)

        self._returned_date = returned_date

    def get_late_days(self) -> int:
        """Tính số ngày trả muộn (trả về 0 nếu trả đúng hạn hoặc chưa trả)."""
        if not self.is_returned_late or self._returned_date is None:
            return 0
        return (self._returned_date - self._due_date).days

    def calculate_late_fee(self) -> Decimal:
        """Tính phí phạt trả muộn của mục thiết bị này."""
        return Decimal(self.get_late_days()) * self._device.daily_late_fee

    def __str__(self) -> str:
        if self.is_returned and self._returned_date is not None:
            status_str = (
                f"Đã trả ngày {self._returned_date.strftime('%d/%m/%Y')} "
                f"(Muộn: {self.get_late_days()} ngày, Phí phạt: {self.calculate_late_fee():,.0f}đ)"
            )
        else:
            status_str = "Chưa trả"

        return (
            f"- [{self.device.device_id}] {self.device.device_name} | "
            f"Mượn: {self.borrowed_date.strftime('%d/%m/%Y')} -> Hạn: {self.due_date.strftime('%d/%m/%Y')} "
            f"(Tiết {self.from_period}-{self.to_period}) | {status_str}"
        )


class BorrowingSlip:
    """
    Lớp quản lý phiếu mượn thiết bị giảng dạy.
    Hợp thành (Composition) danh sách các BorrowItem và liên kết với IBorrower.
    """

    def __init__(
        self,
        slip_id: str,
        borrower: IBorrower,
        teaching_room: str,
        borrowed_date: date
    ) -> None:
        if not slip_id or not slip_id.strip():
            raise ValueError("Mã phiếu mượn (slip_id) không được để trống.")
        if borrower is None:
            raise ValueError("Người mượn (borrower) không được None.")
        if not teaching_room or not teaching_room.strip():
            raise ValueError("Phòng dạy (teaching_room) không được để trống.")

        self._slip_id: str = slip_id.strip()
        self._borrower: IBorrower = borrower
        self._teaching_room: str = teaching_room.strip()
        self._borrowed_date: date = borrowed_date
        self._items: List[BorrowItem] = []

    @property
    def slip_id(self) -> str:
        """Mã phiếu mượn."""
        return self._slip_id

    @property
    def borrower(self) -> IBorrower:
        """Người đứng tên mượn phiếu."""
        return self._borrower

    @property
    def teaching_room(self) -> str:
        """Phòng học sử dụng thiết bị."""
        return self._teaching_room

    @property
    def borrowed_date(self) -> date:
        """Ngày lập phiếu mượn."""
        return self._borrowed_date

    @property
    def items(self) -> List[BorrowItem]:
        """Danh sách chỉ đọc (bản sao) các mục mượn trong phiếu."""
        return list(self._items)

    def _validate_borrowing(self, device: TeachingDevice, borrow_days: int) -> None:
        """
        Kiểm tra toàn bộ điều kiện nghiệp vụ trước khi thêm thiết bị vào phiếu.
        Đảm bảo nếu có bất kỳ vi phạm nào thì ném ngoại lệ ngay, không làm thay đổi trạng thái hệ thống.
        """
        # 1. Thiết bị không được None
        if device is None:
            raise ValueError("Thiết bị cần mượn không được None.")

        # 2. Thiết bị chưa tồn tại trong phiếu
        if any(item.device.device_id.lower() == device.device_id.lower() for item in self._items):
            raise DuplicateDeviceException(device.device_id)

        # 3. Người mượn chưa đạt giới hạn số lượng thiết bị tối đa
        if len(self._items) >= self._borrower.get_maximum_devices():
            raise BorrowLimitExceededException(
                self._borrower.borrower_id,
                self._borrower.get_maximum_devices()
            )

        # 4. Thiết bị phải đang ở trạng thái Available
        if device.status != DeviceStatus.AVAILABLE:
            raise DeviceUnavailableException(device.device_id, device.status)

        # 5. Số ngày mượn phải lớn hơn 0 và không vượt quá giới hạn cho phép của thiết bị
        if borrow_days <= 0 or borrow_days > device.max_borrow_days:
            raise InvalidBorrowPeriodException(device.device_id, borrow_days, device.max_borrow_days)

    def add_device(self, device: TeachingDevice, borrow_days: int) -> None:
        """
        Thêm một thiết bị vào phiếu mượn theo hướng an toàn (Transactional Consistency):
        1. Kiểm tra toàn bộ điều kiện hợp lệ.
        2. Tạo đối tượng BorrowItem.
        3. Chuyển trạng thái thiết bị sang Borrowed.
        4. Thêm item vào danh sách của phiếu.
        """
        self._validate_borrowing(device, borrow_days)

        due_date = self._borrowed_date + timedelta(days=borrow_days)
        item = BorrowItem(device=device, borrowed_date=self._borrowed_date, due_date=due_date)

        device.mark_as_borrowed()
        self._items.append(item)

    def return_device(self, device_id: str, returned_date: date) -> Decimal:
        """
        Thực hiện trả thiết bị theo mã thiết bị và ngày trả.
        Trả về phí phạt trả muộn (nếu có).
        """
        # 1. Kiểm tra device_id hợp lệ
        if not device_id or not device_id.strip():
            raise ValueError("Mã thiết bị cần trả không được để trống.")

        # 2. Tìm BorrowItem theo mã thiết bị
        normalized_id = device_id.strip().lower()
        target_item: Optional[BorrowItem] = next(
            (item for item in self._items if item.device.device_id.lower() == normalized_id),
            None
        )

        # 3. Nếu không tìm thấy trong phiếu -> phát sinh DeviceNotInSlipException
        if target_item is None:
            raise DeviceNotInSlipException(device_id.strip(), self._slip_id)

        # 4, 5 & 6. Kiểm tra đã trả chưa, kiểm tra ngày trả hợp lệ và ghi nhận ngày trả
        # (Nếu vi phạm sẽ ném ngoại lệ ngay bên trong return_item, thiết bị không bị đổi trạng thái sai)
        target_item.return_item(returned_date)

        # 7. Chuyển trạng thái thiết bị về Available
        target_item.device.mark_as_available()

        return target_item.calculate_late_fee()

    def calculate_total_late_fee(self) -> Decimal:
        """Tính tổng phí phạt trả muộn của toàn bộ các mục trong phiếu."""
        return sum((item.calculate_late_fee() for item in self._items), start=Decimal("0"))

    def has_late_or_unreturned_items(self) -> bool:
        """Kiểm tra phiếu có chứa thiết bị chưa trả hoặc trả muộn hay không."""
        return any(not item.is_returned or item.is_returned_late for item in self._items)

    def __str__(self) -> str:
        lines = [
            f"Phiếu mượn [{self.slip_id}] | Phòng dạy: {self.teaching_room} | Ngày mượn: {self.borrowed_date.strftime('%d/%m/%Y')}",
            f"Người mượn: {self.borrower}",
            "Danh sách thiết bị:"
        ]
        for item in self._items:
            lines.append(f"  {item}")
        lines.append(f"Tổng phí phạt trả muộn: {self.calculate_total_late_fee():,.0f}đ")
        return "\n".join(lines)